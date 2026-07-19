# Sod Shock Tube

## Physics

The Riemann problem for the 1D Euler equations --- a classic test for compressible flow solvers. A diaphragm at x=0.5 separates two quiescent gas states at different densities and pressures. At t=0 the diaphragm is removed and three waves propagate: a rarefaction fan (left), a contact discontinuity, and a shock wave (right).

## Initial Conditions

| Region | rho | u | p |
|--------|---|---|---|
| Left (x < 0.5) | 1.0 | 0.0 | 1.0 |
| Right (x > 0.5) | 0.125 | 0.0 | 0.1 |

Ideal gas: γ = 1.4

## Features

- Rarefaction fan (smooth expansion wave)
- Contact discontinuity (density jump, constant p and u)
- Shock wave (sharp jump in all variables)

## Expected Quantities at t = 0.2

| Quantity | Features tested |
|----------|----------------|
| rho | Contact discontinuity, rarefaction |
| u | Shock speed, rarefaction |
| p | Shock strength |
| e = p/((γ-1)·rho) | Internal energy |

## Reference Data

`reference/analytical/solution_t0.2.csv` --- exact Riemann solver solution at 10 key positions

## References

1. Sod, G.A. "A Survey of Several Finite Difference Methods for Systems of Nonlinear Hyperbolic Conservation Laws", J. Comput. Phys., 27, 1-31, 1978. [DOI](https://doi.org/10.1016/0021-9991(78)90023-2)
2. Toro, E.F. *Riemann Solvers and Numerical Methods for Fluid Dynamics*, 3rd ed., Springer, 2009. [DOI](https://doi.org/10.1007/b79761)
