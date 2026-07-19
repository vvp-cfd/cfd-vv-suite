import math, os

L = 2 * math.pi
nx = 64
ny = 64
h = L / nx

lines = [
    'FoamFile { version 2.0; format ascii; class volVectorField; object U; }',
    'dimensions [0 1 -1 0 0 0 0];',
    'internalField nonuniform List<vector> ' + str(nx * ny) + '('
]
for j in range(ny):
    for i in range(nx):
        xc = (i + 0.5) * h
        yc = (j + 0.5) * h
        ux = -math.cos(xc) * math.sin(yc)
        uy = math.sin(xc) * math.cos(yc)
        lines.append('({:.10g} {:.10g} 0)'.format(ux, uy))
lines += [
    ');',
    'boundaryField {',
    '    cyc_x0 { type cyclic; }',
    '    cyc_x1 { type cyclic; }',
    '    cyc_y0 { type cyclic; }',
    '    cyc_y1 { type cyclic; }',
    '    frontAndBack { type empty; }',
    '}'
]
with open('0/U', 'w') as f:
    f.write('\n'.join(lines) + '\n')
