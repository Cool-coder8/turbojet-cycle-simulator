from station import Station


class Compressor:

    def __init__(self, pressure_ratio):

        self.pressure_ratio = pressure_ratio
        self.work = None

    def calculate(self, station2):

        station3 = Station(3)
        Tt3 = (station2.Tt) * (self.pressure_ratio ** ((station3.gamma - 1) / station3.gamma))
        station3.Tt = round(Tt3, 2)
        Pt3 = (station2.Pt) * self.pressure_ratio
        station3.Pt = Pt3
        self.work = round(station3.cp * (station3.Tt - station2.Tt),2)
        
        # add calcs later



        return station3