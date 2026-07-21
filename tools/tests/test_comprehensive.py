import os, tempfile, pytest, io, glob
import numpy as np

from cfdvv.yaml_reader import parse, _parse_scalar
from cfdvv.readers import read_csv, read_vtk, read_file
from cfdvv.norms import compute_all_norms
from cfdvv.schema import validate_case_dir
from cfdvv.compare import _find_coordinate_columns, _find_field_column, _match_by_coordinates, compare_case, compare_field
import cfdvv

_THIS = os.path.dirname(os.path.abspath(__file__))
_CASES = os.path.join(os.path.dirname(cfdvv.__file__), 'cases')
_PROJ = os.path.dirname(os.path.dirname(os.path.dirname(cfdvv.__file__)))  # repo root


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
        cases_root = os.path.dirname(cfdvv.__file__)  # tools/cfdvv/ containing cases/
        result = runner.invoke(main, ['list', '--cases-root', cases_root])
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
        assert len(mr) == 20  # interpolation maps result to all ref points
        assert len(mref) == 20

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


class TestInterpolationAccuracy:
    """Verify that compare_field produces correct L2 norms for 1D profile
    comparison with known functions via interpolation."""

    def _make_result_csv(self, y_vals, u_vals):
        """Write a result CSV with x,y,U:0 columns and return the path."""
        import tempfile
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        f.write('x,y,U:0\n')
        for yi, ui in zip(y_vals, u_vals):
            f.write(f'0.5,{yi},{ui}\n')
        f.close()
        return f.name

    def test_interpolation_exact_for_linear_function(self):
        """Linear function interpolated exactly → L2 ≈ 0 regardless of grid size."""
        from cfdvv.compare import compare_field
        y_ref = np.linspace(0, 1, 103)
        u_ref = 2.0 * y_ref + 1.0
        ref_data = np.column_stack([y_ref, u_ref])
        ref_cols = ['y', 'u']

        y_res = np.linspace(0, 1, 7)
        u_res = 2.0 * y_res + 1.0
        result_path = self._make_result_csv(y_res, u_res)

        try:
            result = compare_field(result_path, ref_data, ref_cols, 'u', 'L2')
            assert result['n_points'] == len(y_ref), (
                f"Expected {len(y_ref)} points, got {result['n_points']}"
            )
            assert result['norm_value'] == pytest.approx(0.0, abs=1e-14), (
                f"Linear interpolation of linear function should be exact, got {result['norm_value']}"
            )
        finally:
            os.unlink(result_path)

    def test_interpolation_sine_known_error(self):
        """Interpolation error of sin(πy) from 11→101 points matches manual np.interp."""
        from cfdvv.compare import compare_field
        from cfdvv.norms import l2_norm

        y_ref = np.linspace(0, 1, 101)
        u_ref = np.sin(np.pi * y_ref)
        ref_data = np.column_stack([y_ref, u_ref])
        ref_cols = ['y', 'u']

        y_res = np.linspace(0, 1, 11)
        u_res = np.sin(np.pi * y_res)
        result_path = self._make_result_csv(y_res, u_res)

        try:
            result = compare_field(result_path, ref_data, ref_cols, 'u', 'L2')
            u_interp = np.interp(y_ref, y_res, u_res)
            expected_l2 = l2_norm(u_interp, u_ref)

            assert result['n_points'] == len(y_ref), (
                f"Expected {len(y_ref)} points, got {result['n_points']}"
            )
            assert result['norm_value'] == pytest.approx(expected_l2, rel=1e-10, abs=1e-12), (
                f"L2 mismatch: {result['norm_value']} vs {expected_l2}"
            )
        finally:
            os.unlink(result_path)

    def test_interpolation_1d_ref_vs_2d_result(self):
        """Reference has only y, result has x,y → still interpolates correctly."""
        from cfdvv.compare import compare_field
        from cfdvv.norms import l2_norm

        y_ref = np.linspace(0, 1, 51)
        u_ref = np.sin(np.pi * y_ref)
        ref_data = np.column_stack([y_ref, u_ref])
        ref_cols = ['y', 'u']

        y_res = np.linspace(0, 1, 6)
        u_res = np.sin(np.pi * y_res)
        result_path = self._make_result_csv(y_res, u_res)

        try:
            result = compare_field(result_path, ref_data, ref_cols, 'u', 'L2')
            u_interp = np.interp(y_ref, y_res, u_res)
            expected_l2 = l2_norm(u_interp, u_ref)

            assert result['n_points'] == len(y_ref), (
                f"Expected {len(y_ref)} points, got {result['n_points']}"
            )
            assert result['norm_value'] == pytest.approx(expected_l2, rel=1e-10, abs=1e-12), (
                f"L2 mismatch: {result['norm_value']} vs {expected_l2}"
            )
        finally:
            os.unlink(result_path)

    def test_interpolation_result_on_reference_grid(self):
        """Result on the exact same y-grid as reference → L2 ≈ 0 (interpolation exact)."""
        from cfdvv.compare import compare_field
        y = np.linspace(0, 1, 21)
        u = np.sin(2 * np.pi * y) + 0.5 * np.cos(3 * np.pi * y)
        ref_data = np.column_stack([y, u])
        ref_cols = ['y', 'u']
        result_path = self._make_result_csv(y, u)

        try:
            result = compare_field(result_path, ref_data, ref_cols, 'u', 'L2')
            assert result['n_points'] == len(y)
            assert result['norm_value'] == pytest.approx(0.0, abs=1e-14)
        finally:
            os.unlink(result_path)


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


