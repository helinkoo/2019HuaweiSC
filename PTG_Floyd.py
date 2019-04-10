"""
Floyd最短路径算法
"""
import PTG_ALLCars
import PTG_ALLCross
import PTG_ALLRoads
import os

INF_val = 9999
# 全局变量设置
TIMELINE = [0]
# 存放所有的信息
ALLCarsInfoWithDIC, ALLRoadsInfoWithDIC, ALLCrossInfoWithDIC = {}, {}, {}
# 记录所有的ＩＤ
ALLCarIndexToID, ALLRoadIndexToID, ALLCrossIndexToID = {}, {}, {}
# 记录已经到达终点的车辆
ALLCarIDToIndex, ALLRoadIDToIndex, ALLCrossIDToIndex = {}, {}, {}
# 记录已经到达终点的车辆
NUMOFENDINGCARS = 0

NUMOFCARS = 0


class roadIdAndLength(object):  # 存入长度和id的类，进行封装
    def __init__(self, cost, roadId):
        self.length = cost
        self.roadId = roadId


def ReadTxtData():
    # 设置文件路径
    Carspath = "./1-map-exam-2/car.txt"
    Roadspath = "./1-map-exam-2/road.txt"
    Crosspath = "./1-map-exam-2/cross.txt"

    # 读取ＴＸＴ文件信息
    CarsInfo = open(Carspath, 'r').read().split('\n')[1:]  # 车辆信息
    RoadsInfo = open(Roadspath, 'r').read().split('\n')[1:]  # 道路信息
    CrossInfo = open(Crosspath, 'r').read().split('\n')[1:]  # 路口信息

    # ------------开始初始化 道路类　路口类　车辆类　基本信息-------------- #

    # 提取车辆信息 创建车辆字典 字典value为ALLCarIDs类
    for index, info in enumerate(CarsInfo):
        [Cid, Cfrom, Cto, Cspeed, CplanTime] = info.replace(' ', '').replace('\t', '')[1:-1].split(',')
        ALLCarIDToIndex[int(Cid)] = index + 10000  # 所有车辆的ID
        ALLCarIndexToID[index + 10000] = int(Cid)
        ALLCarsInfoWithDIC[int(Cid)] = PTG_ALLCars.CARS([Cid, Cfrom, Cto, Cspeed, CplanTime])

    # 提取道路信息 创建道路字典 字典value为ALLRoadIDs类
    for index, info in enumerate(RoadsInfo):
        [Rid, Rlength, Rspeed, Rchannel, Rfrom, Rto, RisDuplex] = info.replace(' ', '').replace('\t', '')[1:-1].split(',')
        ALLRoadIDToIndex[int(Rid)] = index + 5000  # 所有车辆的ID
        ALLRoadIndexToID[index + 5000] = int(Rid)
        ALLRoadsInfoWithDIC[int(Rid)] = PTG_ALLRoads.ROADS([Rid, Rlength, Rspeed, Rchannel, Rfrom, Rto, RisDuplex])

    # 提取路口信息 创建路口字典 字典value为ALLCrossIDs类
    for index, info in enumerate(CrossInfo):
        [crossId, roadNId, roadEId, roadSId, roadWId] = info.replace(' ', '').replace('\t', '')[1:-1].split(',')
        ALLCrossIDToIndex[int(crossId)] = index  # 所有车辆的ID
        ALLCrossIndexToID[index] = int(crossId)
        ALLCrossInfoWithDIC[int(crossId)] = PTG_ALLCross.CROSS([crossId, roadNId,
                                                                roadEId, roadSId, roadWId], ALLRoadsInfoWithDIC)


