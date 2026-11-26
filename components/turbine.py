
from .station import Station




class Turbine:

    def __init__(self, efficiency):
        self.efficiency = efficiency #placeholder for now, will be used later for isentropic efficiency calculations
        self.work = None

    def calculate(self, station4, compressor_work):
        self.work = compressor_work
        station5 = Station(5)
        station5.mdot = station4.mdot
        Tt5 = station4.Tt - (self.work / (station5.cp*(1 + station4.f)))
        Tt5s = station4.Tt - ((station4.Tt - Tt5) / self.efficiency)
        station5.Tt = Tt5
        Pt5 = round(station4.Pt * (Tt5s / station4.Tt) ** (station5.gamma / (station5.gamma - 1)), 2)
        station5.Pt = Pt5
        station5.f = station4.f
        
        # calculations go here later


        return station5