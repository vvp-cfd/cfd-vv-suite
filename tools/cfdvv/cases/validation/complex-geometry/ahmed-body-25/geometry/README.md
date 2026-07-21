# Ahmed Body Geometry

## Description (Ahmed et al., SAE 840300)

The Ahmed body is a simplified car model with a rounded front and a slanted rear surface.

### Dimensions (model scale)

```
Length (L):    1.044 m
Width (W):     0.389 m  
Height (H):    0.288 m
Ground clearance: 0.050 m
Slant angle:   25 deg (this variant)
Slant length:  0.222 m (projected horizontally)
```

### Construction

- Front: rounded nose with radius ~0.1 m (elliptical)
- Main body: rectangular prism L x W x H
- Rear: slanted surface at the specified angle
- Legs: 4 cylindrical struts (0.03 m diameter) for mounting
- Model material: urethane foam, smooth painted surface

### Key References

1. Ahmed, S.R., Ramm, G., Faltin, G. "Some Salient Features of the Time-Averaged Ground Vehicle Wake", SAE Technical Paper 840300, 1984. [DOI](https://doi.org/10.4271/840300)
2. Lienhart, H., Stoots, C., Becker, S. "Flow and Turbulence Structures in the Wake of a Simplified Car Model (Ahmed Model)", DGLR Fachsymp., 2000. [ResearchGate](https://www.researchgate.net/publication/266883948_Flow_and_Turbulence_Structures_in_the_Wake_of_a_Simplified_Car_Model_Ahmed_Model)

### Experimental Setup

- Wind tunnel: 3/4 open-jet Goettingen type
- Nozzle exit area: 2.0 x 1.4 m
- Turbulence intensity: < 0.3%
- Reynolds number: Re_L = 4.29 x 10^6 (based on body length)
- Freestream velocity: 60 m/s
- Ground simulation: stationary ground plane with boundary layer suction
- Measurements: sting balance (forces), pressure taps (Cp)

### Flow Features

**25 deg slant (this case):**
- Flow remains attached on the slant surface
- Strong counter-rotating longitudinal vortices from the slant side edges (C-pillar vortices)
- Highest drag coefficient Cd = 0.285
- Wake dominated by vortex system, not large-scale separation

**35 deg slant (ahmed-body-35):**
- Flow separates at the slant leading edge
- Recirculation bubble on the slant surface
- Lower drag Cd = 0.231, higher lift Cl = 0.165
- Vortex system collapses

The transition angle is ~30 deg where the flow pattern changes abruptly.
