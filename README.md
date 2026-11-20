# Turbojet Simulator

A station-based Python model of a turbojet engine cycle. It can run with user-entered engine parameters, a selected JSON engine preset, or compare all available presets. The simulator calculates flow through the engine and reports thrust and cycle performance.

The atmosphere uses a single tropospheric lapse-rate layer intended for 0–11,000 m; it is not a complete multi-layer ISA model.

## Run

From this directory, run:

```powershell
python main.py
```

The project uses only the Python standard library. At startup, choose a run mode:

- **Custom engine values** — enter component efficiencies, pressure ratios, combustor target temperature, inlet area, flight Mach number, and altitude.
- **Select a preset engine** — choose one of the JSON configurations in `engines/`, then enter altitude and flight Mach number. The preset supplies engine parameters and inlet area.
- **Compare all engines** — enter altitude and flight Mach number to run every available preset and compare performance in a table.

The available JSON presets are:

- Generic Turbojet (`generic`)
- Pratt & Whitney J52 (`j52`)
- Pratt & Whitney J57 (`j57`)
- Pratt & Whitney J58 (`j58`)
- General Electric J79 (`j79`)
- Rolls-Royce/Snecma Olympus 593 (`olympus593`)
- Bristol Siddeley Orpheus (`orpheus`)

Altitude is intended to be within 0–11,000 m. In preset and comparison modes, engine pressure ratios, design turbine-inlet temperature, component efficiencies, and inlet area are loaded from each selected JSON file.

## Engine flow

```text
Choose Run Mode -> Custom Values or Load JSON Configuration(s) -> Station 0 -> Inlet -> Station 2
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
- Runtime selection of a single preset without editing `main.py`
- Custom engine-parameter entry at runtime
- Comparison of all seven presets at the same altitude and Mach number
- Presets for Generic Turbojet, J52, J57, J58, J79, Olympus 593, and Orpheus

## Current Status

In custom and single-preset modes, the program displays Stations 0, 2, 3, 4, 5, and 8, compressor work, momentum thrust, pressure thrust, total thrust, TSFC, and efficiency results. Comparison mode runs all seven presets at the same flight conditions and prints thrust, TSFC, thermal efficiency, propulsive efficiency, and overall efficiency for each; it suppresses the station-by-station output.

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
- Added a custom-input mode for engine parameters.
- Added a comparison mode that evaluates all seven presets at shared altitude and Mach inputs and prints a performance table.
- Added inlet total-pressure recovery while conserving total temperature.
- Added nozzle exit density and continuity-based exit area calculations.
- Added momentum and pressure thrust reporting.

#### Validation Completed

- Choked nozzle cases were checked for exit pressure above ambient and positive pressure-thrust contribution.
- Unchoked nozzle cases were checked for exit pressure equal to ambient, zero pressure thrust, and subsonic exit Mach.
- Lower inlet efficiency was checked to reduce Station 2 pressure, turbine-exit pressure, and thrust.

#### Current Simulator Capability

Atmosphere → Freestream → Inlet → Compressor → Combustor → Turbine → Nozzle → Geometry Calculations → Momentum Thrust → Pressure Thrust → TSFC → Thermal Efficiency → Propulsive Efficiency → Overall Efficiency → Preset Comparison

The simulator now supports configurable engine presets and non-ideal component parameter values. It remains a simplified cycle model rather than a validated, geometry-resolved engine performance tool.

## Next Milestone

Improve engine comparison by validating preset data and documenting the basis for each engine configuration.

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
