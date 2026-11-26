# Turbojet Simulator Equation Reference

This document describes equations currently used by the simulator and identifies modeling assumptions and unfinished features. Engine parameters can be entered interactively or loaded from JSON files in `engines/`; preset comparison runs all configured engines at the same flight conditions.

Calculations use SI units and ideal-gas properties, with the following defaults on each `Station`:

| Symbol | Value | Meaning |
|---|---:|---|
| \(\gamma\) | 1.4 | Ratio of specific heats |
| \(c_p\) | 1004 J/(kg·K) | Specific heat at constant pressure |
| \(R\) | 287 J/(kg·K) | Gas constant for air |

## Atmosphere

`isa_atmosphere(altitude)` in `atmosphere.py` uses a tropospheric lapse-rate layer from 0 to 11,000 m, followed by an isothermal layer from 11,000 to 20,000 m.

\[
T = T_0 - Lh
\]

\[
P = P_0\left(\frac{T}{T_0}\right)^{g/(LR)}
\]

\[
\rho = \frac{P}{RT}
\]

For \(11{,}000 < h \le 20{,}000\ \text{m}\), temperature is held at \(T=216.65\ \text{K}\), and pressure and density are:

\[
P=P_{11}\exp\left(-\frac{g(h-11{,}000)}{RT}\right), \qquad
\rho=\frac{P}{RT}
\]

where \(P_{11}=22{,}614.21\ \text{Pa}\).

- \(h\): altitude (m), supported range 0–20,000 m
- \(T_0 = 288.15\ \text{K}\): sea-level temperature
- \(P_0 = 101325\ \text{Pa}\): sea-level pressure
- \(L = 0.0065\ \text{K/m}\): temperature lapse rate
- \(g = 9.81\ \text{m/s}^2\)
- \(R = 287\ \text{J/(kg·K)}\)

The implementation rounds \(T\) and \(P\) to two decimal places and \(\rho\) to four. It does not implement higher ISA layers or return a clear validation error for unsupported altitudes.

## Engine Configuration

In preset mode, `main.py` loads the selected `engines/<name>.json` file; comparison mode loads each configured preset in turn. The presets currently available are:

- Generic Turbojet
- Pratt & Whitney J52, J57, and J58
- General Electric J79
- General Electric J47 GE-25/-27
- Rolls-Royce/Snecma Olympus 593
- Bristol Siddeley Orpheus

The JSON parameters include compressor pressure ratio and efficiency, combustor exit total temperature, component efficiencies, inlet and turbine throat areas, design Mach numbers, fixed internal areas, and published reference data. The program supports custom input, a single JSON preset, and comparison of all presets. The Generic preset's single-engine information display still accesses `published_thrust_n` and `notes`, which are absent from its configuration.

## Internal Flowpath Sizing and Off-Design Solve

The design Mach targets `M3_design`, `M4_design`, and `M5_design` define preset sizing conditions at the compressor exit, combustor exit, and turbine exit. They are internal design-point targets, not the flight Mach number. Presets store the corresponding areas `A3`, `A4_station`, and `A5`.

For a selected design Mach \(M\), the sizing calculation first derives the static state:

\[
T = \frac{T_t}{1+\frac{\gamma-1}{2}M^2}, \qquad
P = \frac{P_t}{\left(1+\frac{\gamma-1}{2}M^2\right)^{\gamma/(\gamma-1)}}
\]

\[
\rho=\frac{P}{RT}, \qquad V=M\sqrt{\gamma RT}
\]

Continuity gives:

\[
A=\frac{\dot m}{\rho V}
\]

The equivalent mass-flow parameter is:

\[
\operatorname{MFP}(M)=M\left(1+\frac{\gamma-1}{2}M^2\right)^{-\frac{\gamma+1}{2(\gamma-1)}}
\]

\[
\dot m = \frac{P_t A}{\sqrt{T_t}}\sqrt{\frac{\gamma}{R}}\operatorname{MFP}(M)
\]

`area_from_mach()` uses the MFP form to size an area from a design Mach. `area_from_design_mach()` uses the static-state and continuity form as a cross-check.

