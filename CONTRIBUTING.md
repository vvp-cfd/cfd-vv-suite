# Contributing to cfd-vv-suite

## Contributor License Agreement (CLA)

By contributing to this project, you agree that:

1. You grant the cfd-vv-suite project an irrevocable, royalty-free, worldwide right to use, modify, distribute, and sublicense your contribution under the MIT license.
2. You confirm that you are the author of the contribution or have the right to provide it under these terms.
3. Your contribution does not infringe third-party rights.
4. You receive no royalties for the contribution.

Project author: **Valeria Puzikova** (valeria.puzikova@gmail.com).

## Adding a New Test Case

1. Copy the template: `cp -r templates/case-template tools/cfdvv/cases/<category>/<case-name>`
2. Fill in `case.yaml` --- case metadata (including `mesh:` section)
3. Write `README.md` with physics description, geometry, BCs, and expected results
4. Add reference data to `reference/` (CSV format: `x, y, z, field1, field2, ...`)
5. Add geometry to `geometry/` (STEP/STL) and optional meshes to `meshes/`
6. Add scripts to `scripts/`: solution generation or solver result extraction
7. Add a `## How to Cite` section in the case README listing the original references with DOIs (see template)

## How to Cite

Each case README must include a **How to Cite** section listing the original publications for that case's reference data. Users of cfd-vv-suite should cite:

1. The cfd-vv-suite project itself (see [CITATION.cff](CITATION.cff))
2. The original reference(s) for the specific test case used

Example for a case README:

```markdown
## How to Cite

If you use this test case, please cite:

1. Puzikova, V. "cfd-vv-suite", 2026. https://github.com/vvp-cfd/cfd-vv-suite
2. Ghia, U., Ghia, K.N., Shin, C.T. "High-Re solutions for incompressible flow...", J. Comput. Phys., 48, 387-411, 1982. https://doi.org/10.1016/0021-9991(82)90058-4
```

## mesh: in case.yaml (required)

Every case must contain a `mesh:` section with mesh requirements:

```yaml
mesh:
  type: uniform                    # uniform | stretched | unstructured
  recommended: [32, 32]            # minimum recommended resolution
  convergence_study: [[16,16],[32,32],[64,64],[128,128]]  # for GCI
  wall_refinement: false
  notes: "Uniform mesh in both directions"
```

## scripts/ --- generating a reference solution

It is recommended to add an executable script in `scripts/` that generates the solution on the required mesh:

- `generate_solution.py` --- writes the analytical solution to CSV at mesh points
- `Allrun` --- OpenFOAM: `blockMesh && icoFoam && postProcess && ...`

## Reference Data Format

CSV with standard column names:

```csv
x, y, u, v, w, p, ...
```

First 1--3 columns are coordinates. Separator: comma. Encoding: UTF-8.

## Field Naming

- `u`, `v`, `w` --- velocity components
- `p` --- pressure
- `T` --- temperature
- `rho` --- density
- `k`, `omega`, `epsilon` --- turbulence quantities
- `mu_t` --- turbulent viscosity
- `tau_xx`, `tau_xy`, ... --- stress tensor
- `Cp` --- pressure coefficient
- `Cf` --- skin friction coefficient

## Code Style

- Python: PEP 8, type hints
- Markdown: GitHub-flavored
- YAML: 2-space indent
- CSV: UTF-8 without BOM, comma separator
