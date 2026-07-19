import numpy as np, csv, sys
n = int(sys.argv[1]) if len(sys.argv) > 1 else 21
out = sys.argv[2] if len(sys.argv) > 2 else 'beltrami_solution.csv'

L = 2*np.pi
x = np.linspace(0, L, n)
X, Y, Z = np.meshgrid(x, x, x, indexing='ij')
u = np.sin(Y) - np.cos(Z)
v = np.sin(Z) - np.cos(X)
w = np.sin(X) - np.cos(Y)
p = -(np.sin(X)*np.cos(Y)+np.sin(Y)*np.cos(Z)+np.sin(Z)*np.cos(X))

with open(out, 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['x','y','z','u','v','w','p'])
    for i in range(n):
        for j in range(n):
            for k in range(n):
                w.writerow([X[i,j,k], Y[i,j,k], Z[i,j,k], u[i,j,k], v[i,j,k], w[i,j,k], p[i,j,k]])
print(f'Written {out} ({n}^3 = {n**3} points)')