At an off-design condition, `solve_station_flow()` holds the preset area fixed and solves the MFP relation for Mach using bisection. The current search is limited to the subsonic interval \(0\le M\le1\); it reconstructs \(T,P,\rho,a,V\) from the solved Mach and total state. At or above the maximum MFP target it assigns \(M=1\), but does not signal an impossible requested mass flow or solve the supersonic branch.

Preset runs apply this solver at Station 2 using inlet area and at Stations 3–5 using `A3`, `A4_station`, and `A5`. Custom-input mode currently calculates design areas after its cycle run but does not pass them back through the solver. Station 8 total properties are recovered from its exit static values and Mach. The nozzle exit area itself is still recalculated from continuity for each operating point.

## Freestream / Station 0

The program prompts for altitude and Mach number and obtains \(T\), \(P\), and \(\rho\) from the atmosphere model.

### Speed of sound and flight velocity

\[
a = \sqrt{\gamma R T}
\]

\[
V_a = Ma
\]

Here \(a\) is speed of sound, \(M\) is flight Mach number, and \(V_a\) is freestream/aircraft velocity. The code rounds both \(a\) and \(V_a\) to two decimal places.

### Stagnation temperature

\[
T_{t0} = T\left(1+\frac{\gamma-1}{2}M^2\right)
\]

### Stagnation pressure

\[
P_{t0} = P\left(1+\frac{\gamma-1}{2}M^2\right)^{\gamma/(\gamma-1)}
\]

These are ideal-gas, isentropic stagnation relations. The program rounds \(T_{t0}\) and \(P_{t0}\) to two decimal places.

## Mass Flow Rate

The original freestream estimate \(\dot{m}_0=\rho A V_a\) is no longer used to set engine airflow. That expression approaches zero as flight Mach approaches zero, even though a running turbojet draws air at static conditions.

The current model assumes choked flow through the turbine nozzle-guide-vane throat and uses Station 4 total conditions and throat area:

\[
\dot{m}_4 =
\frac{P_{t4}A_4}{\sqrt{T_{t4}}}
\times\sqrt{\frac{\gamma}{R}}
\times\left(\frac{\gamma+1}{2}\right)^{-\frac{\gamma+1}{2(\gamma-1)}}
\]

\[
\dot{m}_0 = \frac{\dot{m}_4}{1+f}
\]

- \(\dot{m}_4\): combustor-exit / turbine-inlet gas mass flow, including fuel (kg/s)
- \(\dot{m}_0\): air mass flow (kg/s)
- \(A_4\): turbine throat area (m²)
- \(P_{t4}\): combustor-exit total pressure (Pa)
- \(T_{t4}\): combustor-exit total temperature (K)
- \(f\): fuel-air ratio
- \(\gamma\): ratio of specific heats
- \(R\): specific gas constant (J/(kg·K))

This is the ideal-gas choked mass-flow relation. The implementation uses it without a separate check that the turbine throat is actually choked. The JSON turbine throat area, rather than inlet area, is the primary mass-flow calibration parameter. Inlet area remains available for geometric reference and future inlet-flow calculations.

## Inlet / Station 0 → Station 2

The inlet copies total temperature and the throat-derived air mass flow and applies inlet efficiency \(\eta_{\text{inlet}}\) to total pressure:

\[
T_{t2}=T_{t0},\qquad P_{t2}=\eta_{\text{inlet}}P_{t0},\qquad \dot{m}_2=\dot{m}_0
\]

This models stagnation-pressure recovery with unchanged total temperature.

## Compressor / Station 2 → Station 3

The compressor uses pressure ratio \(\pi_c\) and efficiency \(\eta_c\), loaded from the selected engine configuration.

### Total pressure

\[
P_{t3} = \pi_c P_{t2}
\]

### Isentropic and actual total temperature

\[
T_{t3s}=T_{t2}\pi_c^{(\gamma-1)/\gamma}
\]

\[
T_{t3}=T_{t2}+\frac{T_{t3s}-T_{t2}}{\eta_c}
\]

For \(\eta_c<1\), the actual compressor temperature rise is larger than the isentropic rise. This models compressor isentropic efficiency.

### Specific compressor work

