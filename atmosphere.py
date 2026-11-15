# atmosphere.py
from station import Station

def isa_atmosphere(altitude):
    T = round(288.15 - 0.0065 * altitude, 2) #Kelvin
    P = round(101325 * (T / 288.15) ** (9.81 / (0.0065 * 287)), 2) # Pascals
    rho = round(P / (287 * T), 4) # kg/m^3
    return T, P, rho
