# Case Index

## Verification --- Incompressible

### Steady

| ID | Name | Dim | Reference type | Key quantities |
|----|------|-----|----------------|----------------|
| [poiseuille-2d](../tools/cfdvv/cases/verification/incompressible/poiseuille-2d/README.md) | Plane Poiseuille Flow | 2D | analytical | u(y) profile |
| [poiseuille-3d](../tools/cfdvv/cases/verification/incompressible/poiseuille-3d/README.md) | Square Duct Poiseuille | 3D | analytical | u(y,z) profile |
| [couette-2d](../tools/cfdvv/cases/verification/incompressible/couette-2d/README.md) | Plane Couette Flow | 2D | analytical | u(y) profile |
| [couette-3d](../tools/cfdvv/cases/verification/incompressible/couette-3d/README.md) | Plane Couette Flow | 3D | analytical | u(y) profile |
| [lid-driven-cavity](../tools/cfdvv/cases/verification/incompressible/lid-driven-cavity/README.md) | Lid-Driven Cavity, Re=100 | 2D | reference (Ghia) | u(y), v(x) profiles |
| [lid-driven-cavity-3d](../tools/cfdvv/cases/verification/incompressible/lid-driven-cavity-3d/README.md) | Lid-Driven Cavity | 3D | reference | u(y) at midplane |
| [manufactured-ns-2d](../tools/cfdvv/cases/verification/incompressible/manufactured-ns-2d/README.md) | MMS --- 2D Navier-Stokes | 2D | MMS | u, v, p fields + source terms |
| [manufactured-ns-3d](../tools/cfdvv/cases/verification/incompressible/manufactured-ns-3d/README.md) | MMS --- 3D Navier-Stokes | 3D | MMS | u, v, w, p fields + source terms |
| [beltrami-flow-3d](../tools/cfdvv/cases/verification/incompressible/beltrami-flow-3d/README.md) | Beltrami Flow | 3D | analytical | u, v, w, p (exact steady) |
| [pipe-flow-3d](../tools/cfdvv/cases/verification/incompressible/pipe-flow-3d/README.md) | Hagen-Poiseuille Pipe Flow | 3D | analytical | u(r) profile |
| [flat-plate-blausius](../tools/cfdvv/cases/verification/incompressible/flat-plate-blausius/README.md) | Blasius Boundary Layer | 2D | analytical | u(y), Cf, delta(x) |
| [flat-plate-blausius-3d](../tools/cfdvv/cases/verification/incompressible/flat-plate-blausius-3d/README.md) | Blasius Boundary Layer | 3D | analytical | u(y), w = 0 check |
| [natural-convection-cavity](../tools/cfdvv/cases/verification/incompressible/natural-convection-cavity/README.md) | Natural Convection (de Vahl Davis) | 2D | reference | Nu, T(x), u(x), v(y) |
| [natural-convection-cavity-3d](../tools/cfdvv/cases/verification/incompressible/natural-convection-cavity-3d/README.md) | Natural Convection (Fusegi) | 3D | reference | Nu_mean |

### Unsteady

| ID | Name | Dim | Reference type | Key quantities |
|----|------|-----|----------------|----------------|
| [taylor-green-vortex-2d](../tools/cfdvv/cases/verification/incompressible/taylor-green-vortex-2d/README.md) | Taylor-Green Vortex | 2D | analytical | u, v, p (t=0, t=0.5) |
| [taylor-green-vortex-3d](../tools/cfdvv/cases/verification/incompressible/taylor-green-vortex-3d/README.md) | Taylor-Green Vortex | 3D | analytical | u, v, w, p (t=0) |

## Verification --- Compressible

