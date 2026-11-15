# Turbojet Simulator Equation Reference

This reference describes the equations currently implemented in the simulator, along with the simplifying assumptions and equations that are still pending.

All calculations use SI units. The model uses an ideal gas with constant properties:

| Symbol | Value | Meaning |
|---|---:|---|
| \(\gamma\) | 1.4 | Ratio of specific heats |
| \(c_p\) | 1004 J/(kg·K) | Specific heat at constant pressure |
| \(R\) | 287 J/(kg·K) | Gas constant for air |

These are the defaults assigned to each `Station`.

## Atmosphere

`isa_atmosphere(altitude)` in `atmosphere.py` calculates static properties using a single tropospheric lapse-rate layer:

\[
T = T_0 - Lh
\]

\[
P = P_0\left(\frac{T}{T_0}\right)^{g/(LR)}
\]

\[
\rho = \frac{P}{RT}
\]

- \(h\): altitude (m), intended range 0–11,000 m
- \(T_0 = 288.15\ \text{K}\): sea-level temperature
- \(P_0 = 101325\ \text{Pa}\): sea-level pressure
- \(L = 0.0065\ \text{K/m}\): temperature lapse rate
- \(g = 9.81\ \text{m/s}^2\)
- \(R = 287\ \text{J/(kg·K)}\)

The implementation rounds temperature and pressure to two decimal places and density to four. It uses this one layer only; higher ISA layers and explicit altitude-range validation are not implemented.

## Freestream / Station 0

`main.py` sets the flight Mach number and atmospheric state on Station 0, then calculates sound speed, flight velocity, and stagnation conditions.

### Speed of sound

\[
a = \sqrt{\gamma R T}
\]

- \(a\): speed of sound (m/s)
- \(T\): static temperature (K)
- \(R\): gas constant (J/(kg·K))
- \(\gamma\): ratio of specific heats

### Flight velocity

\[
V = M a
\]

- \(V\): freestream velocity (m/s)
- \(M\): freestream Mach number

### Stagnation temperature

\[
T_t = T\left(1 + \frac{\gamma - 1}{2}M^2\right)
\]

- \(T_t\): stagnation temperature (K)
- \(T\): static temperature (K)

### Stagnation pressure

\[
P_t = P\left(1 + \frac{\gamma - 1}{2}M^2\right)^{\gamma/(\gamma-1)}
\]

- \(P_t\): stagnation pressure (Pa)
- \(P\): static pressure (Pa)

Both stagnation relations assume steady, isentropic deceleration of a perfect gas with constant \(\gamma\). `main.py` rounds sound speed, velocity, and stagnation properties to two decimal places.

## Mass Flow Rate

Purpose: Determine the airflow entering the engine.

Equation:

\[
\dot{m} = \rho A V
\]

Variables:

- \(\dot{m}\): air mass flow rate (kg/s)
- \(\rho\): freestream air density (kg/m³)
- \(A\): user-provided inlet area (m²)
- \(V\): freestream velocity (m/s)

Physical meaning: Mass flow rate determines how much air enters the engine and directly affects the thrust estimate.

`main.py` calculates this at Station 0 and rounds it to two decimal places.

## Inlet / Station 0 → Station 2

`Inlet.calculate` implements an ideal inlet for total properties:

\[
T_{t2} = T_{t0}, \qquad P_{t2} = P_{t0}
\]

There is no pressure recovery factor or loss model. The inlet currently copies only total temperature and pressure; Station 2 static properties and velocity are not calculated.

## Compressor / Station 2 → Station 3

`Compressor` is initialized with compressor pressure ratio \(\pi_c\).

### Total pressure

\[
P_{t3} = \pi_c P_{t2}
\]

\[
\pi_c = \frac{P_{t3}}{P_{t2}}
\]

### Total temperature

