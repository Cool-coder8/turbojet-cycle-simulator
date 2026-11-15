from station import Station


class Combustor:

    def __init__(self, Tt4, efficiency):

        self.Tt4 = Tt4
        self.efficiency = efficiency
        self.QR = 43e6 #J/kg assume we're using Jet A fuel(kerosene)

    def calculate(self, station3):

        station4 = Station(4)
        Tt4 = self.Tt4
        station4.Tt = Tt4
        Pt4 = station3.Pt
        station4.Pt = Pt4
        station4.f = round((station4.cp * (station4.Tt - station3.Tt)) / ((self.efficiency * self.QR) - (station4.cp * station4.Tt)), 2)

        

        # calculations go here later

        return station4