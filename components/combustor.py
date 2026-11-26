from .station import Station


class Combustor:

    def __init__(self, Tt4, efficiency, bpressure_ratio):

        self.Tt4 = Tt4
        self.efficiency = efficiency
        self.bpressure_ratio = bpressure_ratio
        self.QR = 43e6 #J/kg assume we're using Jet A fuel(kerosene), if you forget the definition of QR, it is the heat of combustion of the fuel, which is the amount of energy released when a certain amount of fuel is burned. It is usually measured in Joules per kilogram (J/kg) or British thermal units per pound (BTU/lb). The value of QR can vary depending on the type of fuel being used. For example, the QR for Jet A fuel is approximately 43 MJ/kg, while the QR for gasoline is approximately 44 MJ/kg. The QR value is important in calculating the amount of fuel needed to achieve a certain level of thrust or power output in an engine.

    def calculate(self, station3):

        station4 = Station(4)
        Tt4 = self.Tt4
        station4.Tt = Tt4
        Pt4 = station3.Pt*self.bpressure_ratio
        station4.Pt = Pt4
        station4.f = round((station4.cp * (station4.Tt - station3.Tt)) / ((self.efficiency * self.QR) - (station4.cp * station4.Tt)), 8)
        

        # calculations go here later

        return station4