# cfdvv --- CLI tools for CFD Verification & Validation

## Installation

```bash
pip install -e .                # editable install (dev)
pip install -e ".[dev]"         # with test dependencies
pip install cfdvv               # from PyPI (all cases included)
```

## Usage

```bash
cfdvv list                                    # List all cases
cfdvv list -c verification -t laminar         # Filter by category and tags
cfdvv info tools/cfdvv/cases/verification/incompressible/poiseuille-2d  # Case details
cfdvv validate tools/cfdvv/cases/verification/incompressible/poiseuille-2d  # Validate YAML
cfdvv compare tools/cfdvv/cases/verification/incompressible/poiseuille-2d -r my_results.csv
cfdvv gci tools/cfdvv/cases/... -r coarse.csv -r medium.csv -r fine.csv
```

## Running tests

```bash
cd tools
pip install -e ".[dev]"
pytest tests/
```
