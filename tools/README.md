# cfdvv --- CLI tools for CFD Verification & Validation

## Installation

```bash
pip install -e .                # base install
pip install -e ".[dev]"         # with test dependencies
pip install -e ".[openfoam]"    # with OpenFOAM support
```

## Usage

```bash
cfdvv list                                    # List all cases
cfdvv list -c verification -t laminar         # Filter by category and tags
cfdvv info cases/verification/incompressible/poiseuille-2d  # Case details
cfdvv validate cases/verification/incompressible/poiseuille-2d  # Validate YAML
cfdvv compare cases/verification/incompressible/poiseuille-2d -r my_results.csv
cfdvv gci cases/... -r coarse.csv -r medium.csv -r fine.csv
```

## Running tests

```bash
cd tools
pip install -e ".[dev]"
pytest tests/
```
