# Double Mach Reflection

## Physics

A planar Mach 10 shock in air (gamma=1.4) hits a 30-degree ramp. The shock is initially at x=1/6 and propagates rightward. When it hits the ramp, complex reflection patterns form: Mach stem, incident and reflected shocks, contact discontinuity. At t=0.2 the characteristic "double Mach" structure is visible.

## Initial Conditions (pre-shock/post-shock)

Pre-shock (x > 0.5): rho=1.4, u=0, v=0, p=1.0
Post-shock (x < 0.5+ y/sqrt(3)/3): rho=8.0, u=8.25*cos(30deg), v=-8.25*sin(30deg), p=116.5

## Geometry

Domain: [0,4] x [0,1]. Reflecting wedge starts at x=1/6.

## Boundary Conditions

| Boundary | Condition |
|----------|-----------|
| Left | Post-shock inflow |
| Right | Outflow (extrapolation) |
| Top (y=1) | Time-dependent: shock propagation |
| Bottom | Reflecting for x>1/6, inflow for x<1/6 |

## Expected Features at t=0.2

- Maximum density ~ 20.9
- Triple point y-coordinate ~ 0.42
- Two Mach stems visible
- Kelvin-Helmholtz instability along contact surface

## Reference Data

key_features.csv -- characteristic values at t=0.2

## References

1. Woodward, P., Colella, P. "The numerical simulation of two-dimensional fluid flow with strong shocks", J. Comput. Phys., 54, 115-173, 1984. [DOI](https://doi.org/10.1016/0021-9991(84)90142-6)
