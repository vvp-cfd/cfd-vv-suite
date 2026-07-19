import os, tempfile, pytest, io, glob
import numpy as np

from cfdvv.yaml_reader import parse, _parse_scalar
from cfdvv.readers import read_csv, read_vtk, read_file
from cfdvv.norms import compute_all_norms
from cfdvv.schema import validate_case_dir

_THIS = os.path.dirname(os.path.abspath(__file__))
_PROJ = os.path.dirname(os.path.dirname(_THIS))
_CASES = os.path.join(_PROJ, 'cases')


class TestYamlReader:
    def test_parse_scalar_string(self):
        assert _parse_scalar("hello") == "hello"

    def test_parse_scalar_int(self):
        assert _parse_scalar("42") == 42
        assert _parse_scalar("-10") == -10

    def test_parse_scalar_float(self):
        assert _parse_scalar("3.14") == pytest.approx(3.14)
        assert _parse_scalar("1e-6") == pytest.approx(1e-6)
        assert _parse_scalar("-2.5e3") == pytest.approx(-2500.0)

    def test_parse_scalar_bool(self):
        assert _parse_scalar("true") is True
        assert _parse_scalar("False") is False
        assert _parse_scalar("yes") is True
        assert _parse_scalar("no") is False

    def test_parse_scalar_quoted(self):
        assert _parse_scalar('"hello world"') == "hello world"
        assert _parse_scalar("'single quote'") == "single quote"

    def test_parse_simple_yaml(self):
        text = "id: test\nname: 'Test Case'\ndimension: 2D\n"
        d = parse(text)
        assert d['id'] == 'test'
        assert d['name'] == 'Test Case'
        assert d['dimension'] == '2D'

    def test_parse_nested_yaml(self):
        text = """physics:
  type: incompressible
  regime: laminar
quantities:
  - name: u
    type: profile
  - name: v
    type: profile
"""
        d = parse(text)
        assert d['physics']['type'] == 'incompressible'
        assert len(d['quantities']) == 2
        assert d['quantities'][0]['name'] == 'u'

    def test_parse_list_with_values(self):
        text = "tags: [a, b, c]"
        d = parse(text)
        assert d['tags'] == ['a', 'b', 'c']

    def test_parse_multiline_string(self):
        text = "notes: |\n  line one\n  line two\n"
        d = parse(text)
        assert d['notes'] == 'line one\nline two'

    def test_all_case_yamls_parse(self):
        """Test that all 51 case.yaml files parse without error."""
        for f in glob.glob(os.path.join(_CASES, '**', 'case.yaml'), recursive=True):
            with open(f, 'r', encoding='utf-8') as fh:
                d = parse(fh.read())
            assert d is not None, f"Failed to parse {f}"
            assert 'id' in d, f"Missing id in {f}"


class TestVTKReader:
    def test_read_vtk_basic(self):
        pytest.importorskip("meshio", reason="meshio not installed (optional dependency)")
        vtk_content = """# vtk DataFile Version 2.0
Test VTK
ASCII
DATASET UNSTRUCTURED_GRID
POINTS 4 float
0 0 0
1 0 0
0 1 0
1 1 0
CELLS 1 5
4 0 1 3 2
CELL_TYPES 1
9
POINT_DATA 4
SCALARS p float
LOOKUP_TABLE default
1.0
2.0
3.0
4.0
VECTORS U float
1 0 0
0 1 0
1 1 0
0 0 1
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.vtk', delete=False, encoding='ascii') as f:
            f.write(vtk_content)
            tmp = f.name
        try:
            data, cols = read_file(tmp)
            assert data.shape[0] == 4
        finally:
            os.unlink(tmp)


class TestCLIExists:
    """Smoke test that CLI commands run via Click's test runner."""

    def test_help_runs(self):
        from cfdvv.cli import main
        from click.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(main, ['--help'])
        assert result.exit_code == 0
        assert 'compare' in result.output

    def test_list_runs(self):
        from cfdvv.cli import main
        from click.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(main, ['list', '--cases-root', _PROJ])
        assert result.exit_code == 0
        assert 'poiseuille-2d' in result.output

    def test_info_runs(self):
        from cfdvv.cli import main
        from click.testing import CliRunner
        runner = CliRunner()
        case_abs = os.path.join(_CASES, 'verification', 'incompressible', 'poiseuille-2d')
        result = runner.invoke(main, ['info', case_abs])
        assert result.exit_code == 0
        assert 'Poiseuille' in result.output

    def test_validate_runs(self):
        from cfdvv.cli import main
        from click.testing import CliRunner
        runner = CliRunner()
        case_abs = os.path.join(_CASES, 'verification', 'incompressible', 'poiseuille-2d')
        result = runner.invoke(main, ['validate', case_abs])
        assert result.exit_code == 0

    def test_example_output_runs(self):
        from cfdvv.cli import main
        from click.testing import CliRunner
        runner = CliRunner()
        case_abs = os.path.join(_CASES, 'verification', 'incompressible', 'poiseuille-2d')
        result = runner.invoke(main, ['example-output', case_abs])
        assert result.exit_code == 0
        assert 'x,y,u,v' in result.output.replace(' ', '')


