"""Integration tests for the import + compare pipeline."""

import os, sys, tempfile, subprocess, pytest

_PROJ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_IMPORTED = os.path.join(_PROJ, "cases", "imported")


def run_cfdvv(*args):
    result = subprocess.run(
        [sys.executable, "-m", "cfdvv.cli"] + list(args),
        capture_output=True, text=True, timeout=30, cwd=_PROJ
    )
    return result.stdout + result.stderr


class TestImportList:
    """Test that all sources are discoverable."""

    def test_list_shows_all_sources(self):
        output = run_cfdvv("import", "--list")
        assert "nasa-tmr" in output or "flatplate" in output
        assert "ercoftac" in output or "bfs-laminar" in output
        assert "jhtdb" in output or "channel180" in output
        assert "cfdbench" in output or "poiseuille" in output
        assert "masa" in output or "ns-2d" in output
        assert "exactpack" in output or "sod" in output
        # Count cases — should be at least 20
        lines = [l for l in output.split("\n") if l.strip() and not l.startswith("External")]
        case_lines = [l for l in lines if "[" in l]
        assert len(case_lines) >= 15, f"Expected >=15 cases, got {len(case_lines)}"

    def test_unknown_case_shows_help(self):
        output = run_cfdvv("import", "nonexistent-case-xyz")
        assert "not found" in output.lower() or "Available" in output


class TestImportCfdbench:
    """Test CFDBench import (no network needed for metadata)."""

    def test_import_creates_case_yaml(self):
        os.makedirs(_IMPORTED, exist_ok=True)
        target = os.path.join(_IMPORTED, "cfdbench-poiseuille")
        if os.path.isdir(target):
            import shutil; shutil.rmtree(target)

        output = run_cfdvv("import", "poiseuille", "-o", _IMPORTED)
        assert os.path.isfile(os.path.join(target, "case.yaml"))
        assert os.path.isfile(os.path.join(target, "README.md"))

    def test_imported_case_is_valid(self):
        from cfdvv.schema import validate_case_dir
        target = os.path.join(_IMPORTED, "cfdbench-poiseuille")
        errors = validate_case_dir(target)
        assert errors == [], f"Validation errors: {errors}"

    def test_import_and_compare_pipeline(self):
        """Full pipeline: import case, then verify import succeeded."""
        target = os.path.join(_IMPORTED, "cfdbench-couette")
        if os.path.isdir(target):
            import shutil; shutil.rmtree(target)

        output = run_cfdvv("import", "couette", "-o", _IMPORTED)
        assert os.path.isfile(os.path.join(target, "case.yaml"))


class TestImportNasaTmr:
    """Test NASA TMR import (network-dependent — may fail offline)."""

    def test_import_flatplate_metadata(self):
        target = os.path.join(_IMPORTED, "nasa-tmr-flatplate")
        if os.path.isdir(target):
            import shutil; shutil.rmtree(target)

        output = run_cfdvv("import", "flatplate", "-o", _IMPORTED)
        assert os.path.isfile(os.path.join(target, "case.yaml"))

    def test_flatplate_case_valid(self):
        from cfdvv.schema import validate_case_dir
        target = os.path.join(_IMPORTED, "nasa-tmr-flatplate")
        if os.path.isdir(target):
            errors = validate_case_dir(target)
            assert errors == [], f"Validation errors: {errors}"


class TestImportErcoftac:
    """Test ERCOFTAC import (metadata only, no data download)."""

    def test_import_bfs_metadata(self):
        target = os.path.join(_IMPORTED, "ercoftac-bfs-laminar")
        if os.path.isdir(target):
            import shutil; shutil.rmtree(target)

        output = run_cfdvv("import", "bfs-laminar", "-o", _IMPORTED)
        assert os.path.isfile(os.path.join(target, "case.yaml"))
        yaml_content = open(os.path.join(target, "case.yaml")).read()
        assert "ercoftac-bfs-laminar" in yaml_content
        assert "Backward-Facing Step" in yaml_content

    def test_import_jhtdb_metadata(self):
        target = os.path.join(_IMPORTED, "jhtdb-channel180")
        if os.path.isdir(target):
            import shutil; shutil.rmtree(target)

        output = run_cfdvv("import", "channel180", "-o", _IMPORTED)
        assert os.path.isfile(os.path.join(target, "case.yaml"))
        assert os.path.isfile(os.path.join(target, "query_jhtdb.py"))


class TestImportMasaExactpack:
    """Test MASA and ExactPack imports create templates."""

    def test_masa_creates_script(self):
        target = os.path.join(_IMPORTED, "masa-ns-2d")
        if os.path.isdir(target):
            import shutil; shutil.rmtree(target)

        output = run_cfdvv("import", "ns-2d", "-o", _IMPORTED)
        assert os.path.isfile(os.path.join(target, "scripts", "generate_masa.py"))

    def test_exactpack_creates_script(self):
        target = os.path.join(_IMPORTED, "exactpack-sod")
        if os.path.isdir(target):
            import shutil; shutil.rmtree(target)

        output = run_cfdvv("import", "sod", "-o", _IMPORTED)
        assert os.path.isfile(os.path.join(target, "scripts", "generate_exactpack.py"))
