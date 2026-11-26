# Validation Record

The simulator now combines cycle analysis with fixed-area internal-flowpath analysis. Results below include current local runs of the J47 and J52 presets. Agreement in one metric does not validate all engine performance quantities.

## Internal Area Validation

At sea-level static conditions, preset runs use the configured areas and recover the design Mach targets at Stations 3–5:

| Engine | \(A_3\) (m²) | \(A_{4,\mathrm{station}}\) (m²) | \(A_5\) (m²) | Solved \(M_3/M_4/M_5\) |
|---|---:|---:|---:|---|
| GE J47 GE-25/-27 | 0.11776 | 0.56401 | 0.30589 | 0.249996 / 0.080000 / 0.350002 |
| P&W J52 | 0.06950 | 0.29940 | 0.29320 | 0.250007 / 0.079999 / 0.349993 |

These are the fixed geometry values stored in the preset files; the near-target Mach values reflect bisection and floating-point precision.

## MFP and Continuity Cross-Check

For Stations 3–5 in six J47/J52 runs (the conditions listed in the off-design matrix), the continuity-based `area_from_design_mach()` calculation and MFP-based `area_from_mach()` calculation differed by at most \(1.11\times10^{-16}\ \mathrm{m^2}\). The largest difference is at floating-point roundoff scale.

This confirms algebraic implementation agreement between the two area formulas for the tested inputs. It does not independently establish that the chosen design Mach targets or the ideal-gas assumptions represent measured engine geometry.

## Sea-Level Static Engine Validation

Condition: 0 m altitude, flight Mach 0.

| Engine | Modeled air flow (kg/s) | Reference air flow (kg/s) | Modeled thrust (N) | Reference thrust (N) | Thrust error |
|---|---:|---:|---:|---:|---:|
| GE J47 GE-25/-27 | 46.26756 | 46.27 | 26,252.80 | 26,556 | -1.14% |
| P&W J52 | 64.85551 | 64.86 | 42,325.29 | 49,820 | -15.04% |

\[
\text{thrust error} =
\frac{\text{modeled thrust}-\text{reference thrust}}
{\text{reference thrust}}\times100\%
\]

The J47 result is a close single-point thrust comparison. The J52 result matches reference airflow but underpredicts the preset's reference thrust by about 15.04%; it is not a successful thrust validation. Confirm engine variant, rating, and source conditions before treating either comparison as definitive.

## Off-Design Test Matrix

These were executed as preset runs with stored geometry held fixed. Entries show modeled thrust, air flow, and solved internal Mach numbers \(M_3/M_4/M_5\).

| Engine | Altitude / flight Mach | Thrust (N) | Air flow (kg/s) | \(M_3/M_4/M_5\) |
|---|---|---:|---:|---|
| GE J47 | 0 m / 0.00 | 26,252.80 | 46.26756 | 0.249996 / 0.080000 / 0.350002 |
| GE J47 | 11,000 m / 0.85 | 8,406.21 | 16.53290 | 0.230205 / 0.080000 / 0.303180 |
| GE J47 | 18,000 m / 2.00 | 6,705.53 | 26.89428 | 0.296528 / 0.080000 / 0.548027 |
| P&W J52 | 0 m / 0.00 | 42,325.29 | 64.85551 | 0.250007 / 0.079999 / 0.349993 |
| P&W J52 | 11,000 m / 0.85 | 13,147.86 | 23.16146 | 0.230074 / 0.079999 / 0.267374 |
| P&W J52 | 18,000 m / 2.00 | 6,467.62 | 37.75520 | 0.297035 / 0.079999 / 1.000000* |

The changing internal Mach numbers show that the fixed areas are being used off design. The J52 high-altitude/high-Mach case reaches the solver's Mach-1 clamp at Station 5; it is not evidence that a physically complete sonic or supersonic solution was obtained. These operating points are implementation checks, not comparisons against published off-design engine data.

## Previously Reported Static Airflow Comparisons

Reported at 0 m altitude and flight Mach 0:

| Engine | Model airflow (kg/s) | Published/reference airflow (kg/s) | Difference (kg/s) |
|---|---:|---:|---:|
| Pratt & Whitney J52 | 64.86 | 64.86 | 0.00 |
| Pratt & Whitney J57 | 74.39 | 78.19 | -3.80 |
| Pratt & Whitney J58 | 136.08 | 138.00 | -1.92 |
| General Electric J79 | 77.10 | 77.11 | -0.01 |
| Rolls-Royce/Snecma Olympus 593 | 185.96 | 185.97 | -0.01 |
| Bristol Siddeley Orpheus 803 | 38.10 | 38.10 | 0.00 |

The J57/J58 deviations remain visible. Reference variant and rating conditions need confirmation.

## Compressor/Turbine Power Check

The previously reported J52 compressor and turbine powers are both 25.713 MW. Since turbine exit temperature is calculated from compressor specific work and fuel-added mass, that equality is algebraically imposed by the implementation. It is an internal consistency check, not independent validation of physical shaft power.

## Validation Limits

- Turbine-throat airflow assumes choked ideal-gas flow and does not independently verify choking.
- `turbine_throat_area` meters flow, while `A4_station` solves the combustor-exit station. Their physical definitions and consistency with turbine nozzle-guide-vane geometry should be verified; the throat is not a separate solved station.
- The internal flow solver inverts only the subsonic MFP branch. At or above its limit it sets Mach to 1 without reporting whether the requested mass flow exceeds the fixed-area capacity; no supersonic branch or shock model is implemented.
- Constant \(\gamma\), \(c_p\), and \(R\) are used for air and combustion products.
- The nozzle exit area is recalculated from continuity for each run rather than held as a fixed nozzle geometry.
- At static conditions the current \(\eta_p=2V_a/(V_\mathrm{eff}+V_a)\) expression returns zero because \(V_a=0\); this is a limitation of that efficiency metric at static thrust, not a validation result.
- Pressure thrust is folded into an effective velocity for the thermal and propulsive efficiency formulas. That is a simplified surrogate and should be checked against a consistent energy-flux/efficiency definition.
- In the choked nozzle, nozzle efficiency adjusts exit temperature while exit pressure uses a fixed ideal critical ratio. For \(\eta_n<1\), recovered Station 8 total properties need not match Station 5 total properties.
- Current reports validate only the listed implementation points. Off-design thrust, TSFC, thermal efficiency, propulsive efficiency, and overall efficiency need comparison with matched published data.
- The Generic preset's single-engine information display still requests `published_thrust_n` and `notes`, which are absent from its JSON file. The comparison mode does run all configured presets.

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