# ====================================================================
# New tests for coverage gaps
# ====================================================================


class TestReadOpenFOAMField:
    """Tests for readers.read_openfoam_field (previously untested).

    NOTE: the reader has known limitations — it only works when values
    appear in parenthesized blocks after ``internalField`` (without
    ``uniform`` or ``nonuniform`` keywords on the same line).
    """

    def _mkfile(self, tmpdir, name, content):
        d = tmpdir.mkdir("0")
        p = d.join(name)
        p.write(content)
        return str(p)

    def test_scalar_values_in_parentheses(self, tmpdir):
        from cfdvv.readers import read_openfoam_field
        path = self._mkfile(tmpdir, "p", """FoamFile { version 2.0; }
dimensions [0 2 -2 0 0 0 0];
internalField
(
1.0
2.5
-3.0
)
;
""")
        data, cols = read_openfoam_field(path)
        assert len(data) == 3
        assert list(data) == [1.0, 2.5, -3.0]
        # Field name is derived from parent dir name (known quirk)
        assert len(cols) == 1

    def test_vector_field_in_parentheses(self, tmpdir):
        from cfdvv.readers import read_openfoam_field
        path = self._mkfile(tmpdir, "U", """FoamFile { version 2.0; }
dimensions [0 1 -1 0 0 0 0];
internalField
(
(1.0 0.0 0.0)
(0.0 2.0 0.0)
)
;
""")
        data, cols = read_openfoam_field(path)
        assert len(data) == 6
        assert list(data) == [1.0, 0.0, 0.0, 0.0, 2.0, 0.0]

    def test_no_values_raises(self, tmpdir):
        from cfdvv.readers import read_openfoam_field
        path = self._mkfile(tmpdir, "p", "FoamFile { version 2.0; }\n")
        with pytest.raises(ValueError, match="No internalField values found"):
            read_openfoam_field(path)

    def test_read_file_detects_openfoam_field(self, tmpdir):
        from cfdvv.readers import read_file
        path = self._mkfile(tmpdir, "U", """FoamFile { version 2.0; }
dimensions [0 1 -1 0 0 0 0];
internalField
(
0.0
)
;
""")
        data, cols = read_file(path)
        assert len(data) == 1
        assert data[0] == 0.0


class TestReadCSVEdgeCases:
    """Edge cases for readers.read_csv (empty file, garbage rows)."""

    def test_empty_file(self):
        from cfdvv.readers import read_csv
        import tempfile
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        f.write('')
        f.close()
        try:
            data, cols = read_csv(f.name)
            assert len(data) == 0
        finally:
            os.unlink(f.name)

    def test_file_with_garbage_rows(self):
        from cfdvv.readers import read_csv
        import tempfile
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        f.write('x,y\n1.0,2.0\n# comment\ngarbage\n3.0,4.0\n5.0,6.0\n')
        f.close()
        try:
            data, cols = read_csv(f.name)
            assert len(data) == 3
        finally:
            os.unlink(f.name)


class TestCompareFieldErrors:
    """Each error branch in compare_field should raise ValueError."""

    def _write_result_csv(self, content: str) -> str:
        import tempfile
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        f.write(content)
        f.close()
        return f.name

    def test_empty_result_file(self):
        from cfdvv.compare import compare_field
        path = self._write_result_csv('x,y,U:0\n')
        ref = np.array([[0.0, 0.0]])
        try:
            with pytest.raises(ValueError, match="No data read from"):
                compare_field(path, ref, ['y', 'u'], 'u')
        finally:
            os.unlink(path)

    def test_no_ref_coordinate_columns(self):
        from cfdvv.compare import compare_field
        path = self._write_result_csv('x,y,U:0\n0.5,0.0,0.0\n')
        ref_data = np.array([[0.0]])
        ref_cols = ['u']
        try:
            with pytest.raises(ValueError, match="No coordinate columns found in reference data"):
                compare_field(path, ref_data, ref_cols, 'u')
        finally:
            os.unlink(path)

    def test_no_result_coordinate_columns(self):
        from cfdvv.compare import compare_field
        path = self._write_result_csv('U:0\n0.0\n')
        ref_data = np.array([[0.0, 0.0]])
        ref_cols = ['y', 'u']
        try:
            with pytest.raises(ValueError, match="No coordinate columns"):
                compare_field(path, ref_data, ref_cols, 'u')
        finally:
            os.unlink(path)

    def test_field_not_in_reference(self):
        from cfdvv.compare import compare_field
        path = self._write_result_csv('x,y,U:0\n0.5,0.0,0.0\n')
        ref_data = np.array([[0.0, 0.0]])
        ref_cols = ['y', 'v']
        try:
            with pytest.raises(ValueError, match="not found in reference data"):
                compare_field(path, ref_data, ref_cols, 'u')
        finally:
            os.unlink(path)

    def test_field_not_in_result(self):
        from cfdvv.compare import compare_field
        path = self._write_result_csv('x,y,V:0\n0.5,0.0,0.0\n')
        ref_data = np.array([[0.0, 0.0]])
        ref_cols = ['y', 'u']
        try:
            with pytest.raises(ValueError, match="not found in result columns"):
                compare_field(path, ref_data, ref_cols, 'u')
        finally:
            os.unlink(path)

    def test_no_common_coordinate_columns(self):
        from cfdvv.compare import compare_field
        path = self._write_result_csv('x,U:0\n0.5,0.0\n')
        ref_data = np.array([[0.0, 0.0]])
        ref_cols = ['y', 'u']
        try:
            with pytest.raises(ValueError, match="No common coordinate columns"):
                compare_field(path, ref_data, ref_cols, 'u')
        finally:
            os.unlink(path)


