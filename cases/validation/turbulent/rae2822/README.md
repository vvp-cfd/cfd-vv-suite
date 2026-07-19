# RAE 2822 Transonic Airfoil

## Physics

Transonic turbulent flow over the RAE 2822 supercritical airfoil. A shock wave forms on the upper surface, interacting with the turbulent boundary layer. The shock position and strength are sensitive tests for RANS turbulence models.

## Geometry

RAE 2822 airfoil, chord c=1.0. Supercritical profile designed for transonic cruise.

## Test Cases (Cook et al. 1979)

| Case | M | alpha | Re | Cl | Cd | Features |
|------|---|-------|------|-----|------|----------|
| 9 | 0.73 | 2.79 | 6.5e6 | 0.803 | 0.0168 | Weak shock at x/c~0.55 |
| 10 | 0.75 | 3.19 | 6.2e6 | 0.921 | 0.0254 | Strong shock, incipient separation |

## Boundary Conditions

| Boundary | Condition |
|----------|-----------|
| Far-field | Riemann invariants |
| Airfoil surface | No-slip adiabatic wall |

## Reference Data

- cp_case9.csv -- surface Cp for Case 9 (upper/lower surfaces)
- cp_case10.csv -- surface Cp for Case 10 (upper/lower surfaces)
- integral.csv -- Cl, Cd for both cases

## References

1. Cook, P.H., McDonald, M.A., Firmin, M.C.P. "Aerofoil RAE 2822 --- Pressure Distributions and Boundary Layer and Wake Measurements", AGARD Advisory Report No. 138, 1979
2. Haase, W. et al. (eds.) *EUROVAL --- An European Initiative on Validation of CFD Codes*, Vieweg, 1993
