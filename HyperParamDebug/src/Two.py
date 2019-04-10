from Grahp_exp import Graph
import os
import numpy as np
import math
import copy


"""
同一速度的车辆放在一个集合当中
"""
class DispatchCar(object):
    def __init__(self, graph:Graph, timeStamp, sliceNum, timeAdd, carGoingNumber, timeAddSpeed):
        self.graph = graph
        self.timeAndPath = []
        self.upCar = []
        self.downCar = []
        self.timeStamp = timeStamp
        self.sliceNum = sliceNum
        self.timeAdd = timeAdd
        self.carGoingNumber = carGoingNumber
        self.timeAddSpeed = timeAddSpeed

    #计算跑完路程所需的代价
    def computeCost(self):
        roadLineRaw= self.graph.findCarShortPathNotUpdate()
        carCost = []
        for i in range(len(self.graph.cars.carsInfo)):
            cost = 0  # 计算每一车按照最短路径行驶的时间
            info = []
            info.append(self.graph.cars.carsInfo[i].planTime)
            # 计算每一辆车跑完整个路径需要的时间
            for timeIndex in range(len(roadLineRaw[i])):
                cost = cost + 0.9 * self.graph.rRoads.roadsInfo[roadLineRaw[i][timeIndex] - 5000].channel + 0.1 * self.graph.rRoads.roadsInfo[roadLineRaw[i][timeIndex] - 5000].speed
            carCost.append(cost)
        return carCost

    #给出每一辆车所走路径以及所需花费的时间片
    def computeTimeandPath(self):
        roadLine = self.graph.findCarShortPath()
        cost = self.computeCost()
        # 为每一辆车计算跑完整个路径所需的时间片（只考虑一辆车跑的情况）
        for i in range(len(self.graph.cars.carsInfo)):
            count = 0  # 计算每一车按照最短路径行驶的时间
            nextGoLength = 0  # 下一条路能够行驶的距离
            info = []
            info.append(int(self.graph.cars.carsInfo[i].id))
            info.append(self.graph.cars.carsInfo[i].planTime)
            info.append(self.graph.cars.carsInfo[i].speed)
            # 计算每一辆车跑完整个路径需要的时间
            for timeIndex in range(len(roadLine[i])):
                # print(ros.roadsInfo[roadLine[timeIndex] - 5000])
                remainLength = self.graph.rRoads.roadsInfo[roadLine[i][timeIndex] - 5000].length - nextGoLength  # 定义当前路段剩余的距离
                # print(remainLength)
                while (remainLength):
                    count = count + 1
                    nowSpeed = min(self.graph.rRoads.roadsInfo[roadLine[i][timeIndex] - 5000].speed,
                                   self.graph.cars.carsInfo[i].speed)  # 当前道路能够行驶的速度
                    if (timeIndex >= len(roadLine[i]) - 1):
                        nextSpeed = 0  # 接下来道路能够行驶的速度
                    else:
                        nextSpeed = min(self.graph.cars.carsInfo[i].speed, self.graph.rRoads.roadsInfo[roadLine[i][timeIndex + 1] - 5000].speed)
                    # print(nowSpeed)
                    # print(nextSpeed)
                    nowLength = nowSpeed
                    nextLength = nextSpeed
                    if remainLength >= nowLength:  # 剩余道路有空余可走
                        remainLength = remainLength - nowLength  # 当前道路剩余路径
                    else:  # 剩余道路没有一个时间片可走
                        if (nextLength - remainLength < 0):  # 当前道路的剩余路径大于下一路口能够使用的
                            remainLength = 0  #
                        else:
                            nextGoLength = nextLength - remainLength
                            remainLength = 0
            #print(count)
            info.extend(roadLine[i])
            info.append(cost[i])
            self.timeAndPath.append(info)

    def statisticSameSpeed(self):
        self.computeTimeandPath()
        self.timeAndPath.sort(key=lambda x : x[2])
        sameSpeedCars = self.staticDifferentValueByCol(self.timeAndPath, 2)#字典，字典当中存放的为相应的车辆的路径新洗
        speedSet = self.getValueSet(self.timeAndPath, 2)#不同的速度的集合
        #timeSumSet = self.getValueSet(self.timeAndPath, -1)#花费的总时间
        timeSumSet = {}
        for i in speedSet:
            sameSpeedCars[i].sort(key=lambda x : x[-1])#根据走完所有路程所需要时间进行排序
            timeSumSet[i] = self.getValueSet(sameSpeedCars[i], -1)  # 花费的总时间
        return speedSet, sameSpeedCars#得到速度的集合以及相应速度的车辆集合

    #确定发车策略
    def DispatchCarBySpeed(self):
        timeStamp = self.timeStamp
        speedSet, sameSpeedCars = self.statisticSameSpeed()#返回速度集合以及相同速度车辆集合
        speedList = list(speedSet)
        speedList.sort(key=lambda x: x, reverse=True)  # 转换为列表然后降序排列
        sliceNum = self.sliceNum#相同速度拥有多少个时间片
        timeAdd = self.timeAdd#时间间隔
        maxSpeed = speedList[0]#最大速度
        minWeight = float('inf')
        maxWeight = 0
        for i in speedList:
            for j in range(len(sameSpeedCars[i])):
                if(minWeight > sameSpeedCars[i][j][-1]):
                    minWeight = sameSpeedCars[i][j][-1]
                if(maxWeight < sameSpeedCars[i][j][-1]):
                    maxWeight = sameSpeedCars[i][j][-1]
        cutOffLine = (maxWeight - minWeight) / sliceNum
        cutLineList = []
        for i in range(sliceNum):
            cutLineList.extend([minWeight + i * cutOffLine])
        cutLineList.sort(key=lambda x:x,reverse=True)
        #cutLineList.extend([maxWeight])
        weightDict = {}
        costIndex = 0
        sameSpeedCarsInfo = copy.deepcopy(sameSpeedCars)
        carGoingNumber = self.carGoingNumber
        ans = []
        for i in speedList:#相同速度进行统计
            costIndex = 0
            for k in range(len(cutLineList)):
                info = []
                for j in range(len(sameSpeedCars[i])):
                    if(sameSpeedCars[i][j][-1] != 0 and sameSpeedCars[i][j][-1] >= cutLineList[k]):
                        info.append(sameSpeedCarsInfo[i][j])
                        sameSpeedCars[i][j][-1] = 0
                weightDict[costIndex] = info#相同速度下的同样的权重
                costIndex = costIndex + 1
            #发车策略
            for l in range(costIndex):#扫面同一权重索引的车辆
                carCount = 0
                realPlanTime = (maxSpeed / i) * 35 * ((minWeight + (sliceNum - l - 1) * cutOffLine) / maxWeight) + timeStamp
                for m in range(len(weightDict[sliceNum - l - 1])):
                    tmp = []
                    if ((carCount != 0) and (carCount % carGoingNumber == 0)):
                        realPlanTime = realPlanTime + timeAdd
                    weightDict[sliceNum - l - 1][carCount][1] = max(weightDict[sliceNum - l - 1][carCount][1], math.ceil(realPlanTime))
                    tmp.extend(weightDict[sliceNum - l - 1][carCount][0:2])
                    tmp.extend(weightDict[sliceNum - l - 1][carCount][3:-1])
                    ans.append(tmp)
                    carCount = carCount + 1
            weightDict = {}
            timeAddSpeed = self.timeAddSpeed  # 可调参数35->30->25
            timeStamp = timeStamp + timeAddSpeed * (maxSpeed - i)
        return ans

    def writeToFile(self):
        ans = self.DispatchCarBySpeed()
        if os.path.exists(self.graph.answer_path):  # 判断是否存在文件，有则删除
            os.remove(self.graph.answer_path)
        file = open(self.graph.answer_path, 'a')
        #file.write(str("#(carId,StartTime,RoadId...)")+'\n')
        for j in range(len(ans)):
                result = tuple(ans[j])
                file.seek(0)
                file.write(str(result) + '\n')
        file.close()



    def staticDifferentValueByCol(self, listInfo, index):
        timeSet = set()
        for i in range(len(listInfo)):
            #print(listInfo[i][index])
            timeSet.add(listInfo[i][index])
        indexAdd = 0
        countTime = 0
        tmpList = {}
        for i in timeSet:
            indexAdd = indexAdd + countTime
            countTime = 0
            info = []
            for j in range(len(listInfo)):
                if(listInfo[j][index] == i):
                    countTime = countTime + 1
                    info.append(listInfo[j])

            tmpList[i]=info
        return tmpList

    def getValueSet(self, listInfo, index):
        NodeSet = set()
        for i in range(len(listInfo)):
            #print(listInfo[i][index])
            NodeSet.add(listInfo[i][index])
        return NodeSet
    #判断每一个车辆的方向，然后根据方向来进行选择性发车


if __name__ == "__main__":
    car_path = "../config/car.txt"
    road_path = "../config/road.txt"
    cross_path = "../config/cross.txt"
    answer_path = "../config/answer.txt"

    trafficMap = Graph(car_path, road_path, cross_path, answer_path, 200)#生成交通图
    DispatchSystem = DispatchCar(trafficMap, 1, 4, 15, 160, 20)
    DispatchSystem.writeToFile()
