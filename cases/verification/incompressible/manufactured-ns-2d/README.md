# Manufactured Solution --- Navier-Stokes (2D)

## Purpose

Method of Manufactured Solutions (MMS) for rigorous code verification. A known solution is substituted into the PDEs; the residual becomes prescribed source terms. The solver is then tested on whether it reproduces the manufactured solution when source terms are added.

## Manufactured Solution

```
u(x,y) =  sin(πx)·cos(πy)
v(x,y) = -cos(πx)·sin(πy)
p(x,y) =  sin(πx)·sin(πy)
```

Domain: [0,1]^2, nu = 0.1

This solution satisfies grad·u = 0 exactly (divergence-free).

## Source Terms (Forcing Functions)

The manufactured solution does NOT satisfy the Navier-Stokes equations without additional forcing. The user must add these source terms into the momentum equations:

```
S_u = u·∂u/∂x + v·∂u/∂y + ∂p/∂x - nu·grad^2u
S_v = u·∂v/∂x + v·∂v/∂y + ∂p/∂y - nu·grad^2v
```

Evaluated analytically and provided in `reference/mms/source_terms.csv`.

## Boundary Conditions

All boundaries: Dirichlet from the manufactured solution (no-slip equivalent).

## Verification Procedure

1. Generate meshes: 21^2, 41^2, 81^2, 161^2
2. Run solver with source terms added
3. Compare u, v, p against reference
4. Compute observed order of convergence: p = log(E_h/E_h/2) / log(2)

Expected: second order for central schemes, first order for upwind schemes.

## Reference Data

- `reference/mms/solution.csv`: u, v, p on 51^2 grid
- `reference/mms/source_terms.csv`: S_u, S_v on 51^2 grid

## References

1. Roache, P.J. *Verification and Validation in Computational Science and Engineering*, Hermosa, 1998
2. Oberkampf, W.L. & Roy, C.J. *Verification and Validation in Scientific Computing*, Cambridge, 2010
3. Salari, K. & Knupp, P. "Code Verification by the Method of Manufactured Solutions", SAND2000-1444, 2000
