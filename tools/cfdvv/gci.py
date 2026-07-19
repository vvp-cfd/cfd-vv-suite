"""Grid Convergence Index (GCI) computation.

Based on Roache (1994, 1998) and ASME V&V 20 methodology.
"""

from typing import Dict, List, Optional, Tuple

import numpy as np

from .compare import compare_case


def estimate_order(
    mesh_sizes: List[float],
    key_quantities: List[List[float]],
) -> Dict:
    """Estimate observed order of convergence using Richardson extrapolation.

    Args:
        mesh_sizes: Characteristic mesh sizes (h1 > h2 > h3).
        key_quantities: Values of key quantities for each mesh level.
            key_quantities[i] corresponds to mesh_sizes[i].

    Returns:
        Dict with convergence metrics.
    """
    if len(mesh_sizes) < 3 or len(key_quantities) < 3:
        return {
            "error": "Need at least 3 mesh levels for order estimation",
            "order": None,
            "gci": None,
        }

    h = np.array(mesh_sizes, dtype=float)
    r21 = h[0] / h[1]
    r32 = h[1] / h[2]

    results = []
    n_quantities = len(key_quantities[0])
    for qi in range(n_quantities):
        f1 = key_quantities[0][qi]
        f2 = key_quantities[1][qi]
        f3 = key_quantities[2][qi]

        e32 = f3 - f2
        e21 = f2 - f1

        if abs(e32) < 1e-16 and abs(e21) < 1e-16:
            p = float("inf")
        elif abs(e32) < 1e-16:
            p = None
        else:
            p = np.log(abs(e21 / e32)) / np.log(r21)

            if p < 0:
                p = abs(p)

            if np.isnan(p) or np.isinf(p):
                p = None

        f_extrap = None
        if p is not None and p != float("inf"):
            f_extrap = f1 + (f1 - f2) / (r21**p - 1)
        elif p == float("inf"):
            f_extrap = f1

        gci21 = None
        if p is not None and p != float("inf"):
            Fs = 1.25
            gci21 = Fs * abs(e21 / f1) / (r21**p - 1) if abs(f1) > 1e-16 else Fs * abs(e21)

        results.append({
            "quantity_index": qi,
            "f1": f1, "f2": f2, "f3": f3,
            "order_p": float(p) if p is not None and p != float("inf") else (float("inf") if p == float("inf") else None),
            "extrapolated_value": float(f_extrap) if f_extrap is not None else None,
            "gci21": float(gci21) if gci21 is not None else None,
        })

    return {
        "mesh_sizes": mesh_sizes,
        "refinement_ratios": [float(r21), float(r32)],
        "quantity_results": results,
    }


def compute_gci(
    case_dir: str,
    result_files: List[str],
    mesh_sizes: Optional[List[float]] = None,
    quantity_name: Optional[str] = None,
) -> Dict:
    """Compute GCI from multiple result files on different meshes.

    Args:
        case_dir: Path to the case directory.
        result_files: List of result files (coarse, medium, fine).
        mesh_sizes: Optional list of characteristic mesh sizes.
        quantity_name: Optional specific quantity name.

    Returns:
        Dict with GCI analysis results.
    """
    if len(result_files) < 3:
        return {"error": "Need at least 3 result files for GCI"}

    if mesh_sizes is None:
        mesh_sizes = [1.0, 0.5, 0.25]

    key_values = []
    for rf in result_files:
        comp = compare_case(case_dir, rf)
        vals = []
        for fr in comp["field_results"]:
            if quantity_name is None or fr["field"] == quantity_name:
                vals.append(fr["norm_value"])
        if not vals:
            vals = [0.0]
        key_values.append(vals)

    gci_result = estimate_order(mesh_sizes, key_values)
    gci_result["case_dir"] = case_dir
    gci_result["result_files"] = result_files

    return gci_result
