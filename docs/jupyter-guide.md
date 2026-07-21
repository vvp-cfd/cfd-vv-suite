# Using cfdvv from Jupyter

Import the Python API directly — no shell commands needed.

```python
# Import comparison tools
from cfdvv.compare import compare_case
from cfdvv.readers import read_file
from cfdvv.plot import plot_comparison
from cfdvv.gci import compute_gci
import numpy as np
```

## Compare a result against a case

```python
result = compare_case(
    "tools/cfdvv/cases/verification/incompressible/poiseuille-2d",
    "my_results.csv",
    norm_type="L2",
)

print(f"PASSED: {result['passed']}")
for fr in result["field_results"]:
    if "error" not in fr:
        print(f"  {fr['field']}: L2 = {fr['norm_value']:.4e}")
```

## Generate a comparison plot

```python
ref_data, ref_columns = read_file(
    "tools/cfdvv/cases/verification/incompressible/poiseuille-2d/reference/analytical/solution.csv"
)

filepath = plot_comparison(
    "my_results.csv",
    ref_data, ref_columns,
    field_name="u",
    output_dir=".",
    case_id="poiseuille-2d",
)
print(f"Plot saved: {filepath}")
```

## Display a plot inline

```python
from IPython.display import Image
Image("poiseuille-2d_u.png")
```

## GCI analysis

```python
result = compute_gci(
    "tools/cfdvv/cases/verification/incompressible/poiseuille-2d",
    ["coarse.csv", "medium.csv", "fine.csv"],
    mesh_sizes=[0.05, 0.025, 0.0125],
)

for qr in result["quantity_results"]:
    print(f"p = {qr['order_p']:.2f}, GCI = {qr['gci21']:.4f}")
```

## Scan all cases

```python
import glob, os

for yaml_file in sorted(glob.glob("tools/cfdvv/cases/**/case.yaml", recursive=True)):
    case_dir = os.path.dirname(yaml_file)
    # ... do something with each case
```

## Error norms

```python
from cfdvv.norms import l2_norm, l1_norm, linf_norm, relative_l2_norm

computed = np.array([1.0, 2.0, 3.0])
reference = np.array([1.1, 1.9, 3.2])

print(f"L2:        {l2_norm(computed, reference):.4e}")
print(f"L1:        {l1_norm(computed, reference):.4e}")
print(f"Linf:      {linf_norm(computed, reference):.4e}")
print(f"Rel. L2:   {relative_l2_norm(computed, reference):.4e}")
```
