# Generate Poiseuille analytical solution on a given mesh
import numpy as np, csv, sys

# Usage: python generate_solution.py <nx> <ny> [output.csv]
nx, ny = int(sys.argv[1]), int(sys.argv[2])
out = sys.argv[3] if len(sys.argv) > 3 else 'analytical_solution.csv'

H, L, mu, G = 1.0, 10.0, 1.0, 1.0
y = np.linspace(0, H, ny)
u = (G/(2*mu)) * y * (H - y)

with open(out, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['x', 'y', 'u', 'v', 'p'])
    for yi, ui in zip(y, u):
        w.writerow([0.5*L, yi, ui, 0.0, 0.0])
print(f'Written {out}')