class TestScalarCompare:
    """Tests for _parse_csv_rows and _compare_scalar_dict (scalar-table path)."""

    def test_parse_csv_rows_basic(self):
        from cfdvv.compare import _parse_csv_rows
        import tempfile
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        f.write('Re,100\nCd,0.5\nCl,0.05\n')
        f.close()
        try:
            result = _parse_csv_rows(f.name)
            assert result == {'Re': 100.0, 'Cd': 0.5, 'Cl': 0.05}
        finally:
            os.unlink(f.name)

    def test_parse_csv_rows_skip_bad_rows(self):
        from cfdvv.compare import _parse_csv_rows
        import tempfile
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        f.write('Re,100\nbad\nCd,0.5\n')
        f.close()
        try:
            result = _parse_csv_rows(f.name)
            assert result == {'Re': 100.0, 'Cd': 0.5}
        finally:
            os.unlink(f.name)

    def test_parse_csv_rows_file_not_found(self):
        from cfdvv.compare import _parse_csv_rows
        result = _parse_csv_rows('nonexistent_file.csv')
        assert result == {}

    def test_compare_scalar_dict_no_tolerance(self):
        from cfdvv.compare import _compare_scalar_dict
        result = _compare_scalar_dict({'Re': 100.0, 'Cd': 0.5})
        assert result['passed'] is None
        assert len(result['field_results']) == 2
        for fr in result['field_results']:
            assert fr['norm_value'] == 0.0
            assert fr['passed'] is True

    def test_compare_scalar_dict_with_tolerance(self):
        from cfdvv.compare import _compare_scalar_dict
        result = _compare_scalar_dict({'Re': 100.0, 'Cd': 0.5}, tolerance=0.01)
        assert result['passed'] is True
        assert result['tolerance'] == 0.01

    def test_scalar_case_path_in_compare_case(self, tmpdir):
        """End-to-end via compare_case: CSV with no coordinates → scalar path."""
        from cfdvv.compare import compare_case
        import tempfile
        # Create a minimal case with scalar reference
        casedir = tmpdir.mkdir("scalar_case")
        casedir.join("case.yaml").write("""id: scalar-test
name: Scalar Test
category: verification
tags: [test]
physics:
  type: incompressible
  regime: laminar
  equations: [continuity, navier-stokes]
dimension: 2D
reference:
  type: analytical
quantities:
  - name: Cd
    type: integral
tolerances:
  L2: 0.01
mesh: {type: uniform}
""")
        refdir = casedir.mkdir("reference").mkdir("analytical")
        refdir.join("integral.csv").write("Cd,0.5\nCl,0.05\n")
        # Self-compare the reference CSV
        result = compare_case(str(casedir), str(refdir.join("integral.csv")))
        assert result["case_id"] == "scalar-test"
        assert result["passed"] is True or result["passed"] is None


class TestMatchByCoordinatesEdgeCases:
    """Edge cases in _match_by_coordinates (zero-dim, duplicates, no-match)."""

    def test_zero_dim_coords_raises(self):
        from cfdvv.compare import _match_by_coordinates
        res_coords = np.empty((5, 0))
        ref_coords = np.empty((4, 0))
        res_vals = np.ones(5)
        ref_vals = np.ones(5)
        with pytest.raises(ValueError, match="No common coordinate dimensions"):
            _match_by_coordinates(res_coords, ref_coords, res_vals, ref_vals)

    def test_duplicate_coords_guard_disables_1d(self):
        """Duplicate y values in reference disable 1D interpolation → nearest-neighbor."""
        from cfdvv.compare import _match_by_coordinates
        res_coords = np.linspace(0, 1, 10).reshape(-1, 1)
        ref_coords = np.array([0.0, 0.0, 0.5, 0.5, 1.0]).reshape(-1, 1)
        res_vals = np.linspace(0, 1, 10)
        ref_vals = np.array([0.0, 0.0, 0.5, 0.5, 1.0])
        mr, mref = _match_by_coordinates(res_coords, ref_coords, res_vals, ref_vals, 1e-10)
        assert len(mr) > 0

    def test_no_match_raises(self):
        """Points far apart with tight tolerance → no match → ValueError."""
        from cfdvv.compare import _match_by_coordinates
        res_coords = np.array([[0.0], [1.0]])
        ref_coords = np.array([[100.0], [100.0]])
        res_vals = np.array([0.0, 1.0])
        ref_vals = np.array([1.0, 1.0])
        with pytest.raises(ValueError, match="No matching coordinates found"):
            _match_by_coordinates(res_coords, ref_coords, res_vals, ref_vals, 1e-10)


