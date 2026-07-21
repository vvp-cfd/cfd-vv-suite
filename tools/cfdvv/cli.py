"""CLI entry point for cfdvv."""

import json
import os
import urllib.error
from pathlib import Path
from typing import List, Optional, Tuple

import click

from . import __version__
from .compare import compare_case
from .gci import compute_gci
from .readers import read_file
from .schema import load_case_yaml, validate_case_dir


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__, prog_name="cfdvv")
def main():
    """cfdvv — CFD Verification & Validation Suite.

    Compare CFD simulation results against reference data,
    compute error norms, convergence rates, and GCI.
    """


@main.command("list")
@click.option(
    "--category", "-c",
    type=click.Choice(["verification", "validation", "all"]),
    default="all",
    help="Filter by category.",
)
@click.option(
    "--tag", "-t", multiple=True,
    help="Filter by tags (can be used multiple times).",
)
@click.option(
    "--cases-root",
    default=None,
    help="Root directory for test cases.",
    type=click.Path(exists=True, file_okay=False),
)
def list_cases(category: str, tag: tuple, cases_root: Optional[str]):
    """List available test cases."""
    if cases_root is None:
        cases_root = _find_cases_root()

    cases_dir = Path(cases_root) / "cases"
    if not cases_dir.exists():
        click.echo(f"Cases directory not found: {cases_dir}")
        return

    found = []
    for case_path in sorted(cases_dir.rglob("case.yaml")):
        case_dir = str(case_path.parent)
        try:
            case = load_case_yaml(case_dir)
        except Exception:
            continue

        if category != "all" and case.get("category") != category:
            continue

        if tag:
            case_tags = case.get("tags", [])
            if not all(t in case_tags for t in tag):
                continue

        found.append((case_dir, case))

    if not found:
        click.echo("No cases found.")
        return

    click.echo(f"\n{'ID':<35} {'Category':<20} {'Tags':<50}")
    click.echo("-" * 105)
    for case_dir, case in found:
        case_id = case.get("id", os.path.basename(case_dir))
        cat = f"{case.get('category', '')}/{case.get('subcategory', '')}"
        tags = ", ".join(case.get("tags", []))
        click.echo(f"{case_id:<35} {cat:<20} {tags:<50}")


@main.command("validate")
@click.argument("case_dir", type=click.Path(exists=True, file_okay=False))
def validate_command(case_dir: str):
    """Validate a case YAML file."""
    errors = validate_case_dir(case_dir)
    if errors:
        click.secho(f"Validation failed for {case_dir}:", fg="red")
        for err in errors:
            click.echo(f"  - {err}")
        raise SystemExit(1)
    else:
        click.secho(f"Case {case_dir} is valid.", fg="green")


@main.command("compare")
@click.argument("case_dir", type=click.Path(exists=True, file_okay=False))
@click.option(
    "--result", "-r", "result_file",
    required=True,
    type=click.Path(exists=True, dir_okay=False),
    help="Path to user's result file (CSV/VTK).",
)
@click.option(
    "--reference", "-R", "reference_file",
    default=None,
    type=click.Path(exists=True, dir_okay=False),
    help="Path to specific reference file (overrides case's default).",
)
@click.option(
    "--norm", "-n",
    type=click.Choice(["L1", "L2", "Linf", "Relative_L2"]),
    default="L2",
    help="Error norm type.",
)
@click.option(
    "--tolerance", "tol",
    type=float,
    default=None,
    help="Tolerance for pass/fail decision.",
)
@click.option(
    "--plot/--no-plot",
    default=True,
    help="Generate comparison plots.",
)
@click.option(
    "--output-dir", "-o",
    default="results",
    type=click.Path(file_okay=False),
    help="Output directory for plots and reports.",
)
@click.option(
    "--json", "output_json",
    is_flag=True,
    default=False,
    help="Output results as JSON.",
)
@click.option(
    "--auto-generate/--no-auto-generate",
    default=False,
    help="Auto-generate analytical solution on result grid.",
)
def compare_command(
    case_dir: str,
    result_file: str,
    reference_file: Optional[str],
    norm: str,
    tol: Optional[float],
    plot: bool,
    output_dir: str,
    output_json: bool,
    auto_generate: bool = False,
):
    """Compare user results against reference data for a test case."""
    try:
        result = compare_case(
            case_dir, result_file,
            reference_file=reference_file,
            norm_type=norm,
            tolerance=tol,
            auto_generate=auto_generate,
        )
    except ValueError as e:
        click.secho(f"Error: {e}", fg="red")
        click.echo(f"\nTip: run 'cfdvv info {case_dir}' to see expected CSV format and mesh requirements.")
        raise SystemExit(1)
    except Exception as e:
        click.secho(f"Error: {e}", fg="red")
        raise SystemExit(1)

    if output_json:
        click.echo(json.dumps(result, indent=2, default=str))
    else:
        _print_comparison(result, tol)

    if plot:
        _generate_plots(case_dir, result_file, result, output_dir)

    if tol is not None:
        if result["passed"]:
            click.secho("\nPASSED", fg="green", bold=True)
        else:
            click.secho("\nFAILED", fg="red", bold=True)
            raise SystemExit(1)


