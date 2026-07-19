# MMS Generation Guide

This document explains how manufactured solutions (MMS) are generated for cfd-vv-suite and how contributors can add new MMS cases.

## What is MMS

The Method of Manufactured Solutions (MMS) is a code verification technique:

1. Choose an analytical function for the solution (u, v, w, p)
2. Substitute it into the governing PDEs
3. The residual becomes a source term
4. Add the source term to the solver
5. Verify that the solver recovers the manufactured solution

## MMS cases in cfd-vv-suite

### manufactured-ns-2d

**Manufactured solution:**
```
u(x,y) = sin(pi*x) * cos(pi*y)
v(x,y) = -cos(pi*x) * sin(pi*y)
p(x,y) = sin(pi*x) * sin(pi*y)
nu = 0.1, domain [0,1]^2
```

**Properties:** Exactly divergence-free (div u = 0).

**Source term derivation:**

The Navier-Stokes x-momentum equation:
```
u*du/dx + v*du/dy + dp/dx - nu*(d^2u/dx^2 + d^2u/dy^2) = S_u
```

Substituting the manufactured solution:
```
du/dx = pi*cos(pi*x)*cos(pi*y)
du/dy = -pi*sin(pi*x)*sin(pi*y)
d^2u/dx^2 = d^2u/dy^2 = -pi^2*u
dp/dx = pi*cos(pi*x)*sin(pi*y)
```

Therefore:
```
S_u = u*du/dx + v*du/dy + dp/dx - nu*(d^2u/dx^2 + d^2u/dy^2)
S_v = u*dv/dx + v*dv/dy + dp/dy - nu*(d^2v/dx^2 + d^2v/dy^2)
S_p = 0  (continuity satisfied exactly)
```

**Generation script:** `scripts/generate_solution.py`
```bash
python scripts/generate_solution.py <nx> <ny> [solution.csv] [source_terms.csv]
```

### manufactured-ns-3d

**Manufactured solution:**
```
u(x,y,z) = sin(pi*x) * cos(pi*y) * cos(pi*z)
v(x,y,z) = cos(pi*x) * sin(pi*y) * cos(pi*z)
w(x,y,z) = -2*cos(pi*x) * cos(pi*y) * sin(pi*z)
p(x,y,z) = sin(pi*x) * sin(pi*y) * sin(pi*z)
nu = 0.1, domain [0,1]^3
```

**Properties:** div u = sin*c*c + c*sin*c + (-2*c*c*sin) = ... let's verify:
∂u/∂x = pi*cos(pi*x)*cos(pi*y)*cos(pi*z)
∂v/∂y = pi*cos(pi*x)*cos(pi*y)*cos(pi*z)
∂w/∂z = -2*pi*cos(pi*x)*cos(pi*y)*cos(pi*z)
Sum = pi*c*c*c + pi*c*c*c - 2*pi*c*c*c = 0 v

**Source terms:** Derived symbolically and verified. See `reference/mms/source_terms.csv`.

### beltrami-flow-3d (exact solution, no source terms needed)

Not technically MMS --- this is an exact steady solution:
```
u = sin(y) - cos(z)
v = sin(z) - cos(x)
w = sin(x) - cos(y)
p = -(sin(x)cos(y) + sin(y)cos(z) + sin(z)cos(x))
```
The Beltrami property curl(u) = u means (u·grad)u = -gradp exactly, so no source terms are needed.

## How to create a new MMS case

### 1. Design the manufactured solution

Requirements:
- Must be smooth (infinitely differentiable)
- Should exercise all terms of the PDE (convection, diffusion, pressure, ...)
- Choose a divergence-free velocity field for incompressible flows
- Avoid solutions that make any term identically zero
- Use trigonometric functions for periodic problems
- Use polynomials for bounded non-periodic domains

### 2. Compute source terms

Use symbolic differentiation (recommended: SymPy):

```python
import sympy as sp

x, y, nu = sp.symbols('x y nu')
pi = sp.pi

# Define manufactured solution
u = sp.sin(pi*x) * sp.cos(pi*y)
v = -sp.cos(pi*x) * sp.sin(pi*y)
p = sp.sin(pi*x) * sp.sin(pi*y)

# Compute derivatives
dudx = sp.diff(u, x)
dudy = sp.diff(u, y)
d2udx2 = sp.diff(u, x, 2)
d2udy2 = sp.diff(u, y, 2)

dvdx = sp.diff(v, x)
dvdy = sp.diff(v, y)
d2vdx2 = sp.diff(v, x, 2)
d2vdy2 = sp.diff(v, y, 2)

dpdx = sp.diff(p, x)
dpdy = sp.diff(p, y)

# Source terms
Su = u*dudx + v*dudy + dpdx - nu*(d2udx2 + d2udy2)
Sv = u*dvdx + v*dvdy + dpdy - nu*(d2vdx2 + d2vdy2)

# Simplify
Su = sp.simplify(Su)
Sv = sp.simplify(Sv)

print(f"S_u = {Su}")
print(f"S_v = {Sv}")

# Export as Python functions
Su_func = sp.lambdify((x, y, nu), Su, 'numpy')
Sv_func = sp.lambdify((x, y, nu), Sv, 'numpy')
```

### 3. Verify divergence

```python
div = sp.simplify(sp.diff(u, x) + sp.diff(v, y))
print(f"div(u) = {div}")  # Should be 0
```

### 4. Generate reference data

Use the `scripts/generate_solution.py` template pattern:

```python
import numpy as np, csv, sys

n = int(sys.argv[1])  # grid resolution
x = np.linspace(0, 1, n)
X, Y = np.meshgrid(x, x)

# Evaluate fields
u = ...  # manufactured solution
v = ...
p = ...

# Write CSV
with open('solution.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['x', 'y', 'u', 'v', 'p'])
    for i in range(n):
        for j in range(n):
            w.writerow([X[i,j], Y[i,j], u[i,j], v[i,j], p[i,j]])
```

### 5. Follow the case template

See `templates/case-template/` for the full case structure:

```
my-mms-case/
+-- case.yaml
+-- README.md
+-- reference/
|   +-- mms/
|       +-- solution.csv
|       +-- source_terms.csv
+-- scripts/
    +-- generate_solution.py
```

## References

1. Roache, P.J. *Verification and Validation in Computational Science and Engineering*, Hermosa, 1998
2. Oberkampf, W.L. & Roy, C.J. *Verification and Validation in Scientific Computing*, Cambridge, 2010
3. Salari, K. & Knupp, P. "Code Verification by the Method of Manufactured Solutions", SAND2000-1444, 2000
