# Turbojet Simulator

A station-based Python model of a turbojet engine cycle. It loads engine parameters from a JSON file, accepts altitude, flight Mach number, and inlet area, calculates flow through the engine, and reports thrust and cycle performance.

The atmosphere uses a single tropospheric lapse-rate layer intended for 0–11,000 m; it is not a complete multi-layer ISA model.

## Run

From this directory, run:

```powershell
python main.py
```

The project uses only the Python standard library. At startup, select an engine whose JSON configuration exists in the `engines/` directory:

- Generic Turbojet (`generic`)
- Pratt & Whitney J52 (`j52`)
- Pratt & Whitney J57 (`j57`)
- Pratt & Whitney J58 (`j58`)
- General Electric J79 (`j79`)
- Rolls-Royce/Snecma Olympus 593 (`olympus593`)
- Bristol Siddeley Orpheus (`orpheus`)

The program then prompts for:

- Altitude (m), intended range 0–11,000 m
- Flight Mach number
- Inlet area (m²)

Engine pressure ratios, design turbine-inlet temperature, and component efficiencies are loaded from the selected JSON file.

## Engine flow

```text
Select Engine -> Load JSON configuration -> Station 0 -> Inlet -> Station 2
              -> Compressor -> Station 3 -> Combustor -> Station 4
              -> Turbine -> Station 5 -> Choked/unchoked Nozzle -> Station 8
              -> Geometry calculations -> Engine performance
```

## Implemented Features

### Engine Components

- Single-layer ISA troposphere model (intended range: 0–11 km)
- Inlet pressure recovery using an inlet efficiency factor
- Compressor pressure ratio and isentropic efficiency
- Combustor efficiency and total-pressure loss
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

### Engine Configuration

- JSON-driven engine parameter loading from `engines/`
- Runtime engine selection without editing `main.py`
- Presets for Generic Turbojet, J52, J57, J58, J79, Olympus 593, and Orpheus

## Current Status

The program displays Stations 0, 2, 3, 4, 5, and 8, compressor work, momentum thrust, pressure thrust, total thrust, TSFC, and efficiency results. Outputs depend on the selected engine configuration and entered flight conditions.

Important model limitations:

- The atmosphere uses one lapse-rate layer and does not model higher ISA layers
- Engine presets are data configurations; accuracy against published engine performance still needs validation
- The unchoked nozzle warns if its calculated exit Mach number is at least 1, but does not automatically switch back to the choked branch
- Current thrust uses momentum and exit-pressure terms; geometry and gas-property idealizations remain

The detailed station-by-station model and recent progress are in [engine_design.md](./engine_design.md). Equations and assumptions are in [equations.md](./equations.md).

## Development Log

### Version 1.2 Progress Update

#### Major Features Added

- Added JSON engine configurations and runtime engine selection.
- Added presets for the Generic Turbojet, J52, J57, J58, J79, Olympus 593, and Orpheus.
- Added inlet total-pressure recovery while conserving total temperature.
- Added nozzle exit density and continuity-based exit area calculations.
- Added momentum and pressure thrust reporting.

#### Validation Completed

- Choked nozzle cases were checked for exit pressure above ambient and positive pressure-thrust contribution.
- Unchoked nozzle cases were checked for exit pressure equal to ambient, zero pressure thrust, and subsonic exit Mach.
- Lower inlet efficiency was checked to reduce Station 2 pressure, turbine-exit pressure, and thrust.

#### Current Simulator Capability

Atmosphere → Freestream → Inlet → Compressor → Combustor → Turbine → Nozzle → Geometry Calculations → Momentum Thrust → Pressure Thrust → TSFC → Thermal Efficiency → Propulsive Efficiency → Overall Efficiency

The simulator now supports configurable engine presets and non-ideal component parameter values. It remains a simplified cycle model rather than a validated, geometry-resolved engine performance tool.

## Future Work

### High Priority

- Populate the engine database with validated engine data
- Add default inlet areas to engine JSON files
- Improve engine comparison functionality

### Medium Priority

- Improved nozzle-loss model
- Multi-layer ISA atmosphere
- Better handling of edge-case nozzle expansions

### Long-Term

- Turbofan architecture
- Afterburner support
- Compressor and turbine maps
- Geometry-based flowpath sizing
- Off-design performance analysis
