"""Generate example comparison plots for documentation.

Usage: python docs/generate-example-images.py

Requires matplotlib and cfdvv to be installed (available on CI).
Output: docs/images/u.png, docs/images/u_field.png, etc.
"""

import os, sys

_THIS = os.path.dirname(os.path.abspath(__file__))
_PROJ = os.path.dirname(_THIS)
_OUT = os.path.join(_THIS, "images")
os.makedirs(_OUT, exist_ok=True)

# Check for matplotlib
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError:
    print("matplotlib not available — run on Ubuntu CI or install matplotlib first.")
    print("Generating placeholder instead.")
    # Create a simple placeholder PNG using only stdlib
    import struct, zlib

    def _make_png(w, h, r, g, b):
        """Minimal valid PNG with a single solid color."""
        raw = b""
        for _ in range(h):
            raw += b"\x00" + bytes([r, g, b] * w)
        def chunk(ctype, data):
            c = ctype + data
            return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
        ihdr = struct.pack(">IIBB", w, h, 8, 2)
        return (b"\x89PNG\r\n\x1a\n"
                + chunk(b"IHDR", ihdr)
                + chunk(b"IDAT", zlib.compress(raw))
                + chunk(b"IEND", b""))

    for name in ("u.png",):
        with open(os.path.join(_OUT, name), "wb") as f:
            f.write(_make_png(600, 400, 240, 240, 240))
        print(f"  Placeholder: {name}")
    sys.exit(0)

import numpy as np
from cfdvv.plot import plot_comparison

# Use poiseuille-2d analytical solution as reference
ref_csv = os.path.join(_PROJ, "cases", "verification", "incompressible",
                        "poiseuille-2d", "reference", "analytical", "solution.csv")
ref_data = np.loadtxt(ref_csv, delimiter=",", skiprows=1)
ref_columns = ["x", "y", "u"]

# Generate good comparison plot (result == reference)
import tempfile, shutil
with tempfile.TemporaryDirectory() as tmp:
    good_csv = os.path.join(tmp, "result_good.csv")
    shutil.copy2(ref_csv, good_csv)
    plot_comparison(
        result_file=good_csv,
        reference_data=ref_data,
        reference_columns=ref_columns,
        field_name="u",
        output_dir=_OUT,
        case_id="gen",
    )

# Remove case_id prefix from generated PNGs
for fname in os.listdir(_OUT):
    if fname.startswith("gen_"):
        os.rename(os.path.join(_OUT, fname), os.path.join(_OUT, fname[4:]))

print(f"Images saved to {_OUT}")
