class Station:
    def __init__(self, number):
        self.number = number

        # Static Properties
        self.T = None      # static temperature
        self.P = None      # static pressure

        # Stagnation Properties
        self.Tt = None     # stagnation temperature
        self.Pt = None     # stagnation pressure

        #Flow properties
        self.mdot = None   # mass flow rate
        self.M = None      # Mach number
        self.airvelocity = None # Velocity of air
        self.rho = None    # Density
        self.gamma = 1.4  # specific heat area (Assume constant for now)
        self.cp = 1004     # specific heat capacity (Assume constant for now)
        self.R  = 287    # Gas constant (Assume constant for now)
        self.a = None      # speed of sound

        #Geometry
        self.area = None   # Area
        #self.tau = None    # Temperature ratio (T_exit / T_inlet), commented out for now cos its specifically for compressor / combustor
        #self.pi = None     # Pressure ratio (P_exit / P_inlet),    commented out for now cos its specifically for compressor
        self.f = None      # fuel-to-air (mass flow fuel/ mass flow air)

 
    def display(self):              # Display each component for each station
        print(f"\nStation {self.number}")
        print(f"T  = {self.T}")
        print(f"P  = {self.P}")
        print(f"Tt = {self.Tt}")
        print(f"Pt = {self.Pt}")
        print(f"M  = {self.M}")
        print(f"mdot = {self.mdot}")
        print(f"airvelocity = {self.airvelocity}")
        print(f"rho = {self.rho}")
        print(f"area = {self.area}")
        print(f"gamma = {self.gamma}")
        print(f"cp = {self.cp}")
        print(f"R = {self.R}")
       # print(f"tau = {self.tau}")
       # print(f"pi = {self.pi}")
        print(f"f = {self.f}")
        print(f"a = {self.a}")
''' (Maybe I'll implement a copy function later, but for now I'm good)
    def copy(self, new_number):
        new_station = Station(new_number)
        new_station.T = self.T
        new_station.P = self.P
        new_station.Tt = self.Tt
        new_station.Pt = self.Pt
        new_station.M = self.M
        new_station.mdot = self.mdot
        new_station.airvelocity = self.airvelocity
        new_station.rho = self.rho
        new_station.area = self.area
        new_station.gamma = self.gamma
        new_station.cp = self.cp
        new_station.R = self.R
        new_station.f = self.f
        new_station.a = self.a
        return new_station '''