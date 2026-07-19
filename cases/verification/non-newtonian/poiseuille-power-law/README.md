# Power-Law Poiseuille Flow

## Physics

Laminar flow of a power-law (Ostwald-de Waele) fluid in a channel. The viscosity depends on shear rate: mu_eff = K * |du/dy|^(n-1).

## Analytical Solution

u(y) = n/(n+1) * (G/K)^(1/n) * [(H/2)^(1+1/n) - |y-H/2|^(1+1/n)]

## Parameters

| n | Type | u_max (G=K=H=1) | Flow rate Q |
|---|------|-----------------|-------------|
| 0.5 | Shear-thinning (pseudoplastic) | 0.0625 | 0.0333 |
| 1.0 | Newtonian | 0.125 | 0.0833 |
| 1.5 | Shear-thickening (dilatant) | 0.1875 | 0.1467 |

Lower n -> flatter profile (more plug-like). Higher n -> more peaked.

## Boundary Conditions

| Boundary | Condition |
|----------|-----------|
| Channel walls (y=0, y=H) | No-slip |
| Inlet/Outlet | Periodic or profile inlet/pressure outlet |

## Reference Data

- profile_n0.5.csv -- u(y) for n=0.5 (shear-thinning)
- profile_n0.75.csv -- u(y) for n=0.75
- profile_n1.0.csv -- u(y) for n=1.0 (Newtonian)
- profile_n1.25.csv -- u(y) for n=1.25
- profile_n1.5.csv -- u(y) for n=1.5 (shear-thickening)
- integral.csv -- u_max, Q for all n

## References

1. Bird, R.B., Armstrong, R.C., Hassager, O. *Dynamics of Polymeric Liquids*, Vol. 1, 2nd ed., Wiley, 1987
2. Chhabra, R.P., Richardson, J.F. *Non-Newtonian Flow and Applied Rheology*, 2nd ed., Butterworth-Heinemann, 2008
