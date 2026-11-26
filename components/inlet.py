import math

from .station import Station


class Inlet:

    def __init__(self,efficiency):

        self.efficiency = efficiency #placeholder for now, will be used later for isentropic efficiency calculations

    def calculate(self, station0):

        station2 = Station(2)
        station2.Tt = (station0.Tt)
        station2.Pt = (self.efficiency*station0.Pt) # efficiency serves as inlet total pressure recovery
        station2.T = station0.T
        station2.M =  math.sqrt((2/(station2.gamma-1))*((station2.Tt/station2.T)-1))
        station2.P = station2.Pt/(1+((station2.gamma-1)/2)*(station2.M**2))**(station2.gamma/(station2.gamma-1))
        station2.rho = (station2.P)/(station2.R*station2.T)
        station2.airvelocity = station2.M * (math.sqrt(station2.gamma*station2.R*station2.T))
        station2.area = station0.area


        

        # calculations later

        return station2