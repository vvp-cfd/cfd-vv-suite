# Natural Convection in a Square Cavity

## Physics

Buoyancy-driven flow of air (Pr=0.71) in a square cavity. Left wall heated (T=1), right wall cooled (T=0), horizontal walls adiabatic. The Boussinesq approximation is used.

## Governing Equations

- Continuity: div(u) = 0
- Momentum: (u.grad)u = -grad(p)/rho0 + nu*laplacian(u) + g*beta*(T-T0)*j
- Energy: u.grad(T) = alpha*laplacian(T)

Ra = g*beta*DeltaT*L^3/(nu*alpha), Pr = nu/alpha = 0.71

## Geometry

Square [0,1] x [0,1].

## Boundary Conditions

| Boundary | Velocity | Temperature |
|----------|----------|-------------|
| Left (x=0) | No-slip | T = 1 (hot) |
| Right (x=1) | No-slip | T = 0 (cold) |
| Bottom (y=0) | No-slip | dT/dy = 0 (adiabatic) |
| Top (y=1) | No-slip | dT/dy = 0 (adiabatic) |

## Expected Quantities

| Quantity | Ra=1e3 | Ra=1e4 | Ra=1e5 | Ra=1e6 |
|----------|--------|--------|--------|--------|
| Nu_mean | 1.118 | 2.243 | 4.519 | 8.800 |
| Nu_max (y) | 1.505 (0.092) | 3.528 (0.143) | 7.717 (0.081) | 17.925 (0.038) |
| u_max (x) | 3.649 (0.813) | 16.178 (0.823) | 34.730 (0.855) | 64.630 (0.850) |
| v_max (y) | 3.697 (0.178) | 19.617 (0.119) | 68.590 (0.066) | 219.36 (0.038) |

## Reference Data

- integral_quantities.csv -- Nu and velocity extrema for all Ra
- profiles_Ra1e5.csv -- T(x) and u(x) at mid-height y=0.5, Ra=1e5
- profiles_v_Ra1e5.csv -- v(y) at mid-width x=0.5, Ra=1e5

## References

1. de Vahl Davis, G. "Natural convection of air in a square cavity: a bench mark numerical solution", Int. J. Numer. Methods Fluids, 3, 249-264, 1983. [DOI](https://doi.org/10.1002/fld.1650030305)