| ID | Name | Dim | Reference type | Key quantities |
|----|------|-----|----------------|----------------|
| [sod-shock-tube](../tools/cfdvv/cases/verification/compressible/sod-shock-tube/README.md) | Sod Shock Tube | 1D | analytical | rho, u, p, e (t=0.2) |
| [oblique-shock](../tools/cfdvv/cases/verification/compressible/oblique-shock/README.md) | Oblique Shock, M=2.0 | 2D | analytical | p/p_inf, shock angle |
| [oblique-shock-3d](../tools/cfdvv/cases/verification/compressible/oblique-shock-3d/README.md) | Oblique Shock | 3D | analytical | p/p_inf, spanwise check |
| [double-mach-reflection](../tools/cfdvv/cases/verification/compressible/double-mach-reflection/README.md) | Double Mach Reflection | 2D | reference | rho(t=0.2), triple point |

## Verification --- Non-Newtonian

| ID | Name | Dim | Reference type | Key quantities |
|----|------|-----|----------------|----------------|
| [poiseuille-power-law](../tools/cfdvv/cases/verification/non-newtonian/poiseuille-power-law/README.md) | Power-Law Poiseuille | 2D | analytical | u(y) for n=0.5..1.5 |
| [poiseuille-power-law-3d](../tools/cfdvv/cases/verification/non-newtonian/poiseuille-power-law-3d/README.md) | Power-Law Poiseuille | 3D | analytical | u(y,z) square duct |
| [poiseuille-bingham](../tools/cfdvv/cases/verification/non-newtonian/poiseuille-bingham/README.md) | Bingham Poiseuille | 2D | analytical | u(y) for Bn=0..0.98 |
| [poiseuille-bingham-3d](../tools/cfdvv/cases/verification/non-newtonian/poiseuille-bingham-3d/README.md) | Bingham Poiseuille | 3D | analytical | u(y,z), plug zone |

## Verification --- Moving Bodies

| ID | Name | Dim | Reference type | Key quantities |
|----|------|-----|----------------|----------------|
| [taylor-couette](../tools/cfdvv/cases/verification/moving-bodies/taylor-couette/README.md) | Taylor-Couette Flow | 2D | analytical | u_theta(r) |
| [taylor-couette-3d](../tools/cfdvv/cases/verification/moving-bodies/taylor-couette-3d/README.md) | Taylor-Couette Flow | 3D | analytical | u_theta(r), Taylor vortices |
| [pitching-airfoil](../tools/cfdvv/cases/verification/moving-bodies/pitching-airfoil/README.md) | Pitching NACA 0012 (AGARD CT5) | 2D | experimental | Cl hysteresis |

## Validation --- Laminar

| ID | Name | Dim | Reference type | Key quantities |
|----|------|-----|----------------|----------------|
| [cylinder-re20](../tools/cfdvv/cases/validation/laminar/cylinder-re20/README.md) | Cylinder, Re=20 | 2D | experimental | Cd, Lw/D, theta_sep, Cp |
| [cylinder-re40](../tools/cfdvv/cases/validation/laminar/cylinder-re40/README.md) | Cylinder, Re=40 | 2D | experimental | Cd, Lw/D, theta_sep, Cp |
| [cylinder-re100](../tools/cfdvv/cases/validation/laminar/cylinder-re100/README.md) | Cylinder, Re=100 | 2D | experimental | Cd, St, Cl_rms, Cp |
| [backward-facing-step](../tools/cfdvv/cases/validation/laminar/backward-facing-step/README.md) | Backward-Facing Step (Armaly) | 2D | experimental | x_r/h, velocity profiles |
| [backward-facing-step-3d](../tools/cfdvv/cases/validation/laminar/backward-facing-step-3d/README.md) | Backward-Facing Step | 3D | experimental | x_r/h at midplane |

## Validation --- Turbulent