@main.command("gci")
@click.argument("case_dir", type=click.Path(exists=True, file_okay=False))
@click.option(
    "--results", "-r", "result_files",
    required=True, multiple=True,
    type=click.Path(exists=True, dir_okay=False),
    help="Result files (3+: coarse, medium, fine). Use -r multiple times.",
)
@click.option(
    "--mesh-sizes", "mesh_sizes_str",
    default="1.0,0.5,0.25",
    help="Comma-separated mesh sizes: h_coarse,h_medium,h_fine.",
)
@click.option(
    "--quantity", "-q",
    default=None,
    help="Specific quantity to analyze.",
)
def gci_command(
    case_dir: str,
    result_files: tuple,
    mesh_sizes_str: str,
    quantity: Optional[str],
):
    """Compute Grid Convergence Index (GCI)."""
    try:
        mesh_sizes = [float(x.strip()) for x in mesh_sizes_str.split(",")]
    except ValueError:
        click.secho("Error: --mesh-sizes must be comma-separated numbers", fg="red")
        raise SystemExit(1)

    result = compute_gci(
        case_dir,
        list(result_files),
        mesh_sizes=mesh_sizes,
        quantity_name=quantity,
    )

    if "error" in result:
        click.secho(f"Error: {result['error']}", fg="red")
    else:
        _print_gci(result)


@main.command("info")
@click.argument("case_dir", type=click.Path(exists=True, file_okay=False))
def info_command(case_dir: str):
    """Show detailed info about a test case."""
    try:
        case = load_case_yaml(case_dir)
    except Exception as e:
        click.secho(f"Error: {e}", fg="red")
        raise SystemExit(1)

    click.echo(f"\n{'='*60}")
    click.echo(f"  {case.get('name', case.get('id'))}")
    click.echo(f"{'='*60}")
    click.echo(f"  ID:         {case.get('id')}")
    click.echo(f"  Category:   {case.get('category')}/{case.get('subcategory', '')}")
    click.echo(f"  Dimension:  {case.get('dimension')}")
    click.echo(f"  Tags:       {', '.join(case.get('tags', []))}")

    physics = case.get("physics", {})
    click.echo(f"  Physics:")
    click.echo(f"    Type:       {physics.get('type')}")
    click.echo(f"    Regime:     {physics.get('regime', '—')}")
    click.echo(f"    Equations:  {', '.join(physics.get('equations', []))}")
    click.echo(f"    Convective: {physics.get('convective', '—')}")

    ref = case.get("reference", {})
    click.echo(f"  Reference:  {ref.get('type')} — {ref.get('source', '—')}")
    click.echo(f"  Solution:   {ref.get('solution', case.get('description', '—'))}")

    click.echo(f"\n  Quantities:")
    for q in case.get("quantities", []):
        click.echo(f"    - {q.get('name'):<15} type={q.get('type'):<10} norm={q.get('norm', 'L2')}")

    params = case.get("parameters", {})
    if params:
        click.echo(f"\n  Parameters:")
        for p in params:
            click.echo(f"    {p.get('name')}: default={p.get('default')}")

    click.echo()


