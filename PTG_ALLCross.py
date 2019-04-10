"""
路口数据
"""
DebugCarID = [20101, 18080, 14836, 13747, 11093, 18126, 10779, 12860, 15815, 17913]

class CROSS(object):
    def __init__(self, crossInfo, ALLRoads):
        # -----基本信息----- #
        self.crossId = int(crossInfo[0])
        self.roadNId = int(crossInfo[1])
        self.roadEId = int(crossInfo[2])
        self.roadSId = int(crossInfo[3])
        self.roadWId = int(crossInfo[4])
        self.roadIds = [self.roadNId, self.roadEId, self.roadSId, self.roadWId]
        # -----基本信息----- #
        self.Done = False  # 是否完成本次调度
        self.update = False  # 是否更新状态
        self.Dispatch = False  # 是否使用自己的算法调度系统

        # 设置在当前路口出发的车辆ID
        self.ParkingGarage = []
        self.ParkingCarsNum = 0

        # 设置当前出路口的优先级
        self.OutPriority = {self.roadNId: {self.roadEId: 1, self.roadSId: 2, self.roadWId: 0},
                            self.roadEId: {self.roadSId: 1, self.roadWId: 2, self.roadNId: 0},
                            self.roadSId: {self.roadWId: 1, self.roadNId: 2, self.roadEId: 0},
                            self.roadWId: {self.roadNId: 1, self.roadEId: 2, self.roadSId: 0}}

        # 分别记录从当前路口出发和进入当前路口的车辆 以及有效的道路
        self.RoadFromCross, self.RoadToCross, self.ValidtRoadOFCross = [], [], []
        self.InIndex, self.OutIndex, self.validRoadIndex = [], [], []
        for i, roadid in enumerate(self.roadIds):
            road = None
            if roadid != -1:
                road = ALLRoads[roadid]
            if road is not None and (road.RisDuplex or road.Rfrom == self.crossId):  # 离开该路口的道路(反向)
                self.OutIndex.append(i)
                self.RoadFromCross.append(roadid)
            if road is not None and (road.RisDuplex or road.Rto == self.crossId):  # 进入该路口的道路
                self.InIndex.append(i)
                self.RoadToCross.append(roadid)
            if road is not None:
                self.validRoadIndex.append(i)
                self.ValidtRoadOFCross.append(roadid)
        self.RoadToCross.sort()  # 路口内各道路按道路ID升序进行调度

    # TODO 获得下一时刻该道路可能到来的车辆数 即预测
    def GetNextTimeCars(self):
        pass

    def setCrossInitState(self):
        self.Done = False
        self.update = False

    def PriorityToNum(self, nowRoad, nextRoad):
        return self.OutPriority[nowRoad][nextRoad]

    def DriveAllWaitCarInCrossToEndState(self, ALLCars, ALLRoads):
        self.update = False  # 当前路口是否更新
        # 设计数据结构存储路口的信息 是否发生冲突，只与相关道路的第一优先级车辆的行驶方向进行比较，看是否发生冲突。
        CarIDList = []  # 优先级车辆序列
        CarList = []  # 优先级车辆序列
        NextRoadList = []  # 优先级道路序列
        PriorityList = []  # 优先级序列

        # 循环所有路口第一遍 记录每条道路的优先级最高的车辆ID 车辆 车辆的下一个路口 车辆的优先级
        for index, InroadId in enumerate(self.RoadToCross):  # 进入该路口的道路ID
            CurRoad = ALLRoads[InroadId]  # 当前调度道路
            if self.Dispatch:
                # TODO 动态更新道路
                # 使用算法计算得到车辆的下一条道路
                pass
            # 假设我们当前已经得到了车辆下一条道路 开始调度路口往下一条道路行驶
            FirstPriorityCarID = CurRoad.GetFirstPriorityCar(ALLCars, self.crossId)  # 得到当前道路优先级最高的车辆
            CarIDList.append(FirstPriorityCarID)
            # 如果优先级的车辆存在 记录信息
            if FirstPriorityCarID != -1:
                CarList.append(ALLCars[FirstPriorityCarID])
                NextRoadList.append(CarList[index].GetNextRoadstatic())
                # 如果到达终点了 设置为直行的优先级
                if NextRoadList[index] == -1:
                    PriorityList.append(2)
                else:
                    PriorityList.append(self.PriorityToNum(InroadId, NextRoadList[index]))
            else:  # 如果不存在优先级的车辆
                CarList.append(-1)
                NextRoadList.append(-2)
                PriorityList.append(-1)

        # 只有出路口的车辆才判断优先级
        # 再次循环路口 开始调度路口上所有的车辆 按照优先级开始循环调度
        DispatchCount = 0
        for index, InroadId in enumerate(self.RoadToCross):
            # 调度车辆
            while CarList[index] != -1:  # 当前TIME道路是否还有车可以继续走
                CurRoadID = self.RoadToCross[index]
                Conflict = False
                # 判断是否发生冲突 进入相同道路才会引发冲突 只检查进入相同道路的车辆优先级
                for i in range(len(self.RoadToCross)):
                    if NextRoadList[i] == NextRoadList[index] and PriorityList[i] > PriorityList[index]:
                        Conflict = True
                        break  # 调度冲突 调度下一条道路
                # 如果没有发生冲突
                if Conflict:
                    break

                if NextRoadList[index] == -1:  # 到达终点
                    ALLRoads[CurRoadID].CarInEnding(CarList[index].nowDistanceX, CarList[index].nowChannleY, self.crossId, ALLCars)
                    ALLRoads[CurRoadID].UpdateRoadCarsNumSub(self.crossId)
                    DispatchCount += 1
                    self.update = True
                    CarList[index].state = 3  # 到达终点状态  TODO 更新状态
                else:  # 通过路口
                    # 得到下一条道路
                    NextRoadId = NextRoadList[index]
                    Ret = ALLRoads[CurRoadID].CarGoToNextRoad(ALLRoads, NextRoadId, self.crossId, CarList[index], ALLCars)
                    if Ret == 1:  # 路口优先级车辆需要等待下个路口的车辆 直接退出等待下一次路口循环再调度
                        break
                    DispatchCount += 1
                    self.update = True  # 代表已经更新过当前的路口

                # 继续判断优先级最高的道路车辆
                FirstPriorityCarID = ALLRoads[CurRoadID].GetFirstPriorityCar(ALLCars, self.crossId)  # 继续在当前道路调度 得到优先级最高的车辆
                CarIDList[index] = FirstPriorityCarID  # 继续调度当前路口 直至所有的可以走的车辆调度完毕
                # 如果优先级的车辆存在 记录信息
                if CarIDList[index] != -1:
                    CarList[index] = ALLCars[FirstPriorityCarID]
                    NextRoadList[index] = ALLCars[FirstPriorityCarID].GetNextRoadstatic()  # TODO 道路更新策略
                    # 如果到达终点了 设置为直行的优先级
                    if NextRoadList[index] == -1:
                        PriorityList[index] = 2
                    else:
                        PriorityList[index] = self.PriorityToNum(self.RoadToCross[index], NextRoadList[index])
                else:  # 如果不存在优先级的车辆
                    CarList[index] = -1
                    NextRoadList[index] = -2
                    PriorityList[index] = -1

        if DispatchCount > 0:
            self.update = True

        for i in range(len(self.RoadToCross)):
            if CarList[i] != -1:  # 只有当前路口的道路完成调度 NextCarList[i]才会返回-1 即无车辆调度
                self.Done = False
                return
        self.Done = True
        return

    def NewDriveAllWaitCarInCrossToEndState(self, ALLCars, ALLRoads):
        self.update = False  # 当前路口是否更新
        # 设计数据结构存储路口的信息 是否发生冲突，只与相关道路的第一优先级车辆的行驶方向进行比较，看是否发生冲突。
        CarIDList = []  # 优先级车辆ID序列
        CarList = []  # 优先级车辆序列
        NextRoadList = []  # 优先级道路序列
        PriorityList = []  # 优先级序列

        # 循环所有路口第一遍 记录每条道路的优先级最高的车辆ID 车辆 车辆的下一个路口 车辆的优先级
        for index, InroadId in enumerate(self.RoadToCross):  # 进入该路口的道路ID
            CurRoad = ALLRoads[InroadId]  # 当前调度道路
            # 假设我们当前已经得到了车辆下一条道路 开始调度路口往下一条道路行驶
            FirstPriorityCarID = CurRoad.GetFirstPriorityCar(ALLCars, self.crossId)  # 得到当前道路优先级最高的车辆
            CarIDList.append(FirstPriorityCarID)
            # 如果优先级的车辆存在 记录信息
            if FirstPriorityCarID != -1:
                CarList.append(ALLCars[FirstPriorityCarID])
                NextRoadList.append(ALLCars[FirstPriorityCarID].GetNextRoadstatic())
                # 如果到达终点了 设置为直行的优先级
                if NextRoadList[index] == -1:
                    PriorityList.append(2)
                else:
                    PriorityList.append(self.PriorityToNum(CurRoad.Rid, NextRoadList[index]))
            else:  # 如果不存在优先级的车辆
                CarList.append(-1)
                NextRoadList.append(-2)
                PriorityList.append(-1)

        # 只有出路口的车辆才判断优先级
        # 再次循环路口 开始调度路口上所有的车辆 按照优先级开始循环调度
        DispatchCount = 0
        for index, InroadId in enumerate(self.RoadToCross):
            # 调度车辆
            while CarList[index] != -1:  # 当前TIME道路是否还有车可以继续走
                CurRoadID = self.RoadToCross[index]
                # 判断是否发生冲突 进入相同道路才会引发冲突 只检查进入相同道路的车辆优先级
                for i in range(len(NextRoadList)):
                    if NextRoadList[i] == NextRoadList[index] and PriorityList[i] > PriorityList[index]:
                        CurRoadID = self.RoadToCross[i]
                        index = i
                        # 调度冲突 调度下一条道路

                if NextRoadList[index] == -1:  # 到达终点
                    ALLRoads[CurRoadID].CarInEnding(CarList[index].nowDistanceX, CarList[index].nowChannleY,
                                                    self.crossId, ALLCars)
                    ALLRoads[CurRoadID].UpdateRoadCarsNumSub(self.crossId)
                    DispatchCount += 1
                    self.update = True
                    CarList[index].state = 3  # 到达终点状态  TODO 更新状态
                else:  # 通过路口
                    # 得到下一条道路
                    NextRoadId = NextRoadList[index]
                    Ret = ALLRoads[CurRoadID].CarGoToNextRoad(ALLRoads, NextRoadId, self.crossId, CarList[index],
                                                              ALLCars)
                    if Ret == 1:  # 路口优先级车辆需要等待下个路口的车辆 直接退出等待下一次路口循环再调度
                        break
                    DispatchCount += 1
                    self.update = True  # 代表已经更新过当前的路口
                # 继续判断优先级最高的道路车辆
                FirstPriorityCarID = ALLRoads[CurRoadID].GetFirstPriorityCar(ALLCars,
                                                                             self.crossId)  # 继续在当前道路调度 得到优先级最高的车辆
                CarIDList[index] = FirstPriorityCarID  # 继续调度当前路口 直至所有的可以走的车辆调度完毕
                # if FirstPriorityCarID in DebugCarID:
                #     print("-------------debug-----------------")
                # 如果优先级的车辆存在 记录信息
                if CarIDList[index] != -1:
                    CarList[index] = ALLCars[FirstPriorityCarID]
                    NextRoadList[index] = ALLCars[FirstPriorityCarID].GetNextRoadstatic()  # TODO 道路更新策略
                    # 如果到达终点了 设置为直行的优先级
                    if NextRoadList[index] == -1:
                        PriorityList[index] = 2
                    else:
                        PriorityList[index] = self.PriorityToNum(CurRoadID, NextRoadList[index])
                else:  # 如果不存在优先级的车辆
                    CarList[index] = -1
                    NextRoadList[index] = -2
                    PriorityList[index] = -1

        if DispatchCount > 0:
            self.update = True

        for i in range(len(self.RoadToCross)):
            if CarList[i] != -1:  # 只有当前路口的道路完成调度 NextCarList[i]才会返回-1 即无车辆调度
                self.Done = False
                return
        self.Done = True
        return

    # TODO 调度策略 如何定制发车时间
    def NewDispatchPolicy(self, ALLCars, TIME):
        pass

    def DispatchPolicy(self, ALLCars, TIME):
        DriveCar = []
        for carId in self.ParkingGarage:  # 扫描当前路口的车辆
            if ALLCars[carId].planTime <= TIME:
                DriveCar.append(carId)
        return DriveCar

    # 暂时不需要
    def driveCarInGarage(self, ALLCars, ALLRoads,  TIME):  # 下一条道路相同且出发时间相同 则按车辆ID升序
        DriveCar = self.DispatchPolicy(ALLCars, TIME)
        DriveCar.sort()  # 下一条道路相同且出发时间相同 则按车辆ID升序
        for index, CarId in enumerate(DriveCar):
            flag = 0  # 看是否找到了空位
            Car = ALLCars[CarId]
            NextRoad = ALLRoads[Car.planRoute[0]]
            NextRoadStruct = NextRoad.GetRoadOut(self.crossId)  # 获得下一条道路的数据结构
            V = min(Car.Cspeed, NextRoad.Rspeed)  # 得到在道路上可行驶的最大距离
            # 开始扫描道路 看是否有空余位置
            for channle in range(NextRoad.Rchannel):
                for i in range(V, 0, -1):  # 发车时不存在道路上还有等待的车辆 如果有那么表示已经死锁
                    if NextRoadStruct[NextRoad.Rlength - i][channle] == None:
                        NextRoadStruct[NextRoad.Rlength - i][channle] = CarId
                        Car.UpdatePosAndSta(state=2, x=NextRoad.Rlength - i, y=channle,
                                            NowInRoad=NextRoad.Rid, nextCrossId=NextRoad.GetNextCross(self.crossId))
                        NextRoad.UpdateRoadCarsNumAdd(self.crossId)
                        #DriveCar.remove(CarId)  # 移除车辆Id
                        self.ParkingGarage.remove(CarId)
                        self.ParkingCarsNum -= 1
                        flag = 1  # 已经找到位置停车了
                        break
                if flag == 1:
                    break
            if flag == 0:  # 道路已经满了 无法继续发车
                break
        # # 如果没有空余位置 放回停车场等待下一个时间戳
        # for i in DriveCar:
        #     if ALLCars[i].state == 0:
        #         ALLCars[i].planTime += 1
        return

    def NewdriveCarInGarage(self, ALLCars, ALLRoads,  TIME):   #使用NotCarInBack()
        DriveCar = self.DispatchPolicy(ALLCars, TIME)
        DriveCar.sort()  # 下一条道路相同且出发时间相同 则按车辆ID升序
        for index, CarId in enumerate(DriveCar):
            if CarId in DebugCarID:
                print("-------------debug-----------------")
            flag = 0  # 判断道路是否已经满了
            Car = ALLCars[CarId]
            NextRoad = ALLRoads[Car.planRoute[0]]
            NextRoadStruct = NextRoad.GetRoadOut(self.crossId)  # 获得下一条道路的数据结构
            V = min(Car.Cspeed, NextRoad.Rspeed)  # 得到在道路上可行驶的最大距离
            # 开始扫描道路 看是否有空余位置
            for channle in range(NextRoad.Rchannel):
                NextRoadPos = NextRoad.NotCarInBack(NextRoad.Rlength - 1 - V, NextRoad.Rlength - 1, channle,
                                                NextRoadStruct)
                if NextRoadPos == -1:  # 没有挡住当前车辆的行走
                    NextRoadStruct[NextRoad.Rlength - V][channle] = CarId
                    Car.UpdatePosAndSta(state=2, x=NextRoad.Rlength - V, y=channle,
                                        NowInRoad=NextRoad.Rid, nextCrossId=NextRoad.GetNextCross(self.crossId))
                    NextRoad.UpdateRoadCarsNumAdd(self.crossId)
                    # DriveCar.remove(CarId)  # 移除车辆Id
                    self.ParkingGarage.remove(CarId)
                    self.ParkingCarsNum -= 1
                    flag = 1
                    break
                # FrontCar = ALLCars[NextRoadStruct[NextRoadPos][channle]]
                if NextRoadPos != NextRoad.Rlength - 1:
                    NextRoadStruct[NextRoadPos + 1][channle] = Car.Cid
                    Car.UpdatePosAndSta(state=2, x=NextRoadPos + 1, y=channle,
                                        NowInRoad=NextRoad.Rid, nextCrossId=NextRoad.GetNextCross(self.crossId))
                    NextRoad.UpdateRoadCarsNumAdd(self.crossId)
                    self.ParkingGarage.remove(CarId)
                    self.ParkingCarsNum -= 1
                    flag = 1
                    break
                else:
                    continue
            if flag == 0:  # 道路已经满了 无法继续发车
                break
        return

    def __str__(self):
        return "id:" + str(self.crossId) + " roadNId " + str(self.roadNId) + " roadEId " + str(self.roadEId) + " roadSId " + str(str(self.roadSId)) + " roadWId " + str(self.roadWId)







