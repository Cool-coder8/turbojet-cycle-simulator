# Turbojet Simulator

A station-based turbojet simulator combining thermodynamic cycle analysis with internal-flowpath analysis. It supports user-entered engine parameters, JSON engine presets, and preset comparison. Preset runs size fixed internal areas at design Mach numbers and solve the resulting station Mach numbers and static properties at the requested operating point.

The atmosphere uses ISA troposphere and isothermal-layer relations from 0 to 20,000 m. It does not model higher ISA layers.

## Run

From this directory, run:

```powershell
python main.py
```

The project uses only the Python standard library. At startup, choose a run mode:

- **Custom engine values** — enter component efficiencies, pressure ratios, combustor target temperature, inlet area, turbine throat area, flight Mach number, and altitude.
- **Select a preset engine** — choose one of the JSON configurations in `engines/`, then enter altitude and flight Mach number. The preset supplies engine parameters and geometry.
- **Compare engines** — enter altitude and flight Mach number to compare all preset performance at shared conditions.

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
              -> Fixed-area flowpath solve at Stations 2-5
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

### Internal Flowpath

- Design Mach numbers `M3_design`, `M4_design`, and `M5_design` define preset design-point sizing targets
- MFP-based sizing of `A3`, `A4_station`, and `A5`
- Fixed-area station-flow solution for Mach number and static temperature, pressure, density, and velocity at Stations 2-5
- Station 8 total-property recovery from nozzle exit static properties and Mach number
- MFP-area and continuity-area cross-checks agree to floating-point precision in the tested J47 and J52 cases

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
- Preset comparison runs all eight configured engines at a shared flight condition

## Current Status

Preset runs display Stations 0, 2, 3, 4, 5, and 8, including solved internal-flow static properties where configured geometry is supplied. Comparison mode currently completes the eight-engine preset list. At sea-level static conditions, an execution check reproduced 26,252.80 N for J47 and 42,325.29 N for J52; the latter is about 15.04% below the preset's 49,820 N reference thrust. These results are point checks, not broad validation.

Important model limitations and remaining integration issues:

- The atmosphere does not model ISA layers above 20 km
- Engine presets are data configurations; accuracy against published engine performance still needs validation
- The unchoked nozzle warns if its calculated exit Mach number is at least 1, but does not automatically switch back to the choked branch
- The turbine-throat airflow formula assumes choked, ideal-gas flow at Station 4 and does not independently solve compressor/turbine maps
- The station MFP solver only searches the subsonic branch; at or above its choking limit it sets Mach to 1 without reporting that the requested mass flow may not be achievable. Supersonic internal-flow solutions are not implemented.
- Fixed internal areas are applied in preset mode. Custom mode currently calculates design areas after the cycle run rather than using them to solve Stations 2-5.
- The nozzle exit area is recalculated from continuity at each run; fixed-versus-variable nozzle geometry is not implemented.
- The choked nozzle pressure uses a fixed critical ratio of 1.893, corresponding to air with \(\gamma=1.4\)
- Current thrust uses momentum and exit-pressure terms; geometry and gas-property idealizations remain
- The Generic preset lacks `published_thrust_n` and `notes`, fields accessed by the single-preset information display; selecting it in that mode still raises a `KeyError`.

The detailed station-by-station model and recent progress are in [engine_design.md](./engine_design.md). Equations and assumptions are in [equations.md](../physics/equations.md). See the [development log](./DEVELOPMENT_LOG.md), [validation record](./VALIDATION.md), and [changelog](./CHANGELOG.md) for milestones and comparison details.

## Development Log

The current milestone is the move from cycle analysis alone to cycle analysis plus internal-flowpath analysis. Fixed areas are sized from design Mach targets, then the MFP solver recovers operating-point station states. Validation is now focused on checking both area formulations, documenting where the flow solver reaches its choking limit, and comparing outputs with published engine data.

See [DEVELOPMENT_LOG.md](./DEVELOPMENT_LOG.md) for the implementation decisions and lessons learned, and [VALIDATION.md](./VALIDATION.md) for executed station-flow checks.

## Next Development Priorities

1. Complete validation of all preset engines.
2. Build an off-design test matrix:
   - Sea Level Static
   - 11,000 m, Mach 0.85
   - 18,000 m, Mach 2.0
3. Investigate corrected airflow methods.
4. Investigate simplified compressor-map modelling.
5. Implement fixed-vs-variable nozzle support.
6. Improve off-design component realism.
7. Continue verification against published engine data.
