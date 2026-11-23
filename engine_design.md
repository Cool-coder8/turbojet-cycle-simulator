# Turbojet Simulator Design

This document describes the current component flow and calculations. See [equations.md](./equations.md) for the corresponding relations and assumptions.

## Engine flow

```text
Station 0
    ↓
Inlet
    ↓
Station 2
    ↓
Compressor
    ↓
Station 3
    ↓
Combustor
    ↓
Station 4
    ↓
Turbine-throat airflow calculation
    ↓
Turbine
    ↓
Station 5
    ↓
Nozzle
    ↓
Station 8
    ↓
Engine performance
```

At startup, `main.py` offers three run modes:

1. **Custom values:** prompts for inlet, compressor, combustor, turbine, and nozzle parameters, as well as inlet area, turbine throat area, Mach number, and altitude.
2. **Single preset:** loads one JSON configuration from `engines/`, then prompts for altitude and Mach number. The preset supplies inlet and turbine throat areas and component parameters.
3. **Compare presets:** intended to load each engine JSON file in turn, run the same altitude and Mach inputs, and print a table of performance results. The current list has a malformed combined `orpheus, gej47` entry, so the loop does not complete and omits the J47. Separately, the Generic preset lacks `published_thrust_n` and `notes`, fields required by the single-preset information display.

For preset runs, compressor ratio, design \(T_{t4}\), component efficiencies, combustor pressure ratio, inlet area, turbine throat area, and published airflow reference come from the JSON configuration. Turbine throat area sets modeled airflow; inlet area is retained as a geometric reference.

## Engine Configuration

The current engine database contains:

| Selection | Engine |
|---|---|
| `generic` | Generic Turbojet |
| `j52` | Pratt & Whitney J52 |
| `j57` | Pratt & Whitney J57 |
| `j58` | Pratt & Whitney J58 |
| `j79` | General Electric J79 |
| `olympus593` | Rolls-Royce/Snecma Olympus 593 |
| `orpheus` | Bristol Siddeley Orpheus |
| `gej47` | General Electric J47 GE-25/-27 |

Each JSON file supplies the engine name, compressor pressure ratio and efficiency, combustor exit total temperature, combustor efficiency and pressure ratio, turbine efficiency, nozzle efficiency, inlet efficiency, inlet area, turbine throat area, published mass-flow reference, and (where supplied) published thrust and notes. Airflow is compared with published references; thrust and other performance metrics still require validation at matched operating points.

## Stations and components

### Station 0 — freestream

Inputs:

- Altitude
- Mach number
- Inlet area

Known properties:

- Static temperature \(T\)
- Static pressure \(P\)
- Density \(\rho\)
- Speed of sound \(a\)
- Air velocity \(V_a\)
- Air mass flow rate \(\dot{m}_a\), assigned from the turbine-throat calculation
- Total temperature \(T_{t0}\)
- Total pressure \(P_{t0}\)

The atmosphere uses ISA tropospheric relations from 0 to 11,000 m and an isothermal layer from 11,000 to 20,000 m. Freestream speed of sound, velocity, and total properties use ideal-gas relations. Inlet area remains an input/reference parameter, but the original \(\rho A V\) estimate no longer determines airflow. The model instead sets airflow from the turbine throat after calculating Station 4:

\[
\dot{m}_4 =
\frac{P_{t4}A_4}{\sqrt{T_{t4}}}
\times\sqrt{\frac{\gamma}{R}}
\times\left(\frac{\gamma+1}{2}\right)^{-\frac{\gamma+1}{2(\gamma-1)}}
\]

\[
\dot{m}_a = \frac{\dot{m}_4}{1+f}
\]

This assumes ideal-gas choked flow at a turbine nozzle-guide-vane throat. The code does not test the choking condition separately. The resulting air flow is assigned to Stations 0, 2, and 3; exhaust flow including fuel is assigned to Station 4 and propagated downstream. Consequently, modeled mass flow can remain finite at Mach 0.

### Inlet — Station 0 → Station 2

`Inlet.calculate` copies total temperature and throat-derived mass flow from Station 0 and applies the configured inlet efficiency to total pressure:

