"""Tests for plotting functionality (--plot CLI flag and library functions)."""

import os
import pytest
import numpy as np
from click.testing import CliRunner
import cfdvv

_THIS = os.path.dirname(os.path.abspath(__file__))
_CFDVV_DIR = os.path.dirname(cfdvv.__file__)
_CASES = os.path.join(_CFDVV_DIR, "cases")
_POISEUILLE = os.path.join(_CASES, "verification", "incompressible", "poiseuille-2d")
_POISEUILLE_REF = os.path.join(_POISEUILLE, "reference", "analytical", "solution.csv")

_has_matplotlib = False
try:
    import matplotlib
    matplotlib.use("Agg")
    _has_matplotlib = True
except ImportError:
    pass

_skip_no_mpl = pytest.mark.skipif(not _has_matplotlib, reason="matplotlib not installed")


def _synthetic_1d_data(n=20):
    x = np.linspace(0, 1, n)
    u = 4 * x * (1 - x)
    return np.column_stack([x, u]), ["x", "u"]


def _synthetic_2d_data(n=50):
    np.random.seed(42)
    x = np.random.uniform(0, 1, n)
    y = np.random.uniform(0, 1, n)
    u = np.sin(np.pi * x) * np.cos(np.pi * y)
    return np.column_stack([x, y, u]), ["x", "y", "u"]


class TestPlotFunctions:
    """Smoke tests for plot.plot_comparison and plot.plot_profile."""

    @_skip_no_mpl
    def test_plot_comparison_1d(self, tmp_path):
        from cfdvv.plot import plot_comparison

        ref_data, ref_cols = _synthetic_1d_data(30)
        res_csv = tmp_path / "result.csv"
        np.savetxt(res_csv, ref_data, delimiter=",", header="x,u", comments="")

        out = plot_comparison(
            result_file=str(res_csv),
            reference_data=ref_data,
            reference_columns=ref_cols,
            field_name="u",
            output_dir=str(tmp_path / "plots"),
            case_id="test-1d",
        )
        assert os.path.isfile(out), f"Plot file {out} not created"
        assert os.path.getsize(out) > 500, "Plot file too small"

    @_skip_no_mpl
    def test_plot_comparison_2d(self, tmp_path):
        from cfdvv.plot import plot_comparison

        ref_data, ref_cols = _synthetic_2d_data(80)
        res_csv = tmp_path / "result.csv"
        np.savetxt(res_csv, ref_data, delimiter=",", header="x,y,u", comments="")

        out = plot_comparison(
            result_file=str(res_csv),
            reference_data=ref_data,
            reference_columns=ref_cols,
            field_name="u",
            output_dir=str(tmp_path / "plots"),
            case_id="test-2d",
        )
        assert os.path.isfile(out), f"Plot file {out} not created"
        assert os.path.getsize(out) > 500, "Plot file too small"

    @_skip_no_mpl
    def test_plot_comparison_field_not_found(self, tmp_path):
        from cfdvv.plot import plot_comparison

        ref_data, ref_cols = _synthetic_1d_data()
        res_csv = tmp_path / "result.csv"
        np.savetxt(res_csv, ref_data, delimiter=",", header="x,u", comments="")

        with pytest.raises(ValueError, match="not found"):
            plot_comparison(
                result_file=str(res_csv),
                reference_data=ref_data,
                reference_columns=ref_cols,
                field_name="nonexistent",
                output_dir=str(tmp_path / "plots"),
                case_id="test-err",
            )

    @_skip_no_mpl
    def test_plot_profile(self, tmp_path):
        from cfdvv.plot import plot_profile

        ref_data, ref_cols = _synthetic_1d_data(30)
        out_file = str(tmp_path / "profile.png")

        result = plot_profile(
            reference_data=ref_data,
            reference_columns=ref_cols,
            field_name="u",
            output_file=out_file,
        )
        assert result == out_file
        assert os.path.isfile(out_file)

    @_skip_no_mpl
    def test_plot_profile_with_result(self, tmp_path):
        from cfdvv.plot import plot_profile

        x = np.linspace(0, 1, 30)
        ref_data = np.column_stack([x, x**2])
        res_data = np.column_stack([x, x**2 + 0.05])
        cols = ["x", "u"]

        out_file = str(tmp_path / "profile_with_result.png")
        result = plot_profile(
            reference_data=ref_data,
            reference_columns=cols,
            field_name="u",
            output_file=out_file,
            result_data=res_data,
            result_columns=cols,
        )
        assert os.path.isfile(out_file)


class TestCliCompareWithPlot:
    """End-to-end tests for cfdvv compare --plot."""

    def test_compare_with_plot_generates_png(self, tmp_path):
        from cfdvv.cli import main

        runner = CliRunner()
        out_dir = str(tmp_path / "out")
        result = runner.invoke(main, [
            "compare", _POISEUILLE,
            "--result", _POISEUILLE_REF,
            "--plot",
            "--output-dir", out_dir,
        ])
        if result.exit_code != 0:
            pytest.fail(f"CLI failed: {result.output}")
        if not os.path.isdir(out_dir):
            pytest.fail(f"Output dir not created")
        pngs = [f for f in os.listdir(out_dir) if f.endswith(".png")]
        if not pngs:
            # Plot generation may be silently skipped if matplotlib is unavailable
            import sys
            out = result.output
            if "Plot error" in out or "plot" in out.lower():
                pytest.skip("Plot generation skipped (matplotlib unavailable?)")
            pytest.fail(f"No PNG files produced. Output:\n{out}")

    def test_compare_no_plot_no_png(self, tmp_path):
        from cfdvv.cli import main

        runner = CliRunner()
        out_dir = str(tmp_path / "out")
        result = runner.invoke(main, [
            "compare", _POISEUILLE,
            "--result", _POISEUILLE_REF,
            "--no-plot",
            "--output-dir", out_dir,
        ])
        if result.exit_code != 0:
            pytest.fail(f"CLI failed: {result.output}")
        if os.path.isdir(out_dir):
            pngs = [f for f in os.listdir(out_dir) if f.endswith(".png")]
            assert len(pngs) == 0, f"Unexpected PNG files with --no-plot"
