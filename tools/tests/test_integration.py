import os, glob, pytest
from cfdvv.yaml_reader import parse
from cfdvv.schema import validate_case
from cfdvv.compare import compare_case, compare_field
from cfdvv.norms import l2_norm
from cfdvv.gci import compute_gci
from cfdvv.readers import read_file
import numpy as np

_PROJ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.join(_PROJ, 'cases')
INTEGRATION_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'integration_data')


def _find_cases():
    """Find all case.yaml files."""
    return sorted(glob.glob(os.path.join(ROOT, '**', 'case.yaml'), recursive=True))


class TestAllCasesValid:
    """Verify all 51 case.yaml files are valid."""

    @pytest.mark.parametrize("yaml_path", _find_cases())
    def test_case_yaml_valid(self, yaml_path):
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = parse(f.read())
        errors = validate_case(data, os.path.dirname(yaml_path))
        assert errors == [], f"Validation errors: {errors}"

    @pytest.mark.parametrize("yaml_path", _find_cases())
    def test_case_has_mesh(self, yaml_path):
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = parse(f.read())
        mesh = data.get('mesh', {})
        assert 'type' in mesh, f"No mesh.type in {yaml_path}"
        assert 'recommended' in mesh, f"No mesh.recommended in {yaml_path}"


class TestSelfCompare:
    """Verify analytical cases produce zero error when compared to themselves."""

    analytical_cases = []
    for yf in _find_cases():
        cdir = os.path.dirname(yf)
        ref_dir = os.path.join(cdir, 'reference', 'analytical')
        if not os.path.isdir(ref_dir):
            ref_dir = os.path.join(cdir, 'reference', 'mms')
        if os.path.isdir(ref_dir):
            csvs = sorted([f for f in os.listdir(ref_dir) if f.endswith('.csv')])
            if csvs:
                analytical_cases.append((cdir, os.path.join(ref_dir, csvs[0])))

    @pytest.mark.parametrize("case_dir,ref_file", analytical_cases)
    def test_self_compare_zero_error(self, case_dir, ref_file):
        result = compare_case(case_dir, ref_file, reference_file=ref_file, norm_type='L2')
        for fr in result.get('field_results', []):
            if 'error' in fr:
                continue
            assert fr['norm_value'] < 1e-10, (
                f"{fr['field']} norm={fr['norm_value']:e} (expected 0) in {result['case_id']}"
            )


class TestGCI:
    """Test GCI computation."""

    def test_gci_second_order(self):
        case = os.path.join(ROOT, 'verification', 'incompressible', 'poiseuille-2d')
        data = os.path.join(INTEGRATION_DATA)
        coarse = os.path.join(data, 'gci-coarse.csv')
        medium = os.path.join(data, 'gci-medium.csv')
        fine = os.path.join(data, 'gci-fine.csv')
        result = compute_gci(case, [coarse, medium, fine], mesh_sizes=[0.05, 0.025, 0.0125])
        assert 'error' not in result, f"GCI failed: {result.get('error')}"
        q0 = result['quantity_results'][0]
        assert q0['order_p'] is not None, "order_p should not be None"
        assert 1.5 < q0['order_p'] < 2.5, f"expected p≈2, got {q0['order_p']}"