\[
T_{t2} = T_{t0}, \qquad P_{t2} = \eta_{\text{inlet}}P_{t0}, \qquad \dot{m}_2 = \dot{m}_0
\]

This models stagnation-pressure recovery while assuming adiabatic flow with unchanged total temperature.

### Compressor — Station 2 → Station 3

The compressor pressure ratio \(\pi_c\) and efficiency \(\eta_c\) are loaded from the selected engine configuration. The isentropic outlet temperature and actual outlet temperature are:

\[
T_{t3s} = T_{t2}\pi_c^{(\gamma-1)/\gamma}
\]

\[
T_{t3} = T_{t2} + \frac{T_{t3s}-T_{t2}}{\eta_c}
\]

Pressure and specific work are:

\[
P_{t3} = \pi_c P_{t2}
\]

\[
w_c = c_p(T_{t3}-T_{t2})
\]

The code rounds \(T_{t3}\) and \(w_c\) to two decimal places. It also propagates mass flow to Station 3. Compressor efficiency is configurable per engine preset.

### Station 3 — compressor exit

Known properties:

- \(P_{t3}\)
- \(T_{t3}\)
- Mass flow rate

Used by:

- Combustor

### Combustor — Station 3 → Station 4

Inputs:

- \(P_{t3}\)
- \(T_{t3}\)
- Desired \(T_{t4}\)
- Combustor efficiency \(\eta_b\)
- Burner pressure ratio \(\beta_b\)

Outputs:

- \(P_{t4}\)
- \(T_{t4}\)
- Fuel-air ratio \(f\)
- Air-plus-fuel mass flow rate

Implemented equations:

\[
P_{t4} = \beta_b P_{t3}
\]

\[
f = \frac{c_p(T_{t4}-T_{t3})}{\eta_b Q_R-c_pT_{t4}}
\]

\[
\dot{m}_4 = \dot{m}_3(1+f)
\]

The fuel heating value is \(Q_R=43\times10^6\ \text{J/kg}\). Combustor efficiency and burner pressure ratio are configurable per engine preset. The fuel-air ratio is rounded to eight decimal places before mass flow is calculated.

### Station 4 — combustor exit / turbine inlet

Known properties:

- \(P_{t4}\)
- \(T_{t4}\)
- Fuel-air ratio \(f\)
- Air-plus-fuel mass flow rate

### Turbine — Station 4 → Station 5

Inputs:

- \(P_{t4}\)
- \(T_{t4}\)
- Compressor work \(w_c\)
- Turbine efficiency \(\eta_t\)

The turbine work is set equal to compressor work. Its actual exit temperature accounts for the fuel-added flow:

\[
w_t = w_c
\]

\[
T_{t5} = T_{t4} - \frac{w_t}{c_p(1+f)}
\]

The isentropic exit temperature and pressure calculation are:

\[
T_{t5s} = T_{t4} - \frac{T_{t4}-T_{t5}}{\eta_t}
\]

\[
P_{t5} = P_{t4}\left(\frac{T_{t5s}}{T_{t4}}\right)^{\gamma/(\gamma-1)}
\]

Station 5 mass flow is copied from Station 4, and \(f\) is propagated. Turbine efficiency is configurable per engine preset. No mechanical losses or cooling flow are modeled.

### Station 5 — turbine exit

Known properties:

- \(P_{t5}\)
- \(T_{t5}\)
- Fuel-air ratio \(f\)
- Air-plus-fuel mass flow rate

### Core power and fuel flow

The program reports compressor and turbine power for detailed runs and calculates fuel flow:

\[
\dot{W}_c=\dot{m}_a w_c
\]

\[
\dot{W}_t=\dot{m}_4c_p(T_{t4}-T_{t5})
\]

\[
\dot{m}_f=f\dot{m}_a
\]

Power is printed in MW, and fuel flow in kg/s. Since the turbine exit temperature is calculated directly from compressor work and fuel-added mass, the power balance is algebraically imposed by this model. Matching values check calculation consistency but do not independently validate real-engine shaft power.

### Nozzle — Station 5 → Station 8

