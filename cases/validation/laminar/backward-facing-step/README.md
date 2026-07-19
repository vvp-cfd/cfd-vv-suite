# Backward-Facing Step (Armaly et al.)

## Physics

Laminar flow over a backward-facing step. The sudden expansion causes flow separation and a recirculation bubble. The reattachment length x_r/h is a sensitive function of Re and the key validation metric.

## Geometry

Inlet channel: height h, length >= 5h (fully developed)
Step height: h
Outlet channel: height 1.94h, length >= 30h

## Boundary Conditions

| Boundary | Condition |
|----------|-----------|
| Inlet | Fully developed parabolic: u(y)=6*y*(h-y)/h^2 |
| Outlet | Pressure outlet or convective |
| Walls | No-slip |
| Step face | No-slip |

## Expected Quantities

| Re | x_r/h | Upper wall bubble |
|-----|-------|-------------------|
| 100 | 3.0+/-0.5 | x/h ~ 3.0 |
| 389 | 9.4+/-0.4 | --- |
| 800 | 13.8+/-0.5 | --- |

## Reference Data

- integral.csv -- reattachment lengths for Re=100,389,800
- profile_x*.csv -- u-velocity profiles at x/h stations for Re=389

## References

1. Armaly, B.F., Durst, F., Pereira, J.C.F., Schonung, B. "Experimental and theoretical investigation of backward-facing step flow", J. Fluid Mech., 127, 473-496, 1983. [DOI](https://doi.org/10.1017/S0022112083002839)
