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
Thrust
```

`main.py` prompts for altitude, flight Mach number, and inlet area. It then calculates Station 0 and calls each component in sequence. The compressor pressure ratio is 10; the combustor exit total temperature is 1400 K and combustion efficiency is 1.0.

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
- Air velocity \(V\)
- Mass flow rate \(\dot{m}\)
- Total temperature \(T_{t0}\)
- Total pressure \(P_{t0}\)

The atmosphere model uses one lapse-rate layer, intended for altitudes from 0 to 11,000 m. Freestream speed of sound, velocity, and total properties are calculated using ideal-gas relations. Mass flow rate is:

\[
\dot{m} = \rho A V
\]

### Inlet — Station 0 → Station 2

`Inlet.calculate` creates Station 2 and copies:

\[
T_{t2} = T_{t0}, \qquad P_{t2} = P_{t0}
\]

The inlet is assumed ideal. It transfers total properties only; Station 2 static conditions, velocity, and pressure recovery are not calculated.

### Compressor — Station 2 → Station 3

The compressor pressure ratio \(\pi_c\) is configured in `main.py` as 10.

Implemented equations:

\[
P_{t3} = \pi_c P_{t2}
\]

\[
T_{t3} = T_{t2}\left(\frac{P_{t3}}{P_{t2}}\right)^{(\gamma-1)/\gamma}
\]

\[
w_c = c_p(T_{t3} - T_{t2})
\]

Outputs:

- \(P_{t3}\)
- \(T_{t3}\)
- Compressor specific work \(w_c\)

The model assumes isentropic compression and constant gas properties. Station 3 is newly constructed with default gas properties; the component does not copy other Station 2 fields.

### Station 3 — compressor exit

Known properties:

- \(P_{t3}\)
- \(T_{t3}\)

Used by:

- Combustor

### Combustor — Station 3 → Station 4

Inputs:

- \(P_{t3}\)
- \(T_{t3}\)
- Desired \(T_{t4}\)

Outputs:

- \(P_{t4}\)
- \(T_{t4}\)
- Fuel-air ratio \(f\)

Implemented equations:

\[
P_{t4} = P_{t3}
\]

\[
f = \frac{c_p(T_{t4} - T_{t3})}{\eta_b Q_R - c_p T_{t4}}
\]

Current assumptions:

- Ideal, constant-pressure combustor
- \(\eta_b = 1.0\)
- \(Q_R = 43 \times 10^6\ \text{J/kg}\)
- Constant \(c_p\) and \(\gamma\)

### Station 4 — combustor exit / turbine inlet

Known properties:

- \(P_{t4}\)
- \(T_{t4}\)
- \(f\)

### Turbine — Station 4 → Station 5

Inputs:

- \(P_{t4}\)
- \(T_{t4}\)
- Compressor work \(w_c\)

Outputs:

- \(P_{t5}\)
- \(T_{t5}\)

Implemented equations:

\[
w_t = w_c
\]

\[
T_{t5} = T_{t4} - \frac{w_t}{c_p}
\]

\[
P_{t5} = P_{t4}\left(\frac{T_{t5}}{T_{t4}}\right)^{\gamma/(\gamma-1)}
\]

Assumptions:

- Ideal turbine
- No mechanical losses
- Constant \(c_p\) and \(\gamma\)
- Turbine work balance neglects the added fuel mass

### Station 5 — turbine exit

Known properties:

- \(P_{t5}\)
- \(T_{t5}\)
- \(f\)

Station 5 carries the fuel-air ratio from Station 4.

### Nozzle — Station 5 → Station 8

Inputs:

- \(P_{t5}\)
- \(T_{t5}\)
- Ambient pressure (used by the choking check in `main.py`)

Outputs:

- Exit pressure \(P_e\)
- Exit temperature \(T_e\)
- Exit velocity \(V_e\)
- Exit Mach number \(M_e\) when the choking check passes

The nozzle calculates properties using a choked converging-nozzle assumption:

\[
T_e = T_{t5}\frac{2}{\gamma+1}
\]

\[
P_e = \frac{P_{t5}}{\left((\gamma+1)/2\right)^{\gamma/(\gamma-1)}}
\]

\[
V_e = \sqrt{2c_p(T_{t5} - T_e)}
\]

The main program compares \(P_{t5}/P_{\text{ambient}}\) with the critical pressure ratio. If the threshold is exceeded, it sets \(M_e=1\). There is no unchoked exit-state calculation or alternate nozzle branch; the nozzle equations above are evaluated regardless of the check.

### Station 8 — nozzle exit

Known properties assigned by the nozzle:

- \(P_e\), stored as Station 8 static pressure \(P\)
- \(T_e\), stored as Station 8 static temperature \(T\)
- \(V_e\), stored as Station 8 air velocity
- \(M_e=1\) if the main-program choking check passes; otherwise it remains unset
- Fuel-air ratio \(f\), copied from Station 5

## Engine Performance

### Mass flow rate

Station 0 mass flow rate is calculated from freestream density, inlet area, and velocity:

\[
\dot{m} = \rho A V
\]

### Thrust

The intended momentum thrust relation is:

\[
F = (1+f)\dot{m}V_e - \dot{m}V_a
\]

However, the current expression in `main.py` is:

\[
F_{\text{code}} = (1+f)\dot{m}(V_e - V_a)
\]

These expressions differ in the treatment of inlet momentum for the fuel flow. The code's expression is what is currently evaluated. Neither expression currently includes a pressure-thrust term.

## Station data

`Station` provides fields for:

- Static state: \(T\), \(P\), and \(\rho\)
- Total state: \(T_t\) and \(P_t\)
- Flow: \(\dot{m}\), Mach number, air velocity, and speed of sound
- Gas properties: \(\gamma\), \(c_p\), and \(R\)
- Geometry: area
- Combustion: fuel-air ratio \(f\)

Each new station initializes \(\gamma=1.4\), \(c_p=1004\text{ J/(kg·K)}\), and \(R=287\text{ J/(kg·K)}\). Other fields start unset unless a component or `main.py` assigns them.

## Current assumptions and scope

- Ideal gas with constant \(\gamma\), \(c_p\), and \(R\)
- Continuous single-layer lapse-rate atmosphere intended for 0–11,000 m
- Ideal inlet with no total-pressure loss
- Isentropic compressor and turbine
- Ideal combustor with no pressure loss
- Choked converging-nozzle equations, without an unchoked solution
- Thrust estimate excludes pressure thrust
- No TSFC or component efficiency model

## Current Simulator Capability

Completed:

- ✅ Atmosphere
- ✅ Freestream state
- ✅ Inlet
- ✅ Compressor
- ✅ Combustor
- ✅ Turbine
- ✅ Nozzle
- ✅ Mass flow rate
- ✅ Thrust

Next component:

- ➡ TSFC