\[
T_{t3} = T_{t2}\left(\frac{P_{t3}}{P_{t2}}\right)^{(\gamma-1)/\gamma}
= T_{t2}\pi_c^{(\gamma-1)/\gamma}
\]

This relation assumes isentropic compression and constant specific heats.

### Specific compressor work

\[
w_c = c_p(T_{t3} - T_{t2})
\]

- \(w_c\): specific compressor work (J/kg)
- \(c_p\): specific heat at constant pressure

The simulator calculates and stores `Compressor.work`; `main.py` reports it. This is a thermodynamic specific-work calculation, not a blade-speed/Euler calculation.

## Combustor / Station 3 → Station 4

Purpose: Add thermal energy to the airflow through fuel combustion.

Inputs:

- \(P_{t3}\)
- \(T_{t3}\)
- Desired \(T_{t4}\)

Outputs:

- \(P_{t4}\)
- \(T_{t4}\)
- Fuel-air ratio \(f\)

Assumptions:

- Ideal combustor with constant-pressure combustion
- \(P_{t4} = P_{t3}\)
- Constant \(c_p\) and \(\gamma\)
- Constant fuel heating value
- Combustor efficiency \(\eta_b = 1.0\) in the current run

`Combustor` is initialized with a specified turbine-inlet total temperature \(T_{t4}\) and combustion efficiency \(\eta_b\). It uses a Jet A lower heating value assumption:

\[
Q_R = 43 \times 10^6\ \text{J/kg}
\]

### Combustor exit temperature

\[
T_{t4} = \text{user-defined design value}
\]

The turbine inlet temperature is specified as a design parameter. The combustor adds sufficient fuel to reach this temperature.

### Combustor exit pressure

\[
P_{t4} = P_{t3}
\]

The model neglects combustor pressure loss.

### Fuel-air ratio

Equation:

\[
f = \frac{c_p(T_{t4} - T_{t3})}{\eta_b Q_R - c_p T_{t4}}
\]

Variables:

- \(f\): fuel-to-air mass ratio
- \(c_p\): specific heat capacity at constant pressure
- \(T_{t3}\), \(T_{t4}\): combustor inlet and exit total temperatures
- \(\eta_b\): combustion efficiency
- \(Q_R\): fuel lower heating value

Physical meaning: Fuel-air ratio determines how much fuel must be burned to raise the total temperature from \(T_{t3}\) to \(T_{t4}\).

Current assumptions:

- \(\eta_b = 1.0\)
- \(Q_R = 43 \times 10^6\ \text{J/kg}\)

This is a simplified steady-flow combustor balance using constant \(c_p\); it does not model variable gas properties or pressure loss. The calculated `f` is rounded to two decimal places when stored on Station 4.

Example result for altitude 10,000 m and flight Mach 0.8:

- \(T_{t4} = 1400\ \text{K}\)
- \(P_{t4} = 402974.5\ \text{Pa}\)
- \(f = 0.02\)

## Turbine / Station 4 → Station 5

Purpose: Extract work from the hot gas stream to drive the compressor.

Inputs:

- \(P_{t4}\)
- \(T_{t4}\)
- Compressor work

Outputs:

- \(P_{t5}\)
- \(T_{t5}\)

Assumptions:

- Ideal turbine
- Turbine work equals compressor work
- Constant \(c_p\) and \(\gamma\)
- No mechanical losses

`Turbine.calculate` receives Station 4 and the compressor's specific work. The current turbine model balances that work using the same constant \(c_p\), without accounting for fuel mass in the turbine flow.

### Turbine work balance

\[
w_t = w_c
\]

Equation used:

\[
c_p(T_{t4} - T_{t5}) = w_t
\]

Rearranged:

\[
T_{t5} = T_{t4} - \frac{w_t}{c_p}
\]

Physical meaning: The turbine extracts just enough work from the flow to drive the compressor.

### Turbine pressure ratio

\[
\frac{T_{t5}}{T_{t4}} = \left(\frac{P_{t5}}{P_{t4}}\right)^{(\gamma-1)/\gamma}
\]

