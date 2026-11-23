# Changelog

Project changes are summarized here by milestone. Validation values are reported project results unless explicitly noted otherwise.

## Current Update

### Added

- ISA isothermal atmosphere layer from 11,000 to 20,000 m.
- Compressor power, turbine power, and fuel-flow calculations in detailed engine output.
- General Electric J47 GE-25/-27 JSON preset with published/reference airflow and static thrust values.
- Validation documentation for sea-level static airflow comparisons and the reported J47 static thrust result.
- Development log and project validation record.

### Changed

- Airflow is calculated from a choked turbine nozzle-guide-vane throat instead of the earlier freestream \(\rho A V\) estimate.
- Turbine throat area is the airflow calibration parameter; inlet area is retained as a geometric reference.
- Choked nozzle exit pressure is set from the fixed critical pressure ratio, \(P_8=P_{t5}/1.893\).
- Effective jet velocity includes the pressure-thrust term in thermal and propulsive efficiency calculations.

### Validation Notes

- Reported static J47 result: 26,253 N versus 26,556 N reference thrust, or -1.14%.
- Reported airflow comparisons are close for most listed engines, with remaining J57 and J58 deviations.
- Reported J52 compressor and turbine powers both equal 25.713 MW, but this follows algebraically from the turbine temperature calculation and is not an independent power-balance validation.
- The J47 comparison-list entry and Generic preset display metadata require integration fixes.

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
