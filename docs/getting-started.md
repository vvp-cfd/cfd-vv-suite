# Quick Start

## 1. Install

```bash
# From PyPI (recommended — no clone needed)
pip install cfdvv

# Or from source (includes cases + OpenFOAM templates)
git clone https://github.com/vvp-cfd/cfd-vv-suite.git
cd cfd-vv-suite
pip install -e tools/
```

## 2. Browse Cases

```bash
cfdvv list                             # all cases
cfdvv list -c verification             # verification only
cfdvv list -c validation               # validation only
cfdvv list -c verification -t 3d       # verification, 3D
```

## 3. Inspect a Case

```bash
cfdvv info cases/verification/incompressible/poiseuille-2d
```

Shows: physics, boundary conditions, **mesh requirements** (including recommended resolution and grids for convergence study), expected quantities, and tolerances.

## 4. Run Your Solver

### Option A: Any solver -> CSV

1. Read the case `README.md` and `case.yaml` --- geometry, BCs, and **mesh requirements** (`mesh:`)
2. Generate a mesh per the recommended resolution
3. Run the simulation
4. Export results as CSV:

```csv
x, y, u, v, p
0.0, 0.0, 0.0, 0.0, 1.5
```

### Option B: OpenFOAM (ready-to-run cases)

Five cases have complete OpenFOAM directories with `blockMeshDict` and `Allrun`:

```bash
cd cases/verification/incompressible/poiseuille-2d/openfoam && ./Allrun
cd cases/verification/incompressible/couette-2d/openfoam && ./Allrun
cd cases/verification/incompressible/lid-driven-cavity/openfoam && ./Allrun
cd cases/verification/incompressible/taylor-green-vortex-2d/openfoam && ./Allrun
cd cases/verification/compressible/sod-shock-tube/openfoam    # blockMesh + rhoCentralFoam
```

### Option C: Generate analytical solution on your mesh

For cases with analytical solutions, use `scripts/generate_solution.py`:

```bash
python cases/verification/incompressible/poiseuille-2d/scripts/generate_solution.py <nx> <ny> output.csv
python cases/verification/incompressible/taylor-green-vortex-2d/scripts/generate_solution.py 64 output.csv
python cases/verification/incompressible/beltrami-flow-3d/scripts/generate_solution.py 21 beltrami.csv
```

## 5. Compare Results

### Verification (analytical)

```bash
cfdvv compare cases/verification/incompressible/poiseuille-2d \
    --result my_results.csv --norm L2 --plot
```

### Auto-generate reference on your grid

If your grid differs from the reference, use `--auto-generate`:

```bash
cfdvv compare cases/verification/incompressible/poiseuille-2d \
    --result my_results.csv --auto-generate --plot
```

For analytical cases, this runs `scripts/generate_solution.py` on-the-fly with your grid dimensions.
For MMS and experimental cases with CSV data, it falls back to nearest-neighbor matching.

### Validation (experimental/DNS)

```bash
cfdvv compare cases/validation/laminar/cylinder-re20 \
    --result my_results.csv --norm Relative_L2

cfdvv compare cases/validation/turbulent/channel-flow-retau180 \
    --result my_uplus_profile.csv --norm L2
```

### Expected errors when grid mismatch occurs

When comparing without `--auto-generate` and your grid doesn't match the reference:

```
Case: Plane Poiseuille Flow (poiseuille-2d)
Result: my_coarse_results.csv

Field           Norm         Value          Min(ref)     Max(ref)
--------------------------------------------------------------------------------
u               L2           3.270e-02     0.0000       0.1250
v               L2           1.450e-03     0.0000       0.0000

WARNING: Reference has 101 points but result has 11 points.
         Consider using --auto-generate or matching the reference grid.
         Expected L2 < 1e-6 for matching grid.
PASS/FAIL: the tolerance check compares matched points only.
```

## 6. Generate a Report

```bash
cfdvv report cases/verification/incompressible/poiseuille-2d \
    --result my_results.csv --output report.html
```

The report is a standalone HTML file containing:

- Case metadata (physics, geometry, reference source with DOI links)
- Comparison table with all error norms (L1, L2, Linf, Relative L2)
- PASSED / FAILED badge with color coding
- Case parameters with descriptions
- No external dependencies --- open in any browser

Example output (opened in browser):

