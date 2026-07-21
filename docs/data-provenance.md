# Data Provenance

## How reference data was obtained

### Analytical solutions

Exact formulas from the literature were evaluated at specified grid points using Python/NumPy scripts. For series solutions (e.g., Poiseuille-3D square duct, Bingham plug flow), 30--50 terms were summed to achieve double-precision accuracy (relative error < 1e-12).

### MMS (Method of Manufactured Solutions)

Manufactured solutions were analytically differentiated to compute convective, pressure gradient, and viscous terms. Source terms were evaluated from these derivatives and verified by symbolic differentiation with SymPy for a subset of cases.

### Experimental data

Experimental profiles were digitized from published figures using WebPlotDigitizer. The digitization resolution was chosen to exceed the published measurement uncertainty. Integral quantities (Cd, St, Nu) were taken directly from tables in the cited papers. Values are quoted with uncertainties where provided by the original authors.

Key experimental sources:

| Case | Source | Method |
|------|--------|--------|
| Cylinder Re=20,40,100 | Tritton (1959), Dennis & Chang (1970), Grove et al. (1964) | Cd from force balance; Cp from surface taps |
| Cylinder Re=3900 | Norberg (2003), Parnaudeau et al. (2008) | PIV wake profiles; hot-wire for St |
| Backward-facing step (laminar) | Armaly et al. (1983) | LDA velocity measurements |
| Backward-facing step (turbulent) | Driver & Seegmiller (1985) | Pitot tube + hot-wire; Cf from Preston tubes |
| Flat plate TBL | Wieghardt (1947) via Coles & Hirst (1968) | Pitot tube mean velocity profiles |
| NACA 0012 | McCroskey (1987), Gregory & O'Reilly (1970), Ladson (1988) | Wind tunnel force balance + pressure taps |
| RAE 2822 | Cook et al. (1979), AGARD AR-138 | Wind tunnel pressure taps at M=0.73,0.75 |
| NASA hump | Greenblatt et al., CFDVAL2004 | Wind tunnel PIV + pressure taps |
| Ahmed body | Ahmed et al. (1984), SAE 840300 | 3/4 open-jet wind tunnel, sting balance |
| FSI2 | Turek & Hron (2006) | Computational benchmark (high-resolution FEM) |
| VIV | Khalak & Williamson (1997) | Water channel, LVDT for displacements |
| Oldroyd-B contraction | Alves et al. (2001) | Computational benchmark (high-resolution FVM) |
| Natural convection | de Vahl Davis (1983), Fusegi et al. (1991) | Computational benchmark (finite-difference) |

### DNS data

Mean profiles from DNS databases were extracted from published tables and figures. For the channel flow cases (Re_tau = 180, 550, 1000), data was taken from Moser, Kim, Mansour (1999) and Lee & Moser (2015). Values are time- and space-averaged over statistically stationary flow.

## Accuracy and Limitations

- **Analytical data**: exact to machine precision at the stated grid points.
- **Digitized data**: accuracy is limited by the original measurement uncertainty (quoted) plus digitization error (typically < 1% of range).
- **DNS data**: statistical uncertainty from finite averaging time (quoted in source papers, typically < 1% for mean quantities).
- **Experimental data**: subject to wind/water tunnel corrections (blockage, wall interference) which may not be fully documented in the original paper. Users should consult the original source for detailed uncertainty analysis.

## Verifying the Data

All reference CSV files in `reference/` are self-consistent: comparing `cfdvv compare` with the reference file as both result and reference yields zero error (or < 1e-12 due to floating-point rounding).

To verify a specific dataset:

```bash
cfdvv compare tools/cfdvv/cases/.../case-dir -r tools/cfdvv/cases/.../case-dir/reference/analytical/solution.csv --no-plot
# All field errors should be 0.000000e+00
```