class TestNormsExtended:
    """Norms edge cases: rmse, zero denominator, compute_norm aliases."""

    def test_rmse(self):
        from cfdvv.norms import rmse, l2_norm
        a = np.array([1.0, 2.0, 3.0])
        b = np.array([2.0, 3.0, 4.0])
        assert rmse(a, b) == l2_norm(a, b)

    def test_relative_l2_zero_reference(self):
        from cfdvv.norms import relative_l2_norm, l2_norm
        a = np.array([1.0, 2.0])
        b = np.array([0.0, 0.0])
        result = relative_l2_norm(a, b)
        assert result == l2_norm(a, b)

    def test_compute_norm_aliases(self):
        from cfdvv.norms import compute_norm, l2_norm, relative_l2_norm
        a = np.array([1.0, 2.0])
        b = np.array([3.0, 4.0])
        # RMSE → L2
        v, lab = compute_norm(a, b, "RMSE")
        assert lab == "L2"
        assert v == l2_norm(a, b)
        # LINF → Linf
        v, lab = compute_norm(a, b, "LINF")
        assert lab == "Linf"
        # L_INF → Linf
        v, lab = compute_norm(a, b, "L_INF")
        assert lab == "Linf"
        # MAX → Linf
        v, lab = compute_norm(a, b, "MAX")
        assert lab == "Linf"
        # REL_L2 → Relative L2
        v, lab = compute_norm(a, b, "REL_L2")
        assert lab == "Relative L2"
        assert v == relative_l2_norm(a, b)
        # RELATIVE_L2 → Relative L2
        v, lab = compute_norm(a, b, "RELATIVE_L2")
        assert lab == "Relative L2"
        # L1 norm
        v, lab = compute_norm(a, b, "L1")
        assert lab == "L1"


class TestGCIExtended:
    """GCI edge cases: too few levels, degenerate p, zero f1."""

    def test_too_few_levels(self):
        from cfdvv.gci import estimate_order
        result = estimate_order([1.0, 0.5], [[1.0], [2.0]])
        assert "error" in result

    def test_both_errors_zero_p_is_inf(self):
        from cfdvv.gci import estimate_order
        result = estimate_order([4.0, 2.0, 1.0], [[1.0], [1.0], [1.0]])
        q = result["quantity_results"][0]
        assert q["order_p"] == float("inf")
        assert q["extrapolated_value"] == 1.0
        assert q["gci21"] is None

    def test_e32_zero_p_is_none(self):
        from cfdvv.gci import estimate_order
        result = estimate_order([4.0, 2.0, 1.0], [[2.0], [1.0], [1.0]])
        q = result["quantity_results"][0]
        assert q["order_p"] is None
        assert q["extrapolated_value"] is None
        assert q["gci21"] is None

    def test_e21_zero_p_is_none(self):
        from cfdvv.gci import estimate_order
        result = estimate_order([4.0, 2.0, 1.0], [[1.0], [1.0], [2.0]])
        q = result["quantity_results"][0]
        assert q["order_p"] is None

    def test_negative_p_becomes_positive(self):
        from cfdvv.gci import estimate_order
        result = estimate_order([4.0, 2.0, 1.0], [[1.0], [2.0], [4.0]])
        q = result["quantity_results"][0]
        assert q["order_p"] == 1.0

    def test_equal_mesh_sizes_p_is_inf_becomes_none(self):
        """r21 = 1 → log(r21) = 0 → p = inf → reset to None."""
        from cfdvv.gci import estimate_order
        result = estimate_order([2.0, 2.0, 1.0], [[1.0], [2.0], [4.0]])
        q = result["quantity_results"][0]
        assert q["order_p"] is None

    def test_f1_near_zero_gci_fallback(self):
        """abs(f1) <= 1e-16 → gci21 = Fs * abs(e21) instead of division."""
        from cfdvv.gci import estimate_order
        result = estimate_order([4.0, 2.0, 1.0], [[0.0], [1.0], [3.0]])
        q = result["quantity_results"][0]
        assert q["order_p"] == 1.0
        assert q["gci21"] == 1.25 * abs(1.0 - 0.0)

    def test_compute_gci_few_files(self):
        from cfdvv.gci import compute_gci
        result = compute_gci("/tmp", ["a.csv", "b.csv"])
        assert "error" in result

    def test_compute_gci_no_mesh_sizes(self):
        from cfdvv.gci import compute_gci
        from unittest.mock import patch

        def mock_compare(case_dir, result_file):
            return {"field_results": [
                {"field": "u", "norm_value": 0.1},
                {"field": "v", "norm_value": 0.2},
            ]}

        with patch("cfdvv.gci.compare_case", side_effect=mock_compare):
            result = compute_gci("/tmp", ["c.csv", "m.csv", "f.csv"])
            assert "quantity_results" in result
            assert len(result["quantity_results"]) == 2
            assert result["mesh_sizes"] == [1.0, 0.5, 0.25]

    def test_compute_gci_quantity_filter(self):
        from cfdvv.gci import compute_gci
        from unittest.mock import patch

        def mock_compare(case_dir, result_file):
            return {"field_results": [
                {"field": "u", "norm_value": 0.1},
                {"field": "v", "norm_value": 0.2},
            ]}

        with patch("cfdvv.gci.compare_case", side_effect=mock_compare):
            result = compute_gci("/tmp", ["c.csv", "m.csv", "f.csv"], quantity_name="u")
            assert len(result["quantity_results"]) == 1
            assert result["quantity_results"][0]["f1"] == 0.1

    def test_compute_gci_no_vals_fallback(self):
        from cfdvv.gci import compute_gci
        from unittest.mock import patch

        def mock_compare(case_dir, result_file):
            return {"field_results": [
                {"field": "other", "norm_value": 0.1},
            ]}

        with patch("cfdvv.gci.compare_case", side_effect=mock_compare):
            result = compute_gci("/tmp", ["c.csv", "m.csv", "f.csv"], quantity_name="u")
            assert result["quantity_results"][0]["f1"] == 0.0


