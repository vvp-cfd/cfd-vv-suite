import numpy as np, csv, sys
ny = int(sys.argv[1]) if len(sys.argv) > 1 else 51
out = sys.argv[2] if len(sys.argv) > 2 else 'analytical_solution.csv'

H, U0, L = 1.0, 1.0, 4.0
y = np.linspace(0, H, ny)
u = U0 * y / H
with open(out, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['x', 'y', 'u', 'v', 'p'])
    for yi, ui in zip(y, u):
        w.writerow([0.5*L, yi, ui, 0.0, 0.0])
print(f'Written {out}')
