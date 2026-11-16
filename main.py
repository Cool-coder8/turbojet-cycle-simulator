import math
from station import Station
from inlet import Inlet
from compressor import Compressor
from combustor import Combustor
from turbine import Turbine
from nozzle import Nozzle
from atmosphere import isa_atmosphere
import json


def print_engine_info(engine):
    print("Loaded Engine:")
    print(f"{engine["name"]}\n")
    print(f"OPR: {engine["compressor_pr"]}")
    print(f"TT4: {engine["combustor_tt4"]}K")
    print(f"Inlet Area: {engine["inlet_area"]}m^2\n")
    print(f"Notes: \n {engine["notes"]} \n")

def run_engine(inlet, compressor, combustor, turbine, nozzle, area, mach, T, P, rho, display):
    station0 = Station(0)
    station0.area = area
    station0.T = T
    station0.P = P
    station0.rho = rho
    station0.M = mach

    speed_of_sound(station0)
    air_v(station0)
    stag_temp_pressure(station0)
    station0.mdot = round(station0.rho * station0.airvelocity * station0.area, 2)  # is constant throughout engine, so initial mass flow rate is the same as the final mass flow rate, so we can just calculate it here and use it for all stations
    station2 = inlet.calculate(station0)
    station3 = compressor.calculate(station2)
    station4 = combustor.calculate(station3)
    station5 = turbine.calculate(station4, compressor.work)
    pressure_ratio = station5.Pt/station0.P
    critical_ratio = ((station5.gamma + 1)/2)**(station5.gamma/(station5.gamma-1)) # should be about 1.893
    if pressure_ratio > critical_ratio:
        choked = True
        station8 = nozzle.calculate_choked(station5)
        station8.M = 1 #assuming converging nozzle
    else:
        choked = False
        station8 = nozzle.calculate_unchoked(station5, station0.P)
    momentum_thrust = (station8.mdot * station8.airvelocity) - (station0.mdot * station0.airvelocity)

    #General Engine Performance Calculations
    pressure_thrust = (station8.area*(station8.P - station0.P))
    thrust = momentum_thrust + pressure_thrust
    sfc = (((station8.f * station0.mdot)/thrust) * 3600)  # kg/(N.hr)
    nth = ((((1+station8.f)*(station8.airvelocity**2)) - (station0.airvelocity**2))/2)/(station8.f*combustor.QR) # thermal efficiency
    np = 2*station0.airvelocity/(station8.airvelocity + station0.airvelocity) # propulsive efficiency
    overall_efficiency = nth * np

    if display:
        station0.display()
        station2.display()
        station3.display()
        print(f"Compressor Work: {compressor.work}")
        station4.display()
        station5.display()
        station8.display()
        print("\nFinal Important Values:")
        print(f"Thrust: {thrust:.2f} N")
        print(f"SFC: {sfc:.8f} kg/(N.hr)")
        print(f"Thermal Efficiency: {(nth*100):.4f}%")
        print(f"Propulsive Efficiency: {(np*100):.4f}%")
        print(f"Overall Efficiency: {(overall_efficiency*100):.4f}%")
        print(f"momentum_thrust: {momentum_thrust}")
        print(f"pressure_thrust: {pressure_thrust}")

    return {
        "thrust": thrust,
        "sfc": sfc,
        "nth": nth,
        "np": np,
        "overall_efficiency": overall_efficiency,
        "momentum_thrust": momentum_thrust,
        "pressure_thrust": pressure_thrust
    }
        
def speed_of_sound(station0):  #calcs  speed of sound at a temp
    station0.a = round(math.sqrt(station0.gamma * station0.R * station0.T), 2)
def air_v(station0):   #calcs v = Ma
    station0.airvelocity = round(station0.M * station0.a, 2)
def stag_temp_pressure(station0):
    station0.Tt = round(station0.T * (1 + (station0.gamma - 1) / 2 * station0.M**2), 2)
    station0.Pt = round(station0.P * (1 + (station0.gamma - 1) / 2 * station0.M**2)**(station0.gamma / (station0.gamma - 1)), 2)

