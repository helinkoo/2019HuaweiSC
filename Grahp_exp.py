import Cross
import Road
import Car
from collections import defaultdict
from heapq import *
import os

class roadIdAndLength(object):  # 存入长度和id的类，进行封装
    def __init__(self, length, roadId):
        self.length = length
        self.roadId = roadId


class Graph(object):
    def __init__(self, car_path, road_path, cross_path, answer_path, OnesnumberCar):
        self.cCross = Cross.CrossS(cross_path, road_path, car_path)  # 读入路口信息
        self.cCross.crossLocGen()#添加坐标
        self.rRoads = Road.RoadS(road_path)  # 读入道路信息
        self.answer_path = answer_path  # 保存answer.txt文件的路径
        self.cars = Car.Cars(car_path)  # 车辆文件的路径
        self.answerIn = []  # 根据出发时间排序的车辆id、路径信息
        self.answer = []  # 用于保存最后的输出结果
        self.nodePath = []
        self.numberCar = OnesnumberCar  # 一次性行驶车辆数
        self.carPath = []
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
        # print(edges)
        self.graph = graph
        self.edges = edges

    # Dijkstra算法用于计算相应两点之间的最点路径以及路径总长度
    def dijkstra_raw(self, from_node, to_node):
        g = defaultdict(list)
        for l, r, c, gg in self.edges:
            g[l].append((c, r))
        q, seen = [(0, from_node, ())], set()
        while q:
            (cost, v1, path) = heappop(q)
            if v1 not in seen:
                seen.add(v1)
                path = (v1, path)
                if v1 == to_node:
                    return cost, path
                for c, v2 in g.get(v1, ()):
                    if v2 not in seen:
                        heappush(q, (cost + c, v2, path))
        return float("inf"), []

    # 计算图中两点之间最短距离以及路径
    def dijkstra(self, from_node, to_node):
        len_shortest_path = -1
        ret_path = []
        length, path_queue = self.dijkstra_raw(from_node, to_node)
        if len(path_queue) > 0:
            len_shortest_path = length  ## 1. Get the length firstly;
            ## 2. Decompose the path_queue, to get the passing nodes in the shortest path.
            left = path_queue[0]
            ret_path.append(left)  ## 2.1 Record the destination node firstly;
            right = path_queue[1]
            while len(right) > 0:
                left = right[0]
                ret_path.append(left)  ## 2.2 Record other nodes, till the source-node.
                right = right[1]
            ret_path.reverse()  ## 3. Reverse the list finally, to make it be normal sequence.
        return len_shortest_path, ret_path

    # 为每一辆车初始规划最短行驶路径
    def findCarShortPath(self):
        for i in range(len(self.cars.carsInfo)):  # 为每一辆车规划最短路径
            distance, path = self.dijkstra(int(self.cars.carsInfo[i].start) - 1, int(self.cars.carsInfo[i].to) - 1)  # 得到车辆的路径信息（路口到路口）
            self.updateGraph(path)
            #print(self.cars.carsInfo[i].id, distance, path)
            self.nodePath.append(path)
            roadLine = []  # 初始化路信息
            for j in range(len(path) - 1):
                roadLine.append(int(self.graph[path[j]][path[j + 1]].roadId))  # 将车辆所经过的路口信息转换为道路的ID，满足题目要求
            #print(roadLine)
            self.carPath.append(roadLine)
        return self.carPath


    #根据已经路径上走过的车辆，然后对图当中的权值进行更新
    def updateGraph(self, nodeList):
        numberCarInRoad = 0.01
        for i in range(len(nodeList) - 1):#访问每一个车辆的所经过的节点，对应的车辆的权值
            self.graph[nodeList[i]][nodeList[i+1]].length = self.graph[nodeList[i]][nodeList[i+1]].length + numberCarInRoad

    #为每一个路口添加在该路口发车的车辆id以及出发的路径
    def addCarInfoInCross(self):
        for i in range(len(self.cCross.crossInfo)):
            for j in range(self.cCross.carInfo.len()):
                if(int(self.cCross.carInfo.carsInfo[j].start) == int(self.cCross.crossInfo[i].crossId)):
                    info = [self.cCross.carInfo.carsInfo[j].id, self.cCross.carInfo.carsInfo[j].planTime, self.cCross.carInfo.carsInfo[j].speed]
                    info.extend(self.carPath[j])
                    self.cCross.crossInfo[i].carId.append(info)


if __name__ == "__main__":
    car_path = "../config/car.txt"
    road_path = "../config/road.txt"
    cross_path = "../config/cross.txt"
    answer_path = "../config/answer.txt"

    g = Graph(car_path, road_path, cross_path, answer_path, 70)
    g.findCarShortPath()
    print("xixi")





