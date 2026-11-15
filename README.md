# Turbojet Simulator

A station-based Python model of a turbojet engine cycle. It accepts altitude, flight Mach number, and inlet area, calculates the flow through the engine, and reports thrust and cycle performance.

The atmosphere uses a single tropospheric lapse-rate layer intended for 0–11,000 m; it is not a complete multi-layer ISA model. The nozzle has a choked converging-nozzle calculation and a choking check, but the unchoked calculation is not implemented yet.

## Run

From this directory, run:

```powershell
python main.py
```

The project uses only the Python standard library. The program prompts for:

- Altitude (m), intended range 0–11,000 m
- Flight Mach number
- Inlet area (m²)

The compressor pressure ratio is 10, combustor exit total temperature is 1400 K, and the current component settings in `main.py` are:

- Compressor efficiency: 1.0
- Combustor efficiency: 1.0
- Combustor pressure ratio: 1.0 (no pressure loss)
- Turbine efficiency: 1.0
- Nozzle efficiency: 1.0

The efficiency and burner pressure-ratio models accept non-ideal values, but these current settings represent ideal components.

## Engine flow

```text
Station 0 -> Inlet -> Station 2 -> Compressor -> Station 3
          -> Combustor -> Station 4 -> Turbine -> Station 5
          -> Nozzle -> Station 8 -> Engine performance
```

## Current model

Implemented:

- Single-layer tropospheric atmosphere properties: temperature, pressure, and density
- Freestream speed of sound, velocity, mass flow rate, and stagnation temperature/pressure
- Ideal inlet transfer of total temperature, total pressure, and mass flow
- Compressor pressure rise, isentropic-efficiency temperature correction, and specific work
- Combustor efficiency, burner pressure ratio, fuel-air ratio, and fuel mass addition
- Turbine work balance with fuel-flow correction and turbine isentropic-efficiency pressure calculation
- Choked converging-nozzle exit calculation with a nozzle-efficiency correction
- Thrust, TSFC, thermal efficiency, propulsive efficiency, and overall efficiency calculations

Current assumptions and limitations:

- The atmosphere uses one lapse-rate layer and is intended for 0–11,000 m; altitude input is not range-validated
- Inlet efficiency is currently unused; inlet pressure recovery/loss is not modeled
- Gas properties are constant
- The current run sets component efficiencies to 1.0 and burner pressure ratio to 1.0, so it does not demonstrate non-ideal component settings
- Unchoked nozzle flow is not implemented; selecting an unchoked condition currently reaches a placeholder
- The thrust estimate omits pressure thrust

The detailed station-by-station model and limitations are in [engine_design.md](./engine_design.md). Equations and assumptions are in [equations.md](./equations.md).

## Current Status

Implemented model capabilities:

- ✅ Tropospheric atmosphere model
- ✅ Freestream state and mass-flow calculation
- ✅ Ideal inlet flow propagation
- ✅ Compressor isentropic-efficiency model
- ✅ Combustor efficiency and burner pressure-ratio models
- ✅ Fuel-air ratio and fuel addition
- ✅ Turbine efficiency and fuel-flow correction
- ✅ Choked nozzle efficiency calculation and choking check
- ✅ TSFC, thermal efficiency, propulsive efficiency, and overall efficiency

The program displays Stations 0, 2, 3, 4, 5, and 8, compressor work, thrust, TSFC, and efficiency results. The default component parameters are ideal values, and results depend on the entered flight condition and inlet area.

## Development Log

### Version 1.1 Changes

- Added non-ideal compressor, combustor, turbine, and choked-nozzle calculation models.
- Added burner pressure-ratio support and fuel-flow propagation through the engine.
- Added turbine work correction for the fuel-added mass flow.
- Added TSFC, thermal efficiency, propulsive efficiency, and overall efficiency outputs.
- Added a choked-flow pressure-ratio check and a choked converging-nozzle calculation.

## Next Milestone

Improve model completeness and fidelity by implementing:

- A working unchoked nozzle model and complete automatic choking behavior
- Inlet pressure recovery/loss
- A multi-layer ISA atmosphere
- Pressure thrust in the engine thrust calculation
- Engine configuration files for selecting operating parameters
