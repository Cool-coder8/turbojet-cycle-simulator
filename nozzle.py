from station import Station
import math


class Nozzle:

    def __init__(self):

        pass

    def calculate(self, station5):

        station8 = Station(8)

        T8 = round((station5.Tt)*(2/(station5.gamma+1)), 2)
        station8.T = T8
        P8 = round((station5.Pt)/(((station5.gamma+1)/2)**(station5.gamma/(station5.gamma-1))), 2)
        station8.P = P8
        v8 = round(math.sqrt((2*station5.cp*(station5.Tt-station8.T))), 2)
        station8.airvelocity = round(v8, 2)
        station8.f = station5.f
        
        

        return station8