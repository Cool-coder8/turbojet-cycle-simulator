import math

from .station import Station


class Nozzle:

    def __init__(self,efficiency):

        self.efficiency = efficiency #placeholder for now, will be used later for isentropic efficiency calculations

    def calculate_choked(self, station5):

        station8 = Station(8)
        station8.mdot = station5.mdot


        T8s = round((station5.Tt)*(2/(station5.gamma+1)), 3)
        T8 = station5.Tt - ((station5.Tt - T8s)*self.efficiency)
        station8.T = T8
        station8.Tt = station8.T * ((station8.gamma+1)/2)
        P8 = station5.Pt / 1.893 # new updated Pressure because efficiency should really only affect T and V 
        station8.P = P8
        station8.Pt = station8.P * ((station8.gamma+1)/2)**(station8.gamma/(station8.gamma-1))
        # maybe later i'll implement nozzle pressure ratio or veloc coefficient
        v8 = round(math.sqrt((2*station5.cp*(station5.Tt-station8.T))), 3)
        station8.airvelocity = round(v8, 3)
        station8.f = station5.f
        station8.rho = station8.P/(station8.R*station8.T)
        station8.area = station8.mdot/(station8.rho*station8.airvelocity)
        

        return station8

    def calculate_unchoked(self, station5, amb_press):

        station8 = Station(8)
        station8.mdot = station5.mdot

        #we get static temp here as equal to amb
        station8.P = amb_press
        T8s = round((station5.Tt)*(station8.P/station5.Pt)**((station5.gamma-1)/station5.gamma), 3)
        T8 = station5.Tt - (self.efficiency)*(station5.Tt - T8s)
        station8.T = T8
        V8 = round(math.sqrt((2*station5.cp*(station5.Tt-station8.T))), 3)
        station8.airvelocity = V8
        station8.M = math.sqrt((2/(station5.gamma-1))*((station5.Tt/station8.T)-1))
        station8.a = station8.airvelocity/station8.M
        isen = (1+((station8.gamma - 1)/2)* station8.M**2)
        station8.Tt = station8.T * isen
        station8.Pt = (station8.P* isen**(station8.gamma /(station8.gamma - 1)))
        station8.f = station5.f
        station8.rho = station8.P/(station8.R*station8.T)
        station8.area = station8.mdot/(station8.rho*station8.airvelocity)
        if station8.M >= 1:
            print("Warning: unchoked solution produced M >= 1")

        return station8
        
