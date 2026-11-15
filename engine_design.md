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

`main.py` prompts for altitude, flight Mach number, and inlet area. It then calculates Station 0 and calls each component in sequence. The compressor pressure ratio is 10, combustor exit total temperature is 1400 K, and the current component efficiencies and burner pressure ratio are configured as 1.0.

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
- Air mass flow rate \(\dot{m}_a\)
- Total temperature \(T_{t0}\)
- Total pressure \(P_{t0}\)

The atmosphere uses a single tropospheric lapse-rate layer intended for 0–11,000 m, rather than a complete multi-layer ISA model. Freestream speed of sound, velocity, and total properties use ideal-gas relations. Mass flow rate is:

\[
\dot{m}_a = \rho A V_a
\]

### Inlet — Station 0 → Station 2

`Inlet.calculate` copies total temperature, total pressure, and mass flow from Station 0:

\[
T_{t2} = T_{t0}, \qquad P_{t2} = P_{t0}, \qquad \dot{m}_2 = \dot{m}_0
\]

The inlet assumes ideal flow. An inlet efficiency value is passed in `main.py` but is not currently used; inlet pressure recovery and losses are future work.

### Compressor — Station 2 → Station 3

The compressor pressure ratio \(\pi_c\) is configured in `main.py` as 10. The isentropic outlet temperature and actual outlet temperature are:

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

The code rounds \(T_{t3}\) and \(w_c\) to two decimal places. It also propagates mass flow to Station 3. Compressor efficiency is configurable; the current setting is 1.0.

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

The fuel heating value is \(Q_R=43\times10^6\ \text{J/kg}\). Combustor efficiency and burner pressure ratio are configurable; both are 1.0 in the current run. The fuel-air ratio is rounded to eight decimal places before mass flow is calculated.

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

Station 5 mass flow is copied from Station 4, and \(f\) is propagated. Turbine efficiency is configurable; the current setting is 1.0. No mechanical losses or cooling flow are modeled.

### Station 5 — turbine exit

Known properties:

- \(P_{t5}\)
- \(T_{t5}\)
- Fuel-air ratio \(f\)
- Air-plus-fuel mass flow rate

### Nozzle — Station 5 → Station 8

The main program compares \(P_{t5}/P_{\text{ambient}}\) with the critical pressure ratio:

\[
\left(\frac{\gamma+1}{2}\right)^{\gamma/(\gamma-1)}
\]

If the ratio is greater than the critical value, it calls `calculate_choked` and sets \(M_e=1\). Otherwise it calls `calculate_unchoked`, which is currently a placeholder (`pass`), so unchoked operation is not yet supported end to end.

For the choked converging-nozzle calculation, the code determines the ideal critical temperature and applies nozzle efficiency \(\eta_n\):

\[
T_{t8s} = T_{t5}\frac{2}{\gamma+1}
\]

\[
T_8 = T_{t5} - \eta_n(T_{t5}-T_{t8s})
\]

\[
P_8 = P_{t5}\left(\frac{T_8}{T_{t5}}\right)^{\gamma/(\gamma-1)}
\]

\[
V_8 = \sqrt{2c_p(T_{t5}-T_8)}
\]

The choked calculation copies mass flow and fuel-air ratio to Station 8. Nozzle efficiency is configurable; the current setting is 1.0. This is a simplified model; the exit pressure relation applies the isentropic pressure-temperature relation to the efficiency-adjusted temperature.

### Station 8 — nozzle exit

Known properties in the choked branch:

- Exit pressure \(P_8\), stored as static pressure
- Exit temperature \(T_8\), stored as static temperature
- Exit velocity \(V_8\)
- Exit Mach number \(M_e=1\)
- Air-plus-fuel mass flow rate
- Fuel-air ratio \(f\)

## Engine Performance

### Thrust

The current momentum thrust calculation is:

\[
F = \dot{m}_8 V_8 - \dot{m}_0 V_a
\]

Station 8 mass flow includes fuel; Station 0 mass flow is air only. Pressure thrust is not included.

### TSFC

\[
\text{TSFC} = \frac{f\dot{m}_0}{F}\times3600
\]

The reported units are kg/(N·hr).

### Thermal efficiency

\[
\eta_{th} =
\frac{\left((1+f)V_8^2 - V_a^2\right)/2}{fQ_R}
\]

### Propulsive and overall efficiency

\[
\eta_p = \frac{2V_a}{V_8+V_a}
\]

\[
\eta_o = \eta_{th}\eta_p
\]

These are simplified ideal-jet performance relations; pressure thrust and losses beyond the component efficiency corrections are not represented.

## Station data

`Station` provides fields for static and total thermodynamic properties, flow properties, gas properties, geometry, and fuel-air ratio. New stations default to \(\gamma=1.4\), \(c_p=1004\ \text{J/(kg·K)}\), and \(R=287\ \text{J/(kg·K)}\). Components explicitly propagate only the properties they use.

## Current assumptions and scope

- Ideal gas with constant \(\gamma\), \(c_p\), and \(R\)
- Single-layer tropospheric atmosphere intended for 0–11,000 m; input is not range-validated
- Ideal inlet; configured inlet efficiency is not used
- Configurable compressor, combustor, turbine, and choked-nozzle efficiency models
- Current efficiencies and burner pressure ratio are all set to 1.0
- Fuel mass is included in turbine flow and Station 8 mass flow
- Unchoked nozzle calculation is unimplemented
- Thrust omits pressure thrust

## Current Simulator Capability

Implemented:

- ✅ Tropospheric atmosphere and freestream state
- ✅ Mass-flow propagation and fuel addition
- ✅ Compressor efficiency model
- ✅ Combustor efficiency and burner pressure-ratio model
- ✅ Turbine efficiency and fuel-flow correction
- ✅ Choked nozzle efficiency calculation
- ✅ Thrust, TSFC, thermal efficiency, propulsive efficiency, and overall efficiency

Next milestone:

- ➡ Unchoked nozzle model and complete choking behavior

## Version 1.1 Changes

- Added non-ideal component calculation models and efficiency inputs.
- Added burner pressure-ratio support and fuel-flow propagation.
- Added fuel-mass correction to turbine work balance.
- Added TSFC, thermal, propulsive, and overall efficiency calculations.
- Added a choked-flow check and choked converging-nozzle model.
