"""File readers for CFD data formats: CSV, VTK/VTU, OpenFOAM."""

import csv
import os
from typing import Dict, List, Optional, Tuple

import numpy as np


def _find_data_row(lines: List[str], delimiter: str = ",") -> int:
    """Find the first row that looks like numeric data."""
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = stripped.split(delimiter)
        try:
            for p in parts:
                float(p.strip())
            return i
        except ValueError:
            continue
    return len(lines)


def _parse_header(lines: List[str], data_start: int, delimiter: str = ",") -> List[str]:
    """Extract column names from comments above data or from the row just before data."""
    if data_start == 0:
        return [f"col_{i}" for i in range(100)]

    header_candidate = lines[data_start - 1].strip()
    header_parts = header_candidate.split(delimiter)
    try:
        for p in header_parts:
            float(p.strip())
        return [f"col_{i}" for i in range(100)]
    except ValueError:
        return [p.strip().strip('"') for p in header_parts]


def read_csv(filepath: str) -> Tuple[np.ndarray, List[str]]:
    """Read a CSV file. Returns (data_array, column_names)."""
    with open(filepath, "r", encoding="utf-8-sig") as f:
        lines = f.readlines()

    delimiter = ","
    if not lines:
        return np.array([]), []

    data_start = _find_data_row(lines, delimiter)
    headers = _parse_header(lines, data_start, delimiter)

    rows = []
    for line in lines[data_start:]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = stripped.split(delimiter)
        try:
            rows.append([float(p.strip()) for p in parts])
        except ValueError:
            continue

    data = np.array(rows) if rows else np.array([])
    return data, headers


def read_vtk(filepath: str) -> Tuple[np.ndarray, List[str]]:
    """Read VTK/VTU files using meshio. Returns (points_with_fields, field_names)."""
    try:
        import meshio
    except ImportError:
        raise ImportError(
            "meshio is required for VTK support. Install with: pip install meshio"
        )

    mesh = meshio.read(filepath)

    all_data: Dict[str, np.ndarray] = {}

    if mesh.points is not None:
        ndim = mesh.points.shape[1]
        for i in range(ndim):
            col_name = ["x", "y", "z"][i]
            all_data[col_name] = mesh.points[:, i]

    for location in ["point_data", "cell_data"]:
        data_dict = getattr(mesh, location, {})
        for name, arr in data_dict.items():
            if isinstance(arr, np.ndarray):
                if arr.ndim == 2 and arr.shape[1] > 1:
                    for j in range(arr.shape[1]):
                        all_data[f"{name}_{j}"] = arr[:, j]
                elif arr.ndim == 1:
                    all_data[name] = arr

    if not all_data:
        raise ValueError(f"No data found in {filepath}")

    min_len = min(len(v) for v in all_data.values())
    columns = list(all_data.keys())
    data_matrix = np.column_stack([all_data[col][:min_len] for col in columns])

    return data_matrix, columns


def read_openfoam_field(filepath: str) -> Tuple[np.ndarray, List[str]]:
    """Read an OpenFOAM field file (U, p, k, etc.) in raw format.

    Parses the internalField section. Returns (values, [field_name]).
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    values = []
    in_internal = False
    value_count = 0

    for line in content.split("\n"):
        stripped = line.strip()

        if stripped.startswith("internalField"):
            in_internal = True
            if "nonuniform" in stripped:
                value_count = int(stripped.split("nonuniform")[1].split("(")[0].strip())
            continue

        if not in_internal:
            continue

        if stripped == ")":
            break

        if stripped == "(" or stripped == ";":
            continue

        for token in stripped.replace("(", " ").replace(")", " ").split():
            try:
                values.append(float(token))
            except ValueError:
                pass

    if not values:
        raise ValueError(f"No internalField values found in {filepath}")

    field_name = os.path.basename(os.path.dirname(filepath))
    return np.array(values), [field_name]


def read_file(filepath: str) -> Tuple[np.ndarray, List[str]]:
    """Auto-detect format and read. Returns (data_array, column_names)."""
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".csv":
        return read_csv(filepath)
    elif ext in (".vtk", ".vtu", ".vtp", ".vts", ".vtr", ".vti"):
        return read_vtk(filepath)
    elif os.path.basename(os.path.splitext(filepath)[0]) in ("U", "p", "k", "omega", "epsilon", "nut", "nuTilda"):
        return read_openfoam_field(filepath)
    else:
        try:
            return read_csv(filepath)
        except Exception:
            raise ValueError(f"Unsupported file format: {filepath}")
