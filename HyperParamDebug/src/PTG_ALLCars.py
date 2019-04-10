"""
车辆数据
"""


class CARS(object):
    def __init__(self, carInfo):
        # -----基本信息----- #
        self.Cid = int(carInfo[0])
        self.Cfrom = int(carInfo[1])
        self.Cto = int(carInfo[2])
        self.Cspeed = int(carInfo[3])
        self.CplanTime = int(carInfo[4])
        # -----基本信息----- #

        # 记录车辆的位置信息和状态
        self.state = 0  # 状态０　１　２　３　分别表示等待发车　等待状态　停止状态　到达终点
        # 记录车辆在当前道路的位置 初始设置为-1
        self.nowDistanceX = -1
        self.nowChannleY = -1
        # 记录车辆的当前道路
        self.NowRoad = None
        # 记录车辆的下一条道路
        self.NextRoad = None
        self.NextCrossID = self.Cfrom
        self.planTime, self.planRoute, self.routeIndex = -1, [], -1

        self.CarCurRoadLeft = -1

    def InitAnswers(self, PlanTime, PlanRoute):
        self.planTime = int(PlanTime)
        self.planRoute = PlanRoute  # 规划路线
        self.routeIndex = 0

    def setCarInitState(self):
        if self.state == 2:
            self.state = 1

    # TODO 通过已经规划的路径获得下一条道路
    def GetNextRoadstatic(self):
        try:
            return self.planRoute[self.routeIndex]
        except:
            return -1

    def GetAvailableSpeed(self, NextRoad):
        return min(self.Cspeed, NextRoad.Rspeed)

    # 获得下一次道路的ID 可以通过算法
    def GetNextRoad(self):
        # TODO 算法更新道路
        pass

    def UpdatePosAndSta(self, state, x=None, y=None, NowInRoad = None, nextCrossId=None):
        if self.state != 0 or NowInRoad is not None:  # 更新状态
            self.state = state
        self.nowDistanceX = x if x is not None else self.nowDistanceX  # 车辆的位置坐标
        self.nowChannleY = y if y is not None else self.nowChannleY  # 车辆的位置坐标

        # TODO 在已经规划好的道路上行驶
        if NowInRoad is not None and self.state != 0 and self.routeIndex < len(self.planRoute):
            self.routeIndex += 1

        self.NowRoad = NowInRoad if NowInRoad is not None else self.NowRoad

        if nextCrossId is not None:  # 下一个路口的ＩＤ
            self.NextCrossID = nextCrossId  # 将下一个路口的ＩＤ存入车辆类中

    def __str__(self):
        return "id:" + str(self.Cid) + " from " + str(self.Cfrom) + " to " + str(self.Cto) + " speed " + str(self.Cspeed) + " planTime " + str(self.CplanTime)






