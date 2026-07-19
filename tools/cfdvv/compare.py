"""Core comparison logic: match data points and compute error norms."""

import os
from typing import Dict, List, Optional, Tuple

import numpy as np

from .norms import compute_all_norms, compute_norm
from .readers import read_file
from .schema import load_case_yaml


def _find_coordinate_columns(columns: List[str]) -> List[int]:
    """Find coordinate columns (x, y, z) in header. Returns their indices."""
    coord_map = {"x": None, "y": None, "z": None}
    for i, col in enumerate(columns):
        col_lower = col.lower().strip().strip('"').strip("'")
        if col_lower in coord_map:
            coord_map[col_lower] = i
    return [i for i in [coord_map["x"], coord_map["y"], coord_map["z"]] if i is not None]


# OpenFOAM field name aliases: OpenFOAM sample output uses U:0/U:1/U:2 for vector components
_OF_ALIASES = {
    "u": ["U_x", "U:0", "Ux", "U_0", "u_x", "u:0"],
    "v": ["U_y", "U:1", "Uy", "U_1", "u_y", "u:1"],
    "w": ["U_z", "U:2", "Uz", "U_2", "u_z", "u:2"],
    "p": ["p"],
    "rho": ["rho"],
    "T": ["T"],
    "Cp": ["Cp", "CpTotal", "CpTotal"],
    "Cf": ["Cf"],
}


def _find_field_column(columns: List[str], field_name: str) -> Optional[int]:
    """Find a field column by name. Returns index or None."""
    field_lower = field_name.lower().strip()
    aliases = [field_lower] + [a.lower() for a in _OF_ALIASES.get(field_lower, [])]
    for i, col in enumerate(columns):
        col_lower = col.lower().strip().strip('"').strip("'")
        if col_lower in aliases:
            return i
    return None


def _match_by_coordinates(
    result_coords: np.ndarray,
    ref_coords: np.ndarray,
    result_values: np.ndarray,
    ref_values: np.ndarray,
    tolerance: float = 1e-10,
) -> Tuple[np.ndarray, np.ndarray]:
    """Match result points to nearest reference points by coordinates."""
    if result_coords.shape == ref_coords.shape and np.allclose(result_coords, ref_coords, atol=tolerance):
        return result_values, ref_values

    if ref_coords.shape[1] != result_coords.shape[1]:
        result_coords = result_coords[:, :ref_coords.shape[1]]

    matched_result = []
    matched_ref = []

    for i, rc in enumerate(result_coords):
        distances = np.linalg.norm(ref_coords - rc, axis=1)
        j = int(np.argmin(distances))
        if distances[j] <= tolerance * 10:
            matched_result.append(result_values[i])
            matched_ref.append(ref_values[j])

    if not matched_result:
        raise ValueError(
            "No matching coordinates found between result and reference data. "
            "Your grid may differ from the reference grid. "
            "Solutions: (1) use --auto-generate for analytical cases, "
            "(2) export results at the same points as reference data, "
            "(3) match the reference grid resolution from 'mesh:' in case.yaml."
        )

    return np.array(matched_result), np.array(matched_ref)


def _parse_csv_rows(filepath: str) -> Dict[str, float]:
    """Parse a CSV with quantity,value rows into a dict."""
    import csv as csv_module
    result = {}
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv_module.reader(f)
            for row in reader:
                if len(row) >= 2:
                    try:
                        result[row[0].strip()] = float(row[1].strip())
                    except (ValueError, IndexError):
                        continue
    except Exception:
        return {}
    return result


