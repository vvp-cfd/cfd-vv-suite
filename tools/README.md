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

# Case ID works for all commands (no full path needed)
cfdvv info poiseuille-2d                      # Case details
cfdvv compare poiseuille-2d -r my_results.csv # Compare against reference
cfdvv gci poiseuille-2d -r coarse.csv -r medium.csv -r fine.csv
cfdvv report poiseuille-2d -r my_results.csv -o report.html
cfdvv validate poiseuille-2d                  # Validate YAML file
cfdvv example-output poiseuille-2d            # Show expected CSV format

# Full paths also work (backward-compatible)
cfdvv info tools/cfdvv/cases/verification/incompressible/poiseuille-2d
cfdvv compare tools/cfdvv/cases/verification/incompressible/poiseuille-2d -r my_results.csv
cfdvv gci tools/cfdvv/cases/... -r coarse.csv -r medium.csv -r fine.csv
```

## Running tests

```bash
cd tools
pip install -e ".[dev]"
pytest tests/
```
