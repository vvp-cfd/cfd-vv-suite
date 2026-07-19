"""Schema validation for case.yaml files."""

from pathlib import Path
from typing import Any, Dict, List, Optional

from . import yaml_reader


def _parse_yaml_file(filepath: str) -> dict:
    """Parse YAML file using built-in reader or pyyaml if available."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    try:
        import yaml
        return yaml.safe_load(content)
    except ImportError:
        return yaml_reader.parse(content)


REQUIRED_TOP_KEYS = ["id", "name", "category", "tags", "physics", "dimension", "reference", "quantities", "mesh"]
OPTIONAL_TOP_KEYS = ["subcategory", "parameters", "tolerances", "version", "description", "notes"]

VALID_CATEGORIES = ["verification", "validation"]
VALID_SUBCATEGORIES = [
    "incompressible/steady", "incompressible/unsteady",
    "compressible", "non-newtonian",
    "moving-bodies",
    "laminar", "turbulent", "complex-geometry",
]
VALID_PHYSICS_TYPES = ["incompressible", "compressible"]
VALID_REGIMES = ["laminar", "turbulent", "transitional"]
VALID_DIMENSIONS = ["1D", "2D", "3D", "axisymmetric"]
VALID_REF_TYPES = ["analytical", "experimental", "dns", "les", "mms", "manufactured"]
VALID_NORMS = ["L1", "L2", "Linf", "L_inf", "RMSE", "Relative_L2", "relative_l2"]


class CaseSchemaError(Exception):
    """Raised when case.yaml fails validation."""
    pass


def load_case_yaml(case_dir: str) -> Dict[str, Any]:
    """Load and parse case.yaml from a case directory."""
    yaml_path = Path(case_dir) / "case.yaml"
    if not yaml_path.exists():
        raise CaseSchemaError(f"case.yaml not found in {case_dir}")

    data = _parse_yaml_file(str(yaml_path))

    if data is None:
        raise CaseSchemaError("case.yaml is empty")

    return data


def _validate_required_keys(data: Dict[str, Any], path: str) -> List[str]:
    errors = []
    for key in REQUIRED_TOP_KEYS:
        if key not in data:
            errors.append(f"[{path}] Missing required key: '{key}'")
    return errors


def _validate_category(data: Dict[str, Any], path: str) -> List[str]:
    errors = []
    if data.get("category") not in VALID_CATEGORIES:
        errors.append(
            f"[{path}] Invalid category '{data.get('category')}'. "
            f"Must be one of: {VALID_CATEGORIES}"
        )
    return errors


def _validate_physics(data: Dict[str, Any], path: str) -> List[str]:
    errors = []
    physics = data.get("physics", {})
    if not isinstance(physics, dict):
        errors.append(f"[{path}] 'physics' must be a dict")
        return errors
    if "type" not in physics:
        errors.append(f"[{path}] Missing required key: 'physics.type'")
    elif physics["type"] not in VALID_PHYSICS_TYPES:
        errors.append(
            f"[{path}] Invalid physics.type '{physics['type']}'"
        )
    if "equations" not in physics:
        errors.append(f"[{path}] Missing required key: 'physics.equations'")
    return errors


def _validate_dimension(data: Dict[str, Any], path: str) -> List[str]:
    errors = []
    if data.get("dimension") not in VALID_DIMENSIONS:
        errors.append(
            f"[{path}] Invalid dimension '{data.get('dimension')}'. "
            f"Must be one of: {VALID_DIMENSIONS}"
        )
    return errors


def _validate_reference(data: Dict[str, Any], path: str) -> List[str]:
    errors = []
    ref = data.get("reference", {})
    if not isinstance(ref, dict):
        errors.append(f"[{path}] 'reference' must be a dict")
        return errors
    if "type" not in ref:
        errors.append(f"[{path}] Missing required key: 'reference.type'")
    elif ref["type"] not in VALID_REF_TYPES:
        errors.append(
            f"[{path}] Invalid reference.type '{ref['type']}'"
        )
    return errors


def _validate_quantities(data: Dict[str, Any], path: str) -> List[str]:
    errors = []
    quantities = data.get("quantities", [])
    if not isinstance(quantities, list) or len(quantities) == 0:
        errors.append(f"[{path}] 'quantities' must be a non-empty list")
        return errors
    for i, q in enumerate(quantities):
        if not isinstance(q, dict):
            errors.append(f"[{path}] quantities[{i}] must be a dict")
            continue
        if "name" not in q:
            errors.append(f"[{path}] quantities[{i}] missing 'name'")
        if "type" not in q:
            errors.append(f"[{path}] quantities[{i}] missing 'type'")
        if "norm" in q and q["norm"] not in VALID_NORMS:
            errors.append(f"[{path}] quantities[{i}] invalid norm '{q.get('norm')}'")
    return errors


def validate_case(data: Dict[str, Any], case_dir: str = "") -> List[str]:
    """Validate a case.yaml dict. Returns a list of error messages (empty = valid)."""
    path = case_dir or data.get("id", "unknown")
    errors = []

    if not isinstance(data, dict):
        return [f"[{path}] case.yaml root must be a dict"]

    errors.extend(_validate_required_keys(data, path))
    errors.extend(_validate_category(data, path))
    errors.extend(_validate_physics(data, path))
    errors.extend(_validate_dimension(data, path))
    errors.extend(_validate_reference(data, path))
    errors.extend(_validate_quantities(data, path))

    return errors


def validate_case_dir(case_dir: str) -> List[str]:
    """Load and validate case.yaml from a directory."""
    try:
        data = load_case_yaml(case_dir)
        return validate_case(data, case_dir)
    except CaseSchemaError as e:
        return [str(e)]
    except Exception as e:
        return [f"[{case_dir}] Parse error: {e}"]
