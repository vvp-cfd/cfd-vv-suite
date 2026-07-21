# Taylor-Green Vortex (2D, decaying)

## Physics

Incompressible viscous flow in a doubly-periodic domain [0, 2π]^2. The initial velocity field is a periodic array of counter-rotating vortices that decay exponentially due to viscous dissipation.

## Analytical Solution

```
u(x,y,t) = -cos(x)·sin(y)·exp(-2nut)
v(x,y,t) =  sin(x)·cos(y)·exp(-2nut)
p(x,y,t) = -¼·(cos(2x) + cos(2y))·exp(-4nut)
```

This is an exact solution of the incompressible Navier-Stokes equations. The nonlinear convective terms cancel identically: u·gradu + gradp = 0.

## Purpose

- **Spatial accuracy**: compare at t = 0 (purely kinematic test, no time-stepping error)
- **Temporal accuracy**: compare at t = 0.5 with fixed fine mesh, varying Deltat
- **Order of convergence**: run on 3+ mesh levels (e.g., 32^2, 64^2, 128^2)

## Boundary Conditions

Periodic in both x and y directions.

| Boundary | Condition |
|----------|-----------|
| All      | Periodic  |

## Expected Quantities

| Quantity | Type | t | Norm |
|----------|------|---|------|
| u, v, p  | field | t=0, t=0.5 | L2 |

## Reference Data

- `reference/analytical/solution_t0.csv`: Fields at t = 0 on 101^2 grid
- `reference/analytical/solution_t0.5.csv`: Fields at t = 0.5 on 101^2 grid

## References

1. Taylor, G.I. & Green, A.E. "Mechanism of the production of small eddies from large ones", Proc. R. Soc. Lond. A, 158, 499-521, 1937
2. Chorin, A.J. "Numerical solution of the Navier-Stokes equations", Math. Comp., 22, 745-762, 1968. [DOI](https://doi.org/10.1090/S0025-5718-1968-0242392-2)
