# cfd-vv-suite Documentation

**Author: Valeria Puzikova** (valeria.puzikova@gmail.com)

Published via GitHub Pages at: `https://vvp-cfd.github.io/cfd-vv-suite`

An open test suite for CFD code verification & validation. 51 cases, solver-agnostic CLI, OpenFOAM integration.

## Contents

- [Quick Start](getting-started.md)
- [Case Format Specification](case-format-spec.md)
- [Comparison Methodology](comparison-methodology.md)
- [Solver Integration](solver-integration.md)
- [Case Index](case-index.md)
- [Glossary](glossary.md)
- [Data Provenance](data-provenance.md)
- [Digitization Guide](digitization-guide.md)
- [MMS Generation Guide](mms-generation.md)

## Related Projects

- **NASA TMR** ([tmbwg.github.io/turbmodels](https://tmbwg.github.io/turbmodels/)) — turbulence model validation databases
- **ERCOFTAC Classic Collection** ([cfd.mace.manchester.ac.uk/ercoftac](http://cfd.mace.manchester.ac.uk/ercoftac)) — 80+ turbulent validation cases
- **CFDBench** ([github.com/ricardodpcosta/CFDBench](https://github.com/ricardodpcosta/CFDBench)) — analytical verification cases
- **MASA** ([github.com/manufactured-solutions/MASA](https://github.com/manufactured-solutions/MASA)) — C++ MMS library
- **ExactPack** ([github.com/lanl/ExactPack](https://github.com/lanl/ExactPack)) — exact solutions for verification
- **JHTDB** ([turbulence.idies.jhu.edu](https://turbulence.idies.jhu.edu)) — DNS/LES turbulence databases
- **fieldcompare** ([github.com/dglaeser/fieldcompare](https://github.com/dglaeser/fieldcompare)) — field comparison Python package

## Key Concepts

- **Verification**: checking that equations are solved correctly (comparison with analytical/MMS solutions, grid convergence analysis).
- **Validation**: checking that the right equations are solved (comparison with experimental/DNS data).
- **Case-as-data**: case description in YAML + CSV format, independent of the solver.
- **Solver-agnostic**: the tool works with any solver capable of producing CSV/VTK output.
