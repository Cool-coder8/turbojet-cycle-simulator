from station import Station
import math


class Nozzle:

    def __init__(self,efficiency):

        self.efficiency = efficiency #placeholder for now, will be used later for isentropic efficiency calculations

    def calculate_choked(self, station5):

        station8 = Station(8)
        station8.mdot = station5.mdot


        T8s = round((station5.Tt)*(2/(station5.gamma+1)), 2)
        T8 = station5.Tt - ((station5.Tt - T8s)*self.efficiency)
        station8.T = T8
        P8 = station5.Pt * (T8 / station5.Tt) ** (station5.gamma / (station5.gamma - 1))
        station8.P = P8
        v8 = round(math.sqrt((2*station5.cp*(station5.Tt-station8.T))), 2)
        station8.airvelocity = round(v8, 2)
        station8.f = station5.f
        
        

        return station8

    def calculate_unchoked(self, station5):
        pass