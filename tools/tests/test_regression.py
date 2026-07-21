import os, subprocess, sys, pytest

_THIS = os.path.dirname(os.path.abspath(__file__))
_PROJ = os.path.dirname(os.path.dirname(_THIS))
TEST_DIR = os.path.join(_THIS, "integration_data")
CASE = os.path.join(_PROJ, "cases", "verification", "incompressible", "poiseuille-2d")


def run_cfdvv(*args):
    result = subprocess.run(
        [sys.executable, "-m", "cfdvv.cli"] + list(args),
        capture_output=True, text=True, timeout=30, cwd=_PROJ
    )
    return result.stdout + result.stderr


def _read_golden(name):
    with open(os.path.join(TEST_DIR, name), "r", encoding="utf-8") as f:
        return f.read()


def _strip_paths(text):
    """Normalize machine-specific paths in CLI output for cross-platform comparison."""
    import re
    # Replace the Result: line with a placeholder (paths differ per machine)
    text = re.sub(r'Result:.*\n', 'Result: <PATH>\n', text)
    return text


class TestGoodSolution:
    def test_good_compare_zero(self):
        result_csv = os.path.join(TEST_DIR, "good_poiseuille.csv")
        output = run_cfdvv("compare", CASE, "-r", result_csv, "--no-plot")
        golden = _read_golden("golden_good.txt")
        assert _strip_paths(output) == _strip_paths(golden), "CLI output changed"

    def test_good_report_html(self):
        import tempfile
        report_path = os.path.join(tempfile.gettempdir(), "test_report.html")
        result_csv = os.path.join(TEST_DIR, "good_poiseuille.csv")
        run_cfdvv("report", CASE, "-r", result_csv, "-o", report_path)
        with open(report_path, "r", encoding="utf-8") as f:
            result = f.read()
        assert "poiseuille-2d" in result
        assert "Plane Poiseuille" in result
        assert "Comparison Plot" in result, "report should contain embedded plot sections"
        assert "Result (user)" in result, "report should show user result path"
        assert "Reference" in result, "report should show reference path"
        # Plots should appear after the comparison table
        assert result.find("Comparison Plot") > result.find("Comparison Results"), \
            "plot section must be after comparison results"


class TestBadSolution:
    def test_bad_compare_detects_error(self):
        result_csv = os.path.join(TEST_DIR, "bad_poiseuille.csv")
        output = run_cfdvv("compare", CASE, "-r", result_csv, "--no-plot")
        golden = _read_golden("golden_bad.txt")
        assert _strip_paths(output) == _strip_paths(golden), "CLI output changed"


class TestFewPoints:
    def test_few_points_stable(self):
        result_csv = os.path.join(TEST_DIR, "few_points.csv")
        output = run_cfdvv("compare", CASE, "-r", result_csv, "--no-plot")
        golden = _read_golden("golden_few.txt")
        assert _strip_paths(output) == _strip_paths(golden), "CLI output changed"


class TestExampleOutput:
    def test_example_output_stable(self):
        output = run_cfdvv("example-output", CASE)
        golden = _read_golden("golden_example.txt")
        assert _strip_paths(output) == _strip_paths(golden), "CLI output changed"
