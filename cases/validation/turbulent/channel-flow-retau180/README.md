# Turbulent Channel Flow (Re_tau=180)

## Physics

Fully developed turbulent flow between two parallel plates. Friction Reynolds number Re_tau = u_tau*h/nu = 180, where u_tau is friction velocity and h is half-channel height. Bulk Reynolds number Re_b = 2800.

## DNS Reference

Moser, Kim, Mansour (1999) -- spectral DNS with 128x129x128 grid (after dealiasing).

## Geometry

Channel: Lx x Ly x Lz = 4*pi*h x 2h x 4/3*pi*h. Periodic in x and z.

## Boundary Conditions

| Boundary | Condition |
|----------|-----------|
| x, z | Periodic |
| y = -h, +h | No-slip walls |

## Expected Quantities

| Quantity | Description |
|----------|-------------|
| u+ | Mean velocity in wall units: u/u_tau vs y+ = y*u_tau/nu |
| u_rms+, v_rms+, w_rms+ | Turbulence intensities |
| -uv+ | Reynolds shear stress |
| Cf = 2*tau_w/(rho*Ub^2) = 0.00818 | Skin friction coefficient |

## Reference Data

- mean_profiles.csv -- u+, u_rms+, v_rms+, w_rms+, -uv+ vs y+
- integral.csv -- Re_tau, Re_bulk, Cf, Ub+

## References

1. Moser, R.D., Kim, J., Mansour, N.N. "Direct numerical simulation of turbulent channel flow up to Re_tau=590", Phys. Fluids, 11(4), 943-945, 1999. [DOI](https://doi.org/10.1063/1.869966)
2. Kim, J., Moin, P., Moser, R.D. "Turbulence statistics in fully developed channel flow at low Reynolds number", J. Fluid Mech., 177, 133-166, 1987. [DOI](https://doi.org/10.1017/S0022112087000892)
