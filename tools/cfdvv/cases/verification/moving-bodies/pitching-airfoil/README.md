# Pitching NACA 0012 (AGARD CT5)

## Physics

NACA 0012 airfoil undergoing forced pitching oscillation: alpha(t) = 2.5 + 2.5*sin(omega*t). Tests unsteady aerodynamics with moving boundaries. The lift coefficient forms a hysteresis loop due to dynamic stall effects.

## Parameters

| Parameter | Value |
|-----------|-------|
| Re | 4.8e6 |
| M | 0.3 |
| k | 0.081 |
| alpha_mean | 2.5 deg |
| alpha_amp | 2.5 deg |
| Pivot | x/c = 0.25 |

## Expected Results

- Cl hysteresis loop (upper branch ~0.55, lower branch ~0.03)
- Light dynamic stall: Cl slightly exceeds steady-state
- Cm hysteresis (small loop)

## Reference Data

integral.csv -- Cl_max, Cl_min, Cm_max, parameters

## References

1. AGARD-R-702. "Compendium of Unsteady Aerodynamic Measurements", 1982
2. McCroskey, W.J. et al. "Dynamic stall experiments on oscillating airfoils", AIAA J., 14(1), 1976
