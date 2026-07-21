# Taylor-Green Vortex (3D)

## Physics

Classic 3D vortex array in a triply-periodic domain [0,2pi]^3.

## Analytical Solution (t=0)

u = sin(x)cos(y)cos(z)
v = cos(x)sin(y)cos(z)
w = -2cos(x)cos(y)sin(z)

Exactly divergence-free. Nonlinear term does NOT cancel with grad(p) --
this is an initial condition, not an exact time-dependent solution.

## Boundary Conditions

Triply periodic.

## Reference Data

- solution_t0.csv -- fields on 21^3 grid
- slice_y_mid.csv -- u,v,w on xz-plane at y=pi
