from Grahp_exp import Graph
import os
import numpy as np
import math
"""
同一速度的车辆放在一个集合当中
"""
class DispatchCar(object):
    def __init__(self, graph:Graph):
        self.graph = graph
        self.timeAndPath = []
        self.upCar = []
        self.downCar = []

    #给出每一辆车所走路径以及所需花费的时间片
    def computeTimeandPath(self):
        roadLine = self.graph.findCarShortPath()
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
            info.append(count)
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

    #将所有的权重根据大小之间划分为很多的区间
    def splitSameSpeddCarByCost(self):
        sliceNum = 4#划分的区间的个数，超参数可调整
        speedSet, sameSpeedCars = self.statisticSameSpeed()  # 返回速度集合以及相同速度车辆集合
        speedList = list(speedSet)
        speedList.sort(key=lambda x: x, reverse=True)#转换为列表然后降序排列
        #统计出最大的花费时间以及最小的花费时间
        minCost =float('inf')
        maxCost = 0
        #统计车辆运行过程当中所需的最大和最小花费
        for i in speedList:
            for j in range(len(sameSpeedCars[i])):
                if (maxCost < sameSpeedCars[i][j][-1]):
                    maxCost = sameSpeedCars[i][j][-1]
                if(minCost > sameSpeedCars[i][j][-1]):
                    minCost = sameSpeedCars[i][j][-1]
        #对花费区间进行切片，求出划分的基准线（minCost）——||——||——||——||（maxCost）
        baseSplitLine = (maxCost - minCost) / sliceNum
        splitLine = []
        for i in range(1, sliceNum):
            splitLine.extend(minCost + i * baseSplitLine)
        splitLine.extend(maxCost)#储存划分的标记点
        #得到每一个权重段的车辆信息
        for i in speedList:
            for j in range(len(sameSpeedCars[i])):
                pass




    #确定发车策略
    def DispatchCarBySpeed(self):
        speedSet, sameSpeedCars = self.statisticSameSpeed()#返回速度集合以及相同速度车辆集合
        speedList = list(speedSet)
        speedList.sort(key=lambda x: x, reverse=True)  # 转换为列表然后降序排列
        sliceNum = 4
        batchSize = 1000#时间片的个数
        batchTime = 1000#时间大小
        timeCount = 1
        realTime = 1
        qTime = 0
        for i in speedList:#依次为8 6 2 4
            sameSpeedCarListLength = len(sameSpeedCars[i])#统计当前速度相同的车辆的个数
            carNumEachSlice = sameSpeedCarListLength / sliceNum#每一时间片车辆的个数

        for i in speedList:
            for j in range(len(sameSpeedCars[i])):
                timeCount = timeCount + 1
                if ((timeCount % (len(sameSpeedCars[i]) // batchSize)) == 0):
                    qTime = qTime + 1
                    realTime = qTime * math.ceil(batchTime / batchSize)
                sameSpeedCars[i][j][1] = max(sameSpeedCars[i][j][1], realTime)
        return sameSpeedCars, speedList



    def writeToFile(self):
        sameSpeedCars, speedList = self.DispatchCarBySpeed()
        if os.path.exists(self.graph.answer_path):  # 判断是否存在文件，有则删除
            os.remove(self.graph.answer_path)
        file = open(self.graph.answer_path, 'a')
        file.write(str("#(carId,StartTime,RoadId...)")+'\n')
        for i in speedList:
            for j in range(len(sameSpeedCars[i])):
                ans = [sameSpeedCars[i][j][0], sameSpeedCars[i][j][1]]
                ans.extend(sameSpeedCars[i][j][3 : -1])
                result = tuple(ans)
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
    DispatchSystem = DispatchCar(trafficMap)
    DispatchSystem.computeTimeandPath()
    print("xixi")
