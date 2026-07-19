import numpy as np, csv, sys
nx = int(sys.argv[1]) if len(sys.argv) > 1 else 32
ny = int(sys.argv[2]) if len(sys.argv) > 2 else nx
t = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
out = sys.argv[4] if len(sys.argv) > 4 else 'analytical_solution.csv'

L = 2*np.pi; nu = 0.01
x = np.linspace(0, L, nx)
y = np.linspace(0, L, ny)
X, Y = np.meshgrid(x, y)
u = -np.cos(X)*np.sin(Y)*np.exp(-2*nu*t)
v = np.sin(X)*np.cos(Y)*np.exp(-2*nu*t)
p = -0.25*(np.cos(2*X)+np.cos(2*Y))*np.exp(-4*nu*t)

with open(out, 'w', newline='') as f:
    w = csv.writer(f)
    if ny == 1 and nx > 1:
        w.writerow(['x', 'u', 'v', 'p'])
        for j in range(nx):
            w.writerow([X[0,j], u[0,j], v[0,j], p[0,j]])
    elif nx == 1 and ny > 1:
        w.writerow(['y', 'u', 'v', 'p'])
        for i in range(ny):
            w.writerow([Y[i,0], u[i,0], v[i,0], p[i,0]])
    else:
        w.writerow(['x', 'y', 'u', 'v', 'p'])
        for i in range(ny):
            for j in range(nx):
                w.writerow([X[i,j], Y[i,j], u[i,j], v[i,j], p[i,j]])
print(f'Written {out} ({nx}x{ny}) t={t}')
