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
    print(f"Turbine Throat Area: {engine['turbine_throat_area']} m^2")
    print(f"Inlet Area: {engine["inlet_area"]}m^2\n")
    print("Reference Values (Sea Level Static):")
    print(f"Published Thrust(Mach 0, Sea Level): {engine['published_thrust_n']} N")
    print(f"Published Airflow: {engine['published_mdot']} kg/s\n")
    print(f"Notes: \n {engine["notes"]} \n")

def run_engine(inlet, compressor, combustor, turbine, nozzle, area, A4, mach, T, P, rho, display):
    station0 = Station(0)
    station0.area = area
    station0.T = T
    station0.P = P
    station0.rho = rho
    station0.M = mach

    speed_of_sound(station0)
    air_v(station0)
    stag_temp_pressure(station0)
    #station0.mdot = round(station0.rho * station0.airvelocity * station0.area, 2)  # is constant throughout engine, so initial mass flow rate is the same as the final mass flow rate, so we can just calculate it here and use it for all stations
    station2 = inlet.calculate(station0)
    station3 = compressor.calculate(station2)
    station4 = combustor.calculate(station3)
    mdot0, mdot4 = calc_airflow_from_turbine_throat(station4, A4)
    station0.mdot = mdot0
    station2.mdot = mdot0
    station3.mdot = mdot0
    station4.mdot = mdot4

    station5 = turbine.calculate(station4, compressor.work)
    compressor_power = station3.mdot * compressor.work
    compressor_power_MW = compressor_power / 1e6
    turbine_work = (station5.cp)*(station4.Tt-station5.Tt)
    turbine_power = (station5.mdot) * (turbine_work)
    turbine_power_MW = turbine_power / 1e6


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
    fuel_flow = station0.mdot * station4.f
    pressure_thrust = (station8.area*(station8.P - station0.P))
    thrust = momentum_thrust + pressure_thrust
    sfc = (((station8.f * station0.mdot)/thrust) * 3600)  # kg/(N.hr)
    #implementing effective jet velocity
    v_eff = station8.airvelocity + (((station8.P - station0.P)*(station8.area))/station8.mdot)

    nth = ((((1+station8.f)*(v_eff**2)) - (station0.airvelocity**2))/2)/(station8.f*combustor.QR) # thermal efficiency
    np = 2*station0.airvelocity/(v_eff + station0.airvelocity) # propulsive efficiency
    overall_efficiency = nth * np

    if display:
        station0.display()
        station2.display()
        station3.display()
        print(f"Compressor Work: {compressor.work}")
        print(f"Compressor Power: {compressor_power/1e6:.3f} MW")
        station4.display()
        station5.display()
        print(f"Turbine Power: {turbine_power/1e6:.3f} MW")
        station8.display()
        print("\nFinal Important Values:")
        print(f"Fuel flow: {fuel_flow:.2f}kg/s")
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
        "pressure_thrust": pressure_thrust,
        "mdot_air": station0.mdot,
        "mdot_exh": station8.mdot,
        "fuel_flow": fuel_flow
    }
        
def speed_of_sound(station0):  #calcs  speed of sound at a temp
    station0.a = round(math.sqrt(station0.gamma * station0.R * station0.T), 2)
def air_v(station0):   #calcs v = Ma
    station0.airvelocity = round(station0.M * station0.a, 2)
def stag_temp_pressure(station0):
    station0.Tt = round(station0.T * (1 + (station0.gamma - 1) / 2 * station0.M**2), 2)
    station0.Pt = round(station0.P * (1 + (station0.gamma - 1) / 2 * station0.M**2)**(station0.gamma / (station0.gamma - 1)), 2)

def calc_airflow_from_turbine_throat(station4, A4):

    mdot4 = (
        (station4.Pt * A4)
        / math.sqrt(station4.Tt)
    ) * math.sqrt(station4.gamma / station4.R) * (
        ((station4.gamma + 1) / 2)
        ** (-(station4.gamma + 1)
            / (2 * (station4.gamma - 1)))
    )

    mdot0 = mdot4 / (1 + station4.f)

    return mdot0, mdot4
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
    A4 = float(input("Enter Turbine Throat Area: "))
    altitude = int(input("Enter altitude (m): from 0-11000): ")) #at some point have this be in the function TODO
    T, P, rho = isa_atmosphere(altitude)
    run_engine(inlet, compressor, combustor, turbine, nozzle, area, A4, mach, T, P, rho, display=True)


    
elif mode == 2:
    engine_name = str(input("Select Engine(generic, j52, j57, j58, j79, olympus593, orpheus, gej47): "))
    
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

    A4 = engine["turbine_throat_area"]

    print_engine_info(engine)
    altitude = int(input("Enter altitude (m): from 0-11000): "))
    mach = float(input("Enter Mach number: "))  # asummed 0.8 up until now, but will be user input later

    T, P, rho = isa_atmosphere(altitude)
    run_engine(inlet, compressor, combustor, turbine, nozzle, area, A4, mach, T, P, rho, display=True)

elif mode ==3:
    engines_list = ["generic", "j52", "j57", "j58", "j79", "olympus593", "orpheus, gej47"]
    altitude = int(input("Enter altitude (m): from 0-11000): "))
    mach = float(input("Enter Mach number: "))  # asummed 0.8 up until now, but will be user input later
    print(f"{'Engine':38}"f"{'Thrust':>10}"f"{'TSFC':>8}"f"{'ηth':>7}"f"{'ηp':>7}"f"{'ηo':>7}"f"{'(ṁ)air':>10}"f"{'(ṁ)exh':>10}"f"{'SLS(ṁ)':>9}"f"{'(ṁ)fuel':>10}")

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
        A4 = engine["turbine_throat_area"]
        results = run_engine(inlet, compressor, combustor, turbine, nozzle, area, A4, mach, T, P, rho, display=False)
        print(f"{engine['name']:38}"f"{results['thrust']:10.1f}"f"{results['sfc']:8.4f}"f"{results['nth']*100:7.2f}"f"{results['np']*100:7.2f}"f"{results['overall_efficiency']*100:7.2f}"f"{results['mdot_air']:10.2f}"f"{results['mdot_exh']:10.2f}"f"{engine['published_mdot']:9.2f}"f"{results['fuel_flow']:10.2f}")
