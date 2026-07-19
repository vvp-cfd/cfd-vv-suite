# Natural Convection in a Cube

## Physics

Buoyancy-driven flow in a cubic cavity [0,1]^3. Left wall hot (T=1), right wall cold (T=0), other walls adiabatic. 3D effects: end-wall boundary layers at z=0, z=1 modify Nusselt number distribution.

## Reference (Fusegi et al. 1991)

| Ra | Nu_mean | Notes |
|-----|---------|-------|
| 1e4 | 2.10 | Weak convection |
| 1e5 | 4.45 | Moderate, steady |
| 1e6 | 8.60 | Strong, may be unsteady |

## Boundary Conditions

| Boundary | T | Velocity |
|----------|---|----------|
| x=0 | T=1 (hot) | No-slip |
| x=1 | T=0 (cold) | No-slip |
| y=0, y=1 | Adiabatic | No-slip |
| z=0, z=1 | Adiabatic | No-slip |

## Reference Data

integral.csv -- Nu_mean, velocity maxima for Ra=1e4,1e5,1e6

## References

1. Fusegi, T. et al. "A numerical study of 3D natural convection in a differentially heated cubical enclosure", Int. J. Heat Mass Transfer, 34(6), 1543-1557, 1991. [DOI](https://doi.org/10.1016/0017-9310(91)90295-P)