Rearranged:

\[
P_{t5} = P_{t4}\left(\frac{T_{t5}}{T_{t4}}\right)^{\gamma/(\gamma-1)}
\]

Physical meaning: Pressure decreases as the turbine extracts energy from the flow. This is the isentropic total-pressure/total-temperature relation applied to turbine expansion. No turbine efficiency, cooling flow, or pressure-loss correction is included. Station 5 also receives the fuel-air ratio from Station 4.

Example results for altitude 10,000 m and flight Mach 0.8:

- \(T_{t5} = 1165.73\ \text{K}\)
- \(P_{t5} = 212286.49\ \text{Pa}\)

## Nozzle / Station 5 → Station 8

Purpose: Convert thermal and pressure energy into exhaust velocity.

Current assumption: Choked converging nozzle, with exit Mach number \(M_e=1\) when the main-program choking check passes.

### Critical pressure ratio

\[
\frac{P_t}{P_{\text{crit}}}
= \left(\frac{\gamma+1}{2}\right)^{\gamma/(\gamma-1)}
\]

For air with \(\gamma=1.4\):

\[
\frac{P_t}{P_{\text{crit}}} \approx 1.893
\]

The main program compares \(P_{t5}/P_{\text{ambient}}\) with this ratio. If the threshold is exceeded, it sets \(M_e=1\). There is no unchoked-flow branch; the nozzle calculation always uses the choked relations below.

### Exit temperature

\[
T_e = T_{t5}\left(\frac{2}{\gamma+1}\right)
\]

This follows from the stagnation-temperature relation at Mach 1.

### Exit pressure

\[
P_e = \frac{P_{t5}}{\left((\gamma+1)/2\right)^{\gamma/(\gamma-1)}}
\]

This is the exit pressure for the assumed choked converging nozzle.

### Exit velocity

\[
V_e = \sqrt{2c_p(T_{t5}-T_e)}
\]

This converts the drop in total temperature into kinetic energy using constant \(c_p\).

`Nozzle.calculate` stores \(T_e\), \(P_e\), and \(V_e\) in Station 8's static temperature, static pressure, and air-velocity fields, respectively, and copies \(f\) from Station 5. It does not set \(M_e\); `main.py` sets it to 1 only if the pressure-ratio check passes.

## Thrust

Purpose: Estimate net engine thrust from the change in stream momentum.

The momentum equation specified for the model is:

\[
F = (1+f)\dot{m}V_e - \dot{m}V_a
\]

Variables:

- \(F\): thrust (N)
- \(f\): fuel-air ratio
- \(\dot{m}\): air mass flow rate (kg/s)
- \(V_e\): nozzle exit velocity (m/s)
- \(V_a\): aircraft/freestream velocity (m/s)

Physical meaning: Thrust results from increasing the momentum of the airflow passing through the engine.

Implementation note: `main.py` currently evaluates

\[
F_{\text{code}} = (1+f)\dot{m}(V_e - V_a)
\]

which differs from the equation above. The current program output follows \(F_{\text{code}}\). Neither form includes pressure thrust.

## Future Improvements

- Pressure-thrust term
- TSFC
- Component efficiencies and pressure losses
- Nozzle efficiency
- Separate choked and unchoked nozzle solutions
- Extended ISA atmosphere layers above 11 km

## Simplifying assumptions and limitations

- Ideal-gas air with constant \(\gamma\), \(c_p\), and \(R\)
- Single-layer tropospheric atmosphere intended for 0–11,000 m
- Ideal inlet with no total-pressure loss
- Isentropic compressor and turbine relations
- No combustor pressure loss
- Turbine work balance neglects the added fuel mass
- No cooling bleed, afterburner, or component maps
- Choked converging-nozzle relations, with no unchoked exit-state solution
- Thrust estimate excludes pressure thrust
- No TSFC or component efficiency model
