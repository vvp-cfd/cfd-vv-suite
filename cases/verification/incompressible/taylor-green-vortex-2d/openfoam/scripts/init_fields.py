#!/usr/bin/env python3
"""Generate Taylor-Green initial conditions as OpenFOAM field files.

Reads blockMeshDict to get mesh size, then writes 0/U and 0/p
with the analytical Taylor-Green vortex solution at t=0.

Usage: python3 init_fields.py [case_dir]
"""
import os, re, math, sys

case_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

bmd_path = os.path.join(case_dir, "system", "blockMeshDict")
with open(bmd_path) as f:
    bmd = f.read()

m = re.search(r'\((\d+)\s+(\d+)\s+\d+\)', bmd)
if not m:
    raise ValueError(f"Cannot find mesh dimensions in {bmd_path}")
nx, ny = int(m.group(1)), int(m.group(2))
L = 2.0 * math.pi
hx = L / nx
hy = L / ny
n = nx * ny

def _header(cls, obj):
    return (
        'FoamFile { version 2.0; format ascii; class ' + cls + '; object ' + obj + '; }',
        'dimensions [0 1 -1 0 0 0 0];' if obj == 'U' else 'dimensions [0 2 -2 0 0 0 0];',
    )

def _bc_block():
    return (
        'boundaryField',
        '{',
        '    cyc_x0  { type cyclic; }',
        '    cyc_x1  { type cyclic; }',
        '    cyc_y0  { type cyclic; }',
        '    cyc_y1  { type cyclic; }',
        '    frontAndBack { type empty; }',
        '}',
    )

# --- U field ---
lines = []
lines.extend(_header('volVectorField', 'U'))
lines.append(f'internalField nonuniform List<vector> {n}(')
for j in range(ny):
    for i in range(nx):
        xc = (i + 0.5) * hx
        yc = (j + 0.5) * hy
        ux = -math.cos(xc) * math.sin(yc)
        uy = math.sin(xc) * math.cos(yc)
        lines.append(f'({ux:.10g} {uy:.10g} 0)')
lines.append(');')
lines.extend(_bc_block())
lines.append('')

os.makedirs(os.path.join(case_dir, '0'), exist_ok=True)
with open(os.path.join(case_dir, '0', 'U'), 'w') as f:
    f.write('\n'.join(lines))

# --- p field ---
lines = []
lines.extend(_header('volScalarField', 'p'))
lines.append(f'internalField nonuniform List<scalar> {n}(')
for j in range(ny):
    for i in range(nx):
        xc = (i + 0.5) * hx
        yc = (j + 0.5) * hy
        lines.append(str(-0.25 * (math.cos(2*xc) + math.cos(2*yc))))
lines.append(');')
lines.extend(_bc_block())
lines.append('')

with open(os.path.join(case_dir, '0', 'p'), 'w') as f:
    f.write('\n'.join(lines))

print(f'Initialized Taylor-Green fields: {nx}x{ny}')
