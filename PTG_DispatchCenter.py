"""
调度中心
"""

import PTG_ALLCars
import PTG_ALLCross
import PTG_ALLRoads
import time
import PTG_Floyd
# from Grahp_exp import Graph
# import os
# import numpy as np
# import math

# 全局变量设置
TIMELINE = [0]
# 存放所有的信息
ALLCarsInfoWithDIC, ALLRoadsInfoWithDIC, ALLCrossInfoWithDIC = {}, {}, {}
# 记录所有的ＩＤ
ALLCarIDs, ALLRoadIDs, ALLCrossIDs = [], [], []
# 记录已经到达终点的车辆
NUMOFENDINGCARS = 0

NUMOFCARS = 0




class DispatchCenter(object):
    def __init__(self):
        self.DeadLock = False
        self.planRoute = None
        self.AnswerPath = "./config/answer.txt"
        self.SetParkingGarage()
        #self.SetPlanRouteInit(ALLCarsInfoWithDIC, ALLRoadsInfoWithDIC, ALLCrossInfoWithDIC,self.AnswerPath,100)

    def SetPlanRouteInit(self, ALLCars, ALLRoads, ALLCross,AnswerPath, ALLCarIDs, ALLRoadIDs, ALLCrossIDs, Batchsize):
        PlanRoute = PTG_Floyd.FloydAlgorithm(ALLCars, ALLRoads, ALLCross, AnswerPath, ALLCarIDs, ALLRoadIDs, ALLCrossIDs, Batchsize)
        self.planRoute = PlanRoute.findCarShortPathWithFloyd()

    def SetParkingGarage(self):  # 初始化所有车辆在出发点
        for carId in ALLCarIDs:
            Car = ALLCarsInfoWithDIC[carId]
            ALLCrossInfoWithDIC[Car.Cfrom].ParkingGarage.append(carId)
            ALLCrossInfoWithDIC[Car.Cfrom].ParkingCarsNum += 1  # 记录当前路口的等待出发的车辆储量

    def SortParkingCarByplanTime(self):
        for CrossId in ALLCrossIDs:
            ALLCrossInfoWithDIC[CrossId].ParkingGarage.sort(key=lambda x: x.planTime)

    def DebugState(self):
        for RoadID in ALLRoadIDs:
            CurRoad = ALLRoadsInfoWithDIC[RoadID]
            for i in range(CurRoad.Rlength):
                for j in range(CurRoad.Rchannel):
                    if CurRoad.FromtoToRoad[i][j] != None:
                        if ALLCarsInfoWithDIC[CurRoad.FromtoToRoad[i][j]].state != 2:
                            print("ALLCarsInfoWithDIC[%d.FromtoToRoad[%d][%d]].state : %d " % (RoadID, i, j, ALLCarsInfoWithDIC[
                                    CurRoad.FromtoToRoad[i][j]].state))
                    if CurRoad.RisDuplex:
                        if CurRoad.TotoFromRoad[i][j] != None:
                            if ALLCarsInfoWithDIC[CurRoad.TotoFromRoad[i][j]].state != 2:
                                print("ALLCarsInfoWithDIC[%d.TotoFromRoad[%d][%d]].state : %d " % (RoadID, i, j, ALLCarsInfoWithDIC[
                                    CurRoad.TotoFromRoad[i][j]].state))

    def NotDeadLock(self, Cross):
        if ALLCrossInfoWithDIC[Cross].update or ALLCrossInfoWithDIC[Cross].Done:
            return True
        return False

    def isDeadLock(self):
        for cross in ALLCrossIDs:
            if ALLCrossInfoWithDIC[cross].update or ALLCrossInfoWithDIC[cross].Done:
                return False
        return True

    def isAllCarFinish(self):
        pass

    def IsALLCarEnd(self):
        for CarId in ALLCarIDs:
            if ALLCarsInfoWithDIC[CarId].state != 3:
                return False
        return True

    def DispatchCenterStep(self):
        while True:

            print("Current Dispatch TIMELINE : %d" % TIMELINE[0])
            #  路口设置初始状态
            for CrossId in ALLCrossIDs:  # 初始化所有路口为False
                ALLCrossInfoWithDIC[CrossId].setCrossInitState()

            # 调试
            self.DebugState()

            # 道路上的车辆设置初始等待状态
            # for carId in ALLCarIDs:
            #    ALLCarsInfoWithDIC[carId].setCarInitState()

            #  开始调度在道路上的车辆　先处理每条道路上的车辆
            print("The Dispatch Of Vehicles On The Road, TIMELINE : %d" % TIMELINE[0])
            for RoadId in ALLRoadIDs:  # 实现当前车道上的车辆调度
                ALLRoadsInfoWithDIC[RoadId].DriveAllCarJustOnRoadToEndState(ALLCarsInfoWithDIC)

            #  开始循环调度路口的车辆　处理所有路口、道路中处于等待状态的车辆
            print("The Dispatch Of Vehicles On The Cross, TIMELINE : %d" % TIMELINE[0])
            unDoneCross = ALLCrossIDs
            while len(unDoneCross) > 0:  # 判断循环结束条件
                self.DeadLock = True  # 设置死锁状态为真
                NextCycle = []
                for CrossId in unDoneCross:
                    NowCross = ALLCrossInfoWithDIC[CrossId]  # 实现当前路口上的车辆调度
                    NowCross.DriveAllWaitCarInCrossToEndState(ALLCarsInfoWithDIC, ALLRoadsInfoWithDIC)
                    if not NowCross.Done:
                        NextCycle.append(CrossId)
                    if self.NotDeadLock(CrossId):
                        self.DeadLock = False
                unDoneCross = NextCycle
                if self.DeadLock:
                    self.DebugState()
                    print("......DEADLOCK......")
                    print("UnfinishedCross : ", unDoneCross)
                    return

            #  结束循环条件
            if self.IsALLCarEnd():
                print("Complete DispatchCenter In TIMELINE : %d " % TIMELINE[0])
                break

            self.DebugState()

            #  开始发车上路
            print("Move Cars into Roads,TIMELINE : %d" % TIMELINE[0])
            for CrossId in ALLCrossIDs:  # 实现当前路口上的发车调度
                NowCross = ALLCrossInfoWithDIC[CrossId]
                NowCross.NewdriveCarInGarage(ALLCarsInfoWithDIC, ALLRoadsInfoWithDIC, TIMELINE[0])

            TIMELINE[0] += 1


