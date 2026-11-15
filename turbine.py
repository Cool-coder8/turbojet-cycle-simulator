
from station import Station




class Turbine:

    def __init__(self):
        self.work = None

    def calculate(self, station4, compressor_work):
        self.work = compressor_work
        station5 = Station(5)
        Tt5 = station4.Tt - (self.work / station4.cp)
        station5.Tt = Tt5
        Pt5 = round(station4.Pt * (Tt5 / station4.Tt) ** (station5.gamma / (station5.gamma - 1)), 2)
        station5.Pt = Pt5
        station5.f = station4.f
        
        # calculations go here later


        return station5