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
