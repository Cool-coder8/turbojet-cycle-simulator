# Development Log

## Current Project Phase: Validation and Analysis

The simulator has moved from adding core thermodynamic components toward validating its airflow and performance predictions. Current development priorities are matching published engine conditions, investigating thrust discrepancies, and refining the model rather than adding new cycle components.

## Current Architecture

- Engine configurations are selected from JSON presets or supplied interactively.
- The atmosphere model supports the ISA troposphere (0–11,000 m) and the isothermal layer (11,000–20,000 m).
- Engine air mass flow is inferred from an assumed choked turbine nozzle-guide-vane throat, not freestream \(\rho A V\).
- Turbine throat area is the mass-flow calibration parameter; inlet area is retained for reference.
- Choked nozzle exit pressure uses the fixed critical ratio \(P_8=P_{t5}/1.893\).
- Effective jet velocity includes the pressure-thrust term in thermal and propulsive efficiency calculations.
- Detailed runs report compressor power, turbine power, and fuel flow.
- Engine presets include the Generic Turbojet, J52, J57, J58, J79, Olympus 593, Orpheus 803, and GE J47 GE-25/-27.

## Recent Validation Results

### Sea-Level Static Airflow Comparisons

Reported at 0 m altitude and Mach 0:

| Engine | Model airflow (kg/s) | Reference airflow (kg/s) |
|---|---:|---:|
| J52 | 64.86 | 64.86 |
| J57 | 74.39 | 78.19 |
| J58 | 136.08 | 138.00 |
| J79 | 77.10 | 77.11 |
| Olympus 593 | 185.96 | 185.97 |
| Orpheus 803 | 38.10 | 38.10 |

These are airflow comparisons. They do not establish thrust, TSFC, or efficiency accuracy.

### GE J47 Static Comparison

Reported GE J47 GE-25/-27 results at sea-level static conditions:

- Airflow: 46.27 kg/s model versus 46.27 kg/s reference
- Thrust: 26,253 N model versus 26,556 N reference
- Reported thrust error: -1.14%

This is one reported independent validation point, not validation across the full engine database or operating envelope.

### Power Calculation Check

The reported J52 compressor and turbine powers are both 25.713 MW. Turbine exit temperature is calculated from compressor specific work and fuel-added mass, so the resulting power equality is algebraically imposed by the model. Treat it as an internal consistency check rather than an independent energy-balance validation.

## Known Documentation and Integration Caveats

- The GE J47 is available as `gej47` in preset selection, but the compare-mode list contains `"orpheus, gej47"` as one item. The comparison loop therefore attempts to open a nonexistent combined filename and does not complete.
- The Generic preset does not define `published_thrust_n` or `notes`, but the single-preset information display accesses those keys.
- The atmosphere implementation has no explicit handling for altitude outside 0–20,000 m. The prompts in `main.py` also still describe an altitude range ending at 11,000 m.
- The static J47 result and airflow comparison values are recorded as supplied results; this document does not claim to have rerun those validations.

## Next Work

### Short Term

- Fix preset integration and compare-mode handling.
- Validate thrust against published values for every engine at matched conditions.
- Investigate Orpheus 803 and J58 thrust discrepancies.
- Verify turbine-work and nozzle-expansion assumptions.
- Add thrust-error reporting and check performance at altitude.

### Medium Term

- Calculate additional station properties and areas.
- Add flowpath analysis.
- Add corrected mass-flow calculations.

### Long Term

- Compressor and turbine maps
- Multi-spool engines
- Afterburners
- Variable-geometry systems
- Off-design performance analysis
