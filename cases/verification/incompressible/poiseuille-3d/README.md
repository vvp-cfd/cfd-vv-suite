# Square Duct Poiseuille Flow (3D)

## Physics

Fully developed laminar flow in a square duct driven by a constant pressure gradient dp/dx = -G. The flow is unidirectional u(y,z) with a characteristic saddle-shaped profile due to no-slip on all four walls.

## Analytical Solution

Series solution (Shah & London):

u(y,z) = (16a^2G/π⁴) · Σ_{n=1,3,5,...} Σ_{m=1,3,5,...} sin(nπξ/(2a))·sin(mπη/(2a)) / (nm(n^2+m^2))

where ξ = y + a, η = z + a, a = H/2. The series converges rapidly.

Maximum velocity: u_max = u(0,0) at duct center.

## Boundary Conditions

All walls: no-slip (u = v = w = 0).

| Boundary | Condition |
|----------|-----------|
| Inlet | Velocity or periodic |
| Outlet | Pressure or periodic |
| y = +/-a | No-slip wall |
| z = +/-a | No-slip wall |

## Reference Data

- `solution.csv`: u(y,z) on 31^2 cross-section at x = L/2
- `profile_centerline.csv`: u(y) profile at z = 0 (101 points)

## References

1. Shah, R.K. & London, A.L. *Laminar Flow Forced Convection in Ducts*, Academic Press, 1978
2. White, F.M. *Viscous Fluid Flow*, 3rd ed., McGraw-Hill, 2006
