"""Plotting utilities for comparison visualization."""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

from .compare import _find_coordinate_columns, _find_field_column, _match_by_coordinates
from .readers import read_file


def _setup_matplotlib():
    """Configure matplotlib for headless environments."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        return plt
    except ImportError:
        raise ImportError(
            "matplotlib is required for plotting. Install with: pip install cfdvv[plot]"
        )


def plot_comparison(
    result_file: str,
    reference_data: np.ndarray,
    reference_columns: List[str],
    field_name: str,
    output_dir: str,
    case_id: str = "",
) -> str:
    """Generate comparison plots and save to output_dir."""
    plt = _setup_matplotlib()

    result_data, result_columns = read_file(result_file)

    ref_coord_indices = _find_coordinate_columns(reference_columns)
    res_coord_indices = _find_coordinate_columns(result_columns)
    ref_field_idx = _find_field_column(reference_columns, field_name)
    res_field_idx = _find_field_column(result_columns, field_name)

    if ref_field_idx is None or res_field_idx is None:
        raise ValueError(f"Field '{field_name}' not found in data")

    ref_coords = reference_data[:, ref_coord_indices]
    res_coords = result_data[:, res_coord_indices]
    ref_values = reference_data[:, ref_field_idx]
    res_values = result_data[:, res_field_idx]

    matched_res, matched_ref = _match_by_coordinates(
        res_coords, ref_coords, ref_values, res_values
    )

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    ndim = len(ref_coord_indices)

    fig, axes = plt.subplots(1, 3 if ndim >= 1 else 1, figsize=(15, 5))
    if ndim == 1:
        axes = [axes]
    axes = list(axes)

    if ndim == 1:
        x_ref = ref_coords[:, 0]
        x_res = res_coords[:, 0]
        axes[0].plot(x_ref, ref_values, "k-", linewidth=2, label="Reference")
        axes[0].plot(x_res, res_values, "ro", markersize=4, label="Computed")
        axes[0].set_xlabel("x")
    elif ndim >= 2:
        sc = axes[0].scatter(
            ref_coords[:, 0], ref_coords[:, 1],
            c=ref_values, cmap="viridis", s=2,
        )
        plt.colorbar(sc, ax=axes[0])
        axes[0].set_title("Reference")
        sc2 = axes[1].scatter(
            res_coords[:, 0], res_coords[:, 1],
            c=res_values, cmap="viridis", s=2,
        )
        plt.colorbar(sc2, ax=axes[1])
        axes[1].set_title("Computed")

    axes[-1].scatter(matched_ref, matched_res, s=2, alpha=0.6)
    min_val = min(matched_ref.min(), matched_res.min())
    max_val = max(matched_ref.max(), matched_res.max())
    axes[-1].plot([min_val, max_val], [min_val, max_val], "k--", linewidth=1)
    axes[-1].set_xlabel("Reference")
    axes[-1].set_ylabel("Computed")
    axes[-1].set_title(f"Scatter: {field_name}")

    fig.suptitle(f"{case_id} - {field_name}")
    plt.tight_layout()

    filename = f"{case_id}_{field_name}.png" if case_id else f"{field_name}.png"
    filepath = os.path.join(output_dir, filename)
    fig.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close(fig)

    return filepath


def plot_profile(
    reference_data: np.ndarray,
    reference_columns: List[str],
    field_name: str,
    coordinate_name: str = "y",
    output_file: Optional[str] = None,
    result_data: Optional[np.ndarray] = None,
    result_columns: Optional[List[str]] = None,
    label_ref: str = "Reference",
    label_result: str = "Computed",
) -> str:
    """Plot a 1D profile of a field along a coordinate axis."""
    plt = _setup_matplotlib()

    ref_coord_indices = _find_coordinate_columns(reference_columns)
    ref_field_idx = _find_field_column(reference_columns, field_name)

    coord_lower = coordinate_name.lower()
    coord_map = {"x": 0, "y": 1, "z": 2}
    coord_idx = None
    for i, ci in enumerate(ref_coord_indices):
        if ref_columns[ci].lower() == coord_lower:
            coord_idx = i
            break

    if coord_idx is None:
        if len(ref_coord_indices) > coord_map.get(coord_lower, 0):
            coord_idx = coord_map.get(coord_lower, 0)
        else:
            coord_idx = 0

    ref_coord = reference_data[:, ref_coord_indices[coord_idx]]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(ref_coord, reference_data[:, ref_field_idx], "k-", linewidth=2, label=label_ref)

    if result_data is not None and result_columns is not None:
        res_coord_indices = _find_coordinate_columns(result_columns)
        res_field_idx = _find_field_column(result_columns, field_name)
        if res_field_idx is not None:
            res_coord = result_data[:, res_coord_indices[coord_idx]]
            ax.plot(res_coord, result_data[:, res_field_idx], "ro--", markersize=4, label=label_result)

    ax.set_xlabel(coordinate_name)
    ax.set_ylabel(field_name)
    ax.set_title(f"{field_name} profile")
    ax.legend()
    ax.grid(True, alpha=0.3)

    if output_file:
        Path(os.path.dirname(output_file) or ".").mkdir(parents=True, exist_ok=True)
        fig.savefig(output_file, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return output_file

    plt.close(fig)
    return ""