The main program compares \(P_{t5}/P_{\text{ambient}}\) with the critical pressure ratio:

\[
\left(\frac{\gamma+1}{2}\right)^{\gamma/(\gamma-1)}
\]

If the ratio is greater than the critical value, it calls `calculate_choked` and sets \(M_e=1\). Otherwise it calls `calculate_unchoked` with ambient pressure. The unchoked calculation sets exit pressure equal to ambient and computes exit temperature, velocity, Mach number, density, and area. It prints a warning if the calculated exit Mach number is at least 1; it does not automatically switch to the choked branch in that case.

For the choked converging-nozzle calculation, the code determines the ideal critical temperature and applies nozzle efficiency \(\eta_n\):

\[
T_{t8s} = T_{t5}\frac{2}{\gamma+1}
\]

\[
T_8 = T_{t5} - \eta_n(T_{t5}-T_{t8s})
\]

\[
P_8 = \frac{P_{t5}}{1.893}
\]

\[
V_8 = \sqrt{2c_p(T_{t5}-T_8)}
\]

The code uses a fixed critical pressure ratio of 1.893 for air with \(\gamma=1.4\). Nozzle efficiency affects exit temperature and velocity, while the choked exit pressure is set independently using this ratio. For unchoked flow, the code sets \(P_8=P_{\text{ambient}}\), then calculates the isentropic temperature corresponding to that pressure:

\[
T_{t8s}=T_{t5}\left(\frac{P_8}{P_{t5}}\right)^{(\gamma-1)/\gamma}
\]

It applies nozzle efficiency as:

\[
T_8=T_{t5}-\eta_n(T_{t5}-T_{t8s})
\]

and derives velocity and Mach number from the calculated exit temperature. Both nozzle methods calculate exit density from \(\rho_8=P_8/(R T_8)\) and area from \(A_8=\dot{m}_8/(\rho_8 V_8)\). Nozzle efficiency comes from the selected engine configuration. The unchoked method warns on \(M_e\ge1\), but does not choose a different branch automatically.

### Station 8 — nozzle exit

Known properties:

- Exit pressure \(P_8\), stored as static pressure
- Exit temperature \(T_8\), stored as static temperature
- Exit velocity \(V_8\)
- Exit Mach number \(M_e=1\) for the choked branch, or calculated from the temperature ratio for the unchoked branch
- Air-plus-fuel mass flow rate
- Fuel-air ratio \(f\)
- Exit density \(\rho_8\)
- Exit area \(A_8\)

## Engine Performance

### Thrust

The current thrust calculation combines momentum and pressure thrust:

\[
F = \dot{m}_8 V_8 - \dot{m}_0 V_a + (P_8-P_a)A_8
\]

Station 8 mass flow includes fuel; Station 0 mass flow is air only. The pressure term becomes zero when \(P_8=P_a\), as in the ideal unchoked calculation.

### TSFC

\[
\text{TSFC} = \frac{f\dot{m}_0}{F}\times3600
\]

The reported units are kg/(N·hr).

### Effective jet velocity

\[
V_{\text{eff}} = V_8 + \frac{(P_8-P_a)A_8}{\dot{m}_8}
\]

### Thermal efficiency

\[
\eta_{th} =
\frac{\left((1+f)V_{\text{eff}}^2 - V_a^2\right)/2}{fQ_R}
\]

### Propulsive and overall efficiency

\[
\eta_p = \frac{2V_a}{V_{\text{eff}}+V_a}
\]

\[
\eta_o = \eta_{th}\eta_p
\]

The effective jet velocity folds pressure thrust into the velocity used by both efficiency calculations. These remain simplified performance relations.

## Station data

`Station` provides fields for static and total thermodynamic properties, flow properties, gas properties, geometry, and fuel-air ratio. New stations default to \(\gamma=1.4\), \(c_p=1004\ \text{J/(kg·K)}\), and \(R=287\ \text{J/(kg·K)}\). Components explicitly propagate only the properties they use.

## Current assumptions and scope

