# Bingham Poiseuille Flow

## Physics

Flow of a Bingham viscoplastic fluid: flows only when stress exceeds yield stress tau_y. Unyielded plug zone in channel center.

## Analytical Solution

Shear zone: mu_p*du/dy = -G*(|y-H/2|-y_p)*sign(y-H/2), for |y-H/2|>y_p
Plug zone: u = const, for |y-H/2|<=y_p
y_p = tau_y/G (half-width of plug)

## Bingham Number

Bn = tau_y*H/(mu_p*U_char)

| Bn | tau_y | y_p/H | u_max | Regime |
|-----|-------|-------|-------|--------|
| 0 | 0 | 0 | 0.125 | Newtonian |
| 0.2 | 0.1 | 0.2 | 0.108 | Weak viscoplastic |
| 0.5 | 0.25 | 0.5 | 0.070 | Moderate |
| 0.8 | 0.4 | 0.8 | 0.022 | Strong |
| 0.98 | 0.49 | 0.98 | ~0 | Nearly solid |

## Reference Data

- profile_Bn*.csv -- u(y) for Bn=0,0.2,0.5,0.8,0.98
- integral.csv -- y_p, u_max, Q for all Bn

## References

1. Bird, R.B., Dai, G.C., Yarusso, B.J. "The rheology and flow of viscoplastic materials", Rev. Chem. Eng., 1(1), 1983. [DOI](https://doi.org/10.1515/revce-1983-0102)
2. Chhabra, R.P., Richardson, J.F. *Non-Newtonian Flow and Applied Rheology*, 2nd ed., 2008
