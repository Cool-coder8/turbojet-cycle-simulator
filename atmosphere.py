# atmosphere.py
import math
from station import Station

def isa_atmosphere(altitude):
    if altitude >= 0 and altitude <= 11000:
        T = round(288.15 - 0.0065 * altitude, 2) #Kelvin
        P = round(101325 * (T / 288.15) ** (9.81 / (0.0065 * 287)), 2) # Pascals
        rho = round(P / (287 * T), 4) # kg/m^3
        return T, P, rho
    elif altitude > 11000 and altitude <= 20000:
       T = 216.65 #Kelvin
       P11 = 22614.21 #Pascals
       P = round(P11 * math.exp(-(9.81 * (altitude - 11000))/ (287 * T)),2)
       rho = round(P / (287 * T), 4) #kg/m^3
       return T, P, rho
