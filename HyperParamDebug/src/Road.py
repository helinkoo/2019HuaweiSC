import numpy as np


class Road(object):
    def __init__(self, roadsInfo):
        self.id = roadsInfo[0]
        self.length = int(roadsInfo[1])
        self.speed = int(roadsInfo[2])
        self.channel = int(roadsInfo[3])
        self.start = roadsInfo[4]
        self.to = roadsInfo[5]
        self.isDuplex = roadsInfo[6]
        self.roadMatrix = np.zeros((self.channel,self.length))
        if self.isDuplex:
            self.RroadMatrix = np.zeros((self.channel, self.length))

    def __str__(self):
        return "id:" + (self.id) + " length " + str(self.length) + " speed " + str(self.speed) + " channel " + str(self.channel) + " start " + self.start + " to " + self.to+ " isDuplex " + self.isDuplex


class RoadS(object):
    def __init__(self, dataPath):
        self.roadsInfo = self.readTxt(dataPath)

    def __getitem__(self, key):
        return self.roadsInfo[key]

    def readTxt(self, dataPath):
        f = open(dataPath)  # 返回一个文件对象
        next(f)
        line = f.readline()  # 调用文件的 readline()方法
        car = []
        while line:
            a = line.split(',')
            b = a[0].split('(')
            c = a[6].split(')')
            a[0] = b[1]
            a[6] = c[0]
            # print(a)
            car.append(Road(a))
            line = f.readline()
        # print(car)
        # print(len(car))
        f.close()
        return car





