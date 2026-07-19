# Plane Poiseuille Flow (2D)

## Physics

Fully developed laminar flow in a 2D channel driven by a constant pressure gradient. The flow is unidirectional (u = u(y), v = 0) with a parabolic velocity profile.

## Governing Equations

- Continuity: ∂u/∂x + ∂v/∂y = 0
- Navier-Stokes (steady, incompressible):
  - x-momentum: 0 = -∂p/∂x + mu·∂^2u/∂y^2
  - y-momentum: 0 = -∂p/∂y

## Analytical Solution

For a channel of height H with dynamic viscosity mu and constant pressure gradient G = -dp/dx:

```
u(y) = (G / (2mu)) · y · (H - y)
v(y) = 0
p(x) = p₀ - G·x
```

Maximum velocity: u_max = G·H^2/(8mu) at y = H/2

## Geometry

- Domain: [0, L] x [0, H], where L = 10H
- Channel aspect ratio L/H >= 10 to ensure fully developed flow

## Boundary Conditions

| Boundary | Condition |
|----------|-----------|
| Inlet (x = 0)   | Velocity inlet: u = parabolic profile |
| Outlet (x = L)  | Pressure outlet: p = 0 |
| Bottom wall (y = 0) | No-slip: u = 0, v = 0 |
| Top wall (y = H)    | No-slip: u = 0, v = 0 |

## Expected Quantities

| Quantity | Type | Location | Norm | Tolerance |
|----------|------|----------|------|-----------|
| u        | profile | x = L/2 (mid-channel) | L2 | 1e-6 |
| v        | profile | x = L/2 | L2 | 1e-6 |

## Reference Data

- `reference/analytical/solution.csv`: u(y) profile at 101 points across the channel

## References

1. White, F.M. *Viscous Fluid Flow*, 3rd ed., McGraw-Hill, 2006
2. Batchelor, G.K. *An Introduction to Fluid Dynamics*, Cambridge, 1967
