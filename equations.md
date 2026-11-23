# Turbojet Simulator Equation Reference

This document describes equations currently used by the simulator and identifies modeling assumptions and unfinished features. Engine parameters can be entered interactively or loaded from JSON files in `engines/`; comparison mode is intended to apply each preset at the same flight conditions, but currently has a malformed list entry.

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

In preset mode, `main.py` loads the selected `engines/<name>.json` file; comparison mode attempts to load each preset in turn but currently has an invalid combined identifier. The presets currently available are:

- Generic Turbojet
- Pratt & Whitney J52, J57, and J58
- General Electric J79
- General Electric J47 GE-25/-27
- Rolls-Royce/Snecma Olympus 593
- Bristol Siddeley Orpheus

The JSON parameters include compressor pressure ratio and efficiency, combustor exit total temperature, combustor efficiency and pressure ratio, turbine efficiency, nozzle efficiency, inlet efficiency, inlet area, turbine throat area, and published reference data. The program supports three workflows: entering component parameters interactively, loading one JSON preset, or attempting to run all presets at the same altitude and Mach number for comparison. The comparison loop does not complete because of a malformed engine identifier; the Generic preset display also lacks metadata keys required by the single-preset display.

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

## Future Improvements

- Validate thrust at matched published conditions and report percentage error
- Investigate the Orpheus 803 and J58 thrust discrepancies
- Correct preset comparison integration for the J47 and Generic entries
- Validate thrust prediction at altitude
- Calculate additional station areas and support flowpath analysis
- Add corrected mass flow, compressor and turbine maps, variable geometry, and off-design analysis
- Improve choking control, nozzle-loss modeling, and input validation
- Implement higher ISA layers and extend performance modeling to turbofans and afterburners

## Simplifying assumptions and limitations

- Ideal gas with constant \(\gamma\), \(c_p\), and \(R\)
- ISA atmosphere implemented from 0–20,000 m; input outside the supported layers is not handled with a clear validation error
- Inlet, compressor, combustor, turbine, and nozzle use simplified efficiency/pressure-ratio models
- Component parameters vary by selected JSON engine preset
- Air mass flow is inferred from an assumed choked turbine throat; the implementation does not verify that this throat is choked
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

- Added the ISA isothermal layer from 11,000 to 20,000 m.
- Added compressor power, turbine power, and fuel-flow calculations to detailed output.
- Added the General Electric J47 GE-25/-27 preset with reported reference airflow and thrust.
- Reported independent static J47 result: model airflow 46.27 kg/s and thrust 26,253 N versus reference values of 46.27 kg/s and 26,556 N (reported thrust error: -1.14%).
- Reported J52 compressor and turbine power: 25.713 MW each. Because the turbine temperature drop is derived directly from compressor specific work, this agreement is an implementation consistency check rather than independent physical validation.
- The comparison-mode list currently contains the combined string `orpheus, gej47`, which does not match an engine JSON filename. The Generic preset also lacks `published_thrust_n` and `notes`, fields accessed by current display code; preset integration should be corrected before claiming all-engine comparison.
- Airflow reference agreement does not by itself validate thrust, TSFC, or efficiencies.
