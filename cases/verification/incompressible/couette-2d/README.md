# Plane Couette Flow (2D)

## Physics

Fully developed shear-driven flow between two parallel plates. The bottom wall is stationary, the top wall moves at constant velocity U₀. Zero pressure gradient.

## Analytical Solution

u(y) = U₀ · y/H, v = 0, p = const

This is the simplest validation of viscous wall boundary conditions and shear stress computation.

## Boundary Conditions

| Boundary | Condition |
|----------|-----------|
| Inlet (x = 0)   | Periodic or inlet with linear profile |
| Outlet (x = L)  | Periodic or pressure outlet |
| Bottom wall     | No-slip: u = 0, v = 0 |
| Top wall        | Moving wall: u = U₀, v = 0 |

## Reference Data

- `reference/analytical/solution.csv`: u(y), v(y), p(y) at 101 points

## References

1. White, F.M. *Viscous Fluid Flow*, 3rd ed., McGraw-Hill, 2006
