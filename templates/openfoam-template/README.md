# OpenFOAM Case Template

This directory contains a template for running cfd-vv-suite cases with OpenFOAM.

## Usage

1. Copy the relevant case directory from cfd-vv-suite
2. Create OpenFOAM case files following this template
3. Run the simulation
4. Export results as CSV using OpenFOAM's `sample` utility
5. Compare with `cfdvv compare`

## Typical OpenFOAM structure

```
case/
+-- 0/               # Initial/boundary conditions
|   +-- U
|   +-- p
|   +-- ...
+-- constant/
|   +-- transportProperties
|   +-- turbulenceProperties
|   +-- polyMesh/
+-- system/
|   +-- controlDict
|   +-- fvSchemes
|   +-- fvSolution
|   +-- sampleDict      # For exporting results
+-- Allrun              # Run script
```

## Exporting Results

Create a `system/sampleDict`:

```
sampleDict
{
    type sets;
    libs ("libsampling.so");
    interpolationScheme cellPoint;
    setFormat csv;

    sets
    (
        centerline
        {
            type uniform;
            axis y;
            start (0.5 0.0 0.005);
            end   (0.5 1.0 0.005);
            nPoints 101;
        }
    );
}
```

Then: `postProcess -func sampleDict [-time <time>]`

## Comparing Results

```bash
cfdvv compare cases/verification/incompressible/poiseuille-2d \
    --result postProcessing/sets/<time>/centerline_U.xy \
    --norm L2 --plot
```

## Reference Solvers by Case

| Case | Recommended OpenFOAM Solver |
|------|---------------------------|
| poiseuille-2d | icoFoam, simpleFoam |
| couette-2d | icoFoam, simpleFoam |
| taylor-green-vortex-2d | icoFoam |
| lid-driven-cavity | icoFoam |
| sod-shock-tube | rhoCentralFoam, sonicFoam |
| manufactured-ns-2d | icoFoam (with fvOptions source) |
