# Beltrami Flow (3D, exact steady NS)

## Physics

Exact steady solution of 3D incompressible Navier-Stokes with nontrivial velocity, pressure, and convective terms. Beltrami property: curl(u) = u.

## Analytical Solution

Domain: [0,2pi]^3, periodic, nu = 1.

u = sin(y) - cos(z)
v = sin(z) - cos(x)
w = sin(x) - cos(y)
p = -(sin(x)cos(y) + sin(y)cos(z) + sin(z)cos(x))

## Key Properties

- Divergence-free: div(u) = 0
- Beltrami: curl(u) = u
- Convective-pressure balance: (u.grad)u = -grad(p)

One of the rare exact steady 3D solutions with all terms active.

## Boundary Conditions

Triply periodic in x, y, z.

## Reference Data

solution.csv -- u,v,w,p on 21^3 grid

## References

1. Ethier, C.R. and Steinman, D.A. "Exact fully 3D Navier-Stokes solutions for benchmarking", Int. J. Numer. Methods Fluids, 19(5), 369-375, 1994
