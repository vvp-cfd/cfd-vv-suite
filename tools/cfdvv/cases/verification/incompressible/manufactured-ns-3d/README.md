# Manufactured Solution -- 3D Navier-Stokes

## Physics

Full 3D MMS for rigorous code verification. All terms active: convection, diffusion, pressure gradient in all three directions.

## Manufactured Solution (divergence-free)

Domain: [0,1]^3, nu = 0.1

u = sin(pi*x)cos(pi*y)cos(pi*z)
v = cos(pi*x)sin(pi*y)cos(pi*z)
w = -2cos(pi*x)cos(pi*y)sin(pi*z)
p = sin(pi*x)sin(pi*y)sin(pi*z)

## Source Terms

The solution does NOT satisfy NS equations without forcing. Source terms S_u, S_v, S_w are computed analytically and provided in source_terms.csv.

## Boundary Conditions

All boundaries: Dirichlet from manufactured solution.

## Verification Procedure

1. Generate meshes: 11^3, 21^3, 41^3
2. Add source terms to momentum equations
3. Compare u,v,w,p against reference
4. Compute observed order: p = log(E_h / E_{h/2}) / log(2)

## Reference Data

- solution.csv -- u,v,w,p on 21^3 grid
- source_terms.csv -- S_u,S_v,S_w on 21^3 grid
