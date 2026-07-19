# Oblique Shock (M=2.0, 10 deg wedge)

## Physics

Steady supersonic inviscid flow over a wedge. An attached oblique shock forms at the leading edge. The flow deflection angle (wedge half-angle) and upstream Mach number determine the shock angle via the theta-beta-M relation.

## Analytical Solution

For M_inf=2.0, theta=10 deg, gamma=1.4:

- Shock angle beta = 39.31 deg
- M2 = 1.640, p2/p1 = 1.866, rho2/rho1 = 1.706, T2/T1 = 1.093

## Geometry

Rectangular domain with wedge on lower boundary. Wedge starts at x=0 with angle 10 deg.

## Boundary Conditions

| Boundary | Condition |
|----------|-----------|
| Inlet (left) | Supersonic inflow: rho=1, u=M_inf*sqrt(gamma), v=0, p=1 |
| Outlet (right) | Supersonic outflow (extrapolation) |
| Top | Freestream or extrapolation |
| Wedge | Slip wall (inviscid) |

## Reference Data

- integral.csv -- shock relations
- wall_pressure.csv -- p/p_inf along wedge surface

## References

1. Anderson, J.D. *Fundamentals of Aerodynamics*, 6th ed., McGraw-Hill, 2017
