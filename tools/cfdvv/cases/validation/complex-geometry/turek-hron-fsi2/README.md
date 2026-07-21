# FSI2: Elastic Flag behind Cylinder (Turek & Hron)

## Physics

Fluid-structure interaction (FSI) benchmark. A rigid cylinder with a flexible elastic flag in a channel at Re=100. The flag oscillates due to vortex shedding. Tests partitioned or monolithic FSI coupling.

## Geometry

Channel: 2.5m x 0.41m
Cylinder: D=0.1m, centered at (0.2, 0.2)
Flag: 0.35m long, 0.02m thick, attached to cylinder at (0.6, 0.2)

## Material Properties

| Property | Value |
|----------|-------|
| Density ratio | 10 |
| Young modulus | 1.4e6 Pa |
| Poisson ratio | 0.4 |

## Expected Quantities (FSI2, Re=100)

| Quantity | Value |
|----------|-------|
| Tip y-amplitude | 0.035 (+-0.005) |
| Frequency | 2.0 (+-0.1) Hz |
| Mean Cd | 3.22 (+-0.05) |
| Cl amplitude | 2.55 (+-0.1) |

## References

1. Turek, S. & Hron, J. "Proposal for Numerical Benchmarking of Fluid-Structure Interaction between an Elastic Object and Laminar Incompressible Flow", Tech. Report, Uni Dortmund, 2006. [ResearchGate](https://www.researchgate.net/publication/226447172_Proposal_for_Numerical_Benchmarking_of_Fluid-Structure_Interaction_Between_an_Elastic_Object_and_Laminar_Incompressible_Flow)
2. Turek, S. et al. "Numerical Benchmarking of FSI", in *Fluid-Structure Interaction II*, Springer, 2011. [ResearhGate](https://www.researchgate.net/publication/226685329_Numerical_Benchmarking_of_Fluid-Structure_Interaction_A_Comparison_of_Different_Discretization_and_Solution_Approaches)