\[
w_c = c_p(T_{t3}-T_{t2})
\]

- \(w_c\): compressor work per unit air mass (J/kg)
- \(c_p\): specific heat at constant pressure

The program rounds \(T_{t3}\) and \(w_c\) to two decimal places, and propagates \(\dot{m}_2\) to Station 3.

## Combustor / Station 3 → Station 4

The combustor uses target temperature \(T_{t4}\), efficiency \(\eta_b\), burner pressure ratio \(\beta_b\), and fuel lower heating value \(Q_R=43\times10^6\ \text{J/kg}\).

### Exit pressure

\[
P_{t4}=\beta_b P_{t3}
\]

The selected configuration supplies \(\beta_b\). A value of 1.0 means no total-pressure loss; values below 1 represent pressure loss in this model.

### Fuel-air ratio

\[
f = \frac{c_p(T_{t4}-T_{t3})}{\eta_b Q_R-c_pT_{t4}}
\]

- \(f\): fuel-to-air mass ratio
- \(\eta_b\): combustor efficiency
- \(Q_R\): fuel lower heating value

The selected configuration supplies \(\eta_b\). The code rounds \(f\) to eight decimal places.

### Fuel addition and mass flow

\[
\dot{m}_4=\dot{m}_3(1+f)
\]

This treats Station 3 flow as air flow and adds fuel mass at the combustor.

## Turbine / Station 4 → Station 5

The turbine uses compressor specific work \(w_c\) and turbine efficiency \(\eta_t\).

### Work balance and actual exit temperature

The turbine work is set equal to compressor work:

\[
w_t=w_c
\]

Because combustor exit mass flow includes fuel, the code calculates:

\[
T_{t5}=T_{t4}-\frac{w_t}{c_p(1+f)}
\]

This accounts for the fuel-added mass when converting work per unit air mass to turbine temperature drop.

### Isentropic exit temperature and pressure

\[
T_{t5s}=T_{t4}-\frac{T_{t4}-T_{t5}}{\eta_t}
\]

\[
P_{t5}=P_{t4}\left(\frac{T_{t5s}}{T_{t4}}\right)^{\gamma/(\gamma-1)}
\]

For \(\eta_t<1\), the isentropic temperature drop needed to produce the actual work is larger; the pressure relation uses \(T_{t5s}\). The code rounds \(P_{t5}\) to two decimal places and propagates mass flow and \(f\) to Station 5.

### Power and fuel flow

The program reports compressor and turbine powers using:

\[
\dot{W}_c=\dot{m}_0w_c
\]

\[
w_t=c_p(T_{t4}-T_{t5}), \qquad
\dot{W}_t=\dot{m}_4w_t
\]

Fuel flow is:

\[
\dot{m}_f=f\dot{m}_0
\]

Because \(T_{t5}\) is calculated from \(w_c/[c_p(1+f)]\), this implementation makes \(\dot{W}_t\) algebraically equal to \(\dot{W}_c\), subject to rounding. Matching reported powers are an internal consistency check, not an independent validation of a real engine's shaft power.

## Station 8 Stagnation Recovery

The nozzle methods populate Station 8 static exit properties and Mach. The program then obtains total properties from the isentropic stagnation relations:

\[
T_{t8}=T_8\left(1+\frac{\gamma-1}{2}M_8^2\right)
\]

\[
P_{t8}=P_8\left(1+\frac{\gamma-1}{2}M_8^2\right)^{\gamma/(\gamma-1)}
\]

These are recovered reporting values, not separate outputs from a nozzle-flow solution. In the choked branch with \(\eta_n<1\), the adjusted static temperature, fixed ideal critical exit pressure, and imposed \(M_8=1\) do not generally reconstruct the upstream \(T_{t5}\) and \(P_{t5}\). This is a known consistency question for the current simplified nozzle model.

## Nozzle / Station 5 → Station 8

The main program checks the ratio of turbine-exit total pressure to ambient pressure:

\[
\frac{P_{t5}}{P_0} >
\left(\frac{\gamma+1}{2}\right)^{\gamma/(\gamma-1)}
\]

