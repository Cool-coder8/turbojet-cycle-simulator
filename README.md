# Turbojet Simulator

A station-based Python model of a turbojet engine cycle. The simulator accepts altitude, flight Mach number, and inlet area, then calculates atmospheric and freestream properties, processes the flow through the engine components, and estimates thrust.

The atmosphere uses a continuous lapse-rate model for the troposphere from 0 m to 11,000 m. The nozzle uses choked converging-nozzle relations; automatic choking detection is currently limited to a pressure-ratio check and does not calculate an unchoked exit state.

## Run

From this directory, run:

```powershell
python main.py
```

The project uses only the Python standard library. The program prompts for:

- Altitude (m), intended range 0–11,000 m
- Flight Mach number
- Inlet area (m²)

The compressor pressure ratio is 10, and the combustor exit total temperature and efficiency are 1400 K and 1.0, respectively, in `main.py`.

## Engine flow

```text
Station 0 -> Inlet -> Station 2 -> Compressor -> Station 3
          -> Combustor -> Station 4 -> Turbine -> Station 5
          -> Nozzle -> Station 8 -> Thrust
```

## Current model

Implemented:

- Continuous tropospheric atmosphere properties: temperature, pressure, and density
- Freestream speed of sound, velocity, mass flow rate, and stagnation temperature/pressure
- Ideal inlet transfer of total temperature and pressure
- Compressor pressure and temperature rise, and specific work
- Combustor exit total temperature, pressure, and fuel-air ratio
- Turbine temperature and pressure drop, balanced to compressor work
- Choked converging-nozzle exit temperature, pressure, and velocity
- Engine thrust estimate

Current assumptions and limitations:

- The atmosphere calculation uses a single lapse-rate layer and is intended for 0–11,000 m
- Ideal inlet and combustor; no inlet or combustor pressure loss
- Constant gas properties, ideal compressor and turbine
- Choked nozzle relations; no unchoked exit-state solution or complete choking control
- Thrust model does not include pressure thrust
- TSFC and component efficiencies are not calculated

The detailed station-by-station design and limitations are in [engine_design.md](./engine_design.md). Equations and assumptions are in [equations.md](./equations.md).

## Current Status

Completed:

- ✅ Continuous ISA troposphere model (0–11,000 m)
- ✅ Freestream state and mass flow rate
- ✅ Ideal inlet
- ✅ Compressor
- ✅ Combustor
- ✅ Turbine
- ✅ Choked converging nozzle exit properties
- ✅ Thrust estimate

The program displays Stations 0, 2, 3, 4, 5, and 8, along with compressor work and calculated thrust. Numerical outputs depend on the entered altitude, Mach number, and inlet area.

## Development Log

- Implemented the continuous tropospheric temperature, pressure, and density calculation.
- Added user inputs for altitude, flight Mach number, and inlet area.
- Added freestream mass-flow-rate calculation.
- Completed the compressor, combustor, and turbine cycle calculations.
- Added choked converging-nozzle exit properties and a basic choking pressure-ratio check.
- Added the engine thrust estimate.

## Next Milestone

Improve engine performance and operating-condition modeling by implementing:

- TSFC
- Component efficiencies
- Component pressure losses
- Extended ISA atmosphere layers
- Automated choking logic with both choked and unchoked nozzle solutions
