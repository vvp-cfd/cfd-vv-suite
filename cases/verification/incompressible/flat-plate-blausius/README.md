# Blasius Boundary Layer

## Physics

Laminar boundary layer on a flat plate at zero incidence. The flow is self-similar: u(x,y)/U_inf depends only on eta = y*sqrt(U_inf/(2*nu*x)).

## Analytical Solution

- Velocity: u/U_inf = f'(eta), where f''' + f*f'' = 0, f(0)=f'(0)=0, f'(inf)=1
- Boundary layer thickness: delta_99 = 5.0*x/sqrt(Re_x)
- Skin friction: Cf = tau_w/(0.5*rho*U_inf^2) = 0.664/sqrt(Re_x)
- Displacement thickness: delta* = 1.7208*x/sqrt(Re_x)
- Momentum thickness: theta = 0.664*x/sqrt(Re_x)

## Geometry

Flat plate: y=0, 0 <= x <= L=1. Domain: x in [-0.2, 1], y in [0, delta_99(L)*2].

## Boundary Conditions

| Boundary | Condition |
|----------|-----------|
| Inlet (x=0,y>0) | Uniform: u=U_inf, v=0 |
| Plate (y=0,x>=0) | No-slip |
| Symmetry (y=0,x<0) | Slip: v=0, du/dy=0 |
| Top | Far-field or symmetry |
| Outlet | Pressure outlet |

## Reference Data

- similarity_profile.csv -- self-similar profile f'(eta) vs eta
- integral.csv -- delta_99, Cf, delta*, theta for Re_x=1e4..1e6
- profile_x*.csv -- u(y) at x=0.2,0.5,0.8,1.0

## References

1. Blasius, H. "Grenzschichten in Flussigkeiten mit kleiner Reibung", Z. Math. Phys., 56, 1-37, 1908
2. White, F.M. *Viscous Fluid Flow*, 3rd ed., McGraw-Hill, 2006