For \(\gamma=1.4\), the critical ratio is approximately 1.893. When the check passes, the program uses the choked converging-nozzle calculation and sets \(M_e=1\). If it fails, the program calls the unchoked calculation.

### Choked nozzle temperature and efficiency

The ideal critical temperature is:

\[
T_{t8s}=T_{t5}\frac{2}{\gamma+1}
\]

The implemented nozzle efficiency correction is:

\[
T_8=T_{t5}-\eta_n(T_{t5}-T_{t8s})
\]

For \(\eta_n=1\), this reduces to the ideal choked temperature. For lower efficiency, the calculated temperature is higher and the velocity is lower.

### Exit pressure and velocity

The code calculates:

\[
P_8=\frac{P_{t5}}{1.893}
\]

\[
V_8=\sqrt{2c_p(T_{t5}-T_8)}
\]

The implementation uses the fixed critical pressure ratio for air with \(\gamma=1.4\). Nozzle efficiency affects exit temperature and velocity, while the choked exit pressure is set independently using this pressure ratio.

### Unchoked flow

When \(P_{t5}/P_{\text{ambient}}\) is at or below the critical ratio, `calculate_unchoked` sets:

\[
P_8=P_{\text{ambient}}
\]

It calculates the isentropic exit temperature corresponding to that pressure:

\[
T_{t8s}=T_{t5}\left(\frac{P_8}{P_{t5}}\right)^{(\gamma-1)/\gamma}
\]

The actual exit temperature accounts for nozzle efficiency:

\[
T_8=T_{t5}-\eta_n(T_{t5}-T_{t8s})
\]

Then:

\[
V_8=\sqrt{2c_p(T_{t5}-T_8)}
\]

\[
M_8=\sqrt{\frac{2}{\gamma-1}\left(\frac{T_{t5}}{T_8}-1\right)}
\]

The function warns if \(M_8\ge1\), but does not automatically switch to the choked calculation.

### Exit density and area

Both nozzle branches calculate:

\[
\rho_8=\frac{P_8}{RT_8}
\]

\[
A_8=\frac{\dot{m}_8}{\rho_8V_8}
\]

Mass flow and fuel-air ratio are propagated to Station 8.

## Engine Performance

### Thrust

The code calculates momentum thrust plus pressure thrust:

\[
F = \dot{m}_8V_8 - \dot{m}_0V_a + (P_8-P_{\text{ambient}})A_8
\]

Station 8 mass flow includes fuel, while freestream flow is air only. In the unchoked branch, \(P_8=P_{\text{ambient}}\), so the pressure-thrust term is zero.

### Thrust-specific fuel consumption

\[
\text{TSFC} = \frac{f\dot{m}_0}{F}\times3600
\]

The reported units are kg/(N·hr).

### Thermal efficiency

\[
\eta_{th} =
\frac{\left((1+f)V_{\text{eff}}^2 - V_a^2\right)/2}{fQ_R}
\]

### Propulsive and overall efficiency

\[
V_{\text{eff}}=V_8+\frac{(P_8-P_a)A_8}{\dot{m}_8}
\]

\[
\eta_p = \frac{2V_a}{V_{\text{eff}}+V_a}
\]

\[
\eta_o = \eta_{th}\eta_p
\]

The effective jet velocity folds pressure thrust into the velocity used by both efficiency calculations. These remain simplified performance relations.

Because \(V_a=0\) in a static test, the current propulsive-efficiency relation returns \(\eta_p=0\) by construction. Static thrust and TSFC are more useful metrics there; static \(\eta_p\) and \(\eta_o\) should not be interpreted as positive propulsive performance.

## Future Improvements

- Complete validation of all preset engines.
- Build an off-design test matrix: Sea Level Static; 11,000 m/Mach 0.85; 18,000 m/Mach 2.0.
- Investigate corrected airflow methods.
- Investigate simplified compressor-map modelling.
- Implement fixed-vs-variable nozzle support.
- Improve off-design component realism.
- Continue verification against published engine data.
- Investigate choking control, nozzle-loss modeling, and input validation.
- Later: higher ISA layers, turbine maps, turbofans, and afterburners.

## Simplifying assumptions and limitations