class TestNormsComplete:
    def test_all_norms_identical(self):
        a = np.array([1.0, 2.0, 3.0])
        b = np.array([1.0, 2.0, 3.0])
        norms = compute_all_norms(a, b)
        for k, v in norms.items():
            assert v == 0.0, f"{k} should be 0 for identical arrays"

    def test_all_norms_different(self):
        a = np.array([1.0, 2.0])
        b = np.array([3.0, 4.0])
        norms = compute_all_norms(a, b)
        assert norms['L1'] == 2.0
        assert norms['L2'] > 0
        assert norms['Linf'] == 2.0
        assert norms['Relative_L2'] > 0


class TestSchemaValidate:
    def test_template_is_valid(self):
        tmpl = os.path.join(_PROJ, 'templates', 'case-template')
        errors = validate_case_dir(tmpl)
        assert len(errors) == 0

    def test_all_cases_valid(self):
        for f in glob.glob(os.path.join(_CASES, '**', 'case.yaml'), recursive=True):
            dir_path = os.path.dirname(f)
            errors = validate_case_dir(dir_path)
            assert errors == [], f"Validation errors in {dir_path}: {errors}"


class TestCoordinateMatching:
    """Test coordinate matching with dimension mismatches."""

    def test_1d_result_vs_2d_reference(self):
        from cfdvv.compare import _match_by_coordinates
        res_coords = np.linspace(0, 1, 10).reshape(-1, 1)
        x = np.linspace(0, 1, 5)
        y = np.linspace(0, 1, 5)
        X, Y = np.meshgrid(x, y)
        ref_coords = np.column_stack([X.ravel(), Y.ravel()])
        res_vals = np.sin(res_coords[:, 0])
        ref_vals = np.sin(X.ravel())
        mr, mref = _match_by_coordinates(res_coords, ref_coords, res_vals, ref_vals, 1e-10)
        assert len(mr) == 10
        assert len(mref) == 10

    def test_1d_result_vs_1d_reference(self):
        from cfdvv.compare import _match_by_coordinates
        res_coords = np.linspace(0, 1, 10).reshape(-1, 1)
        ref_coords = np.linspace(0, 1, 20).reshape(-1, 1)
        res_vals = np.linspace(0, 1, 10)
        ref_vals = np.linspace(0, 1, 20)
        mr, mref = _match_by_coordinates(res_coords, ref_coords, res_vals, ref_vals, 1e-10)
        assert len(mr) == 10
        assert len(mref) == 10

    def test_dimension_mismatch_2d_vs_1d_no_crash(self):
        from cfdvv.compare import _match_by_coordinates
        res_coords = np.linspace(0, 1, 10).reshape(-1, 1)
        ref_coords = np.column_stack([
            np.linspace(0, 1, 100),
            np.zeros(100)
        ])
        res_vals = np.ones(10)
        ref_vals = np.ones(100)
        mr, mref = _match_by_coordinates(res_coords, ref_coords, res_vals, ref_vals, 1e-10)
        assert len(mr) > 0


class TestFieldMatching:
    """Test OpenFOAM field name aliases."""

    def test_of_aliases_recognized(self):
        from cfdvv.compare import _find_field_column
        cols = ['x', 'U:0', 'U:1', 'U:2', 'p', 'rho', 'T', 'e']
        assert _find_field_column(cols, 'u') == 1
        assert _find_field_column(cols, 'v') == 2
        assert _find_field_column(cols, 'w') == 3
        assert _find_field_column(cols, 'p') == 4
        assert _find_field_column(cols, 'rho') == 5
        assert _find_field_column(cols, 'T') == 6
        assert _find_field_column(cols, 'e') == 7

    def test_of_sample_headers(self):
        from cfdvv.compare import _find_field_column
        cols = ['x', '"U:0"', '"U:1"', 'p']
        assert _find_field_column(cols, 'u') == 1
        assert _find_field_column(cols, 'v') == 2
        assert _find_field_column(cols, 'p') == 3

    def test_missing_field_returns_none(self):
        from cfdvv.compare import _find_field_column
        cols = ['x', 'U:0', 'U:1', 'U:2', 'p']
        assert _find_field_column(cols, 'e') is None
        assert _find_field_column(cols, 'rho') is None


class TestAutoGenerateParameters:
    """Test auto-generate dimension detection from result files."""

    def test_1d_result_ny_defaults_to_1(self):
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('x,U,p\n')
            for i in range(10):
                f.write(f'{i/10},{i/10},{i/10}\n')
            tmp = f.name
        from cfdvv.readers import read_file
        data, cols = read_file(tmp)
        ndim = sum(1 for c in cols[:3] if c.lower() in ('x', 'y', 'z'))
        unique_counts = []
        for d in range(ndim):
            unique_counts.append(len(set(data[:, d])))
        nx = unique_counts[0] if len(unique_counts) > 0 else 32
        ny = unique_counts[1] if len(unique_counts) > 1 else (32 if ndim >= 2 else 1)
        assert nx == 10
        assert ny == 1
        os.unlink(tmp)

    def test_2d_result_ny_detected(self):
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('x,y,U,p\n')
            for i in range(5):
                for j in range(8):
                    f.write(f'{i/5},{j/8},{0},{0}\n')
            tmp = f.name
        from cfdvv.readers import read_file
        data, cols = read_file(tmp)
        ndim = sum(1 for c in cols[:3] if c.lower() in ('x', 'y', 'z'))
        unique_counts = []
        for d in range(ndim):
            unique_counts.append(len(set(data[:, d])))
        nx = unique_counts[0] if len(unique_counts) > 0 else 32
        ny = unique_counts[1] if len(unique_counts) > 1 else (32 if ndim >= 2 else 1)
        assert nx == 5
        assert ny == 8
        os.unlink(tmp)