- Ideal gas with constant \(\gamma\), \(c_p\), and \(R\)
- ISA atmosphere layers from 0–20,000 m; unsupported altitudes are not handled with a clear input-validation error
- Inlet total-pressure recovery is modeled as \(P_{t2}=\eta_{\text{inlet}}P_{t0}\), with \(T_{t2}=T_{t0}\)
- Mass flow assumes ideal-gas choking at the turbine throat; the code does not independently verify that the throat is choked
- Inlet area is retained for reference but does not set mass flow
- Configurable compressor, combustor, turbine, and choked-nozzle efficiency models
- Component efficiencies and burner pressure ratio are entered interactively in custom mode or loaded from the selected engine preset
- Fuel mass is included in turbine flow and Station 8 mass flow
- Both choked and unchoked nozzle calculations are implemented; the unchoked method warns rather than automatically changing branches if \(M_e\ge1\)
- Thrust includes pressure thrust

## Current Simulator Capability

Implemented:

- ✅ Tropospheric atmosphere and freestream state
- ✅ ISA isothermal atmosphere layer through 20,000 m
- ✅ Mass-flow propagation and fuel addition
- ✅ Choked turbine-throat airflow metering
- ✅ Inlet pressure recovery
- ✅ Compressor efficiency model
- ✅ Combustor efficiency and burner pressure-ratio model
- ✅ Turbine efficiency and fuel-flow correction
- ✅ Choked and unchoked converging-nozzle calculations
- ✅ Nozzle exit density and area
- ✅ Momentum and pressure thrust
- ✅ Thrust, TSFC, thermal efficiency, propulsive efficiency, and overall efficiency
- ✅ Compressor power, turbine power, and fuel-flow reporting
- ✅ Custom engine input, single-preset runs, and preset comparison output (with current integration defects noted below)

## Recent Progress

### Version 1.2 Progress Update

#### Major Features Added

- Added JSON engine configuration loading from the `engines/` directory and runtime engine selection.
- Added presets for the Generic Turbojet, Pratt & Whitney J52/J57/J58, General Electric J79, Rolls-Royce/Snecma Olympus 593, and Bristol Siddeley Orpheus.
- Added three execution modes: custom engine values, a single JSON preset, and a comparison table across all presets.
- Added non-ideal inlet total-pressure recovery while conserving total temperature.
- Added nozzle exit density and continuity-based exit area.
- Added momentum and pressure thrust to reported engine performance.

### Version 1.3 Progress Update

#### Architecture and Model Changes

- Replaced the freestream-based \(\rho A V\) mass-flow estimate with choked turbine-throat metering.
- Added turbine throat area and published airflow references to the engine configurations.
- Corrected choked nozzle exit pressure to \(P_8=P_{t5}/1.893\), separating it from the efficiency-adjusted temperature.
- Added effective jet velocity to include pressure thrust in the thermal and propulsive efficiency calculations.

#### Sea-Level Static Airflow Validation

At 0 m altitude and Mach 0, the supplied model/published airflow comparisons are:

| Engine | Model airflow (kg/s) | Published airflow (kg/s) |
|---|---:|---:|
| J52 | 64.86 | 64.86 |
| J57 | 74.39 | 78.19 |
| J58 | 136.08 | 138.00 |
| J79 | 77.10 | 77.11 |
| Olympus 593 | 185.96 | 185.97 |
| Orpheus 803 | 38.10 | 38.10 |

These are airflow comparisons only; thrust, TSFC, and efficiency still require validation at matched published operating conditions.

#### Current Simulator Capability

Atmosphere → Freestream → Inlet → Compressor → Combustor → Turbine-Throat Airflow → Turbine → Nozzle → Geometry Calculations → Momentum Thrust → Pressure Thrust → TSFC → Thermal Efficiency → Propulsive Efficiency → Overall Efficiency → Power/Fuel-Flow Reporting → Preset Comparison (incomplete)

Current project phase: validation and calibration rather than new feature implementation.

### Latest Architecture and Validation Update

#### ISA Layer Expansion

The atmosphere module now supports 0–20,000 m: a lapse-rate troposphere to 11,000 m followed by an isothermal layer at 216.65 K to 20,000 m. Higher layers and clear handling of out-of-range altitude inputs remain unimplemented.

