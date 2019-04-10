import Cross
import Car
import os
import Road

INF_val = 9999


class roadIdAndLength(object):  # 存入长度和id的类，进行封装
    def __init__(self, length, roadId):
        self.length = length
        self.roadId = roadId


class FloydAlgorithm(object):
    def __init__(self, car_path, road_path, cross_path, answer_path, OnesnumberCar):
        self.cCross = Cross.CrossS(cross_path,road_path,car_path)  # 读入路口信息
        self.rRoads = Road.RoadS(road_path)  # 读入道路信息
        self.cCars = Car.Cars(car_path)
        self.numberCar = OnesnumberCar
        self.answer = []

        graph = [[9999 for i in range(len(self.cCross.crossInfo))] for j in range(len(self.cCross.crossInfo))]# 初始化图的权重为无穷大
        for i in range(len(self.rRoads.roadsInfo)):  # 扫描每一辆车，对图相应的边进行赋值4 2
            graph[int(self.rRoads.roadsInfo[i].start) - 1][int(self.rRoads.roadsInfo[i].to) - 1] = roadIdAndLength(0.4 * self.rRoads.roadsInfo[i].channel + 0.1 * self.rRoads.roadsInfo[i].speed, self.rRoads.roadsInfo[i].id)
            if (int(self.rRoads.roadsInfo[i].isDuplex)):  # 判断是否为双向道路
                graph[int(self.rRoads.roadsInfo[i].to) - 1][int(self.rRoads.roadsInfo[i].start) - 1] = roadIdAndLength(0.4 * self.rRoads.roadsInfo[i].channel + 0.1 * self.rRoads.roadsInfo[i].speed, self.rRoads.roadsInfo[i].id)# 如果为双向道路，则对应位置赋值边长（道路长度）
        for i in range(len(self.cCross.crossInfo)):  # 对角线元素设置为0
            graph[i][i] = 0

        edges = []  #初始化边

        # 对图进行扫描，记录相应的边（路径id）已经边的长度
        for i in range(len(graph)):
            for j in range(len(graph[0])):
                if i != j and graph[i][j] != 9999:
                    edges.append((i, j, graph[i][j].length, graph[i][j].roadId))

        self.answer_path = answer_path
        self.node_list = edges
        self.graph = graph
        self.node = [self.cCross.crossInfo[i].crossId for i in range(len(self.cCross.crossInfo))]
        self.nodeNums = len(self.node)
        self.path_map = [[0 for val in range(self.nodeNums)] for val in range(self.nodeNums)]
        self.node_map = [[INF_val for val in range(self.nodeNums)] for val in range(self.nodeNums)]
        self._init_data()
        self._init_myFloyd()


    def _init_data(self):
        for i in range(self.nodeNums):
            # 对角线为0
            self.node_map[i][i] = 0
        for x, y, Length, RoadID in self.node_list:
            self.path_map[x][y] = y
            self.path_map[y][x] = x
        for k in range(self.nodeNums):
            for j in range(self.nodeNums):
                if type(self.graph[k][j]) != int:
                    self.node_map[k][j] = self.graph[k][j].length

        # 手动改变路径权重
        for k in range(9):
            self.node_map[k][k + 1] -= self.node_map[k][k + 1] * 2 / 3
            self.node_map[k+1][k] -= self.node_map[k+1][k] * 2 / 3

        for k in range(6):
            self.node_map[k + 57][k + 58] -= self.node_map[k + 57][k + 58] * 2 / 3
            self.node_map[k + 58][k + 57] -= self.node_map[k + 58][k + 57] * 2 / 3

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
        if os.path.exists(self.answer_path):  # 判断是否存在文件，有则删除
            os.remove(self.answer_path)
        file = open(self.answer_path, 'a')
        file.write(str("#(carId,StartTime,RoadId...)") + '\n')
        for i in range(len(self.cCars.carsInfo)):  # 为每一辆车规划最短路径
            NodePath = self._format_path(int(self.cCars.carsInfo[i].start) - 1, int(self.cCars.carsInfo[i].to) - 1)  # 得到车辆的路径信息（路口到路口）
            print(self.cCars.carsInfo[i].id, NodePath)
            shortestDistance = 0
            roadLine = []  # 初始化路信息
            for j in range(len(NodePath) - 1):
                roadLine.append(int(self.graph[int(NodePath[j]) - 1][int(NodePath[j + 1]) - 1].roadId))  # 将车辆所经过的路口信息转换为道路的ID，满足题目要求
                shortestDistance += self.rRoads[roadLine[j] - 5000].length
            roadLine.append(shortestDistance // self.cCars.carsInfo[i].speed)
            print(roadLine)
            info = [int(self.cCars.carsInfo[i].id), int(self.cCars.carsInfo[i].planTime)]  # 为满足题目要求，需要提供车辆的id以及规划的出发时间
            info.extend(roadLine)
            result = tuple(info)
            self.answer.append(result)

        self.answer.sort(key=lambda x: x[1])  # 根据出发时间进行排序，方便后面进行调度
        timeadd = float("inf")#初始化
        time = 1#
        for i in range(len(self.cCars.carsInfo)):
            #per 20
            if i == 0:  # 最开始出发的车辆，出发时间统一规划为1
                time = 1
            if timeadd > self.answer[i][-1]:  # 寻找出一批车辆当中最快跑完全部路程的时间
                timeadd = self.answer[i][-1]
            if i != 0 and (i % self.numberCar == 0):  # 每隔一个batch的车辆，给下一个batch的车辆的出发时间加上上一个batch中最短时间，以防死锁
                time = time + timeadd
            ans = [self.answer[i][0], time]
            ans.extend(self.answer[i][2:-1])
            result = tuple(ans)
            file.seek(0)
            file.write(str(result) + '\n')
            self.answer.append(ans)

        file.close()


if __name__ == '__main__':
    car_path = "./1-map-exam-2/car.txt"
    road_path = "./1-map-exam-2/road.txt"
    cross_path = "./1-map-exam-2/cross.txt"
    answer_path = "./1-map-exam-2/answer.txt"

    GrahpFloyd = FloydAlgorithm(car_path, road_path, cross_path, answer_path, 15)
    GrahpFloyd.findCarShortPathWithFloyd()

