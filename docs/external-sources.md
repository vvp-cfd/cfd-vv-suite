# External Sources

cfd-vv-suite provides **two kinds** of test cases:

| | Built-in (51 cases) | Imported (35 cases) |
|---|---|---|
| **Where data lives** | In this repository (`tools/cfdvv/cases/.../reference/`) | In external databases |
| **How you get it** | Already present after `git clone` (or `pip install cfdvv`) | Downloaded on demand: `cfdvv import <case>` |
| **Curation level** | Full: README, mesh specs, OpenFOAM files, scripts, 187 tests | Metadata: case.yaml + URL, auto-generated |
| **Update frequency** | With new releases of cfd-vv-suite | Independently, when source database updates |
| **Examples** | poiseuille-2d, cylinder-re100, beltrami-flow-3d | flatplate (NASA TMR), bfs-laminar (ERCOFTAC), sod (ExactPack) |

**Design principle:** cases that require careful curation (exact geometry, mesh specs, OpenFOAM setup, domain-specific README) live in the repo. Cases where the authoritative data lives elsewhere act as **gateways** — `cfdvv import` fetches the latest data from the source and creates a bridge to our comparison tools.

## Quick Start

```bash
# List all external cases from every source
cfdvv import --list

# Import a case by name (auto-detects source)
cfdvv import flatplate

# Import and compare against your results in one command
cfdvv import flatplate -r my_results.csv --plot
```

## Available Sources

### NASA TMR (turbmodels.larc.nasa.gov)

Turbulence Modeling Resource — the primary NASA validation database.

| Case | Description | Data |
|------|-------------|------|
| `flatplate` | ZPG turbulent flat plate BL | Cf vs Re_x, velocity profiles |
| `hump` | Wall-mounted hump (CFDVAL2004) | Cp surface distribution |
| `bump` | 2D bump in turbulent channel | Cp, Cf |
| `naca0012` | NACA 0012 transonic airfoil | Reference (see website) |
| `rae2822` | RAE 2822 transonic airfoil | Reference (see website) |

### ERCOFTAC Classic Collection (cfd.mace.manchester.ac.uk/ercoftac)

The largest curated turbulent flow database — 80+ cases.

| Case | Description | Re |
|------|-------------|-----|
| `bfs-laminar` | Backward-facing step, laminar | 100-800 |
| `bfs-turbulent` | Backward-facing step, turbulent | 36k |
| `cylinder-re3900` | Cylinder, subcritical | 3900 |
| `diffuser` | Conical diffuser | — |
| `channel-exp` | Turbulent channel DNS | 180-590 |
| `jet` | Plane turbulent jet | — |
| `mixing-layer` | Turbulent mixing layer | — |
| `pipe` | Turbulent pipe flow | 40k-500k |

**Note:** ERCOFTAC data requires manual download from the website. The importer creates metadata and provides the download URL.

### JHTDB (turbulence.idies.jhu.edu)

Johns Hopkins Turbulence Database — multi-terabyte DNS/LES data.

| Case | Description | Grid |
|------|-------------|------|
| `channel180` | Turbulent channel Re_tau=180 | 128x129x128 |
| `channel1000` | Turbulent channel Re_tau=1000 | — |
| `isotropic` | Forced isotropic turbulence | 1024^3 |

**Requires:** `pip install giverny`

### CFDBench (github.com/ricardodpcosta/CFDBench)

Curated analytical verification cases.

| Case | Description |
|------|-------------|
| `poiseuille` | Plane Poiseuille flow |
| `couette` | Plane Couette flow |

### MASA (github.com/manufactured-solutions/MASA)

Manufactured solutions library (C++/Python).

| Case | Description |
|------|-------------|
| `ns-2d` | 2D Navier-Stokes MMS |
| `euler-2d` | 2D Euler MMS |

**Requires:** `pip install masa`

### ExactPack (github.com/lanl/ExactPack)

LANL exact solutions for verification.

| Case | Description |
|------|-------------|
| `sod` | Sod shock tube |
| `noh` | Noh implosion problem |
| `sedov` | Sedov blast wave |

**Requires:** `pip install exactpack`

## Architecture

Each source is a Python class implementing:

```python
class MySource(BaseImporter):
    def name(self) -> str:           # "my-source"
    def list_cases(self) -> list:    # ["case1", "case2"]
    def import_case(self, case_id, target_dir) -> str:  # creates case.yaml + data
```

New sources can be added by creating a class in `tools/cfdvv/importers/__init__.py` and registering it in `_register()`.

## Imported Case Structure

```
tools/cfdvv/cases/imported/nasa-tmr-flatplate/
├── case.yaml           # Auto-generated metadata
├── README.md           # Source description + links
└── reference/
    └── experimental/   # Downloaded data files
```

Imported cases are in `.gitignore` — they are regenerated on demand.

## Related Projects

- **NASA TMR** — [tmbwg.github.io/turbmodels](https://tmbwg.github.io/turbmodels/)
- **ERCOFTAC Classic Collection** — [cfd.mace.manchester.ac.uk/ercoftac](http://cfd.mace.manchester.ac.uk/ercoftac)
- **CFDBench** — [github.com/ricardodpcosta/CFDBench](https://github.com/ricardodpcosta/CFDBench)
- **MASA** — [github.com/manufactured-solutions/MASA](https://github.com/manufactured-solutions/MASA)
- **ExactPack** — [github.com/lanl/ExactPack](https://github.com/lanl/ExactPack)
- **JHTDB** — [turbulence.idies.jhu.edu](https://turbulence.idies.jhu.edu)
