# Turbojet Simulator

A station-based Python model of a turbojet engine cycle. It can run with user-entered engine parameters, a selected JSON engine preset, or compare engine presets. Airflow is calculated from a choked turbine-throat model rather than freestream velocity, allowing the model to represent static operation.

The atmosphere uses ISA troposphere and isothermal-layer relations from 0 to 20,000 m. It does not model higher ISA layers.

## Run

From this directory, run:

```powershell
python main.py
```

The project uses only the Python standard library. At startup, choose a run mode:

- **Custom engine values** — enter component efficiencies, pressure ratios, combustor target temperature, inlet area, turbine throat area, flight Mach number, and altitude.
- **Select a preset engine** — choose one of the JSON configurations in `engines/`, then enter altitude and flight Mach number. The preset supplies engine parameters and geometry.
- **Compare engines** — enter altitude and flight Mach number to compare preset performance. See the known limitations below; the current comparison list has an integration issue.

The available JSON presets are:

- Generic Turbojet (`generic`)
- Pratt & Whitney J52 (`j52`)
- Pratt & Whitney J57 (`j57`)
- Pratt & Whitney J58 (`j58`)
- General Electric J79 (`j79`)
- Rolls-Royce/Snecma Olympus 593 (`olympus593`)
- Bristol Siddeley Orpheus (`orpheus`)
- General Electric J47 GE-25/-27 (`gej47`)

The atmosphere model supports 0–20,000 m. In preset and comparison modes, engine pressure ratios, design turbine-inlet temperature, component efficiencies, inlet and turbine throat areas, and reference data are loaded from each JSON file. Inlet area is retained as a geometric reference; turbine throat area determines modeled mass flow. The current CLI altitude prompts still state an upper limit of 11,000 m.

## Engine flow

```text
Choose Run Mode -> Custom Values or Load JSON Configuration(s) -> Station 0 -> Inlet -> Station 2
              -> Compressor -> Station 3 -> Combustor -> Station 4
              -> Choked turbine-throat airflow -> Turbine -> Station 5
              -> Choked/unchoked Nozzle -> Station 8 -> Engine performance
```

## Implemented Features

### Engine Components

- ISA troposphere and isothermal layer model (0–20 km)
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
- Airflow metering from turbine throat area and Station 4 total conditions
- Compressor and turbine power estimates
- Fuel-flow calculation
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
- Presets for Generic Turbojet, J52, J57, J58, J79, Olympus 593, Orpheus, and GE J47
- Preset comparison output is implemented, but the current engine list contains a malformed entry and does not complete successfully

## Current Status

In working custom and single-preset runs, the program displays Stations 0, 2, 3, 4, 5, and 8, compressor work and power, turbine power, fuel flow, momentum thrust, pressure thrust, total thrust, TSFC, and efficiency results. Comparison mode is intended to report performance, modeled air/exhaust mass flow, published airflow, and fuel flow at shared flight conditions; it currently fails before completing the preset list.

Important model limitations and integration issues:

- The atmosphere does not model ISA layers above 20 km
- Engine presets are data configurations; accuracy against published engine performance still needs validation
- The unchoked nozzle warns if its calculated exit Mach number is at least 1, but does not automatically switch back to the choked branch
- The turbine-throat airflow formula assumes choked, ideal-gas flow at Station 4 and does not independently solve compressor/turbine maps
- The choked nozzle pressure uses a fixed critical ratio of 1.893, corresponding to air with \(\gamma=1.4\)
- Current thrust uses momentum and exit-pressure terms; geometry and gas-property idealizations remain
- The comparison-mode list currently combines `orpheus` and `gej47` into one invalid filename, so the loop eventually attempts to open a nonexistent combined JSON filename. The Generic preset also lacks `published_thrust_n` and `notes`, fields accessed by the single-preset display. These need to be reconciled.

