# Turbulent Flat Plate Boundary Layer (Wieghardt)

## Physics

Fully turbulent boundary layer on a smooth flat plate at zero pressure gradient. The canonical test case for RANS turbulence models.

## Experimental Data

Wieghardt (1947) --- wind tunnel measurements, Re_theta up to 20000.
Mean velocity profile u+(y+) at Re_theta=7080 (momentum-thickness Reynolds number).

## Law of the Wall

- Viscous sublayer: u+ = y+ (y+ < 5)
- Buffer layer: 5 < y+ < 30
- Log layer: u+ = (1/kappa)*ln(y+) + B, kappa=0.41, B=5.0 (y+ > 30)

## Expected Quantities

| Quantity | Value |
|----------|-------|
| Cf at Re_theta=7080 | ~0.0029 |
| Shape factor H=delta*/theta | ~1.4 |
| u+ at y+=1000 | ~22 |

## Reference Data

- cf_vs_retheta.csv -- Cf(Re_theta) measurements
- uplus_profile.csv -- u+(y+) at Re_theta=7080
- law_of_wall.csv -- reference lines for u+=y+, log law

## References

1. Wieghardt, K. (1947). In Coles, D.E. & Hirst, E.A. (eds.), *Computation of Turbulent Boundary Layers*, Vol. II, AFOSR-IFP-Stanford, 1968. [NTRL](https://ntrl.ntis.gov/NTRL/dashboard/searchResults/titleDetail/AD696082.xhtml)
2. Coles, D. "The law of the wake in the turbulent boundary layer", J. Fluid Mech., 1, 191-226, 1956. [DOI](https://doi.org/10.1017/S0022112056000135)