class TestSchemaInvalid:
    """Schema validation error branches."""

    def _minimal_valid(self):
        return {
            "id": "t", "name": "t", "category": "verification",
            "tags": [], "physics": {"type": "incompressible", "equations": []},
            "dimension": "2D", "reference": {"type": "analytical"},
            "quantities": [{"name": "u", "type": "profile"}], "mesh": {},
        }

    def test_missing_required_key(self):
        from cfdvv.schema import validate_case
        errors = validate_case({"name": "test", "category": "verification"})
        assert any("Missing required key" in e for e in errors)

    def test_invalid_category(self):
        from cfdvv.schema import validate_case
        data = self._minimal_valid()
        data["category"] = "invalid"
        errors = validate_case(data)
        assert any("Invalid category" in e for e in errors)

    def test_physics_not_dict(self):
        from cfdvv.schema import validate_case
        data = self._minimal_valid()
        data["physics"] = "string"
        errors = validate_case(data)
        assert any("physics' must be a dict" in e for e in errors)

    def test_invalid_physics_type(self):
        from cfdvv.schema import validate_case
        data = self._minimal_valid()
        data["physics"] = {"type": "bad", "equations": []}
        errors = validate_case(data)
        assert any("Invalid physics.type" in e for e in errors)

    def test_missing_physics_type(self):
        from cfdvv.schema import validate_case
        data = self._minimal_valid()
        data["physics"] = {"equations": []}
        errors = validate_case(data)
        assert any("physics.type" in e for e in errors)

    def test_missing_physics_equations(self):
        from cfdvv.schema import validate_case
        data = self._minimal_valid()
        data["physics"] = {"type": "incompressible"}
        errors = validate_case(data)
        assert any("physics.equations" in e for e in errors)

    def test_invalid_dimension(self):
        from cfdvv.schema import validate_case
        data = self._minimal_valid()
        data["dimension"] = "4D"
        errors = validate_case(data)
        assert any("Invalid dimension" in e for e in errors)

    def test_reference_not_dict(self):
        from cfdvv.schema import validate_case
        data = self._minimal_valid()
        data["reference"] = "string"
        errors = validate_case(data)
        assert any("reference' must be a dict" in e for e in errors)

    def test_missing_reference_type(self):
        from cfdvv.schema import validate_case
        data = self._minimal_valid()
        data["reference"] = {"source": "x"}
        errors = validate_case(data)
        assert any("reference.type" in e for e in errors)

    def test_invalid_reference_type(self):
        from cfdvv.schema import validate_case
        data = self._minimal_valid()
        data["reference"] = {"type": "bad"}
        errors = validate_case(data)
        assert any("Invalid reference.type" in e for e in errors)

    def test_quantities_not_list(self):
        from cfdvv.schema import validate_case
        data = self._minimal_valid()
        data["quantities"] = "not a list"
        errors = validate_case(data)
        assert any("quantities' must be a non-empty list" in e for e in errors)

    def test_quantities_item_not_dict(self):
        from cfdvv.schema import validate_case
        data = self._minimal_valid()
        data["quantities"] = ["string"]
        errors = validate_case(data)
        assert any("quantities[0] must be a dict" in e for e in errors)

    def test_quantities_missing_name(self):
        from cfdvv.schema import validate_case
        data = self._minimal_valid()
        data["quantities"] = [{"type": "profile"}]
        errors = validate_case(data)
        assert any("missing 'name'" in e for e in errors)

    def test_quantities_missing_type(self):
        from cfdvv.schema import validate_case
        data = self._minimal_valid()
        data["quantities"] = [{"name": "u"}]
        errors = validate_case(data)
        assert any("missing 'type'" in e for e in errors)

    def test_quantities_invalid_norm(self):
        from cfdvv.schema import validate_case
        data = self._minimal_valid()
        data["quantities"] = [{"name": "u", "type": "profile", "norm": "BAD"}]
        errors = validate_case(data)
        assert any("invalid norm" in e for e in errors)

    def test_root_not_dict(self):
        from cfdvv.schema import validate_case
        errors = validate_case("not a dict", "test")
        assert any("root must be a dict" in e for e in errors)

    def test_load_case_yaml_missing(self, tmpdir):
        from cfdvv.schema import load_case_yaml, CaseSchemaError
        with pytest.raises(CaseSchemaError, match="case.yaml not found"):
            load_case_yaml(str(tmpdir))

    def test_validate_case_dir_parse_error(self, tmpdir):
        from cfdvv.schema import validate_case_dir
        p = tmpdir.join("case.yaml")
        p.write(": broken yaml [")
        errors = validate_case_dir(str(tmpdir))
        assert len(errors) > 0
        assert any(kw in errors[0] for kw in ("Parse error", "case.yaml is empty", "Missing required key"))


