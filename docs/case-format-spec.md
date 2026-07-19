# case.yaml Format Specification

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique case identifier (Latin, hyphens) |
| `name` | string | Human-readable name |
| `category` | string | `verification` or `validation` |
| `tags` | list[string] | Filterable tags |
| `physics` | dict | Physical model |
| `dimension` | string | `1D`, `2D`, `3D`, `axisymmetric` |
| `reference` | dict | Reference data type and source |
| `quantities` | list[dict] | Quantities to compare |
| `mesh` | dict | Mesh requirements |

## Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `subcategory` | string | Subcategory |
| `parameters` | list[dict] | Adjustable parameters |
| `tolerances` | dict | Thresholds for pass/fail |
| `notes` | string | Additional remarks |

## physics

```yaml
physics:
  type: incompressible          # incompressible | compressible
  regime: laminar               # laminar | turbulent | transitional
  convective: true              # whether convective terms are present
  equations:                    # list of governing equations
    - continuity
    - navier-stokes
```

## mesh

```yaml
mesh:
  type: "uniform quadrilateral"       # mesh type
  recommended: [32, 32]               # minimum recommended resolution [nx, ny, ...]
  convergence_study: [[16,16],[32,32],[64,64],[128,128]]  # mesh levels for GCI
  wall_refinement: false              # whether wall refinement is required
  notes: "Uniform mesh in both directions"
```

## reference

```yaml
reference:
  type: analytical              # analytical | experimental | dns | les | mms
  solution: "u(y) = ..."       # formula or description
  source: "Author, Journal"    # bibliographic reference
  doi: "https://doi.org/10.xxxx/yyyy"  # DOI/URL (optional but recommended)
```

## quantities

```yaml
quantities:
  - name: u                     # field name
    type: profile               # profile | field | scalar
    location: "outlet"          # measurement location
    norm: L2                    # comparison norm (L1, L2, Linf, Relative_L2)
```

## parameters

```yaml
parameters:
  - name: Re
    description: "Reynolds number"
    default: 100
    range: [1, 1000]
```

## tolerances

```yaml
tolerances:
  L2: 1e-6
  Linf: 1e-5
  Relative_L2: 0.01
```

## Full Example

See `templates/case-template/case.yaml`.
