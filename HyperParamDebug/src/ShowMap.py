import Car
import Cross
import Road
import graphviz as gz



CityRode = gz.Digraph(name = "UrbanPlanningMap",graph_attr={"style":'filled',"color":'lightgrey'})


if __name__ == '__main__':
    allCars = Car.Cars("./1-map-training-1/car.txt")
    allRoads = Road.RoadS("./1-map-training-1/road.txt")
    allCross = Cross.CrossS("./1-map-training-1/cross.txt")


    for i in range(len(allCross.crossInfo)):
        CityRode.node(allCross.crossInfo[i].crossId)
    for j in range(len(allRoads.roadsInfo)):
        CityRode.edge(allRoads.roadsInfo[j].start, allRoads.roadsInfo[j].to, str(allRoads.roadsInfo[j].length))
        if(int(allRoads.roadsInfo[j].isDuplex)):
            CityRode.edge(allRoads.roadsInfo[j].to, allRoads.roadsInfo[j].start)

    #CityRode.view()
    CityRode.render('test-output/round-table.gv', view=True)