def _print_comparison(result: dict, tol: Optional[float]):
    """Print comparison results in a formatted table."""
    click.echo(f"\nCase: {result['case_name']} ({result['case_id']})")
    click.echo(f"Result: {result['result_file']}")
    if tol is not None:
        click.echo(f"Tolerance: {tol}")
    click.echo()

    header = f"{'Field':<15} {'Norm':<12} {'Value':<14} {'Min(ref)':<12} {'Max(ref)':<12}"
    if tol is not None:
        header += f" {'Pass':<6}"
    click.echo(header)
    click.echo("-" * (80 if tol is None else 86))

    for fr in result.get("field_results", []):
        if "error" in fr:
            click.echo(f"{fr['field']:<15} {'ERROR':<12} {fr['error']}")
            continue
        line = (
            f"{fr['field']:<15} "
            f"{fr.get('norm_type', '-'):<12} "
            f"{fr.get('norm_value', 0):<14.6e} "
            f"{fr.get('reference_range', [0, 0])[0]:<12.4f} "
            f"{fr.get('reference_range', [0, 0])[1]:<12.4f}"
        )
        if tol is not None:
            passed = fr.get("passed", False)
            status = click.style("PASS", fg="green") if passed else click.style("FAIL", fg="red")
            line += f" {status:<6}"
        click.echo(line)


def _generate_plots(case_dir: str, result_file: str, result: dict, output_dir: str):
    """Generate comparison plots."""
    from .plot import plot_comparison

    case = load_case_yaml(case_dir)

    ref_dir = os.path.join(case_dir, "reference")
    ref_type = case["reference"]["type"]
    ref_full_dir = os.path.join(ref_dir, ref_type)

    if not os.path.isdir(ref_full_dir):
        for alt in ["analytical", "experimental", "dns-les"]:
            alt_dir = os.path.join(ref_dir, alt)
            if os.path.isdir(alt_dir):
                ref_full_dir = alt_dir
                break

    csv_files = sorted([f for f in os.listdir(ref_full_dir) if f.endswith(".csv")])
    if not csv_files:
        click.echo("No reference CSV files for plotting.", err=True)
        return

    from .readers import read_file
    ref_data, ref_columns = read_file(os.path.join(ref_full_dir, csv_files[0]))

    case_id = case["id"]
    plot_output_dir = os.path.join(output_dir, case_id)
    Path(plot_output_dir).mkdir(parents=True, exist_ok=True)

    for field_name in [fr["field"] for fr in result.get("field_results", []) if "error" not in fr]:
        try:
            filepath = plot_comparison(
                result_file, ref_data, ref_columns,
                field_name=field_name,
                output_dir=plot_output_dir,
                case_id=case_id,
            )
            click.echo(f"  Plot: {filepath}")
        except Exception as e:
            click.echo(f"  Plot error ({field_name}): {e}", err=True)


