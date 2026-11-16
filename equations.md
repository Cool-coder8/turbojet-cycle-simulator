# Turbojet Simulator Equation Reference

This document describes equations currently used by the simulator and identifies modeling assumptions and unfinished features.

Calculations use SI units and ideal-gas properties, with the following defaults on each `Station`:

| Symbol | Value | Meaning |
|---|---:|---|
| \(\gamma\) | 1.4 | Ratio of specific heats |
| \(c_p\) | 1004 J/(kg·K) | Specific heat at constant pressure |
| \(R\) | 287 J/(kg·K) | Gas constant for air |

## Atmosphere

`isa_atmosphere(altitude)` in `atmosphere.py` uses a single tropospheric lapse-rate layer:

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

The implementation rounds \(T\) and \(P\) to two decimal places and \(\rho\) to four. It does not validate the input altitude or implement higher ISA layers.

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

The user supplies inlet area \(A\). Freestream air mass flow is calculated as:

\[
\dot{m}_0 = \rho A V_a
\]

- \(\dot{m}_0\): freestream air mass flow rate (kg/s)
- \(\rho\): air density (kg/m³)
- \(A\): inlet area (m²)
- \(V_a\): freestream velocity (m/s)

The calculated mass flow is rounded to two decimal places and propagated through the inlet and compressor.

## Inlet / Station 0 → Station 2

The inlet copies total temperature and mass flow and applies inlet efficiency \(\eta_{\text{inlet}}\) to total pressure:

\[
T_{t2}=T_{t0},\qquad P_{t2}=\eta_{\text{inlet}}P_{t0},\qquad \dot{m}_2=\dot{m}_0
\]

This models stagnation-pressure recovery with unchanged total temperature.

## Compressor / Station 2 → Station 3

The compressor uses pressure ratio \(\pi_c\) and efficiency \(\eta_c\).

In the current `main.py` configuration, \(\pi_c=1.2\) and \(\eta_c=0.7\).

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

The current configuration uses \(\beta_b=1.0\), i.e. no total-pressure loss. Values below 1 represent a pressure loss in this model.

### Fuel-air ratio

\[
f = \frac{c_p(T_{t4}-T_{t3})}{\eta_b Q_R-c_pT_{t4}}
\]

- \(f\): fuel-to-air mass ratio
- \(\eta_b\): combustor efficiency
- \(Q_R\): fuel lower heating value

The current configuration uses \(\eta_b=1.0\). The code rounds \(f\) to eight decimal places.

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
P_8=P_{t5}\left(\frac{T_8}{T_{t5}}\right)^{\gamma/(\gamma-1)}
\]

\[
V_8=\sqrt{2c_p(T_{t5}-T_8)}
\]

This is the project's simplified efficiency-adjusted choked-nozzle model; it applies the isentropic pressure-temperature relation using the efficiency-adjusted temperature. Nozzle efficiency in the current configuration is 1.0.

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
\frac{\left((1+f)V_8^2 - V_a^2\right)/2}{fQ_R}
\]

### Propulsive and overall efficiency

\[
\eta_p = \frac{2V_a}{V_8+V_a}
\]

\[
\eta_o = \eta_{th}\eta_p
\]

These are simplified ideal-jet performance relations; pressure thrust is included in the thrust calculation but not in these efficiency formulas.

## Future Improvements

- Improve choking control for cases where the unchoked solution reaches \(M_8\ge1\)
- Improve the nozzle-loss model
- Add an optional nozzle pressure-recovery model
- Implement multi-layer ISA atmosphere
- Add engine configuration files
- Add checks for valid operating inputs and degenerate performance conditions

## Simplifying assumptions and limitations

- Ideal gas with constant \(\gamma\), \(c_p\), and \(R\)
- Single-layer tropospheric atmosphere intended for 0–11,000 m; input is not range-validated
- Inlet, compressor, combustor, turbine, and nozzle use simplified efficiency/pressure-ratio models
- Current run uses \(\eta_c=0.7\); inlet, combustor, turbine, and nozzle efficiencies and burner pressure ratio are 1.0
- Unchoked nozzle method is implemented, but warns rather than switching branches if \(M_8\ge1\)
- Thrust includes pressure thrust; other model simplifications remain
