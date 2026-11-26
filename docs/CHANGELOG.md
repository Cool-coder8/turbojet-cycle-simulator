# Changelog

Project changes are summarized here by milestone. Validation values are reported project results unless explicitly noted otherwise.

## Current Update

### Added

- Design Mach configuration through `M3_design`, `M4_design`, and `M5_design`.
- Preset fixed internal flow areas: compressor exit `A3`, combustor exit `A4_station`, and turbine exit `A5`.
- MFP-based `area_from_mach()` sizing from mass flow, total pressure, total temperature, Mach, and gas properties.
- `solve_station_flow()` to invert MFP for a specified mass flow, stagnation state, and fixed area.
- Static temperature, pressure, density, velocity, Mach number, and area population at internal Stations 2–5 for preset runs.
- Station 8 total-temperature and total-pressure recovery from nozzle exit static properties and Mach.
- Area and MFP-versus-continuity verification results for J47/J52 and an off-design test matrix.
- Detailed development notes and validation records for the new internal-flowpath capability.

### Changed

- Preset runs now apply fixed internal areas designed at configured Mach targets; off-design runs solve for station Mach instead of recomputing those areas.
- The simulator's scope has expanded from cycle analysis alone to cycle analysis plus internal-flowpath analysis.
- Package imports inside `components` now use relative imports to load `components.station.Station` correctly. Unused import statements were removed.

### Verification Notes

- MFP-based and continuity-based area calculations differed by no more than \(1.11\times10^{-16}\ \mathrm{m^2}\) in the tested J47/J52 cases.
- Current local sea-level-static J47 result: 26,252.80 N versus 26,556 N reference (-1.14%).
- Current local sea-level-static J52 result: 42,325.29 N versus 49,820 N preset reference (-15.04%); airflow matches, thrust does not.
- The off-design matrix shows internal Mach changes with fixed geometry, and J52 Station 5 reaches the MFP solver's Mach-1 clamp at 18,000 m/Mach 2.0.
- A local smoke run completes preset comparison for all eight configured engines. The Generic single-preset display still accesses missing `published_thrust_n` and `notes` keys.
- No thermodynamic calculation or performance equation was changed in this update.

## Previous Milestones

### Version 1.3

- Replaced the freestream mass-flow estimate with turbine-throat airflow metering.
- Added turbine throat area and published airflow references to engine presets.
- Updated choked nozzle exit pressure to the critical-pressure-ratio relation.
- Added effective jet velocity to performance efficiency calculations.

### Version 1.2

- Added JSON engine configuration and runtime preset selection.
- Added engine comparison mode.
- Added inlet pressure recovery, nozzle exit density/area, and pressure thrust.
- Added initial non-ideal component efficiencies and performance metrics.
