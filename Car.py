"""
读入车辆数据
"""
class Car(object):
    def __init__(self, carInfo):
        self.id = carInfo[0]
        self.start = carInfo[1]
        self.to = carInfo[2]
        self.speed = int(carInfo[3])
        self.planTime = int(carInfo[4])

    def __str__(self):
        return "id:" + (self.id) + " from " + self.start + " to " + self.to + " speed " + str(self.speed) + " planTime " + str(self.planTime)

class Cars(object):
    def __init__(self, dataPath):
        self.carsInfo = self.readTxt(dataPath)
    def len(self):
        return len(self.carsInfo)

    def __getitem__(self, key):
        return self.carsInfo[key]

    def readTxt(self, dataPath):
        f = open(dataPath)  # 返回一个文件对象
        next(f)
        line = f.readline()  # 调用文件的 readline()方法
        car = []
        while line:
            a = line.split(',')
            b = a[0].split('(')
            c = a[4].split(')')
            a[0] = b[1]
            a[4] = c[0]
            # print(a)
            car.append(Car(a))
            line = f.readline()
        # print(car)
        # print(len(car))
        f.close()
        return car