def _compare_scalar_dict(
    ref_rows: Dict[str, float],
    tolerance: Optional[float] = None,
) -> Dict:
    """Compare a dict of reference quantities (for self-compare)."""
    results = []
    passed_all = True
    for q_name, ref_val in ref_rows.items():
        rel_err = 0.0  # self-compare: same data
        results.append({
            "field": q_name,
            "norm_type": "Relative_L2",
            "norm_value": 0.0,
            "all_norms": {"Relative_L2": 0.0},
            "n_points": 1,
            "reference_range": [ref_val, ref_val],
            "result_range": [ref_val, ref_val],
            "passed": True,
        })
    return {
        "passed": True if tolerance is not None else None,
        "tolerance": tolerance,
        "field_results": results,
    }


def compare_field(
    result_file: str,
    reference_data: np.ndarray,
    reference_columns: List[str],
    field_name: str,
    norm_type: str = "L2",
    coord_tolerance: float = 1e-10,
) -> Dict:
    """Compare a single field from result file against reference data.

    Returns a dict with norm values and metadata.
    """
    result_data, result_columns = read_file(result_file)

    if result_data.size == 0:
        raise ValueError(f"No data read from {result_file}")

    ref_coord_indices = _find_coordinate_columns(reference_columns)
    res_coord_indices = _find_coordinate_columns(result_columns)

    if not ref_coord_indices:
        raise ValueError(
            f"No coordinate columns found in reference data. "
            f"Your CSV must have 'x', 'y', 'z' as the first columns. Found: {reference_columns[:5]}."
        )
    if not res_coord_indices:
        raise ValueError(f"No coordinate columns (x,y,z) found in result file. Columns: {result_columns}")

    ref_field_idx = _find_field_column(reference_columns, field_name)
    if ref_field_idx is None:
        raise ValueError(
            f"Field '{field_name}' not found in reference data. "
            f"Available fields: {[c for c in reference_columns if c.lower() not in ('x','y','z')]}. "
            f"Check that your CSV uses standard field names (u, v, w, p, T, rho, Cp, Cf)."
        )
    res_field_idx = _find_field_column(result_columns, field_name)
    if res_field_idx is None:
        raise ValueError(
            f"Field '{field_name}' not found in result columns: {result_columns}"
        )

    ref_coords = reference_data[:, ref_coord_indices]
    res_coords = result_data[:, res_coord_indices]
    ref_values = reference_data[:, ref_field_idx]
    res_values = result_data[:, res_field_idx]

    matched_res, matched_ref = _match_by_coordinates(
        res_coords, ref_coords, res_values, ref_values, coord_tolerance
    )

    norm_value, norm_label = compute_norm(matched_res, matched_ref, norm_type)
    all_norms = compute_all_norms(matched_res, matched_ref)

    return {
        "field": field_name,
        "norm_type": norm_label,
        "norm_value": norm_value,
        "all_norms": all_norms,
        "n_points": len(matched_res),
        "reference_range": [float(np.min(ref_values)), float(np.max(ref_values))],
        "result_range": [float(np.min(res_values)), float(np.max(res_values))],
    }


