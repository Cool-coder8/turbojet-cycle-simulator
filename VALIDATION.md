# Validation Record

This document records reported comparisons for the turbojet simulator. A close match in one quantity does not validate all model outputs. In particular, airflow agreement alone does not validate thrust, TSFC, or efficiencies.

## Sea-Level Static Airflow

Reported operating point: altitude \(=0\ \text{m}\), Mach \(=0\).

| Engine | Modeled airflow (kg/s) | Published/reference airflow (kg/s) | Difference (kg/s) |
|---|---:|---:|---:|
| Pratt & Whitney J52 | 64.86 | 64.86 | 0.00 |
| Pratt & Whitney J57 | 74.39 | 78.19 | -3.80 |
| Pratt & Whitney J58 | 136.08 | 138.00 | -1.92 |
| General Electric J79 | 77.10 | 77.11 | -0.01 |
| Rolls-Royce/Snecma Olympus 593 | 185.96 | 185.97 | -0.01 |
| Bristol Siddeley Orpheus 803 | 38.10 | 38.10 | 0.00 |

These values are supplied project results. The J57 and J58 retain visible differences, and publication conditions/engine variants should be confirmed before treating these as like-for-like comparisons.

## Independent GE J47 Static Check

Reported engine: General Electric J47 GE-25/-27.

| Quantity | Simulator | Reference | Error |
|---|---:|---:|---:|
| Airflow | 46.27 kg/s | 46.27 kg/s | 0.00% |
| Static thrust | 26,253 N | 26,556 N | -1.14% |

Reported condition: sea-level static (altitude \(=0\ \text{m}\), Mach \(=0\)). The thrust error is calculated relative to the reference thrust:

\[
\text{error} = \frac{\text{simulator}-\text{reference}}{\text{reference}}\times100\%
\]

This result is an encouraging independent single-point comparison, but requires source/variant verification and should not be generalized to other engines or conditions.

## Compressor/Turbine Power Check

Reported J52 values:

| Quantity | Reported value |
|---|---:|
| Compressor power | 25.713 MW |
| Turbine power | 25.713 MW |

The model computes turbine exit temperature from compressor work:

\[
T_{t5}=T_{t4}-\frac{w_c}{c_p(1+f)}
\]

It then computes turbine power from exhaust mass flow times \(c_p(T_{t4}-T_{t5})\). Thus the equality between the reported powers follows algebraically from the implementation (aside from rounding); it is an internal consistency check, not an independent physical validation.

## Model and Validation Limits

- Airflow assumes choked ideal-gas flow at the turbine throat; the code does not independently verify the throat is choked.
- The throat-flow model uses constant \(\gamma\) and \(R\).
- No high-altitude thrust validation results are currently recorded here.
- Thrust, TSFC, thermal efficiency, propulsive efficiency, and overall efficiency need comparisons at matched published conditions.
- The current engine comparison loop contains a malformed `orpheus, gej47` entry and does not complete successfully. The Generic preset's single-engine display also accesses metadata keys not present in its JSON file.
- Current reports have not been independently rerun as part of this documentation update.

## Next Validation Steps

1. Repair and rerun preset selection/comparison for the complete engine database.
2. Verify each reference's exact engine variant, rating, and operating point.
3. Compare predicted static thrust and TSFC for all available engines.
4. Investigate J57, J58, and Orpheus thrust discrepancies.
5. Add altitude thrust validation and report percentage errors.
6. Validate turbine work, nozzle expansion, and station properties independently of the equations that impose their balance.
