# Oldroyd-B 4:1 Planar Contraction

## Physics

Creeping viscoelastic flow (Re=0) through a 4:1 planar contraction. The Oldroyd-B constitutive equation models a constant-viscosity elastic fluid. The upstream corner vortex grows with Weissenberg number We.

## Geometry

Inlet channel: height 4*H2, length 20*H2
Contraction: 4:1 ratio at x=0
Outlet channel: height H2, length 20*H2

## Key Parameters

| We | X_R/H2 | Description |
|----|--------|-------------|
| 0 | 1.48 | Newtonian (no elasticity) |
| 1 | 1.85 | Weak elasticity |
| 2 | 2.15 | Moderate |
| 3 | 2.50 | Strong elasticity |

beta = eta_s/(eta_s+eta_p) = 0.111 (solvent-dominated Boger fluid)

## Reference Data

- integral.csv -- vortex sizes, velocity overshoots
- centerline_velocity.csv -- u(x) along y=0

## References

1. Alves, M.A., Oliveira, P.J., Pinho, F.T. "Benchmark solutions for the flow of Oldroyd-B and PTT fluids in planar contractions", J. Non-Newtonian Fluid Mech., 101, 55-76, 2001. [DOI](https://doi.org/10.1016/S0377-0257(02)00191-X)
