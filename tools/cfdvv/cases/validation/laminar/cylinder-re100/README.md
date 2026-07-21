# UnsteadyFlow Past a Circular Cylinder (Re=100)

## Physics

Unsteady laminar flow past a circular cylinder of diameter D. Von Karman vortex street develops in the wake, characterized by the Strouhal number St = f*D/U_inf.

## Geometry

Cylinder of diameter D=1 centered at origin. Domain: [-15, 30] x [-15, 15] (recommended).

## Boundary Conditions

| Boundary | Condition |
|----------|-----------|
| Inlet | Uniform: u=U_inf, v=0 |
| Outlet | Convective or pressure outlet |
| Top/Bottom | Far-field or slip wall |
| Cylinder | No-slip wall |

## Expected Quantities

| Quantity | Value | Source |
|----------|-------|--------|
| Cd | 1.35+-0.02 | Norberg, Dennis & Chang |
| St | 0.165+-0.005 | Norberg, Williamson |
| Cl_rms | 0.23+-0.02 | Norberg |

## Reference Data

- integral.csv -- key integral quantities
- surface_cp.csv -- pressure coefficient distribution on cylinder surface

## References

1. Tritton, D.J. "Experiments on the flow past a circular cylinder at low Reynolds numbers", J. Fluid Mech., 6, 547-567, 1959. [DOI](https://doi.org/10.1017/S0022112059000829)
2. Dennis, S.C.R. & Chang, G.-Z. "Numerical solutions for steady flow past a circular cylinder at Reynolds numbers up to 100", J. Fluid Mech., 42, 471-489, 1970. [DOI](https://doi.org/10.1017/S0022112070001428)
3. Grove, A.S., Shair, F.H., Petersen, E.E., Acrivos, A. "An experimental investigation of the steady separated flow past a circular cylinder", J. Fluid Mech., 19, 60-80, 1964. [DOI](https://doi.org/10.1017/S0022112064000544)
