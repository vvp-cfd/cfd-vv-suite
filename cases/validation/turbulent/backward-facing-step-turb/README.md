# Turbulent Backward-Facing Step

## Physics

Turbulent flow over a backward-facing step at Re_h=36000 (based on step height and freestream velocity). Expansion ratio 1.125. The flow separates, forming a turbulent recirculation bubble. RANS models typically underpredict reattachment length.

## Expected Quantities

| Quantity | Value |
|----------|-------|
| x_r/h | 6.26 (+-0.10) |
| Cf_min | -0.0011 (+-0.0002) |
| U_inf | 44.2 m/s |

## Boundary Conditions

| Boundary | Condition |
|----------|-----------|
| Inlet | Fully developed turbulent channel flow |
| Outlet | Pressure outlet |
| Walls | No-slip |
| Step face | No-slip |

## Reference Data

- integral.csv -- reattachment length, Cf_min
- cf_wall.csv -- Cf(x/h) along bottom wall

## References

1. Driver, D.M. & Seegmiller, H.L. "Features of a reattaching turbulent shear layer in divergent channel flow", AIAA J., 23(2), 163-171, 1985. [DOI](https://doi.org/10.2514/3.8890)
