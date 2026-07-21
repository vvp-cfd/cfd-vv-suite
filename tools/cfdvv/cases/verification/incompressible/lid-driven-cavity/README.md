# Lid-Driven Cavity (Re=100)

## Physics

Viscous incompressible flow in a square cavity [0,1]^2. The top wall moves at constant velocity U=1, driving a primary vortex. All other walls are stationary.

## Governing Equations

Steady incompressible Navier-Stokes:
- grad·u = 0
- (u·grad)u = -gradp + (1/Re)·grad^2u

## Geometry

Square domain [0,1] x [0,1].

## Boundary Conditions

| Boundary | Condition |
|----------|-----------|
| Top wall (y=1) | Moving wall: u=1, v=0 |
| Bottom wall (y=0) | No-slip: u=0, v=0 |
| Left wall (x=0) | No-slip: u=0, v=0 |
| Right wall (x=1) | No-slip: u=0, v=0 |

## Reference Solution

Numerical reference from Ghia et al. (1982) obtained on a fine 129^2 mesh. This is the de facto standard for lid-driven cavity benchmark.

## Expected Quantities

| Quantity | Location | Values |
|----------|----------|--------|
| u-velocity | x=0.5, y ∈ [0,1] | Parabolic from negative to positive |
| v-velocity | y=0.5, x ∈ [0,1] | Sharp gradients near walls |

## Reference Data

- `reference/analytical/ghia_re100_vertical.csv`: u-velocity along vertical centerline x=0.5
- `reference/analytical/ghia_re100_horizontal.csv`: v-velocity along horizontal centerline y=0.5

## References

1. Ghia, U., Ghia, K.N., Shin, C.T. "High-Re solutions for incompressible flow using the Navier-Stokes equations and a multigrid method", J. Comput. Phys., 48, 387-411, 1982. [DOI](https://doi.org/10.1016/0021-9991(82)90058-4)