def Diapatch():
    # 设置文件路径
    Carspath = "./config/car.txt"
    Roadspath = "./config/road.txt"
    Crosspath = "./config/cross.txt"
    Answerspath = "./config/answer.txt"

    # 读取ＴＸＴ文件信息
    CarsInfo = open(Carspath, 'r').read().split('\n')[1:]  # 车辆信息
    RoadsInfo = open(Roadspath, 'r').read().split('\n')[1:]  # 道路信息
    CrossInfo = open(Crosspath, 'r').read().split('\n')[1:]  # 路口信息
    AnswersInfo = open(Answerspath, 'r').read().split('\n')  # 规划路径信息

    # ------------开始初始化 道路类　路口类　车辆类　基本信息-------------- #

    # 提取车辆信息 创建车辆字典 字典value为ALLCarIDs类
    for info in CarsInfo:
        [Cid, Cfrom, Cto, Cspeed, CplanTime] = info.replace(' ', '').replace('\t', '')[1:-1].split(',')
        ALLCarIDs.append(int(Cid))  # 所有车辆的ID
        ALLCarsInfoWithDIC[int(Cid)] = PTG_ALLCars.CARS([Cid, Cfrom, Cto, Cspeed, CplanTime])

    # 提取道路信息 创建道路字典 字典value为ALLRoadIDs类
    for info in RoadsInfo:
        [Rid, Rlength, Rspeed, Rchannel, Rfrom, Rto, RisDuplex] = info.replace(' ', '').replace('\t', '')[1:-1].split(',')
        ALLRoadIDs.append(int(Rid))  # 所有车辆的ID
        ALLRoadsInfoWithDIC[int(Rid)] = PTG_ALLRoads.ROADS([Rid, Rlength, Rspeed, Rchannel, Rfrom, Rto, RisDuplex])

    # 提取路口信息 创建路口字典 字典value为ALLCrossIDs类
    for info in CrossInfo:
        [crossId, roadNId, roadEId, roadSId, roadWId] = info.replace(' ', '').replace('\t', '')[1:-1].split(',')
        ALLCrossIDs.append(int(crossId))  # 所有车辆的ID
        ALLCrossInfoWithDIC[int(crossId)] = PTG_ALLCross.CROSS([crossId, roadNId,
                                                                roadEId, roadSId, roadWId], ALLRoadsInfoWithDIC)

    # 提取规划行车信息 将规划行车信息放入到车辆中
    for info in AnswersInfo:
        if info.strip() == '':
            break
        info = info.strip()[1:-1].split(',')
        CarId = info[0]
        PlanTime = info[1]
        PlanRoute = [int(rId) for rId in info[2:]]
        # 将Answers初始化到车辆中
        ALLCarsInfoWithDIC[int(CarId)].InitAnswers(PlanTime, PlanRoute)

    # ------------开始初始化 道路类　路口类　车辆类　基本信息-------------- #

    NUMOFCARS = len(ALLCarIDs)  # 车辆总数
    ALLCrossIDs.sort()  # 路口ＩＤ排序
    ALLCarIDs.sort()   # 车辆ＩＤ排序

    # 开始调度中心调度车辆
    print("DispatchCenter Begin....")
    CarDCenter = DispatchCenter()
    CarDCenter.DispatchCenterStep()
    print("DispatchCenter End....")


if __name__ == '__main__':
    start = time.time()
    Diapatch()
    end = time.time()
    print("Program run time : %d" % (end-start))
