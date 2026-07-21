# Using cfdvv from Jupyter

Import the Python API directly — no shell commands needed.

> **Demo notebook:** [`cfdvv-demo.ipynb`](https://github.com/vvp-cfd/cfd-vv-suite/blob/main/example/cfdvv-demo.ipynb) — a complete, runnable walkthrough of all features (Colab-ready).

```python
# Import comparison tools
import os, cfdvv
from cfdvv.compare import compare_case
from cfdvv.readers import read_file
from cfdvv.plot import plot_comparison
from cfdvv.gci import compute_gci
from cfdvv.schema import load_case_yaml
from cfdvv.norms import compute_all_norms
import numpy as np

# Cases are bundled in the installed package
CASES = os.path.join(os.path.dirname(cfdvv.__file__), "cases")
print(f"cfdvv {cfdvv.__version__}  |  {CASES}")
```

## Compare a result against a case

```python
case_dir = os.path.join(CASES, "verification", "incompressible", "poiseuille-2d")

result = compare_case(case_dir, "my_results.csv", norm_type="L2")

print(f"PASSED: {result['passed']}")
for fr in result["field_results"]:
    if "error" not in fr:
        print(f"  {fr['field']}: L2 = {fr['norm_value']:.4e}")
```

## Inspect a case

```python
case = load_case_yaml(
    os.path.join(CASES, "verification", "incompressible", "poiseuille-2d")
)

print(f"{case['name']} ({case['id']})")
print(f"Dimension:  {case['dimension']}")
print(f"Reference:  {case['reference']['type']} — {case['reference']['solution']}")
print(f"Mesh:       {case['mesh']['recommended']}")

for q in case["quantities"]:
    print(f"  {q['name']}: type={q['type']}, norm={q.get('norm', 'L2')}")
```

## Generate a comparison plot

```python
ref_data, ref_columns = read_file(
    os.path.join(CASES, "verification", "incompressible",
                 "poiseuille-2d", "reference", "analytical", "solution.csv")
)

filepath = plot_comparison(
    "my_results.csv", ref_data, ref_columns,
    field_name="u", output_dir=".", case_id="poiseuille-2d",
)
print(f"Plot saved: {filepath}")
```

## Display a plot inline

```python
from IPython.display import Image, display
display(Image("poiseuille-2d_u.png"))
```

## GCI analysis

```python
result = compute_gci(
    os.path.join(CASES, "verification", "incompressible", "poiseuille-2d"),
    ["coarse.csv", "medium.csv", "fine.csv"],
    mesh_sizes=[0.05, 0.025, 0.0125],
)

for qr in result["quantity_results"]:
    print(f"p = {qr['order_p']:.2f}, GCI = {qr['gci21']:.4f}")
```

## Scan all cases

```python
import glob

for yf in sorted(glob.glob(os.path.join(CASES, "**", "case.yaml"), recursive=True)):
    case = load_case_yaml(os.path.dirname(yf))
    # ... do something with each case
```

## Error norms

```python
computed  = np.array([1.0, 2.0, 3.0])
reference = np.array([1.1, 1.9, 3.2])

# All norms at once
norms = compute_all_norms(computed, reference)
print(norms)

# Or individually
from cfdvv.norms import l2_norm, l1_norm, linf_norm, relative_l2_norm
print(f"L2:        {l2_norm(computed, reference):.4e}")
print(f"L1:        {l1_norm(computed, reference):.4e}")
print(f"Linf:      {linf_norm(computed, reference):.4e}")
print(f"Rel. L2:   {relative_l2_norm(computed, reference):.4e}")
```
