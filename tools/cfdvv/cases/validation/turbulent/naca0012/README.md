# NACA 0012 Airfoil

## Physics

Turbulent flow over a symmetric NACA 0012 airfoil at low speed. Transition is tripped near the leading edge, resulting in fully turbulent boundary layers on both surfaces.

## Geometry

NACA 0012: y/c = 0.6*(0.2969*sqrt(x/c) - 0.1260*(x/c) - 0.3516*(x/c)^2 + 0.2843*(x/c)^3 - 0.1015*(x/c)^4)

Chord c = 1.0.

## Boundary Conditions

| Boundary | Condition |
|----------|-----------|
| Far-field | Riemann invariants |
| Airfoil surface | No-slip adiabatic wall |
| Wake cut | Internal boundary |

## Expected Quantities

| alpha | Cl | Cd |
|-------|-----|-----|
| 0 | 0.0 | ~0.008 |
| 10 | 1.05 | ~0.012 |
| 16 | 1.30 | ~0.025 |

## Reference Data

- cl_vs_alpha.csv -- lift curve Cl(alpha)
- cp_alpha0.csv -- surface Cp at alpha=0
- cp_alpha10.csv -- surface Cp at alpha=10 (upper/lower)
- integral.csv -- Cl, Cd, Cm at alpha=10

## References

1. McCroskey, W.J. "A critical assessment of wind tunnel results for the NACA 0012 airfoil", NASA TM-100019, 1987. [NTRS](https://ntrs.nasa.gov/citations/19880002254)
2. Gregory, N. & O'Reilly, C.L. "Low-Speed Aerodynamic Characteristics of NACA 0012 Aerofoil Section", NPL Aero Report 1308, 1970
3. Ladson, C.L. "Effects of Independent Variation of Mach and Reynolds Numbers on the Low-Speed Aerodynamic Characteristics of the NACA 0012 Airfoil Section", NASA TM-4074, 1988. [NTRS](https://ntrs.nasa.gov/citations/19880019495)