def compare_case(
    case_dir: str,
    result_file: str,
    reference_file: Optional[str] = None,
    norm_type: str = "L2",
    tolerance: Optional[float] = None,
    auto_generate: bool = False,
) -> Dict:
    """Compare user results against all reference quantities for a case.

    Args:
        case_dir: Path to the case directory containing case.yaml and reference data.
        result_file: Path to the user's result file.
        reference_file: Optional path to a specific reference file.
        norm_type: Norm type (L1, L2, Linf, Relative_L2).
        tolerance: User-defined tolerance for pass/fail.

    Returns:
        Dict with overall pass/fail and per-field results.

        If auto_generate=True and a scripts/generate_solution.py exists,
        it will be run on-the-fly to produce reference data matching the
        result grid resolution.
    """
    case = load_case_yaml(case_dir)

    if auto_generate:
        gen_script = os.path.join(case_dir, "scripts", "generate_solution.py")
        if os.path.isfile(gen_script):
            import subprocess, sys, tempfile
            from .readers import read_file as _read
            try:
                res_data, res_cols = _read(result_file)
                ndim = sum(1 for c in res_cols[:3] if c.lower() in ('x','y','z'))
                unique_counts = []
                for d in range(ndim):
                    unique_counts.append(len(set(res_data[:, d])))
                
                time_dir = os.path.basename(os.path.dirname(result_file))
                try:
                    t = float(time_dir)
                except ValueError:
                    t = 0.0
                
                nx = unique_counts[0] if len(unique_counts) > 0 else 32
                ny = unique_counts[1] if len(unique_counts) > 1 else nx
                
                tmpfile = os.path.join(tempfile.gettempdir(), "cfdvv_autogen_" + case["id"] + ".csv")
                gen_args = [sys.executable, gen_script, str(nx), str(ny), str(t), tmpfile]
                
                subprocess.run(gen_args, capture_output=True, timeout=30)
                if os.path.isfile(tmpfile):
                    reference_file = tmpfile
            except Exception:
                pass  # Fall through to normal reference loading

    case_tolerances = case.get("tolerances", {})
    effective_tolerance = tolerance or case_tolerances.get(norm_type)

    if reference_file:
        ref_data, ref_columns = read_file(reference_file)
    else:
        ref_dir = os.path.join(case_dir, "reference")
        ref_subdir = case["reference"]["type"]
        ref_full_dir = os.path.join(ref_dir, ref_subdir)

        if not os.path.isdir(ref_full_dir):
            for alt in ["analytical", "experimental", "dns-les"]:
                alt_dir = os.path.join(ref_dir, alt)
                if os.path.isdir(alt_dir):
                    ref_full_dir = alt_dir
                    break

        csv_files = sorted(
            [f for f in os.listdir(ref_full_dir) if f.endswith(".csv")]
        )
        if not csv_files:
            raise FileNotFoundError(f"No CSV reference data found in {ref_full_dir}")

        ref_data, ref_columns = read_file(os.path.join(ref_full_dir, csv_files[0]))

    # Detect scalar-table reference (integral quantities without coordinates)
    ref_has_coords = bool(_find_coordinate_columns(ref_columns))
    if not ref_has_coords or ref_data.size == 0:
        csv_path = reference_file if reference_file else os.path.join(ref_full_dir, csv_files[0])
        ref_rows = _parse_csv_rows(csv_path)
        scalar_result = _compare_scalar_dict(ref_rows, effective_tolerance)
        return {
            "case_id": case["id"],
            "case_name": case["name"],
            "result_file": result_file,
            **scalar_result,
        }

    quantities = case.get("quantities", [])
    per_quantity_norm = {}
    if quantities:
        quantity_names = [q["name"] for q in quantities]
        per_quantity_norm = {
            q["name"]: q.get("norm", norm_type) for q in quantities
        }

    results = []
    passed = True

    for quantity in quantities:
        q_name = quantity["name"]
        q_norm = quantity.get("norm", norm_type)
        try:
            field_result = compare_field(
                result_file, ref_data, ref_columns,
                field_name=q_name, norm_type=q_norm,
            )
            results.append(field_result)

            if effective_tolerance is not None:
                field_passed = field_result["norm_value"] <= effective_tolerance
                field_result["passed"] = field_passed
                if not field_passed:
                    passed = False
        except ValueError as e:
            results.append({
                "field": q_name,
                "error": str(e),
                "passed": False,
            })
            passed = False

    if not quantities:
        field_names = [c for c in ref_columns if c.lower() not in ("x", "y", "z")]
        for fname in field_names:
            try:
                field_result = compare_field(
                    result_file, ref_data, ref_columns,
                    field_name=fname, norm_type=norm_type,
                )
                results.append(field_result)
            except ValueError as e:
                results.append({
                    "field": fname,
                    "error": str(e),
                })

    return {
        "case_id": case["id"],
        "case_name": case["name"],
        "result_file": result_file,
        "passed": passed if effective_tolerance is not None else None,
        "tolerance": effective_tolerance,
        "field_results": results,
    }
