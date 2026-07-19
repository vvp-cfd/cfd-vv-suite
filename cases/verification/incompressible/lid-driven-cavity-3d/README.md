# Lid-Driven Cavity (3D, Re=100)

## Physics

3D flow in a cubic cavity [0,1]^3. Top wall (y=1) moves at U=1. End-walls at z=0 and z=1 create 3D boundary layer effects.

## Geometry

Unit cube [0,1]^3.

## Boundary Conditions

| Boundary | Condition |
|----------|-----------|
| y=1 (lid) | Moving: u=1, v=0, w=0 |
| All other walls | No-slip |

## Flow Features (Re=100)

- Primary vortex dominates midplane
- Secondary corner eddies near bottom corners
- End-wall boundary layers at z=0, z=1
- Weaker z-velocity component near end-walls

## Reference Data

profile_vertical_midplane.csv -- u-velocity along (x=0.5, z=0.5)

## References

1. Chiang, T.P., Sheu, W.H., Hwang, R.R. "Finite volume analysis of spiral motion in a rectangular lid-driven cavity", Int. J. Numer. Meth. Fluids, 23, 325-346, 1997. [DOI](https://doi.org/10.1002/(SICI)1097-0363(19960830)23:4<325::AID-FLD420>3.0.CO;2-7)
2. Bouffanais, R., Deville, M.O., Leriche, E.  "Large-eddy simulation of the flow in a lid-driven cubical cavity", Phys. Fluids, 19, 55-108, 2007. [DOI](https://doi.org/10.1063/1.2723153) 
