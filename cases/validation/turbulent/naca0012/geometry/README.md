# NACA 0012 Geometry

## Formula (NACA 4-digit)

y/c = (t/0.20) * ( 0.2969*sqrt(x/c) - 0.1260*(x/c) - 0.3516*(x/c)^2 + 0.2843*(x/c)^3 - 0.1015*(x/c)^4 )

where t = 0.12 for NACA 0012 (12% thickness).

## Using the Coordinates

`naca0012_coordinates.csv` contains 201 points describing the upper and lower surfaces. To use:

1. Read the CSV
2. The upper surface goes counter-clockwise: (x/c, y_upper/c) from trailing edge (1,0) to leading edge (0,0)
3. The lower surface goes clockwise: (x/c, y_lower/c) from leading edge (0,0) to trailing edge (1,0)
4. Approximate with Bezier splines, B-splines, or use as-is for mesh generation

## Reference

Ladson, C.L. "Effects of Independent Variation of Mach and Reynolds Numbers on the Low-Speed Aerodynamic Characteristics of the NACA 0012 Airfoil Section", NASA TM-4074, 1988.
DOI: https://ntrs.nasa.gov/citations/19880003095
