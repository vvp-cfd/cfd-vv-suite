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

Tolerance depends on the case type:
- Analytical solution: L2 ~ 1e-6
- MMS (with source terms): L2 ~ 1e-5
- Experimental data: L2 ~ 1e-3 to 1e-1 (limited by measurement error)
- DNS data: L2 ~ 0.05 (limited by statistical convergence)

## References

1. Roache, P.J. "Perspective: A Method for Uniform Reporting of Grid Refinement Studies", J. Fluids Eng., 116, 405-413, 1994. [DOI](https://doi.org/10.1115/1.2910291)
2. ASME V&V 20-2009, "Standard for Verification and Validation in Computational Fluid Dynamics and Heat Transfer". [ResearchGate](https://www.researchgate.net/publication/277711647_ASME_VV_20-2009_Standard_for_Verification_and_Validation_in_Computational_Fluid_Dynamics_and_Heat_Transfer_VV20_Committee_Chair_and_principal_author)
3. Oberkampf, W.L. & Roy, C.J. *Verification and Validation in Scientific Computing*, Cambridge, 2010. [DOI](https://doi.org/10.1017/CBO9780511760396)