| ID | Name | Dim | Reference type | Key quantities |
|----|------|-----|----------------|----------------|
| [flat-plate-tbl](../tools/cfdvv/cases/validation/turbulent/flat-plate-tbl/README.md) | Turbulent Flat Plate BL (Wieghardt) | 2D | experimental | Cf(Re_theta), u+(y+) |
| [flat-plate-tbl-3d](../tools/cfdvv/cases/validation/turbulent/flat-plate-tbl-3d/README.md) | Turbulent Flat Plate BL | 3D | experimental | u+(y+), spanwise check |
| [channel-flow-retau180](../tools/cfdvv/cases/validation/turbulent/channel-flow-retau180/README.md) | Turbulent Channel, Re_tau=180 | 3D | DNS (Moser) | u+, u_rms+, v_rms+, w_rms+, -uv+ |
| [channel-flow-retau550](../tools/cfdvv/cases/validation/turbulent/channel-flow-retau550/README.md) | Turbulent Channel, Re_tau=550 | 3D | DNS (Moser) | u+, -uv+ |
| [channel-flow-retau1000](../tools/cfdvv/cases/validation/turbulent/channel-flow-retau1000/README.md) | Turbulent Channel, Re_tau=1000 | 3D | DNS (Lee-Moser) | u+, -uv+ |
| [backward-facing-step-turb](../tools/cfdvv/cases/validation/turbulent/backward-facing-step-turb/README.md) | Turbulent BFS (Driver & Seegmiller) | 2D | experimental | x_r/h, Cf(x/h) |
| [wall-mounted-hump](../tools/cfdvv/cases/validation/turbulent/wall-mounted-hump/README.md) | NASA Wall-Mounted Hump | 2D | experimental | Cp(x/c) |
| [wall-mounted-hump-3d](../tools/cfdvv/cases/validation/turbulent/wall-mounted-hump-3d/README.md) | NASA Wall-Mounted Hump | 3D | experimental | Cp(x/c) |
| [naca0012](../tools/cfdvv/cases/validation/turbulent/naca0012/README.md) | NACA 0012 Airfoil | 2D | experimental | Cl(alpha), Cp(x/c) |
| [naca0012-3d](../tools/cfdvv/cases/validation/turbulent/naca0012-3d/README.md) | NACA 0012 Wing Section | 3D | experimental | Cl, Cp at midspan |
| [rae2822](../tools/cfdvv/cases/validation/turbulent/rae2822/README.md) | RAE 2822 Transonic Airfoil | 2D | experimental | Cp (Case 9 & 10) |
| [rae2822-3d](../tools/cfdvv/cases/validation/turbulent/rae2822-3d/README.md) | RAE 2822 Wing Section | 3D | experimental | Cp at midspan |
| [cylinder-re3900](../tools/cfdvv/cases/validation/turbulent/cylinder-re3900/README.md) | Cylinder, Re=3900 | 3D | experimental | Cd, St, wake profiles |

## Validation --- Non-Newtonian

| ID | Name | Dim | Reference type | Key quantities |
|----|------|-----|----------------|----------------|
| [contraction-oldroyd-b](../tools/cfdvv/cases/validation/non-newtonian/contraction-oldroyd-b/README.md) | Oldroyd-B 4:1 Contraction | 2D | reference (Alves) | X_R, velocity overshoot |

## Validation --- Complex Geometry & FSI

| ID | Name | Dim | Reference type | Key quantities |
|----|------|-----|----------------|----------------|
| [ahmed-body-25](../tools/cfdvv/cases/validation/complex-geometry/ahmed-body-25/README.md) | Ahmed Body, 25 deg slant | 3D | experimental | Cd, Cl |
| [ahmed-body-35](../tools/cfdvv/cases/validation/complex-geometry/ahmed-body-35/README.md) | Ahmed Body, 35 deg slant | 3D | experimental | Cd, Cl |
| [turek-hron-fsi2](../tools/cfdvv/cases/validation/complex-geometry/turek-hron-fsi2/README.md) | FSI2: Flag behind Cylinder | 2D | reference | Ay, f, Cd, Cl_amp |
| [cylinder-viv](../tools/cfdvv/cases/validation/complex-geometry/cylinder-viv/README.md) | VIV Cylinder (Khalak & Williamson) | 2D | experimental | A/D vs Ur |
| [cylinder-viv-3d](../tools/cfdvv/cases/validation/complex-geometry/cylinder-viv-3d/README.md) | VIV Cylinder | 3D | experimental | A/D, spanwise correlation |
