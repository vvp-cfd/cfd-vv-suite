# Descriptive Case Name

## Physics

Brief description of the physical problem.

## Governing Equations

- Continuity: grad·u = 0
- Navier-Stokes: ∂u/∂t + (u·grad)u = -gradp/rho + nugrad^2u

## Geometry

Describe the domain geometry. Dimensions, boundaries.

## Boundary Conditions

| Boundary | Condition |
|----------|-----------|
| Inlet    | ...       |
| Outlet   | ...       |
| Walls    | ...       |

## Initial Conditions

...

## Reference Solution

Explain the reference solution and its source.

## Expected Quantities

| Quantity | Type | Norm | Tolerance |
|----------|------|------|-----------|
| u        | profile | L2 | 1e-6 |
| v        | profile | L2 | 1e-6 |

## References

1. Author, "Title", Journal, Year, DOI

## How to Cite

If you use this test case, please cite:

1. Puzikova, V. "cfd-vv-suite: Open Test Suite for CFD Verification and Validation", 2026. https://github.com/vvp-cfd/cfd-vv-suite
2. [Original reference from above]