#### Power and Fuel-Flow Outputs

Detailed runs now report compressor power, turbine power, and fuel flow. The supplied J52 example reports 25.713 MW for both compressor and turbine power. Because turbine exit temperature is determined directly from compressor work, this equality is a built-in model consistency check rather than independent validation of physical power balance.

#### Sea-Level Static Airflow Comparisons

At 0 m altitude and Mach 0, the supplied model/reference airflow results are:

| Engine | Model airflow (kg/s) | Reference airflow (kg/s) |
|---|---:|---:|
| J52 | 64.86 | 64.86 |
| J57 | 74.39 | 78.19 |
| J58 | 136.08 | 138.00 |
| J79 | 77.10 | 77.11 |
| Olympus 593 | 185.96 | 185.97 |
| Orpheus 803 | 38.10 | 38.10 |

These are airflow comparisons only; they do not validate thrust, TSFC, or efficiencies.

#### Independent Static Thrust Check

The supplied GE J47 GE-25/-27 result is 26,253 N versus a reference value of 26,556 N, an indicated error of -1.14%. The reported model/reference airflow is 46.27 kg/s for both. This is a useful independent single-point check, but does not establish accuracy over other engines or flight conditions.

#### Known Preset Integration Limitation

The preset selection prompt lists `gej47`, and a J47 JSON file exists. However, the comparison-mode list contains `"orpheus, gej47"` as one string rather than two engine identifiers. In addition, the Generic preset lacks `published_thrust_n` and `notes`, fields accessed by the engine display function. Comparison and Generic-preset display need integration fixes before all presets can be considered operational.

#### Validation Roadmap

- Validate thrust against published data for all engines at matched rating conditions.
- Investigate Orpheus 803 and J58 thrust discrepancies.
- Verify turbine work and nozzle expansion assumptions.
- Verify thrust prediction at altitude and add thrust-error reporting.
- Expand station areas and flowpath analysis.

### Nozzle Improvements

Implemented separate nozzle operating modes:

#### Choked Flow

When:

\[
\frac{P_{t5}}{P_{\text{ambient}}} > 1.893
\]

the nozzle is treated as choked:

- Exit Mach number is set to 1
- Exit pressure is set to \(P_8=P_{t5}/1.893\)
- Exit velocity is calculated from the energy equation
- Pressure thrust is included in total thrust

#### Unchoked Flow

When:

\[
\frac{P_{t5}}{P_{\text{ambient}}} \le 1.893
\]

the nozzle is treated as unchoked:

- Exit pressure is set equal to ambient pressure
- Exit Mach number is calculated from static and stagnation temperatures
- Exit velocity is calculated from the energy equation
- Pressure thrust is zero because \(P_8=P_{\text{ambient}}\)

The unchoked calculation warns if its resulting Mach number is at least 1; it does not automatically switch to the choked model.

### Pressure Thrust

The simulator calculates:

\[
F = \dot{m}_8 V_8 - \dot{m}_0 V_a + (P_8-P_a)A_8
\]

where the first two terms are net momentum thrust and the last term is pressure thrust. Nozzle exit area is calculated using:

\[
A_8 = \frac{\dot{m}_8}{\rho_8 V_8}, \qquad \rho_8 = \frac{P_8}{R T_8}
\]

### Inlet Model

The inlet applies pressure recovery:

\[
P_{t2} = \eta_{\text{inlet}}P_{t0}
\]

while assuming:

\[
T_{t2}=T_{t0}
\]

This models stagnation-pressure loss while maintaining total temperature.

## Future Work

### High Priority

- Fix comparison-mode handling of the Generic and J47 presets
- Validate thrust against published values for all engines
- Investigate remaining Orpheus 803 and J58 thrust discrepancies
- Verify turbine work and nozzle expansion assumptions
- Verify thrust predictions at altitude and report thrust error

### Medium Priority

- Expand station-property and station-area calculations
- Add flowpath analysis mode

### Long-Term

- Compressor and turbine maps
- Corrected mass flow
- Variable-geometry systems
- Off-design performance analysis
- Turbofan architecture and afterburner support
