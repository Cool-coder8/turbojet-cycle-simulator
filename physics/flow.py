import math

def area_from_design_mach(mdot,Pt,Tt,M,gamma,R):
    """
    Given:
        mdot
        Pt
        Tt
        design Mach number

    Calculates:
        T
        P
        rho
        V
        Area

    Returns:
        area
    """

    # Static temperature
    T = Tt / (1 + ((gamma - 1) / 2) * M**2)

    # Static pressure
    P = Pt / (
        (1 + ((gamma - 1) / 2) * M**2)
        ** (gamma / (gamma - 1))
    )

    # Density
    rho = P / (R * T)

    # Velocity
    V = M * math.sqrt(gamma * R * T)

    # Continuity equation
    area = mdot / (rho * V)

    return area

def area_from_mach(
    mdot: float,
    Pt: float,
    Tt: float,
    M: float,
    gamma: float = 1.4,
    R: float = 287.0,
) -> float:
  """Design mode: Given a target Mach number, returns the physical area (m^2)."""
  flow_func = M * (1.0 + 0.5 * (gamma - 1.0) * M**2) ** (
      -(gamma + 1.0) / (2.0 * (gamma - 1.0))
  )
  return (mdot * math.sqrt(Tt)) / (Pt * math.sqrt(gamma / R) * flow_func)


def solve_station_flow(station, mdot: float, area: float):
  """Off-design mode: Given fixed physical area (m^2), solves Mach via bisection

    and populates static T, P, rho, airvelocity, and area on the station.
    """
  gamma = station.gamma
  R = station.R

  target = (
      (mdot * math.sqrt(station.Tt))
      / (station.Pt * area)
      * math.sqrt(R / gamma)
  )
  choke_limit = ((gamma + 1.0) / 2.0) ** (-(gamma + 1.0) / (2.0 * (gamma - 1.0)))

  if target >= choke_limit * 0.999999:
    station.M = 1.0
  else:
    lo, hi = 0.0, 1.0
    for _ in range(50):
      mid = 0.5 * (lo + hi)
      val = mid * (1.0 + 0.5 * (gamma - 1.0) * mid**2) ** (
          -(gamma + 1.0) / (2.0 * (gamma - 1.0))
      )
      if val < target:
        lo = mid
      else:
        hi = mid
    station.M = 0.5 * (lo + hi)

  isen = 1.0 + 0.5 * (gamma - 1.0) * (station.M**2)
  station.T = station.Tt / isen
  station.P = station.Pt * (isen ** (-gamma / (gamma - 1.0)))
  station.rho = station.P / (R * station.T)
  station.a = math.sqrt(gamma * R * station.T)
  station.airvelocity = station.M * station.a
  station.area = area
