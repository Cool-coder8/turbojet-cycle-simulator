# Development Log

## Current Project Phase: Cycle and Internal-Flowpath Analysis

The simulator has evolved from a thermodynamic cycle-analysis tool into a cycle-analysis plus internal-flowpath-analysis tool. The current milestone adds fixed-geometry station-state solving on top of the existing component cycle model. The project is now focused on verifying the flow solution and improving off-design realism, rather than adding another idealized cycle component.

## Implementation Process and Engineering Decisions

1. **Keep the cycle model as the state producer.** Inlet, compressor, combustor, and turbine calculations continue to determine total pressure and total temperature. Mass flow continues to be estimated from the assumed choked turbine throat.
2. **Choose design Mach targets before generating passage areas.** Presets specify `M3_design`, `M4_design`, and `M5_design`. These are low-subsonic station targets, not engine flight Mach numbers.
3. **Size fixed areas from each design station's mass flow and total state.** The solver converts each target Mach into static properties and area using continuity; the equivalent MFP relation provides an independent algebraic formulation.
4. **Freeze the resulting geometry for preset runs.** Presets store `A3`, `A4_station`, and `A5`. At another altitude or flight Mach, those areas stay fixed while station Mach and static properties are recalculated.
5. **Use MFP inversion for off-design station states.** `solve_station_flow()` searches the subsonic MFP branch by bisection and reconstructs static temperature, pressure, density, velocity, and Mach from fixed area and total state.
6. **Recover Station 8 total properties from nozzle exit static state.** The current nozzle model retains its choked/unchoked branches; it does not yet solve a fixed nozzle geometry across operating points.

## Lessons Learned

- Continuity sizing and MFP sizing are equivalent when they use the same total conditions and Mach number. Comparing both is a useful independent implementation check, although it does not independently validate the physical model.
- Design Mach is a geometry-sizing assumption. It should be supported by passage data or documented engineering estimates; it is not fitted from operating-point performance by the solver.
- Fixed internal areas naturally change station Mach as flight conditions change. That is a more useful off-design response than recalculating all areas at every condition.
- An MFP inverse has a finite maximum at Mach 1. A solution that reaches the maximum must be reported as choked or infeasible for the requested flow, not treated as an ordinary bisection result.
- Matching airflow or internal consistency does not establish accurate thrust, TSFC, or efficiency. The current J52 static comparison demonstrates this distinction.

## Current Architecture

- Eight JSON presets provide component parameters, design Mach targets, and fixed areas.
- Airflow is inferred from an assumed choked turbine throat rather than freestream \(\rho A V\).
- Preset runs solve stations 2–5 using fixed areas. Custom-input mode currently calculates design areas after its cycle run but does not pass them back into the station solver.
- Station 8 stagnation properties are recovered from its exit static properties and Mach.
- The station solver currently covers the subsonic branch and clamps to Mach 1 at the choking limit; it does not solve a supersonic branch or issue a capacity error.
- The nozzle exit area is recalculated from continuity at each operating point; fixed-versus-variable nozzle geometry is not yet modeled.
- Import paths now use package-relative imports for `Station` inside `components`; a smoke import of all component and physics modules succeeded.

## Validation Results

### Area and MFP Cross-Check

The J47 and J52 sea-level-static runs produced the stored station areas:

| Engine | \(A_3\) (m²) | \(A_{4,\mathrm{station}}\) (m²) | \(A_5\) (m²) |
|---|---:|---:|---:|
| GE J47 | 0.11776 | 0.56401 | 0.30589 |
| P&W J52 | 0.06950 | 0.29940 | 0.29320 |

Across stations 3–5 in the six J47/J52 operating-point runs, the continuity and MFP area functions differed by at most \(1.11\times10^{-16}\ \mathrm{m^2}\), consistent with floating-point roundoff.

### Static Engine Checks

At sea-level static:

- GE J47: 46.26756 kg/s modeled air flow and 26,252.80 N thrust; reference thrust is 26,556 N (about -1.14%).
- P&W J52: 64.85551 kg/s modeled air flow and 42,325.29 N thrust; preset reference thrust is 49,820 N (about -15.04%).

The J52 result means its airflow calibration must not be presented as validation of its thrust prediction.

### Off-Design Matrix

The current implementation was run for J47 and J52 at sea-level static, 11,000 m/Mach 0.85, and 18,000 m/Mach 2.0. Station Mach changed with the operating point while the preset areas remained fixed. At 18,000 m/Mach 2.0, J52 Station 5 reached Mach 1, which exercises the solver's choking clamp rather than a supersonic solution. Exact outputs and interpretation are recorded in [VALIDATION.md](./VALIDATION.md).

## Existing Validation Context

Previously reported static airflow comparisons (kg/s) are J52 64.86/64.86, J57 74.39/78.19, J58 136.08/138.00, J79 77.10/77.11, Olympus 593 185.96/185.97, and Orpheus 803 38.10/38.10 (model/reference). The J57 and J58 differences remain visible.

The reported J52 compressor and turbine powers both equal 25.713 MW. Since turbine exit temperature is derived from compressor work and fuel-added mass, this is an algebraically imposed consistency check, not an independent power-balance validation.

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
