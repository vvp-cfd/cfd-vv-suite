"""Error norms: L1, L2, Linf, relative, RMSE."""

from typing import Tuple

import numpy as np


def l1_norm(computed: np.ndarray, reference: np.ndarray) -> float:
    """L1 norm: mean(abs(computed - reference))."""
    return float(np.mean(np.abs(computed - reference)))


def l2_norm(computed: np.ndarray, reference: np.ndarray) -> float:
    """L2 (Euclidean) norm: sqrt(mean((computed - reference)**2))."""
    return float(np.sqrt(np.mean((computed - reference) ** 2)))


def linf_norm(computed: np.ndarray, reference: np.ndarray) -> float:
    """L-infinity (maximum) norm: max(abs(computed - reference))."""
    return float(np.max(np.abs(computed - reference)))


def relative_l2_norm(computed: np.ndarray, reference: np.ndarray) -> float:
    """Relative L2 norm: L2(computed - reference) / L2(reference)."""
    num = l2_norm(computed, reference)
    den = float(np.sqrt(np.mean(reference**2)))
    return num / den if den > 1e-16 else num


def rmse(computed: np.ndarray, reference: np.ndarray) -> float:
    """Root Mean Square Error: alias for L2 norm."""
    return l2_norm(computed, reference)


def compute_norm(
    computed: np.ndarray,
    reference: np.ndarray,
    norm_type: str = "L2",
) -> Tuple[float, str]:
    """Compute a named norm. Returns (value, label)."""
    norm_type = norm_type.upper()
    if norm_type == "L1":
        return l1_norm(computed, reference), "L1"
    elif norm_type in ("L2", "RMSE"):
        return l2_norm(computed, reference), "L2"
    elif norm_type in ("LINF", "L_INF", "MAX"):
        return linf_norm(computed, reference), "Linf"
    elif norm_type in ("REL_L2", "RELATIVE_L2"):
        return relative_l2_norm(computed, reference), "Relative L2"
    else:
        raise ValueError(f"Unknown norm type: {norm_type}. Use L1, L2, Linf, or Relative_L2.")


def compute_all_norms(
    computed: np.ndarray, reference: np.ndarray
) -> dict:
    """Compute all available norms."""
    return {
        "L1": l1_norm(computed, reference),
        "L2": l2_norm(computed, reference),
        "Linf": linf_norm(computed, reference),
        "Relative_L2": relative_l2_norm(computed, reference),
    }
