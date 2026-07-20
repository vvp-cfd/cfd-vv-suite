# Comparison Methodology

## Error Norms

Standard norms of the difference between computed and reference fields are used.

### L1 (Mean Absolute Error)

```
E_L1 = (1/N) * sum|u_computed(i) - u_reference(i)|
```

Characterizes the average deviation.

### L2 (Root Mean Square Error, RMSE)

```
E_L2 = sqrt((1/N) * sum(u_computed(i) - u_reference(i))^2)
```

More sensitive to outliers. Recommended as the default.

### Linf (Maximum Error)

```
E_Linf = max|u_computed(i) - u_reference(i)|
```

Shows the worst-case local deviation.

### Relative L2

```
E_rel = E_L2(u_computed - u_reference) / E_L2(u_reference)
```

Normalized by the reference magnitude --- useful when comparing quantities of different scales (e.g., Cl, Cd).

## Point Matching

Computed and reference points are matched by nearest-neighbor coordinates. If grids are identical --- direct comparison. If grids differ --- interpolation is NOT performed (the user should output results at reference points or use `--auto-generate` for analytical cases).

### When you get unexpected errors

If your grid differs from the reference and `--auto-generate` is not used:

- The tool matches each computed point to the nearest reference point.
- A warning is shown when point counts differ significantly.
- L1/L2 norms will be larger than expected because fewer points are sampled.
- **Solution**: either match the reference grid resolution, or use `--auto-generate` to produce reference data on your grid.

## Grid Convergence Index (GCI)

Based on Roache's (1994, 1998) methodology and ASME V&V 20:

1. Run simulations on 3+ mesh levels: h1 (fine), h2 (medium), h3 (coarse)
2. Compute refinement ratios: r21 = h2/h1, r32 = h3/h2
3. Estimate observed order: p = ln((f3-f2)/(f2-f1)) / ln(r)
4. Compute GCI: GCI21 = Fs * |(f2-f1)/f1| / (r21^p - 1)

Safety factor Fs = 1.25 (for 3 meshes), 3.0 (for 2 meshes).

### What GCI tells you

- **p close to expected** (e.g., 2 for central schemes): your solver achieves theoretical accuracy
- **p < expected**: possible bug in discretization or boundary conditions
- **GCI < few percent**: the fine-mesh solution is within the asymptotic range
- **GCI large**: you need a finer mesh

## Pass/Fail Criteria

- Passed: E <= tolerance (from case.yaml)
- Failed: E > tolerance

## Choosing Tolerances

Tolerance should be set **larger than the expected discretization error** on the target mesh. A tolerance that is too tight will cause false failures; one that is too loose will mask real regressions.

### Effect of mesh resolution

For a second-order accurate scheme on a uniform mesh of size N (N×N in 2D), the discretization error in the L2 norm scales roughly as:

```
E_L2 ≈ C · (L/N)²
```

where L is the domain length scale and C is a problem-dependent constant (typically 1–50 for smooth flows). Halving the mesh spacing (doubling N) reduces the error by approximately 4×.

### Rule-of-thumb estimates

| Mesh N² | Estimated L2 range (smooth flow, 2nd order) | Typical usage |
|---------|---------------------------------------------|--------------|
| 32²     | 0.1 – 0.5                                   | Coarse scoping |
| 64²     | 0.02 – 0.1                                  | Quick CI checks |
| 128²    | 0.005 – 0.03                                | Standard verification |
| 256²    | 0.001 – 0.008                               | High-precision |

### Recommendations by case type

| Case type | Typical L2 tolerance | Notes |
|-----------|---------------------|-------|
| Analytical solution, fine mesh (256²+) | 1e-6 – 1e-4 | Machine precision possible on matching grid |
| MMS with source terms | 1e-5 – 1e-3 | Depends on quadrature accuracy |
| Analytical, moderate mesh (128²) | 1e-4 – 1e-2 | 2nd-order schemes on uniform grid |
| Analytical, coarse mesh (64²) | 0.01 – 0.1 | Allow for discretization error |
| Experimental data | 1e-3 – 1e-1 | Limited by measurement uncertainty |
| DNS reference data | 0.01 – 0.1 | Limited by statistical convergence |

### Calibrating for your mesh

1. **Run a mesh convergence study** on 3 levels (e.g., 32², 64², 128²).
2. Compute the GCI (see above) to estimate the numerical error on the finest mesh.
3. Set the **L2 tolerance to 2–3× the estimated error**. This guards against regressions without being overly strict.
4. For a single mesh, compare with a known reference (e.g., a published benchmark) and set the tolerance 2× higher than your observed error.

### Example: Lid-driven cavity at Re=100

| Mesh | Observed L2 (vs Ghia 129²) | Recommended tolerance |
|------|---------------------------|----------------------|
| 32²  | ≈ 0.08                    | 0.1 – 0.2 |
| 64²  | ≈ 0.03                    | 0.05 – 0.1 |
| 128² | ≈ 0.005                   | 0.005 – 0.01 |

The current `lid-driven-cavity/case.yaml` sets L2 = 1e-3, which is appropriate for 129² but too tight for the default 64² mesh used in the OpenFOAM template. Bin the tolerance to your actual mesh resolution.

## References

1. Roache, P.J. "Perspective: A Method for Uniform Reporting of Grid Refinement Studies", J. Fluids Eng., 116, 405-413, 1994. [DOI](https://doi.org/10.1115/1.2910291)
2. ASME V&V 20-2009, "Standard for Verification and Validation in Computational Fluid Dynamics and Heat Transfer". [ResearchGate](https://www.researchgate.net/publication/277711647_ASME_VV_20-2009_Standard_for_Verification_and_Validation_in_Computational_Fluid_Dynamics_and_Heat_Transfer_VV20_Committee_Chair_and_principal_author)
3. Oberkampf, W.L. & Roy, C.J. *Verification and Validation in Scientific Computing*, Cambridge, 2010. [DOI](https://doi.org/10.1017/CBO9780511760396)
