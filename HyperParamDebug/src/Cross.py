from Road import RoadS
from Car import Cars
class Cross(object):
    def __init__(self, crossInfo):
        self.crossId = crossInfo[0]
        self.roadIds = [crossInfo[1], crossInfo[2], crossInfo[3], crossInfo[4]]
        self.x = 0
        self.y = 0
        self.done = False
        self.validRoadIndex = []
        self.carId = []#属于每一个路口的车
        for index in range(len(self.roadIds)):
            if int(self.roadIds[index]) != -1:
                self.validRoadIndex.append(index)
        self.validRoad = [self.roadIds[index] for index in self.validRoadIndex]

    def __validRoadIndex__(self):
        return self.validRoadIndex

    def __validRoad__(self):
        return self.validRoad
    def setDone(self, bool):
            self.done = bool

    def setLoc(self,x,y):
        self.x,self.y = x,y
    def __loc__(self):
        return self.x,self.y

    def roadDirection(self,roadId):
        if self.roadIds[0]==roadId:
            return 0
        elif self.roadIds[1]==roadId:
            return 1
        elif self.roadIds[2]==roadId:
            return 2
        elif self.roadIds[3]==roadId:
            return 3
        else:
            return -1


    def __str__(self):
        return "id:" + (self.crossId) + " roadNId " + self.roadNId + " roadEId " + self.roadEId + " roadSId " + str(self.roadSId) + " roadWId " + str(self.roadWId)

class CrossS(object):
    def __init__(self, dataPath, roadPath, carPath):
        self.crossInfo = self.readTxt(dataPath)
        self.roads = RoadS(roadPath)
        self.carInfo = Cars(carPath)
        print(self.carInfo.len())


    def __getitem__(self, key):
        return self.crossInfo[key]

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
            car.append(Cross(a))
            line = f.readline()
        # print(car)
        # print(len(car))
        f.close()
        return car

    def crossLocGen(self):
        #**** relative location ****#
        # denote the first cross as the origin of coordinates
        crossList = [self.crossInfo[0].crossId]
        #for i in range(len(self.crossInfo)):
        #crossList.append(self.crossInfo[0].crossId)
        minX,minY = 0,0
        while(crossList.__len__()>0):
            nextCrossList = []
            for crossId in crossList:
                presentX,presntY = self.crossInfo[int(crossId) - 1].__loc__()
                validRoad = self.crossInfo[int(crossId) - 1].__validRoad__()
                for roadId in validRoad:
                    nextCrossId = self.roads.roadsInfo[int(roadId) - 5000].to if self.roads.roadsInfo[int(roadId) - 5000].start != crossId \
                        else self.roads.roadsInfo[int(roadId) - 5000].start

                    # if next cross is visited
                    if not self.crossInfo[int(nextCrossId) - 1].done:
                        # visit sets true
                        self.crossInfo[int(nextCrossId) - 1].setDone(True)
                        # relative location of nextcross
                        nextX,nextY = self.crossRelativeLoc(presentX,presntY,crossId,roadId)
                        # update location
                        self.crossInfo[int(nextCrossId) - 1].setLoc(nextX,nextY)
                        minX,minY = min(nextX,minX),min(nextY,minY)
                        nextCrossList.append(int(nextCrossId))
            crossList = nextCrossList
        for crossId in crossList:
            x,y = self.crossInfo[int(crossId)].__loc__()
            self.crossInfo[int(crossId) - 1].setLoc(x-minX,y-minY)
    def crossRelativeLoc(self,x,y,crossId,roadId):
        roadDirection = self.crossInfo[int(crossId) - 1].roadDirection(roadId)
        if roadDirection==0:
            return x,y+1
        elif roadDirection==1:
            return x+1,y
        elif roadDirection==2:
            return x,y-1
        elif roadDirection==3:
            return x-1,y
        else:
            print("Cross(%d) don't interact with road(%d)"%(self.id_,roadId))

if __name__ == "__main__":
    car_path = "../config/car.txt"
    road_path = "../config/road.txt"
    cross_path = "../config/cross.txt"
    answer_path = "../config/answer.txt"

    ll = CrossS(cross_path, road_path, car_path)
    ll.crossLocGen()
    print(ll)



