from Two import DispatchCar
import PTG_DispatchCenter
from Grahp_exp import Graph
from hyperopt import fmin, tpe, hp, STATUS_OK, Trials



def hyperopt_train_test(params):
    car_path_three = "../config/1-map-training-3/car.txt"
    road_path_three = "../config/1-map-training-3/road.txt"
    cross_path_three = "../config/1-map-training-3/cross.txt"
    answer_path_three = "../config/1-map-training-3/answer.txt"
    trafficMapThree = Graph(car_path_three, road_path_three, cross_path_three, answer_path_three, 200)  # 生成交通图
    DispatchSystemThree = DispatchCar(trafficMapThree, **params)

    car_path_four = "../config/1-map-training-4/car.txt"
    road_path_four = "../config/1-map-training-4/road.txt"
    cross_path_four = "../config/1-map-training-4/cross.txt"
    answer_path_four = "../config/1-map-training-4/answer.txt"
    trafficMapFour = Graph(car_path_four, road_path_four, cross_path_four, answer_path_four, 200)  # 生成交通图
    DispatchSystemFour = DispatchCar(trafficMapFour, **params)

    AnswersInfoThree = DispatchSystemThree.DispatchCarBySpeed()
    AnswersInfoFour = DispatchSystemFour.DispatchCarBySpeed()

    timeThree = PTG_DispatchCenter.Dispatch(car_path_three, road_path_three, cross_path_three, AnswersInfoThree)#调度时间
    timeFour = PTG_DispatchCenter.Dispatch(car_path_four, road_path_four, cross_path_four, AnswersInfoFour)  # 调度时间
    return timeThree + timeFour

listNumber = [i for i in range(1, 21)]
carGoingNumber = [i for i in range(100, 1001)]
print(listNumber)
space = {
    'timeAdd': hp.uniform('timeAdd', 2, 100),
    'sliceNum': hp.choice('sliceNum', listNumber),
    'carGoingNumber': hp.choice('carGoingNumber', carGoingNumber),
    'timeStamp': hp.normal('timeStamp', 1, 5),
    'timeAddSpeed': hp.uniform('timeAddSpeed', 20, 50),
}

def f(params):
    acc = hyperopt_train_test(params)
    return {'loss': acc, 'status': STATUS_OK}

trials = Trials()
best = fmin(f, space, algo=tpe.suggest, max_evals=2000, trials=trials)
print('best:')
print(best)
print(space)