class FloydAlgorithm(object):
    def __init__(self, ALLcars, ALLroads, ALLcross, Answer_path, ALLCarIDToIndex, ALLRoadIDToIndex,
                 ALLCrossIDToIndex, ALLCarIndexToID, ALLRoadIndexToID, ALLCrossIndexToID, OnesnumberCar):
        self.cCross = ALLcross  # 路口信息
        self.rRoads = ALLroads  # 道路信息
        self.cCars = ALLcars  # 车辆信息
        self.numberCar = OnesnumberCar
        self.answer = []
        self.Answerspath = Answer_path

        self.ALLCarIDToIndex = ALLCarIDToIndex  # 获得Index
        self.ALLRoadIDToIndex = ALLRoadIDToIndex
        self.ALLCrossIDToIndex = ALLCrossIDToIndex

        self.ALLCarIndexToID = ALLCarIndexToID  # 获得ID
        self.ALLRoadIndexToID = ALLRoadIndexToID
        self.ALLCrossIndexToID = ALLCrossIndexToID

        graph = [[9999 for i in range(len(self.cCross))] for j in range(len(self.cCross))]  # 初始化图的权重为无穷大

        for i in range(len(self.ALLRoadIDToIndex)):  # 扫描每一辆车，对图相应的边进行赋值 4 2
            graph[self.ALLCrossIDToIndex[self.rRoads[self.ALLRoadIndexToID[i+5000]].Rfrom]][self.ALLCrossIDToIndex[self.rRoads[self.ALLRoadIndexToID[i+5000]].Rto]]\
                = roadIdAndLength(0.4 * self.rRoads[self.ALLRoadIndexToID[i+5000]].Rchannel + 0.1 * self.rRoads[self.ALLRoadIndexToID[i+5000]].Rspeed, self.rRoads[self.ALLRoadIndexToID[i+5000]].Rid)   # i+5000-->index-->ID-->From-->CrossIndex
            if (self.rRoads[self.ALLRoadIndexToID[i+5000]].RisDuplex):  # 判断是否为双向道路
                graph[self.ALLCrossIDToIndex[self.rRoads[self.ALLRoadIndexToID[i+5000]].Rto]][self.ALLCrossIDToIndex[self.rRoads[self.ALLRoadIndexToID[i+5000]].Rfrom]] \
                    = roadIdAndLength(0.4 * self.rRoads[self.ALLRoadIndexToID[i+5000]].Rchannel + 0.1 * self.rRoads[self.ALLRoadIndexToID[i+5000]].Rspeed, self.rRoads[self.ALLRoadIndexToID[i+5000]].Rid)  # 如果为双向道路，则对应位置赋值边长（道路长度）
        for i in self.ALLCrossIndexToID:  # 输出元素为Index 对角线元素设置为0
            graph[i][i] = 0

        edges = []  # 初始化边

        # 对图进行扫描，记录相应的边（路径id）已经边的长度
        for i in range(len(graph)):
            for j in range(len(graph[0])):
                if self.ALLCrossIndexToID[i] != self.ALLCrossIndexToID[j] and graph[i][j] != 9999:
                    edges.append((self.ALLCrossIndexToID[i], self.ALLCrossIndexToID[j], graph[i][j].length,
                                  graph[i][j].roadId))

        self.answer_path = Answer_path
        self.node_list = edges
        self.graph = graph
        self.node = self.ALLCrossIndexToID
        self.nodeNums = len(self.node)
        self.path_map = [[0 for val in range(self.nodeNums)] for val in range(self.nodeNums)]
        self.node_map = [[INF_val for val in range(self.nodeNums)] for val in range(self.nodeNums)]
        self._init_data()
        self._init_myFloyd()

    def DictionaryMap(self, CarDict):
        pass

    def _init_data(self):
        for i in range(self.nodeNums):
            # 对角线为0
            self.node_map[i][i] = 0
        for x, y, Length, RoadID in self.node_list:
            self.path_map[self.ALLCrossIDToIndex[x]][self.ALLCrossIDToIndex[y]] = self.ALLCrossIDToIndex[y]
            self.path_map[self.ALLCrossIDToIndex[y]][self.ALLCrossIDToIndex[x]] = self.ALLCrossIDToIndex[x]
        for k in range(self.nodeNums):
            for j in range(self.nodeNums):
                if type(self.graph[k][j]) != int:
                    self.node_map[k][j] = self.graph[k][j].length
        print('_init_data is end')

    def _init_myFloyd(self):
        for k in range(self.nodeNums):
            for i in range(self.nodeNums):
                for j in range(self.nodeNums):
                    tmp = self.node_map[i][k] + self.node_map[k][j]
                    if self.node_map[i][j] > tmp:
                        self.node_map[i][j] = tmp
                        self.path_map[i][j] = self.path_map[i][k]
        print('_init_myFloyd is end')

    def _format_path(self, from_node, to_node):
        nodelist = []
        temp_node = from_node
        obj_node = to_node
        nodelist.append(self.node[temp_node])
        while True:
            nodelist.append(self.node[self.path_map[temp_node][obj_node]])
            temp_node = self.path_map[temp_node][obj_node]
            if temp_node == obj_node:
                break
        return nodelist

    def findCarShortPathWithFloyd(self):
        if os.path.exists(self.Answerspath):  # 判断是否存在文件，有则删除
            os.remove(self.Answerspath)
        file = open(self.Answerspath, 'a')
        file.write(str("#(carId,StartTime,RoadId...)") + '\n')

        for i in range(len(self.cCars)):  # 为每一辆车规划最短路径
            NodePath = self._format_path(self.ALLCrossIDToIndex[self.cCars[self.ALLCarIndexToID[i+10000]].Cfrom],
                                         self.ALLCrossIDToIndex[self.cCars[self.ALLCarIndexToID[i+10000]].Cto])  # 得到车辆的路径信息（路口到路口）
            print(self.cCars[self.ALLCarIndexToID[i+10000]].Cid, NodePath)
            roadLine = []  # 初始化路信息
            for j in range(len(NodePath) - 1):
                roadLine.append(int(self.graph[self.ALLCrossIDToIndex[NodePath[j]]]
                                    [self.ALLCrossIDToIndex[NodePath[j+1]]].roadId))  # 将车辆所经过的路口信息转换为道路的ID，满足题目要求
            print(roadLine)
            info = [int(self.cCars[self.ALLCarIndexToID[i+10000]].Cid),
                    int(self.cCars[self.ALLCarIndexToID[i+10000]].CplanTime)]  # 为满足题目要求，需要提供车辆的id以及规划的出发时间
            info.extend(roadLine)
            result = tuple(info)
            self.answer.append(result)

        self.answer.sort(key=lambda x: x[1])  # 根据出发时间进行排序，方便后面进行调度

        timeadd = float("inf")#初始化
        time = 1#
        for i in range(len(self.cCars)):
            #per 20
            if i == 0:  # 最开始出发的车辆，出发时间统一规划为1
                time = 1
            if i != 0 and (i % self.numberCar == 0):  # 每隔一个batch的车辆，给下一个batch的车辆的出发时间加上上一个batch中最短时间，以防死锁
                time = time + 50
            ans = [self.answer[i][0], time]
            ans.extend(self.answer[i][2:-1])
            result = tuple(ans)
            file.seek(0)
            file.write(str(result) + '\n')
            self.answer.append(ans)

        file.close()

        return self.answer



if __name__ == '__main__':
    ReadTxtData()
    Answerspath = "./1-map-exam-2/answer.txt"
    GrahpFloyd = FloydAlgorithm(ALLCarsInfoWithDIC, ALLRoadsInfoWithDIC, ALLCrossInfoWithDIC, Answerspath,  ALLCarIDToIndex, ALLRoadIDToIndex,
                 ALLCrossIDToIndex, ALLCarIndexToID, ALLRoadIndexToID, ALLCrossIndexToID, 600)
    ans = GrahpFloyd.findCarShortPathWithFloyd()
    print("Finish")