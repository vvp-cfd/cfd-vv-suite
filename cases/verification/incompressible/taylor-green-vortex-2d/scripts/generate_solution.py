import numpy as np, csv, sys
n = int(sys.argv[1]) if len(sys.argv) > 1 else 32
out = sys.argv[2] if len(sys.argv) > 2 else 'analytical_solution.csv'

L = 2*np.pi; nu = 0.01; t = 0.0
x = np.linspace(0, L, n)
X, Y = np.meshgrid(x, x)
u = -np.cos(X)*np.sin(Y)*np.exp(-2*nu*t)
v = np.sin(X)*np.cos(Y)*np.exp(-2*nu*t)
p = -0.25*(np.cos(2*X)+np.cos(2*Y))*np.exp(-4*nu*t)

with open(out, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['x', 'y', 'u', 'v', 'p'])
    for i in range(n):
        for j in range(n):
            w.writerow([X[i,j], Y[i,j], u[i,j], v[i,j], p[i,j]])
print(f'Written {out} ({n}x{n})')
