# Solver Integration Guide

## General Approach

cfd-vv-suite does not require modifying your solver. Workflow:

1. Read the case description (`README.md`, `case.yaml`) --- geometry, BCs, and **mesh requirements** (`mesh:`)
2. Set up the simulation: geometry, mesh, boundary conditions, fluid properties
3. Run the solver
4. Export results as CSV (coordinates + fields)
5. Compare: `cfdvv compare <case-dir> --result <file.csv>`

## CSV Format for Results

Minimum requirements:

```csv
x,y,u,v,p
0.0,0.0,0.0,0.0,1.5
```

- Separator: comma
- Encoding: UTF-8
- First row: column headers with coordinate names (`x, y, z`) followed by field names (`u, v, w, p, rho, T, ...`)
- All names are case-insensitive during comparison

## Integration with OpenFOAM

### Exporting Results

Use the `sample` utility:

```cpp
// system/sampleDict
sets
(
    centerline
    {
        type    uniform;
        axis    y;
        start   (5 0 0.05);
        end     (5 1 0.05);
        nPoints 101;
    }
);
```

```bash
postProcess -func sampleDict -latestTime
```

Five cases include ready-to-run OpenFOAM directories under `openfoam/`:

| Case | Solver | Command |
|------|--------|---------|
| `poiseuille-2d` | icoFoam | `./Allrun` |
| `couette-2d` | icoFoam | `./Allrun` |
| `lid-driven-cavity` | icoFoam | `./Allrun` |
| `taylor-green-vortex-2d` | icoFoam | `./Allrun` |
| `sod-shock-tube` | rhoCentralFoam | `blockMesh && rhoCentralFoam` |

See `templates/openfoam-template/README.md` for the general approach to other cases.

### Recommended Solvers

| Case | OpenFOAM Solver |
|------|----------------|
| poiseuille-2d/3d, couette-2d/3d | `icoFoam`, `simpleFoam` |
| taylor-green-vortex-2d/3d | `icoFoam` |
| lid-driven-cavity | `icoFoam` |
| sod-shock-tube | `rhoCentralFoam`, `sonicFoam` |
| oblique-shock | `rhoCentralFoam` |
| manufactured-ns-2d/3d | `icoFoam` + `fvOptions` (source terms) |
| backward-facing-step | `simpleFoam` |
| channel-flow-retau* | `pimpleFoam` (DNS/LES) or `simpleFoam` (RANS) |
| naca0012, rae2822 | `simpleFoam` / `rhoSimpleFoam` |
| poiseuille-power-law, poiseuille-bingham | `simpleFoam` with `nonNewtonianIcoFoam` or custom viscosity model |

## Integration with SU2

SU2 config file snippet:

```
% SU2 configuration for Poiseuille verification
SOLVER = INC_NAVIER_STOKES
MESH_FILENAME = poiseuille.su2
MESH_FORMAT = SU2
RESTART_SOL = NO

% Output CSV-compatible format
OUTPUT_FILES = (RESTART, PARAVIEW)
OUTPUT_WRT_FREQ = 1
VOLUME_OUTPUT = (VELOCITY, PRESSURE)

% Boundary conditions
MARKER_INLET = (inlet, 200.0)
MARKER_OUTLET = (outlet, 0.0)
MARKER_HEATFLUX = (top, 0.0, bottom, 0.0)
```

After running SU2, export velocity and pressure at the reference points:

```bash
SU2_CFD poiseuille.cfg
# SU2 outputs .vtu (Paraview) — convert to CSV:
python -c "
import meshio
mesh = meshio.read('flow.vtu')
import numpy as np
# Extract points and data
pts = mesh.points
# Export at reference y-coordinates
y_ref = np.linspace(0, 1, 101)
# Interpolate...
np.savetxt('results.csv', ...)
"
```

## Integration with ANSYS Fluent

1. **Export solution**: File > Export > Solution Data
2. Select **ASCII** format, **CSV** separator
3. Choose surfaces/lines matching reference locations
4. Select quantities: X-Coordinate, Y-Coordinate, X-Velocity, Y-Velocity, Pressure
5. Write to `results.csv`

For 2D profiles: create a **line** surface (Surface > Line/Rake) at the required location (e.g., x=0.5 for cavity centerline), then export data on that line.

For 3D wall quantities: use **Report > Surface Integrals** or export XY-plot data.

## Integration with Custom Solver

### Fortran

```fortran
open(unit=10, file='results.csv', status='replace')
write(10, '(a)') 'x,y,u,v,p'
do i = 1, nx
  do j = 1, ny
    write(10, '(5(f12.6,a))') x(i,j), ',', y(i,j), ',', &
                               u(i,j), ',', v(i,j), ',', &
                               p(i,j)
  end do
end do
close(10)
```

### C/C++

```c
#include <stdio.h>
FILE *f = fopen("results.csv", "w");
fprintf(f, "x,y,u,v,p\n");
for (int i = 0; i < nx; i++)
    for (int j = 0; j < ny; j++)
        fprintf(f, "%f,%f,%f,%f,%f\n", x[i][j], y[i][j], u[i][j], v[i][j], p[i][j]);
fclose(f);
```

### MATLAB

```matlab
[X, Y] = meshgrid(x, y);
data = [X(:), Y(:), u(:), v(:), p(:)];
writematrix(data, 'results.csv');
% Or with header:
fid = fopen('results.csv', 'w');
fprintf(fid, 'x,y,u,v,p\n');
fclose(fid);
writematrix(data, 'results.csv', 'WriteMode', 'append');
```

### Python (numpy-based solver)

```python
import csv
import numpy as np

with open('results.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['x', 'y', 'u', 'v', 'p'])
    for i in range(nx):
        for j in range(ny):
            w.writerow([x[i,j], y[i,j], u[i,j], v[i,j], p[i,j]])
```

### Using cfdvv with your results

After exporting, compare immediately:

```bash
cfdvv example-output tools/cfdvv/cases/verification/incompressible/poiseuille-2d  # see expected format
cfdvv compare tools/cfdvv/cases/verification/incompressible/poiseuille-2d -r results.csv --plot
```

## MMS: Special Requirements

For MMS-type cases (e.g., `manufactured-ns-2d`, `manufactured-ns-3d`), source terms must be added to the equations. They are provided in `reference/mms/source_terms.csv`.

In OpenFOAM this is done via `fvOptions`:

```
momentumSource
{
    type            vectorCodedSource;
    selectionMode   all;
    fields          (U);
    name            momentumSource;
    codeCorrect
    #{
        // Read source_terms.csv and interpolate S_u, S_v to cell centers
    #};
}
```

Alternatively, run `scripts/generate_solution.py <nx> <ny>` to produce the exact solution at your mesh resolution and compare directly.