```
+==============================================================+
|  V&V Report: Plane Poiseuille Flow (2D)                     |
|  +------+                                                   |
|  |PASSED|                                                   |
|  +------+                                                   |
|                                                              |
|  Case Information                                            |
|  -----------------------------------------                   |
|  Case ID      poiseuille-2d                                  |
|  Category     verification / incompressible/steady           |
|  Dimension    2D                                             |
|  Physics      incompressible, laminar                        |
|  Reference    analytical --- White, F.M. Viscous Fluid Flow    |
|  DOI          https://doi.org/10.1016/0021-9991(82)90058-4   |
|  Result file  my_results.csv                                 |
|  Generated    2026-07-19 22:30:00                            |
|                                                              |
|  Comparison Results                                          |
|  +-------+------+----------+----------+----------+-------+   |
|  | Field | Norm | L2       | L1       | Linf     | Rel L2|   |
|  +-------+------+----------+----------+----------+-------+   |
|  | u     | L2   | 1.23e-08 | 8.76e-09 | 3.45e-08 | 9.8e-8|   |
|  | v     | L2   | 4.56e-09 | 3.21e-09 | 1.23e-08 |  ---    |   |
|  +-------+------+----------+----------+----------+-------+   |
|                                                              |
|  Generated by cfdvv v0.2.0 --- CFD V&V Suite                   |
+==============================================================+
```

For validation cases:

```bash
cfdvv report cases/validation/turbulent/channel-flow-retau180 \
    --result my_uplus.csv --output channel_report.html
```

## 7. Grid Convergence Study (GCI)

**GCI** (Grid Convergence Index) estimates how far your solution is from the asymptotic (infinite-mesh) value, based on Roache's uniform reporting methodology (ASME V&V 20).

```bash
cfdvv gci cases/verification/incompressible/poiseuille-2d \
    --results coarse.csv medium.csv fine.csv \
    --mesh-sizes 0.1,0.05,0.025
```

Example output:

```
GCI Analysis for: cases/verification/incompressible/poiseuille-2d
Mesh sizes: [0.1, 0.05, 0.025]
Refinement ratios: [2.0, 2.0]

  Quantity 0:
    f1 (fine)   = 0.00000012
    f2 (med)    = 0.00000048
    f3 (coarse) = 0.00000192
    Order p     = 2.00
    Extrapolated = -0.00000001
    GCI (fine/med) = 0.000005
```

### What this tells you

- **Order p ~ 2.0**: your solver achieves second-order accuracy (expected for central schemes). p < 2 suggests a bug or boundary condition inconsistency.
- **GCI ~ 5e-6**: the fine-mesh error estimate is very small --- your mesh is adequate.
- **Extrapolated value**: Richardson extrapolation estimate of the exact (h->0) solution.

### Requirements

- At least 3 mesh levels with constant refinement ratio (typically r = 2)
- The same quantity evaluated on each mesh (e.g., L2 norm of a field)
- Meshes must be in the asymptotic convergence range (p should be approximately constant)

Typical workflow:

```bash
# Run your solver on 3 meshes, export the same quantity
cfdvv compare cases/... -r coarse_results.csv --no-plot   # Note the L2 value
cfdvv compare cases/... -r medium_results.csv --no-plot
cfdvv compare cases/... -r fine_results.csv --no-plot

# Then compute GCI
cfdvv gci cases/... -r coarse_results.csv -r medium_results.csv -r fine_results.csv
```

See [comparison-methodology.md](comparison-methodology.md) for full mathematical details.

## Case Directory Structure

```
poiseuille-2d/
+-- case.yaml               # Metadata (includes mesh: requirements)
+-- README.md               # Physics, geometry, boundary conditions
+-- reference/              # Reference data (CSV)
|   +-- analytical/
+-- openfoam/               # Ready-to-run OpenFOAM case (selected cases)
|   +-- Allrun
|   +-- system/
|   +-- 0/
+-- scripts/                # Solution generation scripts (selected cases)
|   +-- generate_solution.py
+-- geometry/               # Geometry (STEP/STL)
+-- meshes/                 # Pre-built meshes
```

## Built-in OpenFOAM Cases

| Case | Solver | Mesh | Script |
|------|--------|------|--------|
| `poiseuille-2d` | icoFoam | blockMesh (10x20) | Allrun |
| `couette-2d` | icoFoam | blockMesh (8x16) | Allrun |
| `lid-driven-cavity` | icoFoam | blockMesh (32x32) | Allrun |
| `taylor-green-vortex-2d` | icoFoam | blockMesh (64x64) | Allrun |
| `sod-shock-tube` | rhoCentralFoam | blockMesh (200x1) | blockMesh + run |

For all other cases --- see `mesh:` in `case.yaml` for grid requirements and `scripts/generate_solution.py` for analytical generation.