- Ideal gas with constant \(\gamma\), \(c_p\), and \(R\)
- ISA atmosphere implemented from 0–20,000 m; input outside the supported layers is not handled with a clear validation error
- Inlet, compressor, combustor, turbine, and nozzle use simplified efficiency/pressure-ratio models
- Component parameters vary by selected JSON engine preset
- Air mass flow is inferred from an assumed choked turbine throat; the implementation does not verify that this throat is choked
- `turbine_throat_area` meters flow separately from the Station 4 fixed area `A4_station`; no distinct station is solved for the turbine nozzle-guide-vane throat
- MFP station solving is subsonic-only; at its choking limit it sets \(M=1\) without reporting a capacity mismatch
- Internal fixed-area solving is currently applied in preset runs, not custom mode
- Nozzle exit area is recalculated by continuity at every run; fixed-versus-variable nozzle geometry is not yet implemented
- The nozzle's choked exit temperature correction and fixed critical pressure ratio can yield recovered Station 8 total properties that differ from Station 5 when nozzle efficiency is below 1
- Pressure thrust is incorporated into efficiency calculations through an effective-velocity surrogate; its energy-consistency should be checked against the selected efficiency definitions
- Choked nozzle exit pressure uses a fixed critical ratio of 1.893 for \(\gamma=1.4\)
- Unchoked nozzle method is implemented, but warns rather than switching branches if \(M_8\ge1\)
- Thrust includes pressure thrust; other model simplifications remain

## Version 1.2 Progress

- Added JSON engine configuration loading and runtime engine selection.
- Added Generic Turbojet, J52, J57, J58, J79, Olympus 593, and Orpheus presets.
- Added custom engine-input and all-preset comparison modes alongside single-preset selection.
- Added inlet pressure recovery, \(P_{t2}=\eta_{\text{inlet}}P_{t0}\), with \(T_{t2}=T_{t0}\).
- Added nozzle exit density and continuity-based exit area for pressure-thrust calculations.
- Added momentum and pressure thrust reporting.
- Validated representative choked and unchoked nozzle cases and the expected thrust reduction when inlet efficiency is reduced.

## Version 1.3 Progress

- Replaced the freestream-based \(\rho A V\) mass-flow estimate with choked turbine-throat metering.
- Added turbine throat area and published airflow references to the engine configurations; inlet area is retained for reference and no longer sets mass flow.
- Corrected choked nozzle exit pressure to \(P_8=P_{t5}/1.893\).
- Added effective jet velocity to account for pressure thrust in the thermal and propulsive efficiency calculations.

### Sea-Level Static Airflow Validation

The supplied comparisons at 0 m altitude and Mach 0 are:

| Engine | Model airflow (kg/s) | Published airflow (kg/s) |
|---|---:|---:|
| J52 | 64.86 | 64.86 |
| J57 | 74.39 | 78.19 |
| J58 | 136.08 | 138.00 |
| J79 | 77.10 | 77.11 |
| Olympus 593 | 185.96 | 185.97 |
| Orpheus 803 | 38.10 | 38.10 |

These results validate airflow only at the listed static conditions; thrust, TSFC, and efficiency comparisons remain in progress. The current project phase is validation and calibration.

## Current Project Update

- Added fixed-area MFP station solving and preset design Mach targets.
- Added and locally checked J47/J52 design areas and off-design cases; continuity/MFP area differences are at floating-point roundoff scale.
- Current local static J47 prediction is 26,252.80 N versus 26,556 N reference (-1.14%).
- Current local static J52 prediction is 42,325.29 N versus 49,820 N preset reference (-15.04%), despite modeled air flow matching the reference.
- The comparison mode completes for the eight configured presets; the Generic single-preset information display still lacks two metadata keys.
- Airflow and equation cross-checks do not independently validate thrust, TSFC, or efficiency.

## Next Development Priorities

1. Complete validation of all preset engines.
2. Build an off-design test matrix: Sea Level Static; 11,000 m/Mach 0.85; 18,000 m/Mach 2.0.
3. Investigate corrected airflow methods.
4. Investigate simplified compressor-map modelling.
5. Implement fixed-vs-variable nozzle support.
6. Improve off-design component realism.
7. Continue verification against published engine data.
