# cfd-vv-suite

[![PyPI version](https://img.shields.io/pypi/v/cfdvv?color=blue)](https://pypi.org/project/cfdvv/)
[![Python versions](https://img.shields.io/pypi/pyversions/cfdvv)](https://pypi.org/project/cfdvv/)
[![License](https://img.shields.io/pypi/l/cfdvv)](https://github.com/vvp-cfd/cfd-vv-suite/blob/main/LICENSE)
[![CI](https://github.com/vvp-cfd/cfd-vv-suite/actions/workflows/verify.yml/badge.svg)](https://github.com/vvp-cfd/cfd-vv-suite/actions/workflows/verify.yml)

An open test suite for verification and validation (V&V) of computational fluid dynamics codes.
51 cases: 1D/2D/3D, laminar/turbulent, Newtonian/non-Newtonian, stationary/moving bodies.

## Overview

cfd-vv-suite provides a standardized, reproducible, solver-agnostic toolkit for testing CFD solver accuracy. It works with any solver (OpenFOAM, SU2, Fluent, custom code) — the user provides simulation results as CSV and the CLI tool compares them against reference data, computes error norms, and generates reports.

## Quick Start

### Installation

```bash
# From PyPI (recommended — no clone needed)
pip install cfdvv

# Or from source (includes cases + OpenFOAM templates)
git clone https://github.com/vvp-cfd/cfd-vv-suite.git
cd cfd-vv-suite
pip install -e tools/
```

### Usage

```bash
# List available cases
cfdvv list
cfdvv list -c validation

# Compare your results against reference
cfdvv compare cases/verification/incompressible/poiseuille-2d \
    --result my_results.csv --norm L2 --plot

# OpenFOAM: ready-to-run Poiseuille case (from cloned repo)
cd cases/verification/incompressible/poiseuille-2d/openfoam && ./Allrun

# Generate analytical solution on a given mesh
python cases/verification/incompressible/poiseuille-2d/scripts/generate_solution.py 10 20 my.csv

# See expected output format
cfdvv example-output cases/verification/incompressible/poiseuille-2d

# Run all verification self-tests
cfdvv benchmark

# Generate HTML report
cfdvv report cases/verification/incompressible/poiseuille-2d \
    --result my_results.csv -o report.html
```

Full guide: [docs/getting-started.md](docs/getting-started.md)

## Case Categories

| Category | Subcategory | Examples |
|----------|-------------|----------|
| verification/incompressible | Steady, Unsteady, 3D | Poiseuille, Couette, Taylor-Green, Beltrami, MMS, Lid-Driven, Blasius, Convection |
| verification/compressible | — | Sod Shock Tube, Oblique Shock, Double Mach Reflection |
| verification/non-newtonian | — | Power-Law, Bingham |
| verification/moving-bodies | — | Taylor-Couette, Pitching Airfoil |
| validation/laminar | — | Cylinder Re=20,40,100, BFS Armaly |
| validation/turbulent | — | Flat Plate TBL, Channel DNS, NACA0012, RAE2822, BFS Driver, NASA Hump, Cylinder Re=3900 |
| validation/non-newtonian | — | Oldroyd-B 4:1 Contraction |
| validation/complex-geometry | — | Ahmed Body, FSI Turek-Hron, VIV Cylinder |

See [docs/case-index.md](docs/case-index.md) for the complete listing.

## External Sources — `cfdvv import`

Beyond the 51 built-in cases, cfd-vv-suite connects to external V&V databases:

```bash
cfdvv import --list              # 35 external cases from 6 sources
cfdvv import flatplate           # auto-detects source, downloads data
cfdvv import flatplate -r my.csv --plot  # import + compare in one step
```

| Source | Cases | Type | Access |
|--------|-------|------|--------|
| **NASA TMR** | 8 | Experimental | Direct download |
| **ERCOFTAC** | 14 | Experimental | Metadata + URLs |
| **JHTDB** | 3 | DNS | Python API (giverny) |
| **CFDBench** | 5 | Analytical | Metadata |
| **MASA** | 2 | MMS | pip install + script |
| **ExactPack** | 3 | Exact solutions | pip install + script |

See [docs/external-sources.md](docs/external-sources.md) for details.

## Related Projects

- **NASA TMR** ([tmbwg.github.io/turbmodels](https://tmbwg.github.io/turbmodels/)) — turbulence model validation databases
- **ERCOFTAC** ([cfd.mace.manchester.ac.uk/ercoftac](http://cfd.mace.manchester.ac.uk/ercoftac)) — 80+ turbulent validation cases
- **CFDBench** ([github.com/ricardodpcosta/CFDBench](https://github.com/ricardodpcosta/CFDBench)) — analytical verification cases
- **MASA** ([github.com/manufactured-solutions/MASA](https://github.com/manufactured-solutions/MASA)) — C++ MMS library
- **ExactPack** ([github.com/lanl/ExactPack](https://github.com/lanl/ExactPack)) — exact solutions for verification
- **JHTDB** ([turbulence.idies.jhu.edu](https://turbulence.idies.jhu.edu)) — DNS/LES turbulence databases

## How to Cite

If you use cfd-vv-suite in your research, please cite it as:

```bibtex
@misc{cfdvvsuite2026,
  author       = {Puzikova, Valeria},
  title        = {cfd-vv-suite: Open Test Suite for CFD Verification and Validation},
  year         = {2026},
  publisher    = {GitHub},
  howpublished = {\\url{https://github.com/vvp-cfd/cfd-vv-suite}},
  note         = {Version 0.3.0}
}
```

When using a specific test case, also cite the original reference listed in the case's `case.yaml` and `README.md`.

See [CITATION.cff](CITATION.cff) for the Citation File Format version.

## License

MIT — see [LICENSE](LICENSE). By contributing, you agree to the terms in [CONTRIBUTING.md](CONTRIBUTING.md).

## Contacts

**Author: Valeria Puzikova** — valeria.puzikova@gmail.com

See [AUTHORS.md](AUTHORS.md) for the full list of contributors.
