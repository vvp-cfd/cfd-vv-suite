import numpy as np, csv, sys
n = int(sys.argv[1]) if len(sys.argv) > 1 else 41
out_sol = sys.argv[2] if len(sys.argv) > 2 else 'mms_solution.csv'
out_src = sys.argv[3] if len(sys.argv) > 3 else 'mms_source_terms.csv'

pi = np.pi; nu = 0.1
x = np.linspace(0, 1, n)
X, Y = np.meshgrid(x, x)
u = np.sin(pi*X)*np.cos(pi*Y)
v = -np.cos(pi*X)*np.sin(pi*Y)
p = np.sin(pi*X)*np.sin(pi*Y)

dudx = pi*np.cos(pi*X)*np.cos(pi*Y)
dudy = -pi*np.sin(pi*X)*np.sin(pi*Y)
d2udx2 = -pi**2*u; d2udy2 = -pi**2*u
dvdx = pi*np.sin(pi*X)*np.sin(pi*Y)
dvdy = -pi*np.cos(pi*X)*np.cos(pi*Y)
d2vdx2 = -pi**2*v; d2vdy2 = -pi**2*v
dpdx = pi*np.cos(pi*X)*np.sin(pi*Y)
dpdy = pi*np.sin(pi*X)*np.cos(pi*Y)
Su = u*dudx + v*dudy + dpdx - nu*(d2udx2 + d2udy2)
Sv = u*dvdx + v*dvdy + dpdy - nu*(d2vdx2 + d2vdy2)

with open(out_sol, 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['x','y','u','v','p'])
    for i in range(n):
        for j in range(n):
            w.writerow([X[i,j], Y[i,j], u[i,j], v[i,j], p[i,j]])
with open(out_src, 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['x','y','S_u','S_v','S_p'])
    for i in range(n):
        for j in range(n):
            w.writerow([X[i,j], Y[i,j], Su[i,j], Sv[i,j], 0.0])
print(f'Written {out_sol}, {out_src}')
