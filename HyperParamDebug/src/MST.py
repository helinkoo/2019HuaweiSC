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
        self.cCross = Cross.CrossS(cross_path)  # 读入路口信息
        self.rRoads = Road.RoadS(road_path)  # 读入道路信息
        self.answer_path = answer_path  # 保存answer.txt文件的路径
        self.cars = Car.Cars(car_path)  # 车辆文件的路径
        self.answerIn = []  # 根据出发时间排序的车辆id、路径信息
        self.answer = []  # 用于保存最后的输出结果
        self.nodePath = []
        self.numberCar = OnesnumberCar  # 一次性行驶车辆数
        self.carPath = []
        graph = [[9999 for i in range(len(self.cCross.crossInfo))] for j in range(len(self.cCross.crossInfo))]  # 初始化图的权重为无穷大
        for i in range(len(self.rRoads.roadsInfo)):  # 扫描每一辆车，对图相应的边进行赋值
            if (int(self.rRoads.roadsInfo[i].isDuplex)):  # 判断是否为双向道路
                graph[int(self.rRoads.roadsInfo[i].start) - 1][int(self.rRoads.roadsInfo[i].to) - 1] = roadIdAndLength(100-4*self.rRoads.roadsInfo[i].channel-3*self.rRoads.roadsInfo[i].speed, self.rRoads.roadsInfo[i].id)
                graph[int(self.rRoads.roadsInfo[i].to) - 1][int(self.rRoads.roadsInfo[i].start) - 1] = roadIdAndLength(100-4*self.rRoads.roadsInfo[i].channel-3*self.rRoads.roadsInfo[i].speed, self.rRoads.roadsInfo[i].id)  # 如果为双向道路，则对应位置赋值边长（道路长度）
            else:
                graph[int(self.rRoads.roadsInfo[i].start) - 1][int(self.rRoads.roadsInfo[i].to) - 1] = 9999
        for i in range(len(self.cCross.crossInfo)):  # 对角线元素设置为0
            graph[i][i] = 0
        self.graph = graph
        self.nodenum = self.get_nodenum()
        self.edgenum = self.get_edgenum()
    def get_nodenum(self):
        return len(self.graph)

    def get_edgenum(self):
        count = 0
        for i in range(self.nodenum):
            for j in range(i):
                if i != j and self.graph[i][j] != 9999:
                    count += 1
        return count

    def kruskal(self):
        res = []
        if self.nodenum <= 0 or self.edgenum < self.nodenum - 1:
            return res
        edge_list = []
        for i in range(self.nodenum):
            for j in range(i, self.nodenum):
                if i != j and self.graph[i][j] != 9999:
                    edge_list.append([i, j, self.graph[i][j].length])  # 按[begin, end, weight]形式加入
        edge_list.sort(key=lambda a: a[2])  # 已经排好序的边集合

        group = [[i] for i in range(self.nodenum)]
        for edge in edge_list:
            for i in range(len(group)):
                if edge[0] in group[i]:
                    m = i
                if edge[1] in group[i]:
                    n = i
            if m != n:
                res.append(edge)
                group[m] = group[m] + group[n]
                group[n] = []
        return res

    def spaningTree(self):
        result = self.kruskal()
        graph = [[9999 for i in range(len(self.cCross.crossInfo))] for j in range(len(self.cCross.crossInfo))]  # 初始化图的权重为无穷大
        for m in result:
            graph[m[0]][m[1]] = roadIdAndLength(m[2], self.graph[m[0]][m[1]].roadId)
            graph[m[1]][m[0]] = roadIdAndLength(m[2], self.graph[m[1]][m[0]].roadId)
        self.graph = graph
        #print(self.graph)
        edges = []  # 初始化边
        # 对图进行扫描，记录相应的边（路径id）已经边的长度
        for i in range(len(graph)):
            for j in range(len(graph[0])):
                if i != j and graph[i][j] != 9999:
                    edges.append((i, j, graph[i][j].length, graph[i][j].roadId))
        self.edges = edges

    # Dijkstra算法用于计算相应两点之间的最点路径以及路径总长度
    def dijkstra_raw(self, from_node, to_node):
        self.spaningTree()
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

    def findCarShortPath(self):
        for i in range(len(self.cars.carsInfo)):  # 为每一辆车规划最短路径
            tmpA = int(self.cars.carsInfo[i].start) - 1
            tmpB = int(self.cars.carsInfo[i].to) - 1
            distance, path = self.dijkstra(int(self.cars.carsInfo[i].start) - 1, int(self.cars.carsInfo[i].to) - 1)  # 得到车辆的路径信息（路口到路口）
            print(self.cars.carsInfo[i].id, distance, path)
            self.nodePath.append(path)
            print(path)
            roadLine = []  # 初始化路信息
            for j in range(len(path) - 1):
                roadLine.append(int(self.graph[path[j]][path[j + 1]].roadId))  # 将车辆所经过的路口信息转换为道路的ID，满足题目要求
            print(roadLine)
            self.carPath.append(roadLine)
        return self.carPath

    """
    def prim(self):
        res = []
        if self.nodenum <= 0 or self.edgenum < self.nodenum - 1:
            return res
        res = []
        seleted_node = [0]
        candidate_node = [i for i in range(1, self.nodenum)]

        while len(candidate_node) > 0:
            begin, end, minweight = 0, 0, 9999
            for i in seleted_node:
                for j in candidate_node:
                    if self.graph[i][j] < minweight:
                        minweight = self.graph[i][j]
                        begin = i
                        end = j
            res.append([begin, end, minweight])
            seleted_node.append(end)
            candidate_node.remove(end)
        return res
    """


if __name__ == "__main__":
    car_path = "../config/car.txt"
    road_path = "../config/road.txt"
    cross_path = "../config/cross.txt"
    answer_path = "../config/answer.txt"

    g = Graph(car_path, road_path, cross_path, answer_path, 70)
    ll = g.findCarShortPath()
    print(ll)