The detailed station-by-station model and recent progress are in [engine_design.md](./engine_design.md). Equations and assumptions are in [equations.md](./equations.md). See the [development log](./DEVELOPMENT_LOG.md), [validation record](./VALIDATION.md), and [changelog](./CHANGELOG.md) for milestones and comparison details.

## Development Log

### Current Progress Update

#### Major Features Added

- Added JSON engine configurations and runtime engine selection.
- Added presets for the Generic Turbojet, J52, J57, J58, J79, Olympus 593, Orpheus, and GE J47.
- Added a custom-input mode for engine parameters.
- Added preset-comparison output for shared altitude and Mach inputs; current preset-list integration still needs correction.
- Added inlet total-pressure recovery while conserving total temperature.
- Added nozzle exit density and continuity-based exit area calculations.
- Added momentum and pressure thrust reporting.
- Replaced the freestream \(\rho A V\) mass-flow estimate with choked turbine-throat metering.
- Added turbine throat area and published airflow reference values to the engine configurations.
- Corrected choked nozzle exit pressure to use the critical pressure ratio.
- Added effective jet velocity to the thermal and propulsive efficiency calculations.
- Added the ISA isothermal layer from 11,000 to 20,000 m.
- Added compressor power, turbine power, and fuel-flow calculations to detailed engine output.
- Added a General Electric J47 GE-25/-27 preset and a reported independent static thrust comparison.

#### Sea-Level Static Airflow Checks

At 0 m altitude and Mach 0, the supplied results compare turbine-throat-modeled airflow with published reference values:

| Engine | Model airflow (kg/s) | Published airflow (kg/s) |
|---|---:|---:|
| J52 | 64.86 | 64.86 |
| J57 | 74.39 | 78.19 |
| J58 | 136.08 | 138.00 |
| J79 | 77.10 | 77.11 |
| Olympus 593 | 185.96 | 185.97 |
| Orpheus 803 | 38.10 | 38.10 |

These airflow comparisons are close for most entries, with differences for J57 and J58. They are airflow checks, not validation of thrust, TSFC, or efficiencies.

#### Independent J47 Static Check

The supplied validation result for the General Electric J47 GE-25/-27 at sea-level static conditions is 46.27 kg/s airflow and 26,253 N thrust, compared with references of 46.27 kg/s and 26,556 N. The reported thrust difference is -1.14%. This is a promising single-point check, not broad validation across engines or operating conditions. The current compare-mode list still needs correction before J47 can be run through that mode.

#### Power and Fuel-Flow Reporting

Detailed runs now report compressor power, turbine power, and fuel flow. The supplied J52 example reports compressor and turbine power of 25.713 MW each. Because the turbine temperature drop is calculated from compressor specific work, this matching result is an implementation consistency check, not an independent validation of real-engine power balance.

#### Current Simulator Capability

Atmosphere → Freestream → Inlet → Compressor → Combustor → Turbine-Throat Airflow → Turbine → Nozzle → Geometry Calculations → Momentum Thrust → Pressure Thrust → TSFC → Efficiencies → Power/Fuel-Flow Reporting → Preset Comparison

The simulator now supports configurable engine presets and non-ideal component parameter values. It remains a simplified cycle model rather than a validated, geometry-resolved engine performance tool.

## Next Milestone

Continue validation and calibration against published engine data: fix comparison-mode preset integration, validate thrust at matched conditions, investigate Orpheus 803 and J58 discrepancies, and review turbine work and nozzle-expansion assumptions.

## Future Work

### High Priority

- Fix comparison-mode handling of the Generic and J47 presets
- Validate thrust against published values for all engines
- Investigate remaining Orpheus 803 and J58 thrust discrepancies
- Verify turbine work and nozzle expansion assumptions

### Medium Priority

- Expand station-property and station-area reporting
- Add flowpath analysis mode
- Add thrust error reporting
- Validate thrust predictions at altitude

### Long-Term

- Compressor and turbine maps
- Corrected mass flow and variable geometry effects
- Off-design performance analysis
- Turbofan architecture and afterburner support
