from Grahp_exp import Graph
import os
import numpy as np
import math
"""
调度系统，为车辆安排最右的出发时间以及路径n
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

    """
    统计车辆的方向,然后将车辆分方向不同安排发车
    """
    def staticDirectionOfCars(self):
        self.computeTimeandPath()#车辆出发经过的相应节点都储存在nodePath这个属性当中
        print(self.timeAndPath[6413])
        for i in range(len(self.graph.cars.carsInfo)):
            if self.graph.cCross.crossInfo[int(self.graph.nodePath[i][-1])].y > self.graph.cCross.crossInfo[int(self.graph.nodePath[i][0])].y:
                carDirection = 1#代表方向向上
                upCarInfo = [self.graph.cars.carsInfo[i].id, self.graph.cars.carsInfo[i].planTime]
                upCarInfo.extend(self.timeAndPath[i][2:-1])
                self.upCar.append(upCarInfo)
            else:
                carDirection = 0#代表起点到终点之间的方向向下
                downCarInfo = [self.graph.cars.carsInfo[i].id, self.graph.cars.carsInfo[i].planTime]
                downCarInfo.extend(self.timeAndPath[i][2:-1])
                self.downCar.append(downCarInfo)
        self.upCar.sort(key = lambda x: x[1])
        self.downCar.sort(key = lambda x: x[1])
        upCarDict = self.staticDifferentValueByCol(self.upCar, 1)
        downCarDict = self.staticDifferentValueByCol(self.downCar, 1)

        #添加每一辆车跑完全程所需时间
        for i in range(1, len(upCarDict) + 1):
            for j in range(len(upCarDict[i])):
                #print(j)
                tmpIndex = self.timeAndPath[int(upCarDict[i][j][0]) - 10000][-1]
                upCarDict[i][j].extend([tmpIndex])
            upCarDict[i].sort(key=lambda x: x[-1])

        for i in range(1, len(downCarDict) + 1):
            for j in range(len(downCarDict[i])):
                tmpIndex = self.timeAndPath[int(downCarDict[i][j][0]) - 10000][-1]
                downCarDict[i][j].extend([tmpIndex])
            downCarDict[i].sort(key=lambda x: x[-1])
        return upCarDict, downCarDict

    def mergeSameDirectionCars(self):
        upCarList = []
        downCarList = []
        upCar,downCar = self.staticDirectionOfCars()
        for i in range(1, len(upCar) + 1):
            for j in range(len(upCar[i])):
                upCarList.append(upCar[i][j])
        for i in range(1, len(downCar) + 1):
            for j in range(len(downCar[i])):
                downCarList.append(downCar[i][j])
        print(len(upCarList), len(downCarList))
        return upCarList, downCarList#返回向上以及向下方向的车辆的信息

    def dispatchCarByDirection(self):
        upCarList, downCarList = self.mergeSameDirectionCars()#得到两个列表，其中每一个列表当中从planTime 排序然后根据花费时间排序

        #计算两个批次的车辆之间发车的间隔（保证其中一个批次的车辆完全到达）
        #分时间片进行发车
        #分为timeSlice个时间片，每一个时间片均匀发车
        timeSlice = 10
        timeAdd = 200
        time = 0
        countTime = 0

        rtime = 1
        for i in range(len(upCarList)):
            countTime = countTime + 1
            if((countTime %(len(upCarList) // timeAdd)) == 0):
                time = time + 1
                rtime = rtime + timeAdd / len(upCarList)
            upCarList[i][1] = math.ceil(rtime)
        time = 0
        countTime = 0
        rtime = 1
        for i in range(len(downCarList)):
            countTime = countTime + 1
            if((countTime %(len(downCarList) // timeAdd)) == 0):
                time = time + 1
                rtime = rtime + countTime * (timeAdd / len(downCarList))
            downCarList[i][1] = math.ceil(rtime + timeAdd)

        #將結果寫入文件當中
        if os.path.exists(self.graph.answer_path):  # 判断是否存在文件，有则删除
            os.remove(self.graph.answer_path)
        file = open(self.graph.answer_path, 'a')
        #file.write(str("#(carId,StartTime,RoadId...)")+'\n')


        for i in range(len(upCarList)):
            ans = [int(upCarList[i][0])]
            ans.extend(upCarList[i][1:-1])
            result = tuple(ans)
            file.seek(0)
            file.write(str(result) + '\n')
        for i in range(len(downCarList)):
            ans = [int(downCarList[i][0])]
            ans.extend(downCarList[i][1:-1])
            result = tuple(ans)
            file.seek(0)
            file.write(str(result) + '\n')
        file.close()

    def uniformDispatchCar(self):
        # 1、统计同一个时间片出发的车辆的不同路口的个数
        self.graph.findCarShortPath()
        print(self.graph.nodePath)
        infoCarNode = []
        for i in range(len(self.graph.cars.carsInfo)):
            tmp = [int(self.graph.cars.carsInfo[i].id), self.graph.cars.carsInfo[i].planTime]
            tmp.extend(self.graph.nodePath[i])
            infoCarNode.append(tmp)
        infoCarNode.sort(key = lambda x: x[1])
        #统计同一出发时间的车辆的出发点信息
        samePlanTimeCarFromNode = self.staticDifferentValueByCol(infoCarNode, 1)
        for i in range(1, len(samePlanTimeCarFromNode)):
            samePlanTimeNode = self.getValueSet(samePlanTimeCarFromNode[i], 2)
            rr = len(samePlanTimeNode)
            print(len(samePlanTimeNode))




        #从路口均匀发车

    def staticDifferentValueByCol(self, listInfo, index):
        timeSet = set()
        for i in range(len(listInfo)):
            #print(listInfo[i][index])
            timeSet.add(listInfo[i][index])
        indexAdd = 0
        countTime = 0
        sum = 0
        tmpList = {}
        for i in timeSet:
            indexAdd = indexAdd + countTime
            countTime = 0
            for j in range(len(listInfo)):
                if(listInfo[j][1] == i):
                    countTime = countTime + 1
            tmpList[i] = listInfo[indexAdd: indexAdd + countTime]
        return tmpList

    def getValueSet(self, listInfo, index):
        NodeSet = set()
        for i in range(len(listInfo)):
            #print(listInfo[i][index])
            NodeSet.add(listInfo[i][index])
        return NodeSet
    #判断每一个车辆的方向，然后根据方向来进行选择性发车

    #为每一辆车分配出发时间以及路径并保存成文件
    def dispatchCarAboutTPOneway(self):#方法的极限是70
        if os.path.exists(self.graph.answer_path):  # 判断是否存在文件，有则删除
            os.remove(self.graph.answer_path)
        file = open(self.graph.answer_path, 'a')
        file.write(str("#(carId,StartTime,RoadId...)")+'\n')
        self.computeTimeandPath()
        self.timeAndPath.sort(key=lambda x: x[1])  # 根据出发时间进行排序，方便后面进行调度
        timeadd = float("inf")  # 初始化
        time = 1  #
        for i in range(len(self.graph.cars.carsInfo)):
            # per 20
            if i == 0:  # 最开始出发的车辆，出发时间统一规划为1
                time = 1
            if timeadd > self.timeAndPath[i][-1]:  # 寻找出一批车辆当中最快跑完全部路程的时间
                timeadd = self.timeAndPath[i][-1]
            if i != 0 and (i % self.graph.numberCar == 0):  # 每隔一个batch的车辆，给下一个batch的车辆的出发时间加上上一个batch中最短时间，以防死锁
                time = time + timeadd
            ans = [self.timeAndPath[i][0], time]
            ans.extend(self.timeAndPath[i][2:-1])
            result = tuple(ans)
            file.seek(0)
            file.write(str(result) + '\n')
        file.close()

    def dispatchCarAboutTPTwoway(self):#方法的极限时300
        if os.path.exists(self.graph.answer_path):  # 判断是否存在文件，有则删除
            os.remove(self.graph.answer_path)
        file = open(self.graph.answer_path, 'a')
        #file.write(str("#(carId,StartTime,RoadId...)")+'\n')
        self.computeTimeandPath()
        self.timeAndPath.sort(key=lambda x: x[1])  # 根据出发时间进行排序，方便后面进行调度


        timeSet = set()
        for i in range(len(self.graph.cars.carsInfo)):
            print(self.timeAndPath[i][1])
            timeSet.add(self.timeAndPath[i][1])
        print(timeSet)
        indexAdd = 0
        countTime = 0
        sum = 0
        tmpList = []
        for i in timeSet:
            indexAdd = indexAdd + countTime
            countTime = 0
            for j in range(len(self.graph.cars.carsInfo)):
                if(self.timeAndPath[j][1] == i):
                    countTime = countTime + 1
            AA = self.timeAndPath[indexAdd: indexAdd + countTime]
            AA.sort(key=lambda x: x[-1], reverse=True)
            tmpList.extend(AA)
        self.timeAndPath = tmpList# 根据出发时间进行排序，方便后面进行调度
        timeadd = float("inf")  # 初始化
        time = 1  #
        timeCount = 0
        for i in range(len(self.graph.cars.carsInfo)):
            if i == 0:  # 最开始出发的车辆，出发时间统一规划为1
                time = 1
            if timeadd > self.timeAndPath[i][-1]:  # 寻找出一批车辆当中最快跑完全部路程的时间
                timeadd = self.timeAndPath[i][-1]
            if i != 0 and (i % self.graph.numberCar == 0):  # 每隔一个batch的车辆，给下一个batch的车辆的出发时间加上上一个batch中最短时间，以防死锁
                time = time + timeadd
                timeadd = float("inf")  # 初始化
            ans = [self.timeAndPath[i][0], time]
            ans.extend(self.timeAndPath[i][2:-1])
            result = tuple(ans)
            file.seek(0)
            file.write(str(result) + '\n')
        file.close()

    def dispatchCarAboutTPThreeway(self):  # 方法的极限时
        if os.path.exists(self.graph.answer_path):  # 判断是否存在文件，有则删除
            os.remove(self.graph.answer_path)
        file = open(self.graph.answer_path, 'a')
        #file.write(str("#(carId,StartTime,RoadId...)") + '\n')
        self.computeTimeandPath()
        self.timeAndPath.sort(key=lambda x: x[1])  # 根据出发时间进行排序，方便后面进行调度
        timeSet = set()
        for i in range(len(self.graph.cars.carsInfo)):
            print(self.timeAndPath[i][1])
            timeSet.add(self.timeAndPath[i][1])
        print(timeSet)
        indexAdd = 0
        countTime = 0
        sum = 0
        tmpList = []
        for i in timeSet:
            indexAdd = indexAdd + countTime
            countTime = 0
            for j in range(len(self.graph.cars.carsInfo)):
                if (self.timeAndPath[j][1] == i):
                    countTime = countTime + 1
            AA = self.timeAndPath[indexAdd: indexAdd + countTime]
            AA.sort(key=lambda x: x[-1])
            tmpList.extend(AA)
        self.timeAndPath = tmpList  # 根据出发时间进行排序，方便后面进行调度
        timeadd = float("inf")  # 初始化
        time = 1  #
        for i in range(len(self.graph.cars.carsInfo)):
            if i == 0:  # 最开始出发的车辆，出发时间统一规划为1
                time = 1
            if timeadd > self.timeAndPath[i][-1]:  # 寻找出一批车辆当中最快跑完全部路程的时间
                timeadd = self.timeAndPath[i][-1]
            if i != 0 and (i % self.graph.numberCar == 0):  # 每隔一个batch的车辆，给下一个batch的车辆的出发时间加上上一个batch中最短时间，以防死锁
                time = time + timeadd
                timeadd = float("inf")  # 初始化
            ans = [self.timeAndPath[i][0], time]
            ans.extend(self.timeAndPath[i][2:-1])
            result = tuple(ans)
            file.seek(0)
            file.write(str(result) + '\n')
        file.close()

    def dispatchCarAboutTPFourway(self):  # 方法的极限时200
        if os.path.exists(self.graph.answer_path):  # 判断是否存在文件，有则删除
            os.remove(self.graph.answer_path)
        file = open(self.graph.answer_path, 'a')
        #file.write(str("#(carId,StartTime,RoadId...)") + '\n')
        self.computeTimeandPath()
        self.timeAndPath.sort(key=lambda x: x[1], reversed = True)  # 根据出发时间进行排序，方便后面进行调度
        timeSet = set()
        for i in range(len(self.graph.cars.carsInfo)):
            print(self.timeAndPath[i][1])
            timeSet.add(self.timeAndPath[i][1])
        print(timeSet)
        indexAdd = 0
        countTime = 0
        sum = 0
        tmpList = []
        for i in range(len(self.graph.cars.carsInfo)):
            self.timeAndPath[i].append(len(self.timeAndPath[i][2: -1]))
            self.timeAndPath[i].append(self.graph.cars.carsInfo[self.timeAndPath[i][0] - 10000].speed)
        for i in range(len(self.graph.cars.carsInfo)):
            self.timeAndPath[i].append(
                3 * self.timeAndPath[i][-1] + 3 * self.timeAndPath[i][-2] + 4 * self.timeAndPath[i][-3])
        for i in timeSet:
            indexAdd = indexAdd + countTime
            countTime = 0
            for j in range(len(self.graph.cars.carsInfo)):
                if (self.timeAndPath[j][1] == i):
                    countTime = countTime + 1
            AA = self.timeAndPath[indexAdd: indexAdd + countTime]
            AA.sort(key=lambda x: x[-1])
            tmpList.extend(AA)
        self.timeAndPath = tmpList  # 根据出发时间进行排序，方便后面进行调度

        timeadd = float("inf")  # 初始化
        time = 1  #
        for i in range(len(self.graph.cars.carsInfo)):
            if i == 0:  # 最开始出发的车辆，出发时间统一规划为1
                time = 1
            if timeadd > self.timeAndPath[i][-4]:  # 寻找出一批车辆当中最快跑完全部路程的时间
                timeadd = self.timeAndPath[i][-4]
            if i != 0 and (i % self.graph.numberCar == 0):  # 每隔一个batch的车辆，给下一个batch的车辆的出发时间加上上一个batch中最短时间，以防死锁
                time = time + timeadd
                timeadd = float("inf")  # 初始化
            ans = [self.timeAndPath[i][0], time]
            ans.extend(self.timeAndPath[i][2:-4])
            result = tuple(ans)
            file.seek(0)
            file.write(str(result) + '\n')
        file.close()

    def dispatchCarAboutTPFiveway(self):  #
        result = []
        #file.write(str("#(carId,StartTime,RoadId...)") + '\n')
        self.computeTimeandPath()
        for i in range(len(self.graph.cars.carsInfo)):
            ans = [self.timeAndPath[i][0]]
            ans.extend(self.timeAndPath[i][1:-1])
            result.append(ans)
        return result


    def dispatchCarAboutTPSixway(self):#方法的极限时240
        if os.path.exists(self.graph.answer_path):  # 判断是否存在文件，有则删除
            os.remove(self.graph.answer_path)
        file = open(self.graph.answer_path, 'a')
        #file.write(str("#(carId,StartTime,RoadId...)")+'\n')
        self.computeTimeandPath()
        self.timeAndPath.sort(key=lambda x: x[1])  # 根据出发时间进行排序，方便后面进行调度
        timeSet = set()
        for i in range(len(self.graph.cars.carsInfo)):
            print(self.timeAndPath[i][1])
            timeSet.add(self.timeAndPath[i][1])
        print(timeSet)
        indexAdd = 0
        countTime = 0
        sum = 0
        tmpList = []
        for i in timeSet:
            indexAdd = indexAdd + countTime
            countTime = 0
            for j in range(len(self.graph.cars.carsInfo)):
                if(self.timeAndPath[j][1] == i):
                    countTime = countTime + 1
            AA = self.timeAndPath[indexAdd: indexAdd + countTime]
            AA.sort(key=lambda x: x[-1], reverse=True)
            tmpList.extend(AA)
        self.timeAndPath = tmpList# 根据出发时间进行排序，方便后面进行调度
        timeadd = float("inf")  # 初始化
        time = 1  #
        timeCount = 0
        for i in range(len(self.graph.cars.carsInfo)):
            timeCount = timeCount + 1
            if (timeCount != 0) and (timeCount % self.graph.numberCar == 0):
                time = time + 1
            ans = [self.timeAndPath[i][0], time]
            ans.extend(self.timeAndPath[i][2:-1])
            result = tuple(ans)
            file.seek(0)
            file.write(str(result) + '\n')
        file.close()

    def dispatchCarAboutTPSevenway(self):#方法的极限时240
        if os.path.exists(self.graph.answer_path):  # 判断是否存在文件，有则删除
            os.remove(self.graph.answer_path)
        file = open(self.graph.answer_path, 'a')
        #file.write(str("#(carId,StartTime,RoadId...)")+'\n')
        self.computeTimeandPath()
        self.timeAndPath.sort(key=lambda x: x[1])  # 根据出发时间进行排序，方便后面进行调度
        timeSet = set()
        for i in range(len(self.graph.cars.carsInfo)):
            print(self.timeAndPath[i][1])
            timeSet.add(self.timeAndPath[i][1])
        print(timeSet)
        indexAdd = 0
        countTime = 0
        sum = 0
        tmpList = []
        for i in timeSet:
            indexAdd = indexAdd + countTime
            countTime = 0
            for j in range(len(self.graph.cars.carsInfo)):
                if(self.timeAndPath[j][1] == i):
                    countTime = countTime + 1
            AA = self.timeAndPath[indexAdd: indexAdd + countTime]
            AA.sort(key=lambda x: x[-1], reverse=True)
            tmpList.extend(AA)
        self.timeAndPath = tmpList# 根据出发时间进行排序，方便后面进行调度
        timeadd = float('inf')  # 初始化
        time = 1  #
        timeCount = 0
        for i in range(len(self.graph.cars.carsInfo)):
            if i == 0:  # 最开始出发的车辆，出发时间统一规划为1
                time = 1
            if(self.timeAndPath[i][1] == 1):
                ans = [self.timeAndPath[i][0], time]
                ans.extend(self.timeAndPath[i][2:-1])
                result = tuple(ans)
                file.seek(0)
                file.write(str(result) + '\n')
                if timeadd > self.timeAndPath[i][-1]:  # 寻找出一批车辆当中最快跑完全部路程的时间
                    timeadd = self.timeAndPath[i][-1]
        time = time + timeadd
        timeadd = 0
        for i in range(len(self.graph.cars.carsInfo)):
            if (self.timeAndPath[i][1] != 1):
                if timeadd > self.timeAndPath[i][-1]:  # 寻找出一批车辆当中最快跑完全部路程的时间
                    timeadd = self.timeAndPath[i][-1]
                if i != 0 and (i % self.graph.numberCar == 0):  # 每隔一个batch的车辆，给下一个batch的车辆的出发时间加上上一个batch中最短时间，以防死锁
                    time = time + timeadd
                ans = [self.timeAndPath[i][0], time]
                ans.extend(self.timeAndPath[i][2:-1])
                result = tuple(ans)
                file.seek(0)
                file.write(str(result) + '\n')
        file.close()

if __name__ == "__main__":
    car_path = "../config/car.txt"
    road_path = "../config/road.txt"
    cross_path = "../config/cross.txt"
    answer_path = "../config/answer.txt"

    trafficMap = Graph(car_path, road_path, cross_path, answer_path, 200)#生成交通图
    DispatchSystem = DispatchCar(trafficMap)
    DispatchSystem.dispatchCarAboutTPTwoway()
    print("xixi")
