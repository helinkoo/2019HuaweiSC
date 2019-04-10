import Cross
import Road
import Car
from collections import defaultdict
from heapq import *
import os
if __name__ == "__main__":
    car_path = "../config/car.txt"
    road_path = "../config/road.txt"
    cross_path = "../config/cross.txt"
    answer_path = "../config/answer.txt"

    ll = Cross.CrossS(cross_path, car_path)
