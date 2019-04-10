""""
        for i in speedList:#依次为8 6 4 2
            sameSpeedCarListLength = len(sameSpeedCarsInfo[i])#统计当前速度相同的车辆的个数
            carNumEachSlice = sameSpeedCarListLength / sliceNum#同一速度同一时间片车辆的个数
            carNumber = 0
            for j in range(sliceNum):
                realPlanTime = (maxSpeed / i) * 35 * ((minWeight + j * cutOffLine) / maxWeight) + timeStamp
                carCount = 0
                for k in range(math.floor(carNumEachSlice)):
                    if ((carCount != 0) and (carCount % realCarNumber == 0)):
                        realPlanTime = realPlanTime + timeAdd
                        sameSpeedCarsInfo[i][carNumber][1] = max(sameSpeedCarsInfo[i][carNumber][1], math.ceil(realPlanTime))
                    carNumber = carNumber + 1
                    carCount = carCount + 1
            while(carNumber <= (sameSpeedCarListLength - 1)):
                sameSpeedCarsInfo[i][carNumber][1] = max(sameSpeedCarsInfo[i][carNumber][1], math.ceil(realPlanTime))
                carNumber = carNumber + 1

            #不同速度之间的时间间隔
        return sameSpeedCarsInfo, speedList
        """