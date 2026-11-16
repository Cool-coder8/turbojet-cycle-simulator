from station import Station


class Inlet:

    def __init__(self,efficiency):

        self.efficiency = efficiency #placeholder for now, will be used later for isentropic efficiency calculations

    def calculate(self, station0):

        station2 = Station(2)
        station2.Tt = (station0.Tt)
        station2.Pt = (self.efficiency*station0.Pt) 
        station2.mdot = (station0.mdot)

        

        # calculations later

        return station2