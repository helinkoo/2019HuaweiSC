"""
道路数据
"""
DebugCarID = [20101, 18080, 14836, 13747, 11093, 18126, 10779, 12860, 15815, 17913]


HyperParam1, HyperParam2, HyperParam3, HyperParam4 = 1, 1, 1, 1


class ROADS(object):
    def __init__(self, roadsInfo):
        # -----基本信息----- #
        self.Rid = int(roadsInfo[0])
        self.Rlength = int(roadsInfo[1])
        self.Rspeed = int(roadsInfo[2])
        self.Rchannel = int(roadsInfo[3])
        self.Rfrom = int(roadsInfo[4])
        self.Rto = int(roadsInfo[5])
        self.RisDuplex = int(roadsInfo[6])
        # -----基本信息----- #

        # 道路的权重
        self.CostFromtoTo = self.Rlength
        if self.RisDuplex:
            self.CostTotoFrom = self.Rlength

        self.FromtoToCapcity = 0  # 车道当前的容量
        if self.RisDuplex:
            self.TotoFromCapcity = 0

        self.maxCapcity = self.Rchannel * self.Rlength  # 道路的最大容量

        # 创建道路的数据结构
        self.FromtoToRoad = {i: [None for j in range(self.Rchannel)] for i in range(self.Rlength)}
        self.TotoFromRoad = None
        if self.RisDuplex:
            self.TotoFromRoad = {i: [None for j in range(self.Rchannel)] for i in range(self.Rlength)}

    # TODO 更新道路权重
    def GetNRCostRtFtoT(self, NextRoad, cross, car):
        return HyperParam1 * NextRoad.CostFromtoTo + HyperParam2 * NextRoad.Rchannel + HyperParam3 * NextRoad.GetNextRoadAvailableCapacity(cross) + HyperParam4 * car.GetAvailableSpeed(NextRoad)

    def GetNRCostRtTtoF(self, NextRoad, cross, car):
        return HyperParam1 * NextRoad.TotoFromRoad + HyperParam2 * NextRoad.Rchannel + HyperParam3 * NextRoad.GetNextRoadAvailableCapacity(cross) + HyperParam4 * car.GetAvailableSpeed(NextRoad)

    def GetNextCross(self, Cross):
        if self.Rfrom == Cross:
            return self.Rto
        if self.Rto == Cross:
            return self.Rfrom

    # 相对于当前路口的出路和进路
    def GetRoadOut(self, Cross):
        if self.Rfrom == Cross:
            return self.FromtoToRoad
        if self.Rto == Cross:
            return self.TotoFromRoad

    def GetRoadIn(self, Cross):
        if self.Rto == Cross:
            return self.FromtoToRoad
        if self.Rfrom == Cross:
            return self.TotoFromRoad

    def UpdateRoadCarsNumAdd(self, cross):
        if cross == self.Rfrom:
            self.FromtoToCapcity += 1
        if cross == self.Rto:
            self.TotoFromCapcity += 1

    def UpdateRoadCarsNumSub(self, cross):
        if cross == self.Rto:
            self.FromtoToCapcity -= 1
        if cross == self.Rfrom:
            self.TotoFromCapcity -= 1

    def NotCarInFront(self, end, channel, CurRoadStruct):
        for i in range(end):
            if CurRoadStruct[i][channel] != None:
                return i
        return -1

    def NotCarInBack(self, start, end, channel, CurRoadStruct):
        for i in range(end, start, -1):
            if CurRoadStruct[i][channel] != None:
                return i
        return -1

    def ComputeAC(self, CurRoadStruct, channle):
        start = self.Rlength-1
        for i in range(start, -1, -1):
            if CurRoadStruct[i][channle] != None:
                return start - i

    # 得到下一条道路的有效容量
    def GetNextRoadAvailableCapacity(self, cross):
        ACSum = 0
        if self.Rfrom == cross:
            CurRoadStruct = self.FromtoToRoad
            for channle in range(self.Rchannel):
                Capacity = self.ComputeAC(CurRoadStruct, channle)
                ACSum += Capacity
            return ACSum

        if self.Rto == cross:
            CurRoadStruct = self.TotoFromRoad
            for channle in range(self.Rchannel):
                Capacity = self.ComputeAC(CurRoadStruct, channle)
                ACSum += Capacity
            return ACSum

    def DriveCarsInChannle(self, ALLCars, RoadDataStruct, channel):
        FrontCarPos = -1
        FrontCarstate = 1  # 只要是通过路口 状态都设置为等待状态
        for i in range(self.Rlength):  # 从车道前面往后面开始扫描
            if RoadDataStruct[i][channel] is not None:
                CarID = RoadDataStruct[i][channel]  # 车辆ＩＤ
                Car = ALLCars[CarID]
                Sv = min(self.Rspeed, Car.Cspeed)
                if Car.state == 2:  # 当前车辆为停止状态
                    FrontCarPos, FrontCarstate = i, 2  # 记录前面车辆的索引和状态
                    continue
                elif (i - Sv) > FrontCarPos:  # 可以行驶到停止状态 且无车阻挡
                    RoadDataStruct[i - Sv][channel] = RoadDataStruct[i][channel]
                    RoadDataStruct[i][channel] = None
                    FrontCarPos, FrontCarstate = i-Sv, 2
                    Car.UpdatePosAndSta(state=2, x=FrontCarPos, y=channel)
                elif FrontCarstate == 2:  # 前面车辆为停止状态
                    if FrontCarPos + 1 != i:
                        RoadDataStruct[FrontCarPos + 1][channel] = RoadDataStruct[i][channel]
                        RoadDataStruct[i][channel] = None
                    FrontCarPos, FrontCarstate = FrontCarPos + 1, 2
                    Car.UpdatePosAndSta(state=2, x=FrontCarPos, y=channel)
                else:  # 其他情况都标记为等待状态
                    FrontCarPos, FrontCarstate = i, 1  # 更新前面的车辆位置和状态为等待状态
                    #Car.UpdatePosAndSta(state=1, x=FrontCarPos, y=channel)

    # 车辆到达终点
    def CarInEnding(self, Distance, Channel, cross, ALLCars):
        CurRoadStruct = self.GetRoadIn(cross)  # y是当前车辆所在的channel
        CurRoadStruct[Distance][Channel] = None
        self.DriveCarsInChannle(ALLCars, CurRoadStruct, Channel)  # 更新当前道路的当前通道

    def CarGoInNowRoad(self, Car, NowRoadStruct):
        if self.NotCarInFront(Car.nowDistanceX, Car.nowChannleY, NowRoadStruct):
            NowRoadStruct[0][Car.nowChannleY] = NowRoadStruct[Car.nowDistanceX][Car.nowChannleY]
            NowRoadStruct[Car.nowDistanceX][Car.nowChannleY] = None
            Car.UpdatePosAndSta(state=2, x=0)  # 更新状态
        else:
            print("-----------Wrong------------")

    # 车辆进入下一条道路
    def CarGoToNextRoad(self, ALLRoads, NextRoadID, cross, Car, ALLCars):
        NextRoad = ALLRoads[NextRoadID]
        NextRoadStruct = NextRoad.GetRoadOut(cross)
        NowRoadStruct = self.GetRoadIn(cross)

        NowRoadSLeft = min(min(Car.Cspeed, self.Rspeed), Car.nowDistanceX)  # 当前道路剩余可行驶距离
        NextRoadMaxDis = min(NextRoad.Rspeed, Car.Cspeed)  # 下一条道路可行驶的最大距离
        NextRoadDis = NextRoadMaxDis - NowRoadSLeft  # 下一条道路可行驶的距离

        if NextRoadDis <= 0:  # 无法通过路口
            self.CarGoInNowRoad(Car, NowRoadStruct)
            self.DriveCarsInChannle(ALLCars, NowRoadStruct, Car.nowChannleY)  # 每次调度完路口之后都需要将当前道路当前车道的车辆调度
            return 2
        else:  # 可以通过路口
            for channle in range(NextRoad.Rchannel):
                NextRoadPos = NextRoad.NotCarInBack(NextRoad.Rlength-1-NextRoadDis, NextRoad.Rlength-1, channle, NextRoadStruct)
                if NextRoadPos == -1:  # 没有挡住当前车辆的行走
                    NextRoadStruct[NextRoad.Rlength - NextRoadDis][channle] = Car.Cid
                    NowRoadStruct[Car.nowDistanceX][Car.nowChannleY] = None  # 清空上一个位置
                    NextRoad.UpdateRoadCarsNumAdd(cross)
                    self.UpdateRoadCarsNumSub(cross)
                    self.DriveCarsInChannle(ALLCars, NowRoadStruct, Car.nowChannleY)  # 每次调度完路口之后都需要将当前道路当前车道的车辆调度
                    Car.UpdatePosAndSta(state=2, x=NextRoad.Rlength - NextRoadDis, y=channle, NowInRoad=NextRoadID,
                                      nextCrossId=ALLRoads[NextRoadID].GetNextCross(cross))
                    return 2  # 该车调度停止

                FrontCar = ALLCars[NextRoadStruct[NextRoadPos][channle]]  # 返回的不是-1 说明前面有车阻挡位置为i 前面位置车辆ID
                if FrontCar.state == 1:  # 前面车辆为等待状态 标记当前车辆为等待状态 不移动
                    Car.state = 1  # 标记等待状态 等待下次循环
                    return 1
                elif NextRoadPos != NextRoad.Rlength-1:  # 有位置可以进入 走到下一条道路的停止车辆后面
                    NextRoadStruct[NextRoadPos + 1][channle] = Car.Cid
                    NowRoadStruct[Car.nowDistanceX][Car.nowChannleY] = None  # 清空上一个位置
                    NextRoad.UpdateRoadCarsNumAdd(cross)
                    self.UpdateRoadCarsNumSub(cross)
                    self.DriveCarsInChannle(ALLCars, NowRoadStruct, Car.nowChannleY)  # 每次调度完路口之后都需要将当前道路当前车道的车辆调度
                    Car.UpdatePosAndSta(state=2, x=NextRoadPos + 1, y=channle, NowInRoad=NextRoadID,
                                      nextCrossId=ALLRoads[NextRoadID].GetNextCross(cross))
                    return 2
                else:
                    continue
            # 所有路口都已经满了 且为停止状态
            if Car.nowDistanceX != 0:  # 如果不在当前路口的最前面
                NowRoadStruct[0][Car.nowChannleY] = Car.Cid
                NowRoadStruct[Car.nowDistanceX][Car.nowChannleY] = None
            Car.UpdatePosAndSta(state=2, x=0)
            self.DriveCarsInChannle(ALLCars, NowRoadStruct, Car.nowChannleY)  # 每次调度完路口之后都需要将当前道路当前车道的车辆调度
            return 2

    def DriveAllCarJustOnRoadToEndState(self, ALLCars):  # 当前道路开始扫描车辆
        # 循环遍历道路上的每一个位置 将所有道路上的车辆状态初始化为等待状态
        for i in range(self.Rlength):  # 不管是正向还是反向车道 从0开始 0代表头 length代表为尾
            for j in range(self.Rchannel):
                if self.FromtoToRoad[i][j] is not None:  # 如果道路上该位置存在车辆
                    CarID = self.FromtoToRoad[i][j]  # 车辆ＩＤ
                    Car = ALLCars[CarID]
                    Car.UpdatePosAndSta(state=1)  # 更新所有的车辆的信息
                if self.RisDuplex:
                    if self.TotoFromRoad[i][j] is not None:  # 如果道路上该位置存在车辆
                        CarID = self.TotoFromRoad[i][j]  # 车辆ＩＤ
                        Car = ALLCars[CarID]
                        Car.UpdatePosAndSta(state=1)

        for channle in range(self.Rchannel):
            self.DriveCarsInChannle(ALLCars, self.FromtoToRoad, channle)  # 正向车道
            if self.RisDuplex:
                self.DriveCarsInChannle(ALLCars, self.TotoFromRoad, channle)  # 反向车道

    def GetFirstPriorityCar(self, ALLCars, Cross):
        CurRoadIn = self.GetRoadIn(Cross)  # 当前道路的数据结构 即进入该路口的道路
        if CurRoadIn == self.FromtoToRoad:  # TODO 可能判断会出现问题
            if self.FromtoToCapcity == 0:  # 当前道路无车辆
                return -1
        elif CurRoadIn == self.TotoFromRoad:
            if self.TotoFromCapcity == 0:  # 当前道路无车辆
                return -1
        # 扫描当前道路
        for length in range(self.Rlength):
            for channel in range(self.Rchannel):
                CarId = CurRoadIn[length][channel]
                if CarId is not None and ALLCars[CarId].state == 1:  # 当前优先级车辆 扫描到的第一輛不是停止的车就是该道路优先级最高的车
                    # if CarId in DebugCarID:
                    #     print("-------------debug-----------------")
                    Car = ALLCars[CarId]
                    # 计算当前车辆在当前道路可以行驶距离
                    SV1 = min(Car.Cspeed, self.Rspeed)
                    # 判断当前车道前面有没有车辆阻挡 只有出路口的车辆才判断优先级
                    if SV1 > length and self.NotCarInFront(length, channel, CurRoadIn) == -1:
                        return CurRoadIn[length][channel]
        return -1  # 没有出路口优先级的车辆

    def __str__(self):
        return "id:" + str(self.Rid) + " length " + str(self.Rlength) + " speed " + str(self.Rspeed) + " channel " + str(self.Rchannel) + " start " + str(self.Rfrom) + " to " + str(self.Rto) + " isDuplex " + str(self.RisDuplex)