class TestYamlReaderEdgeCases:
    """YAML reader edge cases: inf, nan."""

    def test_parse_inf(self):
        from cfdvv.yaml_reader import _parse_scalar
        import math
        val = _parse_scalar(".inf")
        assert val == float("inf")
        val2 = _parse_scalar("-.inf")
        assert math.isinf(val2) and val2 < 0

    def test_parse_nan(self):
        from cfdvv.yaml_reader import _parse_scalar
        import math
        assert math.isnan(_parse_scalar(".nan"))


class TestBenchmarkCommand:
    """Smoke test for CLI benchmark command."""

    def test_benchmark_runs_on_tiny_subset(self):
        from cfdvv.cli import main
        from click.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(main, [
            'benchmark', '--category=verification', '--tolerance=1.0',
            '--cases-root', os.path.dirname(os.path.dirname(os.path.dirname(_THIS))),
        ])
        # Should run without crashing; exit code depends on whether all cases pass
        assert result.exit_code in (0, 1)


class TestFindCasesRoot:
    """Tests for _find_cases_root() — critical for pip install behaviour."""

    def test_returns_package_dir_when_cases_inside(self, monkeypatch):
        from cfdvv.cli import _find_cases_root
        pkg_dir = os.path.dirname(cfdvv.__file__)
        # The real package dir has cases/ — verify it's found
        found = _find_cases_root()
        assert os.path.isdir(os.path.join(found, 'cases')), \
            f"_find_cases_root() returned {found}, but no cases/ inside"
        assert os.path.isfile(os.path.join(found, 'cases', 'verification',
            'incompressible', 'poiseuille-2d', 'case.yaml'))

    def test_fallback_to_cwd_walk(self, tmp_path, monkeypatch):
        from cfdvv.cli import _find_cases_root
        # Create a fake cases tree outside the package
        fake_cases = tmp_path / 'cases'
        fake_cases.mkdir()
        (fake_cases / 'verification').mkdir()
        (fake_cases / 'verification' / 'incompressible').mkdir()
        poiseuille = fake_cases / 'verification' / 'incompressible' / 'poiseuille-2d'
        poiseuille.mkdir()
        (poiseuille / 'case.yaml').write_text('id: fake\nname: Fake\ncategory: verification\ntags: []\nphysics:\n  type: incompressible\n  regime: laminar\n  equations: []\ndimension: 2D\nreference:\n  type: analytical\n  solution: ""\n  source: ""\nquantities: []\nmesh:\n  type: uniform\n  recommended: [10, 20]\n')

        # Monkey-patch __file__ to a dir WITHOUT cases/
        no_cases_dir = tmp_path / 'no_cases_here'
        no_cases_dir.mkdir()
        fake_init = no_cases_dir / '__init__.py'
        fake_init.write_text('')

        def fake_file():
            return str(fake_init)
        monkeypatch.setattr('cfdvv.cli.__file__', str(fake_init))

        monkeypatch.chdir(tmp_path)
        found = _find_cases_root()
        assert os.path.isdir(os.path.join(found, 'cases'))

    def test_gives_up_returns_cwd_when_no_cases_anywhere(self, tmp_path, monkeypatch):
        from cfdvv.cli import _find_cases_root
        empty = tmp_path / 'empty'
        empty.mkdir()
        fake_init = empty / '__init__.py'
        fake_init.write_text('')

        monkeypatch.setattr('cfdvv.cli.__file__', str(fake_init))
        monkeypatch.chdir(empty)
        found = _find_cases_root()
        assert found == str(empty)


