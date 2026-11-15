import math
from station import Station
from inlet import Inlet
from compressor import Compressor
from combustor import Combustor
from turbine import Turbine
from nozzle import Nozzle
from atmosphere import isa_atmosphere


station0 = Station(0)

inlet = Inlet()
compressor = Compressor(10)
combustor = Combustor(1400, 1.0)
turbine = Turbine()
nozzle = Nozzle()

altitude = int(input("Enter altitude (m): from 0-11000): "))

T, P, rho = isa_atmosphere(altitude)

station0 = Station(0)

station0.T = T
station0.P = P
station0.rho = rho
station0.M = float(input("Enter Mach number: "))  # asummed 0.8 up until now, but will be user input later


def speed_of_sound(station0):
    station0.a = round(math.sqrt(station0.gamma * station0.R * station0.T), 2)

speed_of_sound(station0)
def air_v(station0):
    station0.airvelocity = round(station0.M * station0.a, 2)
air_v(station0)

def stag_temp_pressure(station0):
    station0.Tt = round(station0.T * (1 + (station0.gamma - 1) / 2 * station0.M**2), 2)
    station0.Pt = round(station0.P * (1 + (station0.gamma - 1) / 2 * station0.M**2)**(station0.gamma / (station0.gamma - 1)), 2)
stag_temp_pressure(station0)
station0.area = float(input("Enter inlet area (m^2): "))  # asummed None up until now, but will be user input now ig
station0.mdot = round(station0.rho * station0.airvelocity * station0.area, 2)  # is constant throughout engine, so initial mass flow rate is the same as the final mass flow rate, so we can just calculate it here and use it for all stations


station0.display()



station2 = inlet.calculate(station0)
station2.display()

station3 = compressor.calculate(station2)
station3.display()
print(f"Compressor Work: {compressor.work}")

station4 = combustor.calculate(station3)
station4.display()

station5 = turbine.calculate(station4, compressor.work)
station5.display()

station8 = nozzle.calculate(station5)

pressure_ratio = station5.Pt/station0.P
critical_ratio = ((station5.gamma + 1)/2)**(station5.gamma/(station5.gamma-1))
if pressure_ratio > critical_ratio:
    choked = True
    station8.M = 1 #assuming converging nozzle
        # calculations go here later

station8.display()
thrust = station0.mdot * (1 + station8.f) * (station8.airvelocity - station0.airvelocity)
print(f"\nThrust: {thrust:.2f} N")


