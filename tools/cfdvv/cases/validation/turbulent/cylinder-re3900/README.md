# Cylinder Re=3900 (turbulent wake)

## Physics

Subcritical turbulent flow past a circular cylinder. The boundary layer is laminar at separation (theta_sep~88 deg) but transitions in the free shear layer, producing a fully turbulent wake. This is the most-studied Re for LES/DNS validation.

## Expected Quantities

| Quantity | Value | Source |
|----------|-------|--------|
| Cd_mean | 0.99 (+-0.05) | Norberg |
| Strouhal | 0.215 (+-0.005) | Norberg |
| Cp_base | -1.04 (+-0.05) | Norberg |
| Lw/D | 1.03 (+-0.10) | Parnaudeau |
| theta_sep | 88 (+-2) deg | Ong & Wallace |

## Reference Data

- integral.csv -- key integral quantities
- wake_profile_x*.csv -- velocity profiles in wake at x/D stations

## References

1. Ong, L. & Wallace, J. "The velocity field of the turbulent very near wake of a circular cylinder", Exp. Fluids, 20, 1996. [DOI](https://doi.org/10.1007/BF00189383)
2. Norberg, C. "Fluctuating lift on a circular cylinder: review and new measurements", J. Fluids Struct., 17, 2003. [DOI](https://doi.org/10.1016/S0889-9746(02)00099-3)
3. Parnaudeau, P. et al. "Experimental and numerical studies of the flow over a circular cylinder at Re=3900", Phys. Fluids, 20, 2008. [DOI](https://doi.org/10.1063/1.2957018)