class TestMatchByCoordinates:
    """Tests for _match_by_coordinates — coordinate matching and interpolation."""

    def test_identical_coords_fast_path(self):
        ref = np.array([[0.0, 0.0], [1.0, 1.0], [2.0, 2.0]])
        res = np.array([[0.0, 0.0], [1.0, 1.0], [2.0, 2.0]])
        ref_vals = np.array([0.0, 1.0, 2.0])
        res_vals = np.array([0.1, 1.1, 2.1])
        mr, mref = _match_by_coordinates(res, ref, res_vals, ref_vals)
        assert mr == pytest.approx(res_vals)
        assert mref == pytest.approx(ref_vals)

    def test_1d_profile_interpolation(self):
        ref_coords = np.array([[0.0], [0.5], [1.0]])
        res_coords = np.array([[0.0], [0.3], [0.6], [1.0]])
        ref_vals = np.array([0.0, 2.5, 5.0])
        res_vals = np.array([0.0, 1.5, 3.0, 5.0])
        mr, mref = _match_by_coordinates(res_coords, ref_coords, res_vals, ref_vals)
        assert len(mr) == 3
        assert mr[0] == pytest.approx(0.0)
        assert mr[1] == pytest.approx(2.5)  # at y=0.5: interpolated between 1.5@0.3 and 3.0@0.6
        assert mr[2] == pytest.approx(5.0)

    def test_1d_profile_unsorted_inputs(self):
        ref_coords = np.array([[1.0], [0.0], [0.5]])
        res_coords = np.array([[0.6], [0.0], [1.0], [0.3]])
        ref_vals = np.array([5.0, 0.0, 2.5])
        res_vals = np.array([3.0, 0.0, 5.0, 1.5])
        mr, mref = _match_by_coordinates(res_coords, ref_coords, res_vals, ref_vals)
        assert len(mr) == 3
        assert mr[0] == pytest.approx(0.0)
        assert mr[1] == pytest.approx(2.5)  # at y=0.5
        assert mr[2] == pytest.approx(5.0)

    def test_2d_no_matching_points_raises(self):
        ref = np.array([[0.0, 0.0], [1.0, 1.0], [2.0, 2.0]])
        res = np.array([[10.0, 10.0], [20.0, 20.0]])
        ref_vals = np.array([0.0, 1.0, 2.0])
        res_vals = np.array([5.0, 5.0])
        with pytest.raises(ValueError, match="No matching coordinates"):
            _match_by_coordinates(res, ref, res_vals, ref_vals)

    def test_2d_repeated_points_not_1d_profile(self):
        ref = np.array([[0.0, 0.0], [0.0, 1.0], [0.0, 2.0]])
        res = np.array([[0.0, 0.0], [0.0, 1.0], [0.0, 2.0]])
        ref_vals = np.array([1.0, 2.0, 3.0])
        res_vals = np.array([1.0, 2.0, 3.0])
        mr, mref = _match_by_coordinates(res, ref, res_vals, ref_vals)
        assert len(mr) == 3  # exact match via identity check


class TestFindFieldColumn:
    """Tests for _find_field_column — OpenFOAM and standard field aliases."""

    def test_standard_field_names(self):
        assert _find_field_column(['x', 'y', 'u', 'v', 'p'], 'u') == 2
        assert _find_field_column(['x', 'y', 'u', 'v', 'p'], 'v') == 3
        assert _find_field_column(['x', 'y', 'u', 'v', 'p'], 'p') == 4

    def test_unknown_field_returns_none(self):
        assert _find_field_column(['x', 'y', 'z'], 'u') is None

    @pytest.mark.parametrize('alias', ['U:0', 'U_x', 'Ux', 'U_0', 'u_x', 'u:0'])
    def test_u_aliases(self, alias):
        assert _find_field_column(['x', alias, 'v'], 'u') == 1

    @pytest.mark.parametrize('alias', ['U:1', 'U_y', 'Uy', 'U_1', 'u_y', 'u:1'])
    def test_v_aliases(self, alias):
        assert _find_field_column(['x', alias, 'u'], 'v') == 1

    @pytest.mark.parametrize('alias', ['U:2', 'U_z', 'Uz', 'U_2', 'u_z', 'u:2'])
    def test_w_aliases(self, alias):
        assert _find_field_column(['x', alias, 'u'], 'w') == 1

    def test_cp_aliases(self):
        assert _find_field_column(['x', 'Cp', 'CpTotal'], 'Cp') == 1
        assert _find_field_column(['x', 'CpTotal'], 'Cp') == 1

    def test_cf_alias(self):
        assert _find_field_column(['x', 'Cf'], 'Cf') == 1

    def test_quoted_column_headers(self):
        assert _find_field_column(['"x"', "'u'", 'v'], 'u') == 1
        assert _find_field_column([' x ', ' u ', ' v '], 'u') == 1


class TestCompareCaseEdgeCases:
    """Tests for compare_case — auto_generate, empty quantities, time dir matching."""

    def test_compare_case_with_empty_quantities_auto_detect_fields(self, tmp_path):
        # Create a minimal case.yaml without quantities
        case_dir = tmp_path / 'auto_case'
        case_dir.mkdir()
        ref_dir = case_dir / 'reference' / 'analytical'
        ref_dir.mkdir(parents=True)
        (case_dir / 'case.yaml').write_text(
            'id: auto-case\nname: Auto Case\ncategory: verification\n'
            'tags: []\nphysics:\n  type: incompressible\n  regime: laminar\n'
            '  equations: []\ndimension: 1D\n'
            'reference:\n  type: analytical\n  solution: ""\n  source: ""\n'
            'quantities: []\nmesh:\n  type: uniform\n  recommended: [10]\n'
        )
        ref_csv = ref_dir / 'solution.csv'
        ref_csv.write_text('x,u,v\n0.0,0.0,0.0\n0.5,0.5,0.0\n1.0,1.0,0.0')
        result_csv = tmp_path / 'result.csv'
        result_csv.write_text('x,u,v\n0.0,0.0,0.0\n0.5,0.5,0.0\n1.0,1.0,0.0')

        r = compare_case(str(case_dir), str(result_csv))
        assert r['case_id'] == 'auto-case'
        fields = [fr['field'] for fr in r['field_results'] if 'error' not in fr]
        assert 'u' in fields
        assert 'v' in fields

    def test_compare_case_pass_fail(self, tmp_path):
        case_dir = os.path.join(_CASES, 'verification', 'incompressible', 'poiseuille-2d')
        result_csv = tmp_path / 'result.csv'
        # Create data that fails tolerance for all fields (both u and v wrong)
        result_csv.write_text(
            'y,u,v\n0.0,0.1,0.001\n0.25,0.2,0.001\n0.5,0.3,0.001\n0.75,0.2,0.001\n1.0,0.1,0.001')

        r = compare_case(case_dir, str(result_csv), tolerance=1e-10)
        assert r['passed'] is False
        for fr in r['field_results']:
            if 'error' not in fr:
                assert fr.get('passed') is False, f"{fr['field']} unexpectedly passed"

    def test_compare_case_openfoam_time_dir(self, tmp_path):
        case_dir = os.path.join(_CASES, 'verification', 'incompressible', 'poiseuille-2d')
        # Simulate OpenFOAM result path: postProcessing/sets/0.5/centerline_U.xy
        of_dir = tmp_path / 'postProcessing' / 'sets' / '0.5'
        of_dir.mkdir(parents=True)
        result_csv = of_dir / 'centerline_U.xy'
        result_csv.write_text('y,u,v\n0.0,0.0,0.0\n0.5,0.125,0.0\n1.0,0.0,0.0')

        r = compare_case(case_dir, str(result_csv))
        assert r['case_id'] == 'poiseuille-2d'

    def test_compare_case_nonexistent_result_file(self):
        case_dir = os.path.join(_CASES, 'verification', 'incompressible', 'poiseuille-2d')
        with pytest.raises(FileNotFoundError):
            compare_case(case_dir, 'nonexistent_file.csv')


