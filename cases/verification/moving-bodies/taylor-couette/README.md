# Taylor-Couette Flow

## Physics

Flow between two concentric rotating cylinders. Inner cylinder rotates at Omega1, outer cylinder stationary. Below critical Taylor number Ta_c=1708: steady circular Couette flow.

## Analytical Solution

u_theta(r) = A*r + B/r

A = -Omega1 * eta^2 / (1 - eta^2)
B = Omega1 * R1^2 / (1 - eta^2)
u_r = 0 (no radial flow)

## Configuration

| Parameter | Value |
|-----------|-------|
| R1 | 1.0 (inner) |
| R2 | 2.0 (outer) |
| Omega1 | 1.0 |
| Omega2 | 0.0 (stationary) |
| eta | 0.5 |

## Taylor Instability

Ta = 4*Re^2*(1-eta)/(1+eta)

- Ta < 1708: steady laminar Couette
- Ta > 1708: Taylor vortices (toroidal rolls)
- Tests rotating wall BC and centrifugal instability

## Reference Data

- velocity_profile.csv -- u_theta(r)
- integral.csv -- geometry, Re, Ta

## References

1. Taylor, G.I. "Stability of a viscous liquid contained between two rotating cylinders", Phil. Trans. R. Soc. Lond. A, 223, 289-343, 1923. [DOI](https://doi.org/10.1098/rsta.1923.0008)
2. Chandrasekhar, S. *Hydrodynamic and Hydromagnetic Stability*, Oxford, 1961