def _generate_plot_base64(case_dir: str, result_file: str, result: dict) -> List[Tuple[str, str]]:
    """Generate comparison plots for all fields; returns [(base64, field_name), ...]."""
    import tempfile, base64
    from .plot import plot_comparison
    from .readers import read_file

    try:
        case = load_case_yaml(case_dir)
        ref_dir = os.path.join(case_dir, "reference")
        ref_type = case["reference"]["type"]
        ref_full_dir = os.path.join(ref_dir, ref_type)
        if not os.path.isdir(ref_full_dir):
            for alt in ["analytical", "experimental", "dns-les"]:
                alt_dir = os.path.join(ref_dir, alt)
                if os.path.isdir(alt_dir):
                    ref_full_dir = alt_dir
                    break
        csv_files = sorted([f for f in os.listdir(ref_full_dir) if f.endswith(".csv")])
        if not csv_files:
            return []

        ref_data, ref_columns = read_file(os.path.join(ref_full_dir, csv_files[0]))
        fields = [fr["field"] for fr in result.get("field_results", []) if "error" not in fr]
        if not fields:
            return []

        case_id = case["id"]
        result_list = []
        with tempfile.TemporaryDirectory() as tmp:
            for field_name in fields:
                fp = plot_comparison(
                    result_file, ref_data, ref_columns,
                    field_name=field_name,
                    output_dir=tmp,
                    case_id=case_id,
                )
                with open(fp, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("ascii")
                result_list.append((b64, field_name))
        return result_list
    except Exception:
        return []


def _print_gci(result: dict):
    """Print GCI results."""
    click.echo(f"\nGCI Analysis for: {result.get('case_dir')}")
    click.echo(f"Mesh sizes: {result.get('mesh_sizes')}")
    click.echo(f"Refinement ratios: {result.get('refinement_ratios')}")
    click.echo()

    for qr in result.get("quantity_results", []):
        click.echo(f"  Quantity {qr['quantity_index']}:")
        click.echo(f"    f1 (coarse) = {qr['f1']:.8f}")
        click.echo(f"    f2 (med)    = {qr['f2']:.8f}")
        click.echo(f"    f3 (fine)   = {qr['f3']:.8f}")
        click.echo(f"    Order p     = {qr['order_p']}")
        if qr["extrapolated_value"] is not None:
            click.echo(f"    Extrapolated = {qr['extrapolated_value']:.8f}")
        if qr["gci21"] is not None:
            click.echo(f"    GCI            = {qr['gci21']:.6f}")
        click.echo()


@main.command("report")
@click.argument("case_dir", type=click.Path(exists=True, file_okay=False))
@click.option(
    "--result", "-r", "result_file",
    required=True,
    type=click.Path(exists=True, dir_okay=False),
    help="Path to user's result file.",
)
@click.option(
    "--norm", "-n",
    type=click.Choice(["L1", "L2", "Linf", "Relative_L2"]),
    default="L2",
    help="Error norm type.",
)
@click.option(
    "--output", "-o",
    default="report.html",
    type=click.Path(dir_okay=False),
    help="Output HTML file.",
)
@click.option(
    "--title",
    default=None,
    help="Custom report title.",
)
def report_command(
    case_dir: str,
    result_file: str,
    norm: str,
    output: str,
    title: Optional[str],
):
    """Generate an HTML verification report with embedded comparison plots."""
    try:
        result = compare_case(case_dir, result_file, norm_type=norm)
    except Exception as e:
        click.secho(f"Error: {e}", fg="red")
        raise SystemExit(1)

    plots = _generate_plot_base64(case_dir, result_file, result)
    html = _generate_html_report(case_dir, result, title, norm, plots)
    with open(output, "w", encoding="utf-8") as f:
        f.write(html)
    click.secho(f"Report written: {output}", fg="green")


def _generate_html_report(
    case_dir: str, result: dict, title: Optional[str], norm_type: str,
    plots: Optional[List[Tuple[str, str]]] = None,
) -> str:
    """Generate a standalone HTML report."""
    from datetime import datetime

    case = load_case_yaml(case_dir)
    case_id = case["id"]
    case_name = case.get("name", case_id)
    report_title = title or f"V&V Report: {case_name}"

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    rows_html = ""
    for fr in result.get("field_results", []):
        if "error" in fr:
            row = (
                f'<tr><td>{fr["field"]}</td>'
                f'<td colspan="5" class="error">{fr["error"]}</td></tr>'
            )
        else:
            all_n = fr.get("all_norms", {})
            norms_cell = (
                f'<td>{fr.get("norm_value", 0):.6e}</td>'
                f'<td>{all_n.get("L1", 0):.4e}</td>'
                f'<td>{all_n.get("Linf", 0):.4e}</td>'
                f'<td>{all_n.get("Relative_L2", 0):.4e}</td>'
            )
            row = (
                f'<tr><td>{fr["field"]}</td>'
                f'<td>{fr.get("norm_type", "-")}</td>'
                f'{norms_cell}'
                f'<td>{fr.get("reference_range", [0,0])[0]:.4f}</td>'
                f'<td>{fr.get("reference_range", [0,0])[1]:.4f}</td></tr>'
            )
        rows_html += row

    if plots:
        plot_sections = ""
        for b64, fname in plots:
            plot_sections += f"""<h2>Comparison Plot — {fname}</h2>
<img src="data:image/png;base64,{b64}" alt="Comparison plot - {fname}" style="max-width:100%; height:auto;">
"""
    else:
        plot_sections = ""

    physics = case.get("physics", {})
    ref = case.get("reference", {})

    passed = result.get("passed")
    if passed is True:
        badge = '<span class="pass">PASSED</span>'
    elif passed is False:
        badge = '<span class="fail">FAILED</span>'
    else:
        badge = '<span class="na">NO TOLERANCE</span>'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{report_title}</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
       max-width: 900px; margin: 40px auto; padding: 0 20px; color: #333;
       background: #f8f9fa; }}
h1 {{ color: #1a1a2e; border-bottom: 3px solid #16213e; padding-bottom: 10px; }}
h2 {{ color: #0f3460; margin-top: 30px; }}
table {{ width: 100%; border-collapse: collapse; margin: 15px 0; background: white;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
th, td {{ padding: 10px 14px; text-align: left; border-bottom: 1px solid #e0e0e0; }}
th {{ background: #16213e; color: white; font-weight: 600; }}
tr:hover {{ background: #f1f3f5; }}
.meta {{ display: grid; grid-template-columns: auto 1fr; gap: 4px 16px; margin: 15px 0; }}
.meta dt {{ font-weight: 600; color: #555; }}
.meta dd {{ margin: 0; }}
.pass {{ color: #155724; background: #d4edda; padding: 4px 10px; border-radius: 4px;
        font-weight: bold; }}
.fail {{ color: #721c24; background: #f8d7da; padding: 4px 10px; border-radius: 4px;
        font-weight: bold; }}
.na {{ color: #856404; background: #fff3cd; padding: 4px 10px; border-radius: 4px; }}
.error {{ color: #c00; }}
.footer {{ margin-top: 30px; padding-top: 10px; border-top: 1px solid #ddd;
          font-size: 0.85em; color: #888; }}
</style>
</head>
<body>
<h1>{report_title}</h1>
{badge}

<h2>Case Information</h2>
<dl class="meta">
    <dt>Case ID</dt><dd>{case_id}</dd>
    <dt>Category</dt><dd>{case.get("category", "")} / {case.get("subcategory", "")}</dd>
    <dt>Dimension</dt><dd>{case.get("dimension", "")}</dd>
    <dt>Physics</dt><dd>{physics.get("type", "")}, {physics.get("regime", "")}</dd>
    <dt>Reference</dt><dd>{ref.get("type", "")} — {ref.get("source", "")}</dd>
    <dt>Result (user)</dt><dd>{os.path.relpath(result.get("result_file", ""))}</dd>
    <dt>Reference</dt><dd>{os.path.relpath(result.get("ref_file", ""))}</dd>
    <dt>Generated</dt><dd>{now}</dd>
</dl>

<h2>Comparison Results</h2>
<table>
<tr>
    <th>Field</th><th>Norm</th>
    <th>{norm_type}</th><th>L1</th><th>Linf</th><th>Rel. L2</th>
    <th>Ref Min</th><th>Ref Max</th>
</tr>
{rows_html}
</table>

{plot_sections}

<h2>Parameters</h2>
<dl class="meta">
"""
    for p in case.get("parameters", []):
        html += f"    <dt>{p.get('name')}</dt><dd>{p.get('default')} ({p.get('description', '')})</dd>\n"

    html += f"""</dl>
<div class="footer">
    Generated by <strong>cfdvv</strong> v{__version__} —
    CFD Verification & Validation Suite
</div>
</body>
</html>"""
    return html


@main.command("benchmark")
@click.option(
    "--category", "-c",
    type=click.Choice(["verification", "all"]),
    default="verification",
    help="Category to benchmark.",
)
@click.option(
    "--cases-root",
    default=None,
    type=click.Path(exists=True, file_okay=False),
    help="Root directory for test cases.",
)
@click.option(
    "--tolerance", "-t",
    type=float,
    default=1e-8,
    help="Tolerance for self-compare.",
)
def benchmark_command(category: str, cases_root: Optional[str], tolerance: float):
    """Run self-comparison on all analytical verification cases."""
    import glob as glob_mod

    if cases_root is None:
        cases_root = _find_cases_root()

    cases_dir = Path(cases_root) / "cases"
    if not cases_dir.exists():
        click.secho(f"Cases directory not found: {cases_dir}", fg="red")
        raise SystemExit(1)

    case_files = sorted(glob_mod.glob(str(cases_dir / "**" / "case.yaml"), recursive=True))

    passed, failed, skipped = 0, 0, 0
    for yf in case_files:
        cdir = os.path.dirname(yf)
        case = load_case_yaml(cdir)

        if category == "verification" and case.get("category") != "verification":
            continue

        # Find reference CSV
        ref_dirs = [
            os.path.join(cdir, "reference", "analytical"),
            os.path.join(cdir, "reference", "mms"),
        ]
        ref_file = None
        for rd in ref_dirs:
            if os.path.isdir(rd):
                csvs = sorted([f for f in os.listdir(rd) if f.endswith(".csv")])
                if csvs:
                    ref_file = os.path.join(rd, csvs[0])
                    break

        if not ref_file:
            click.echo(f"  SKIP: {case['id']} (no analytical reference CSV)")
            skipped += 1
            continue

        try:
            result = compare_case(cdir, ref_file, norm_type="L2", tolerance=tolerance)
            if result["passed"]:
                click.echo(f"  PASS: {case['id']}")
                passed += 1
            else:
                click.secho(f"  FAIL: {case['id']}", fg="red")
                for fr in result["field_results"]:
                    if "error" not in fr and not fr.get("passed", True):
                        click.echo(f"    {fr['field']}: {fr['norm_value']:.2e} > {tolerance}")
                failed += 1
        except ValueError:
            # Integral-only CSV (scalar values, no coordinate columns)
            # These can't be self-compared by field — skip
            click.echo(f"  SKIP: {case['id']} (integral-only reference, no field coordinates)")
            skipped += 1
        except Exception as e:
            click.secho(f"  ERROR: {case['id']} — {e}", fg="yellow")
            failed += 1

    click.echo(f"\nResults: {passed} passed, {failed} failed, {skipped} skipped")
    if failed > 0:
        raise SystemExit(1)


@main.command("example-output")
@click.argument("case_dir", type=click.Path(exists=True, file_okay=False))
def example_output_command(case_dir: str):
    """Show expected CSV output format for a test case."""
    case = load_case_yaml(case_dir)

    click.secho(f"\n=== {case['name']} — Expected CSV Format ===\n", bold=True)
    click.echo(f"Case: {case['id']} ({case['dimension']})")
    click.echo(f"Reference type: {case['reference']['type']}")
    click.echo(f"Physics: {case['physics']['type']}, {case['physics']['regime']}")
    click.echo()

    # Build expected CSV header
    dim = case['dimension'].upper()
    coord_cols = ['x', 'y', 'z'] if '3D' in dim else (['x', 'y'] if '2D' in dim else ['x'])
    field_names = [q['name'] for q in case.get('quantities', [])]
    if not field_names:
        field_names = ['u', 'v', 'w', 'p']

    # Remove dups from coords
    field_names = [f for f in field_names if f not in coord_cols]
    all_cols = coord_cols + field_names

    click.secho("CSV header:", fg="green")
    click.echo("  " + ",".join(all_cols))
    click.echo()

    click.secho("Example row:", fg="green")
    example_vals = []
    for c in all_cols:
        if c in ('x', 'y', 'z'):
            example_vals.append("0.0")
        elif c in ('u', 'v', 'w'):
            example_vals.append("0.5")
        elif c == 'p':
            example_vals.append("1.0")
        elif c == 'T':
            example_vals.append("300.0")
        elif c == 'rho':
            example_vals.append("1.0")
        elif c == 'Cp':
            example_vals.append("0.5")
        elif c == 'Cf':
            example_vals.append("0.001")
        elif c == 'Nu' or 'Nu_' in c:
            example_vals.append("4.5")
        else:
            example_vals.append("0.0")
    click.echo("  " + ",".join(example_vals))
    click.echo()

    # Show mesh requirements
    mesh = case.get('mesh', {})
    if mesh:
        click.secho("Mesh requirements:", fg="green")
        click.echo(f"  Type:    {mesh.get('type', 'unspecified')}")
        click.echo(f"  Recommended resolution: {mesh.get('recommended', 'unspecified')}")
        gci_grids = mesh.get('convergence_study', [])
        if gci_grids:
            click.echo(f"  GCI grids: {', '.join(str(g) for g in gci_grids)}")
        click.echo(f"  Wall refinement: {mesh.get('wall_refinement', False)}")
        click.echo(f"  Notes: {mesh.get('notes', '—')}")
        click.echo()

    # Show tolerances
    tols = case.get('tolerances', {})
    if tols:
        click.secho("Tolerances (pass/fail thresholds):", fg="green")
        for k, v in tols.items():
            click.echo(f"  {k}: {v}")

    click.echo()


@main.command("import")
@click.argument("case_id", required=False, default="")
@click.option(
    "--list", "list_flag",
    is_flag=True,
    default=False,
    help="List all available external cases.",
)
@click.option(
    "--result", "-r", "result_file",
    default=None,
    type=click.Path(exists=True, dir_okay=False),
    help="Compare imported case against your result file.",
)
@click.option(
    "--output-dir", "-o",
    default="cases/imported",
    type=click.Path(file_okay=False),
    help="Parent directory for imported cases.",
)
@click.option(
    "--norm", "-n",
    type=click.Choice(["L1", "L2", "Linf", "Relative_L2"]),
    default="L2",
    help="Error norm type.",
)
@click.option(
    "--plot/--no-plot",
    default=True,
    help="Generate comparison plots.",
)
def import_command(case_id: str, list_flag: bool, result_file: Optional[str],
                   output_dir: str, norm: str, plot: bool):
    """Import test cases from external V&V databases and optionally compare.

    Examples:
      cfdvv import --list
      cfdvv import flatplate -r my_results.csv
      cfdvv import hump -r my_cp.csv --norm L2
    """
    from .importers import list_all_cases, find_case, import_case

    if list_flag:
        cases = list_all_cases()
        click.secho(f"\nExternal cases ({len(cases)} available):\n", bold=True)
        for cid, src, _ in cases:
            click.echo(f"  {cid:<25} [{src}]")
        click.echo()
        return

    if not case_id:
        click.secho("Usage: cfdvv import <case> [-r result.csv]", fg="yellow")
        click.echo("       cfdvv import --list")
        raise SystemExit(1)

    source, imp = find_case(case_id)
    if not source:
        cases = list_all_cases()
        click.secho(f"Case '{case_id}' not found in any external source.", fg="red")
        click.echo(f"\nAvailable ({len(cases)}):")
        for cid, src, _ in cases:
            click.echo(f"  {cid} [{src}]")
        raise SystemExit(1)

    try:
        click.echo(f"Importing {case_id} from {source}...")
        target = import_case(source, case_id, output_dir)
        click.secho(f"Imported: {target}", fg="green")
    except Exception as e:
        click.secho(f"Import error: {e}", fg="red")
        raise SystemExit(1)

    if result_file:
        click.echo(f"\nComparing against: {result_file}")
        from .compare import compare_case
        try:
            result = compare_case(target, result_file, norm_type=norm)
            _print_comparison(result, None)
            if plot:
                _generate_plots(target, result_file, result, "results")
        except Exception as e:
            click.secho(f"Comparison error: {e}", fg="red")
            click.echo(f"\nTip: run 'cfdvv info {target}' to see expected CSV format.")
            raise SystemExit(1)


def _find_cases_root() -> str:
    """Find the cases root directory relative to the package."""
    current = Path.cwd()
    for parent in [current] + list(current.parents)[:-1]:
        cases_dir = parent / "cases"
        if cases_dir.is_dir():
            return str(parent)
    return str(current)


if __name__ == "__main__":
    main()