class TestReportEdgeCases:
    """Tests for _generate_html_report — FAIL badge, custom title, errors."""

    def test_generate_html_with_failed_result(self):
        from cfdvv.cli import _generate_html_report
        case_dir = os.path.join(_CASES, 'verification', 'incompressible', 'poiseuille-2d')
        result = {
            'case_id': 'poiseuille-2d', 'case_name': 'Test Case',
            'result_file': 'my.csv', 'ref_file': 'ref.csv',
            'passed': False, 'tolerance': 1e-6,
            'field_results': [
                {'field': 'u', 'norm_type': 'L2', 'norm_value': 0.05,
                 'all_norms': {'L1': 0.03, 'L2': 0.05, 'Linf': 0.07, 'Relative_L2': 0.1},
                 'reference_range': [0.0, 0.125], 'result_range': [0.0, 0.13], 'passed': False},
            ],
        }
        html = _generate_html_report(case_dir, result, title=None, norm_type='L2', plots=None)
        assert 'FAILED' in html
        assert 'class="fail">FAILED</span>' in html
        assert 'Comparison Plot' not in html  # no plots

    def test_generate_html_with_custom_title(self):
        from cfdvv.cli import _generate_html_report
        case_dir = os.path.join(_CASES, 'verification', 'incompressible', 'poiseuille-2d')
        result = {
            'case_id': 'poiseuille-2d', 'case_name': 'Test Case',
            'result_file': 'my.csv', 'ref_file': 'ref.csv',
            'passed': True, 'tolerance': 1e-6,
            'field_results': [
                {'field': 'u', 'norm_type': 'L2', 'norm_value': 0.0,
                 'all_norms': {'L1': 0.0, 'L2': 0.0, 'Linf': 0.0, 'Relative_L2': 0.0},
                 'reference_range': [0.0, 0.125], 'result_range': [0.0, 0.125], 'passed': True},
            ],
        }
        html = _generate_html_report(case_dir, result, title='My Custom Report', norm_type='L2', plots=None)
        assert '<title>My Custom Report</title>' in html
        assert '<h1>My Custom Report</h1>' in html

    def test_generate_html_with_error_field(self):
        from cfdvv.cli import _generate_html_report
        case_dir = os.path.join(_CASES, 'verification', 'incompressible', 'poiseuille-2d')
        result = {
            'case_id': 'poiseuille-2d', 'case_name': 'Test Case',
            'result_file': 'my.csv', 'ref_file': 'ref.csv',
            'passed': False, 'tolerance': 1e-6,
            'field_results': [
                {'field': 'u', 'error': 'Field not found in result', 'passed': False},
                {'field': 'v', 'norm_type': 'L2', 'norm_value': 0.0,
                 'all_norms': {'L1': 0.0, 'L2': 0.0, 'Linf': 0.0, 'Relative_L2': 0.0},
                 'reference_range': [0.0, 0.0], 'result_range': [0.0, 0.0], 'passed': True},
            ],
        }
        html = _generate_html_report(case_dir, result, title=None, norm_type='L2', plots=None)
        assert 'Field not found in result' in html
        assert 'class="error"' in html


class TestFindCoordinateColumns:
    """Tests for _find_coordinate_columns."""

    def test_all_three_coords(self):
        assert _find_coordinate_columns(['x', 'y', 'z', 'u', 'v']) == [0, 1, 2]

    def test_quoted_columns(self):
        assert _find_coordinate_columns(['"x"', "'y'", 'z']) == [0, 1, 2]

    def test_no_coords(self):
        assert _find_coordinate_columns(['a', 'b', 'c']) == []

    def test_partial_coords(self):
        assert _find_coordinate_columns(['x', 'z', 'u']) == [0, 1]