mode = int(input("Pick a Mode: \n1.Plug in your own engine values \n2.Select a preset engine\n3.Compare all Engines & Performance\n: "))

if mode == 1:

    inlet = Inlet(float(input("Enter inlet efficiency: ")))
    compressor = Compressor(float(input("Enter compressor pressure ratio: ")), float(input("Enter compressor efficiency: ")))
    combustor = Combustor(float(input("Enter combustor target temperature (K): ")), 
                          float(input("Enter combustor efficiency: ")), 
                          float(input("Enter combustor pressure ratio: ")))
    turbine = Turbine(float(input("Enter turbine efficiency: ")))
    nozzle = Nozzle(float(input("Enter nozzle efficiency: ")))

    area = float(input("Enter inlet area (m^2): "))  # asummed None up until now, but will be user input now ig
    mach = float(input("Enter Mach number: "))  # asummed 0.8 up until now, but will be user input later
    altitude = int(input("Enter altitude (m): from 0-11000): "))
    T, P, rho = isa_atmosphere(altitude)
    run_engine(inlet, compressor, combustor, turbine, nozzle, area, mach, T, P, rho, display=True)


    
elif mode == 2:
    engine_name = str(input("Select Engine(generic, j52, j57, j58, j79, olympus593, orpheus): "))
    
    with open(f"engines/{engine_name}.json") as f:
        engine = json.load(f)
    
    inlet = Inlet(
    engine["inlet_efficiency"])
    
    compressor = Compressor(
    engine["compressor_pr"],
    engine["compressor_efficiency"])
    
    combustor = Combustor(
    engine["combustor_tt4"],
    engine["combustor_efficiency"],
    engine["combustor_pressure_ratio"])
    
    turbine = Turbine(
    engine["turbine_efficiency"])
    
    nozzle = Nozzle(
    engine["nozzle_efficiency"])

    area = engine["inlet_area"]

    print_engine_info(engine)
    altitude = int(input("Enter altitude (m): from 0-11000): "))
    mach = float(input("Enter Mach number: "))  # asummed 0.8 up until now, but will be user input later

    T, P, rho = isa_atmosphere(altitude)
    run_engine(inlet, compressor, combustor, turbine, nozzle, area, mach, T, P, rho, display=True)

elif mode ==3:
    engines_list = ["generic", "j52", "j57", "j58", "j79", "olympus593", "orpheus"]
    altitude = int(input("Enter altitude (m): from 0-11000): "))
    mach = float(input("Enter Mach number: "))  # asummed 0.8 up until now, but will be user input later
    print(f"{'Engine':40}"f"{'Thrust':>10}"f"{'TSFC':>10}"f"{'ηth':>10}"f"{'ηp':>10}"f"{'ηo':>10}")

    T, P, rho = isa_atmosphere(altitude)
    for engine_name in engines_list:
        with open(f"engines/{engine_name}.json") as f:
                engine = json.load(f)

            
        inlet = Inlet(
        engine["inlet_efficiency"])
            
        compressor = Compressor(
        engine["compressor_pr"],
        engine["compressor_efficiency"])
            
        combustor = Combustor(
        engine["combustor_tt4"],
        engine["combustor_efficiency"],
        engine["combustor_pressure_ratio"])
            
        turbine = Turbine(
        engine["turbine_efficiency"])
            
        nozzle = Nozzle(
        engine["nozzle_efficiency"])
        
        area = engine["inlet_area"]
        results = run_engine(inlet, compressor, combustor, turbine, nozzle, area, mach, T, P, rho, display=False)
        print(f"{engine['name']:40}"f"{results['thrust']:10.1f}"f"{results['sfc']:10.4f}"f"{results['nth']*100:10.2f}"f"{results['np']*100:10.2f}"f"{results['overall_efficiency']*100:10.2f}")
