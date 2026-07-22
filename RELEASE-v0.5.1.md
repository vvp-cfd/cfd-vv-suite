# cfdvv v0.5.1 Release Notes

## Short case IDs for all commands

The BIG one. No more copy-pasting full `tools/cfdvv/cases/verification/incompressible/...` paths:

```bash
# Before (v0.5.0)
cfdvv info    tools/cfdvv/cases/verification/incompressible/poiseuille-2d
cfdvv compare tools/cfdvv/cases/verification/incompressible/poiseuille-2d -r my_results.csv
cfdvv gci     tools/cfdvv/cases/verification/incompressible/poiseuille-2d -r c.csv -r m.csv -r f.csv
cfdvv report  tools/cfdvv/cases/verification/incompressible/poiseuille-2d -r my_results.csv

# After (v0.5.1)
cfdvv info    poiseuille-2d
cfdvv compare poiseuille-2d -r my_results.csv
cfdvv gci     poiseuille-2d -r c.csv -r m.csv -r f.csv
cfdvv report  poiseuille-2d -r my_results.csv
```

- All commands (`info`, `compare`, `gci`, `report`, `validate`, `example-output`) now resolve case IDs automatically
- Full paths still work — fully backward-compatible
- `--cases-root` option added to override auto-detection
- New `_resolve_case_path()` helper searches package directory or walks up from CWD

## Jupyter demo notebook

`example/cfdvv-demo.ipynb` — a runnable walkthrough covering all features: listing cases, inspecting metadata, comparing results, generating reports, GCI analysis, and the Python API.

## Documentation

- Wolfram Mathematica digitization workflow added to the graph digitization guide (1-step `Import` → `LocatorPane` → affine transform → `Export`)
- `tools/README.md` and `docs/getting-started.md` updated with short case-ID examples throughout
- Fixed broken case-index links in GitHub Pages
- Fixed Liquid/Jekyll template escaping for Mathematica `{{x1, y1}}` syntax

## Tests

- 7 new tests for case-ID path resolution (`test_comprehensive.py::TestCLIExists`)
- Covers: case ID lookup, auto-detected root, nonexistent case error, relative path backward compat, `_resolve_case_path` unit tests

## Versions

- `__init__.py`, `pyproject.toml`, `.zenodo.json`, `cfdvv-demo.ipynb` — all synced to 0.5.1

---

```bash
pip install cfdvv --upgrade
cfdvv info couette-2d     # instant case lookup
```
