# Turbojet Simulator

A station-based Python model of a turbojet engine cycle. It accepts altitude, flight Mach number, and inlet area, calculates flow through the engine, and reports thrust and cycle performance.

The atmosphere uses a single tropospheric lapse-rate layer intended for 0–11,000 m; it is not a complete multi-layer ISA model.

## Run

From this directory, run:

```powershell
python main.py
```

The project uses only the Python standard library. The program prompts for:

- Altitude (m), intended range 0–11,000 m
- Flight Mach number
- Inlet area (m²)

The compressor pressure ratio is 1.2, combustor exit total temperature is 1400 K, and the current component parameters in `main.py` are:

- Inlet efficiency: 1.0
- Compressor efficiency: 0.7
- Combustor efficiency: 1.0
- Combustor pressure ratio: 1.0
- Turbine efficiency: 1.0
- Nozzle efficiency: 1.0

## Engine flow

```text
Station 0 -> Inlet -> Station 2 -> Compressor -> Station 3
          -> Combustor -> Station 4 -> Turbine -> Station 5
          -> Choked/unchoked Nozzle -> Station 8 -> Engine performance
```

## Implemented Features

### Engine Components

- Single-layer ISA troposphere model (intended range: 0–11 km)
- Inlet pressure recovery using an inlet efficiency factor
- Compressor pressure ratio and isentropic efficiency
- Combustor efficiency and total-pressure ratio
- Fuel-air ratio calculation and fuel-flow addition
- Turbine efficiency and power-balance model with fuel-flow correction
- Nozzle efficiency for choked and unchoked converging-nozzle calculations

### Nozzle Models

- Choked converging nozzle
- Unchoked converging nozzle
- Automatic choking determination using the critical pressure ratio

### Flow Properties

- Mass-flow propagation through the engine
- Nozzle exit density calculation
- Nozzle exit area calculation

### Performance Metrics

- Momentum thrust
- Pressure thrust
- TSFC
- Thermal efficiency
- Propulsive efficiency
- Overall efficiency

## Current Status

The program displays Stations 0, 2, 3, 4, 5, and 8, compressor work, momentum thrust, pressure thrust, total thrust, TSFC, and efficiency results. Outputs depend on the entered altitude, Mach number, inlet area, and configured component parameters.

Important model limitations:

- The atmosphere uses one lapse-rate layer and does not model higher ISA layers
- Inlet efficiency is applied to total pressure only; total temperature is unchanged
- Gas properties are constant
- The unchoked nozzle warns if its calculated exit Mach number is at least 1, but does not automatically switch back to the choked branch
- Current thrust uses momentum and exit-pressure terms; geometry and gas-property idealizations remain

The detailed station-by-station model and recent progress are in [engine_design.md](./engine_design.md). Equations and assumptions are in [equations.md](./equations.md).

## Development Log

### Recent Progress

- Added inlet total-pressure recovery using the inlet efficiency parameter.
- Implemented separate choked and unchoked converging-nozzle paths selected by the critical pressure ratio.
- Added nozzle exit density and area calculations.
- Added pressure thrust to the momentum-thrust calculation.
- Validated representative unchoked cases for zero pressure thrust and the expected thrust reduction with lower inlet recovery.

### Version 1.1 Changes

- Added compressor, combustor, turbine, and nozzle efficiency parameters.
- Added burner pressure-ratio support and fuel-flow propagation.
- Added turbine work correction for fuel-added mass flow.
- Added TSFC, thermal, propulsive, and overall efficiency outputs.
- Added choking logic and converging-nozzle calculations.

## Future Work

### High Priority

- JSON engine configuration files
- Multiple predefined engine presets
- Validation against real turbojet data

### Medium Priority

- Improved nozzle-loss model
- Nozzle pressure-recovery option
- Multi-layer ISA atmosphere

### Long-Term

- Turbofan support
- Afterburner support
- Compressor and turbine maps
- Geometry-based flowpath sizing
- Multi-spool engine architectures
