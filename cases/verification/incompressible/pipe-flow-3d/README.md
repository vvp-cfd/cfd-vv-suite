# Hagen-Poiseuille Pipe Flow (3D)

## Physics

Laminar flow in a circular pipe. Axisymmetric parabolic profile u(r).

## Analytical Solution

u(r) = G*(R^2 - r^2) / (4*mu),  r = sqrt(y^2+z^2)
v = w = 0

Max centerline velocity: u_max = G*R^2/(4*mu)
Volume flow rate: Q = pi*G*R^4/(8*mu)

## Geometry

Rectangular domain containing a cylinder of radius R=0.5. Pipe axis along x. Tests Cartesian solver ability to represent curved boundaries.

## Boundary Conditions

| Boundary | Condition |
|----------|-----------|
| Inlet | Parabolic profile or periodic |
| Outlet | Pressure or periodic |
| Pipe wall r=R | No-slip |
| Spanwise | Periodic |

## Reference Data

- solution.csv -- u(y,z) at x=L/2 for points inside pipe
- profile_radial.csv -- u(r) radial profile, 101 points

## References

1. White, F.M. *Viscous Fluid Flow*, 3rd ed., McGraw-Hill, 2006
