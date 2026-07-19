"""Import external V&V data: NASA TMR, ERCOFTAC, JHTDB, CFDBench, MASA, ExactPack."""

import os, urllib.request, urllib.error, csv, tempfile, shutil, ssl, json, subprocess, sys
from abc import ABC, abstractmethod
from pathlib import Path


def _urlretrieve(url, path, timeout=10):
    """Download with SSL fallback and timeout."""
    try:
        urllib.request.urlretrieve(url, path)
    except urllib.error.URLError:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(url, context=ctx, timeout=timeout) as resp:
            with open(path, 'wb') as f:
                f.write(resp.read())

def _urlread(url):
    """Read URL content as text with SSL fallback."""
    try:
        with urllib.request.urlopen(url) as resp:
            return resp.read().decode('utf-8', errors='replace')
    except urllib.error.URLError:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(url, context=ctx) as resp:
            return resp.read().decode('utf-8', errors='replace')


def _write_case_yaml(target_dir, case_id, name, dim, tags, source_url, notes, quantities):
    yaml = f"""id: {case_id}
name: "{name}"
category: validation
subcategory: turbulent
tags: {tags}
physics:
  type: incompressible
  regime: turbulent
  convective: true
  equations: [continuity, rans]
dimension: {dim}
reference:
  type: experimental
  source: "{name}"
  doi: "{source_url}"
quantities:
"""
    for q in quantities:
        yaml += f"  - name: {q['name']}\n"
        yaml += f"    type: {q.get('type','profile')}\n"
        yaml += f"    location: \"{q.get('location','')}\"\n"
        yaml += f"    norm: {q.get('norm','L2')}\n"
    yaml += f"""mesh:
  type: "structured"
  recommended: [200, 100]
  wall_refinement: true
  notes: "See source for grid details."
tolerances:
  L2: 0.05
  Linf: 0.15
notes: "{notes} Imported from {source_url}"
"""
    with open(os.path.join(target_dir, "case.yaml"), "w", encoding="utf-8") as f:
        f.write(yaml)


class BaseImporter(ABC):
    @abstractmethod
    def name(self) -> str: pass
    @abstractmethod
    def list_cases(self) -> list: pass
    @abstractmethod
    def import_case(self, case_id: str, target_dir: str) -> str: pass


# ---------- NASA TMR ------------------------------------------------
class NasaTmrImporter(BaseImporter):
    BASE = "https://turbmodels.larc.nasa.gov"

    CASES = {
        "flatplate": {
            "title": "Flat Plate TBL (NASA TMR)", "dim": "2D",
            "tags": ["newtonian","turbulent","boundary-layer","experimental","rans-validation","nasa-tmr"],
            "notes": "Incompressible ZPG turbulent flat plate. Re_theta up to 31000. Cf and velocity profiles.",
            "quants": [{"name":"Cf","type":"profile","location":"plate surface","norm":"L2"}],
            "files": [("flatplate_val_cf.txt","skin_friction.csv"), ("flatplate_val_vel.dat","velocity_profiles.csv")],
        },
        "hump": {
            "title": "Wall-Mounted Hump (NASA TMR)", "dim": "2D",
            "tags": ["newtonian","turbulent","separation","experimental","rans-validation","nasa-tmr"],
            "notes": "NASA CFDVAL2004 Case 3. Cp distribution, separation bubble.",
            "quants": [{"name":"Cp","type":"profile","location":"hump surface","norm":"L2"}],
            "files": [("nasahump_val_cp_exp.dat","cp_experimental.csv")],
        },
        "bump": {
            "title": "2D Bump (NASA TMR)", "dim": "2D",
            "tags": ["newtonian","turbulent","adverse-pressure-gradient","experimental","rans-validation","nasa-tmr"],
            "notes": "2D bump in turbulent channel. Adverse pressure gradient, incipient separation.",
            "quants": [{"name":"Cp","type":"profile","location":"bump surface","norm":"L2"},{"name":"Cf","type":"profile","location":"bump surface","norm":"L2"}],
            "files": [("bump_val_cp.dat","cp.csv")],
        },
        "naca0012": {
            "title": "NACA 0012 (NASA TMR)", "dim": "2D",
            "tags": ["newtonian","turbulent","compressible","airfoil","experimental","rans-validation","nasa-tmr"],
            "notes": "Transonic NACA 0012. M=0.15-0.8, alpha=0-4 deg.",
            "quants": [{"name":"Cp","type":"profile","location":"airfoil surface","norm":"L2"}],
            "files": [],
        },
        "rae2822": {
            "title": "RAE 2822 (NASA TMR)", "dim": "2D",
            "tags": ["newtonian","turbulent","compressible","transonic","airfoil","shock","experimental","rans-validation","nasa-tmr"],
            "notes": "Transonic RAE 2822. Case 9 (M=0.73) and Case 10 (M=0.75).",
            "quants": [{"name":"Cp","type":"profile","location":"airfoil surface","norm":"L2"}],
            "files": [],
        },
        "2dzp": {
            "title": "2D ZPG Flat Plate Profiles (NASA TMR)", "dim": "2D",
            "tags": ["newtonian","turbulent","boundary-layer","experimental","rans-validation","nasa-tmr"],
            "notes": "Velocity and Reynolds stress profiles at Re_theta=4060,7700,14000,31000.",
            "quants": [{"name":"uplus","type":"profile","location":"wall-normal","norm":"L2"}],
            "files": [],
        },
        "convex-curvature": {
            "title": "Convex Curvature BL (NASA TMR)", "dim": "2D",
            "tags": ["newtonian","turbulent","boundary-layer","curvature","experimental","rans-validation","nasa-tmr"],
            "notes": "Turbulent BL on convex wall. Streamline curvature effects on Reynolds stresses.",
            "quants": [{"name":"Cf","type":"profile","location":"wall","norm":"L2"}],
            "files": [],
        },
        "axisymmetric-separated": {
            "title": "Axisymmetric Separated Flow (NASA TMR)", "dim": "2D",
            "tags": ["newtonian","turbulent","separation","axisymmetric","experimental","rans-validation","nasa-tmr"],
            "notes": "Axisymmetric afterbody with separated flow. Bachalo & Johnson (1986).",
            "quants": [{"name":"Cp","type":"profile","location":"afterbody surface","norm":"L2"}],
            "files": [],
        },
    }

    def name(self): return "nasa-tmr"
    def list_cases(self): return list(self.CASES.keys())

    def import_case(self, case_id, target_dir):
        info = self.CASES[case_id]
        os.makedirs(target_dir, exist_ok=True)
        ref_dir = os.path.join(target_dir, "reference", "experimental")
        os.makedirs(ref_dir, exist_ok=True)
        downloaded = 0
        for url_name, local_name in info["files"]:
            try:
                _urlretrieve(f"{self.BASE}/{url_name}", os.path.join(ref_dir, local_name))
                downloaded += 1
            except Exception as e:
                print(f"  Warning: {url_name}: {e}")
        _write_case_yaml(target_dir, f"nasa-tmr-{case_id}", info["title"],
            info["dim"], info["tags"], self.BASE, info["notes"], info["quants"])
        with open(os.path.join(target_dir, "README.md"), "w", encoding="utf-8") as f:
            f.write(f"# {info['title']}\n\nImported from {self.BASE}\n\n{downloaded} files in reference/experimental/\n")
        print(f"  Imported: {target_dir} ({downloaded} files)")
        return target_dir


# ---------- ERCOFTAC ------------------------------------------------
class ErcoftacImporter(BaseImporter):
    BASE = "http://cfd.mace.manchester.ac.uk/ercoftac"

    CASES = {
        "bfs-laminar": {
            "title": "Backward-Facing Step, Laminar (ERCOFTAC)", "dim": "2D",
            "tags": ["newtonian","laminar","separation","experimental","ercoftac"],
            "notes": "Laminar BFS. ER=1.94, Re=100-800. Armaly et al. (1983).",
            "quants": [{"name":"xr_h","type":"scalar","location":"reattachment","norm":"Relative_L2"}],
            "url": f"{BASE}/doku.php?id=cases:case001",
        },
        "bfs-turbulent": {
            "title": "Backward-Facing Step, Turbulent (ERCOFTAC)", "dim": "2D",
            "tags": ["newtonian","turbulent","separation","experimental","ercoftac"],
            "notes": "Turbulent BFS. Driver & Seegmiller (1985). Re_h=36000.",
            "quants": [{"name":"xr_h","type":"scalar","location":"reattachment","norm":"Relative_L2"},{"name":"Cf","type":"profile","location":"bottom wall","norm":"L2"}],
            "url": f"{BASE}/doku.php?id=cases:case012",
        },
        "cylinder-re3900": {
            "title": "Cylinder Re=3900 (ERCOFTAC)", "dim": "2D",
            "tags": ["newtonian","turbulent","bluff-body","cylinder","experimental","ercoftac"],
            "notes": "Subcritical cylinder flow. Re=3900, turbulent wake.",
            "quants": [{"name":"Cd","type":"scalar","location":"cylinder","norm":"Relative_L2"},{"name":"St","type":"scalar","location":"wake","norm":"Relative_L2"}],
            "url": f"{BASE}/doku.php?id=cases:case078",
        },
        "diffuser": {
            "title": "Conical Diffuser (ERCOFTAC)", "dim": "2D",
            "tags": ["newtonian","turbulent","internal-flow","experimental","ercoftac"],
            "notes": "Axisymmetric conical diffuser. Separating turbulent flow.",
            "quants": [{"name":"Cp","type":"profile","location":"diffuser wall","norm":"L2"}],
            "url": f"{BASE}/doku.php?id=cases:case014",
        },
        "channel-exp": {
            "title": "Turbulent Channel (ERCOFTAC)", "dim": "3D",
            "tags": ["newtonian","turbulent","channel","dns","experimental","ercoftac"],
            "notes": "Turbulent channel flow DNS. Re_tau=180, 395, 590.",
            "quants": [{"name":"uplus","type":"profile","location":"wall-normal","norm":"L2"}],
            "url": f"{BASE}/doku.php?id=cases:case077",
        },
        "jet": {
            "title": "Plane Jet (ERCOFTAC)", "dim": "2D",
            "tags": ["newtonian","turbulent","jet","experimental","ercoftac"],
            "notes": "Turbulent plane jet into quiescent air. Self-similar profiles.",
            "quants": [{"name":"u","type":"profile","location":"jet centerline","norm":"L2"}],
            "url": f"{BASE}/doku.php?id=cases:case025",
        },
        "mixing-layer": {
            "title": "Mixing Layer (ERCOFTAC)", "dim": "2D",
            "tags": ["newtonian","turbulent","free-shear","experimental","ercoftac"],
            "notes": "Turbulent mixing layer between two streams. Velocity ratio 0.6.",
            "quants": [{"name":"u","type":"profile","location":"cross-stream","norm":"L2"}],
            "url": f"{BASE}/doku.php?id=cases:case009",
        },
        "pipe": {
            "title": "Turbulent Pipe Flow (ERCOFTAC)", "dim": "2D",
            "tags": ["newtonian","turbulent","pipe","internal-flow","experimental","ercoftac"],
            "notes": "Fully developed turbulent pipe flow. Re=40000-500000.",
            "quants": [{"name":"uplus","type":"profile","location":"radial","norm":"L2"}],
            "url": f"{BASE}/doku.php?id=cases:case079",
        },
        "tbl-flatplate": {
            "title": "Turbulent Flat Plate BL (ERCOFTAC)", "dim": "2D",
            "tags": ["newtonian","turbulent","boundary-layer","experimental","ercoftac"],
            "notes": "ZPG turbulent boundary layer. Wieghardt & Tillmann data. Re_theta up to 20000.",
            "quants": [{"name":"Cf","type":"profile","location":"plate","norm":"L2"},{"name":"uplus","type":"profile","location":"wall-normal","norm":"L2"}],
            "url": f"{BASE}/doku.php?id=cases:case002",
        },
        "cavity": {
            "title": "Lid-Driven Cavity (ERCOFTAC)", "dim": "3D",
            "tags": ["newtonian","laminar","cavity","experimental","ercoftac"],
            "notes": "3D lid-driven cavity flow. Re=100,400,1000. Prasad & Koseff (1989).",
            "quants": [{"name":"u","type":"profile","location":"centerline","norm":"L2"}],
            "url": f"{BASE}/doku.php?id=cases:case013",
        },
        "jet-crossflow": {
            "title": "Jet in Crossflow (ERCOFTAC)", "dim": "3D",
            "tags": ["newtonian","turbulent","jet","crossflow","experimental","ercoftac"],
            "notes": "Turbulent jet issuing into a crossflow. Velocity ratio 2-8.",
            "quants": [{"name":"u","type":"profile","location":"jet centerline","norm":"L2"}],
            "url": f"{BASE}/doku.php?id=cases:case021",
        },
        "rotating-disk": {
            "title": "Rotating Disk BL (ERCOFTAC)", "dim": "3D",
            "tags": ["newtonian","turbulent","rotating","boundary-layer","experimental","ercoftac"],
            "notes": "Turbulent boundary layer on a rotating disk. 3D BL with crossflow.",
            "quants": [{"name":"u_theta","type":"profile","location":"radial","norm":"L2"}],
            "url": f"{BASE}/doku.php?id=cases:case030",
        },
        "bfs-3d": {
            "title": "3D Backward-Facing Step (ERCOFTAC)", "dim": "3D",
            "tags": ["newtonian","turbulent","separation","bfs","3d","experimental","ercoftac"],
            "notes": "3D BFS with side walls. Spanwise variation of reattachment.",
            "quants": [{"name":"xr_h","type":"scalar","location":"reattachment","norm":"Relative_L2"}],
            "url": f"{BASE}/doku.php?id=cases:case055",
        },
        "wake": {
            "title": "Cylinder Near-Wake (ERCOFTAC)", "dim": "2D",
            "tags": ["newtonian","turbulent","cylinder","wake","experimental","ercoftac"],
            "notes": "Near-wake of a circular cylinder at subcritical Re. Mean velocity and Reynolds stresses.",
            "quants": [{"name":"u","type":"profile","location":"wake","norm":"L2"}],
            "url": f"{BASE}/doku.php?id=cases:case058",
        },
    }

    def name(self): return "ercoftac"
    def list_cases(self): return list(self.CASES.keys())

    def import_case(self, case_id, target_dir):
        info = self.CASES[case_id]
        os.makedirs(target_dir, exist_ok=True)
        ref_dir = os.path.join(target_dir, "reference", "experimental")
        os.makedirs(ref_dir, exist_ok=True)

        # Write integral data with ERCOFTAC reference
        with open(os.path.join(ref_dir, "source.txt"), "w") as f:
            f.write(f"ERCOFTAC case: {case_id}\nURL: {info['url']}\n")

        _write_case_yaml(target_dir, f"ercoftac-{case_id}", info["title"],
            info["dim"], info["tags"], info["url"], info["notes"], info["quants"])

        with open(os.path.join(target_dir, "README.md"), "w", encoding="utf-8") as f:
            f.write(f"""# {info['title']}

Imported from ERCOFTAC Classic Collection.

**Source URL:** {info['url']}

## Data

ERCOFTAC provides downloadable data archives (ZIP/dat) at the URL above.
Visit the URL to download experimental data and place it in `reference/experimental/`.

## Notes

{info['notes']}
""")
        print(f"  Imported: {target_dir} (visit {info['url']} for data)")
        return target_dir


# ---------- JHTDB ------------------------------------------------
class JhtdbImporter(BaseImporter):
    """Johns Hopkins Turbulence Database — DNS/LES data via REST API.
    
    Requires: pip install giverny (or pyJHTDB)
    Base: https://turbulence.idies.jhu.edu
    """

    CASES = {
        "channel180": {
            "title": "Turbulent Channel Re_tau=180 (JHTDB)", "dim": "3D",
            "tags": ["newtonian","turbulent","channel","dns","jhtdb"],
            "notes": "DNS channel flow. Moser, Kim, Mansour (1999). 128x129x128.",
            "quants": [{"name":"uplus","type":"profile","location":"wall-normal","norm":"L2"}],
            "dataset": "channel",
            "time": 0.0,
        },
        "channel1000": {
            "title": "Turbulent Channel Re_tau=1000 (JHTDB)", "dim": "3D",
            "tags": ["newtonian","turbulent","channel","dns","jhtdb","high-re"],
            "notes": "DNS channel flow at Re_tau=1000. Lee & Moser (2015).",
            "quants": [{"name":"uplus","type":"profile","location":"wall-normal","norm":"L2"}],
            "dataset": "channel5200",
            "time": 0.0,
        },
        "isotropic": {
            "title": "Isotropic Turbulence 1024^3 (JHTDB)", "dim": "3D",
            "tags": ["newtonian","turbulent","isotropic","dns","jhtdb"],
            "notes": "Forced isotropic turbulence. R_lambda~433. 1024^3 DNS.",
            "quants": [{"name":"k","type":"scalar","location":"domain","norm":"Relative_L2"},{"name":"epsilon","type":"scalar","location":"domain","norm":"Relative_L2"}],
            "dataset": "isotropic1024coarse",
            "time": 0.0,
        },
    }

    def name(self): return "jhtdb"
    def list_cases(self): return list(self.CASES.keys())

    def import_case(self, case_id, target_dir):
        info = self.CASES[case_id]
        os.makedirs(target_dir, exist_ok=True)

        _write_case_yaml(target_dir, f"jhtdb-{case_id}", info["title"],
            info["dim"], info["tags"], "https://turbulence.idies.jhu.edu",
            info["notes"], info["quants"])

        # Try to query JHTDB if giverny is installed
        qscript = f"""
# JHTDB query script for {case_id}
# Install: pip install giverny
try:
    import giverny
    # Access dataset: {info['dataset']}
    # See: https://turbulence.idies.jhu.edu/docs/
    print("giverny installed — query the database interactively")
except ImportError:
    print("Install giverny: pip install giverny")
    print("Then query: https://turbulence.idies.jhu.edu/")
"""
        with open(os.path.join(target_dir, "query_jhtdb.py"), "w") as f:
            f.write(qscript)

        with open(os.path.join(target_dir, "README.md"), "w", encoding="utf-8") as f:
            f.write(f"""# {info['title']}

Imported from Johns Hopkins Turbulence Database.

**URL:** https://turbulence.idies.jhu.edu/

## Setup

```bash
pip install giverny
```

## Querying data

Run `python query_jhtdb.py` for a template, or see:
https://turbulence.idies.jhu.edu/docs/

Dataset: `{info['dataset']}`

## Notes

{info['notes']}
""")
        print(f"  Imported: {target_dir} (JHTDB API query template)")
        return target_dir


# ---------- MASA (Manufactured Solutions) ------------------------
class MasaImporter(BaseImporter):
    """MASA — Manufactured Analytical Solution Abstraction.
    
    Install: pip install masa or clone from github.com/manufactured-solutions/MASA
    """

    CASES = {
        "ns-2d": {
            "title": "Navier-Stokes MMS 2D (MASA)", "dim": "2D",
            "tags": ["mms","manufactured-solution","newtonian","laminar","steady","navier-stokes","masa"],
            "notes": "2D Navier-Stokes manufactured solution from MASA library.",
            "quants": [{"name":"u","type":"field","location":"domain","norm":"L2"},{"name":"v","type":"field","location":"domain","norm":"L2"}],
        },
        "euler-2d": {
            "title": "Euler MMS 2D (MASA)", "dim": "2D",
            "tags": ["mms","manufactured-solution","compressible","inviscid","euler","masa"],
            "notes": "2D compressible Euler manufactured solution.",
            "quants": [{"name":"rho","type":"field","location":"domain","norm":"L2"},{"name":"u","type":"field","location":"domain","norm":"L2"}],
        },
    }

    def name(self): return "masa"
    def list_cases(self): return list(self.CASES.keys())

    def import_case(self, case_id, target_dir):
        info = self.CASES[case_id]
        os.makedirs(target_dir, exist_ok=True)

        _write_case_yaml(target_dir, f"masa-{case_id}", info["title"],
            info["dim"], info["tags"],
            "https://github.com/manufactured-solutions/MASA",
            info["notes"], info["quants"])

        gen_script = f'''"""Generate MASA {case_id} solution. Requires: pip install masa"""

try:
    import masa
    import numpy as np

    print(f"MASA version: {{masa.__version__}}")
    print("Available solutions:", dir(masa))

    # Initialize MASA for {case_id}
    # See: https://github.com/manufactured-solutions/MASA

    n = 41
    x = np.linspace(0, 1, n)
    y = np.linspace(0, 1, n)
    X, Y = np.meshgrid(x, y)

    # Call MASA functions to evaluate solution + source terms
    # Example (adjust based on MASA API):
    # masa.init_param()
    # u = masa.eval_u(X, Y)
    # ...

    with open("solution.csv", "w") as f:
        f.write("x,y,u,v,p\\n")
        for i in range(n):
            for j in range(n):
                f.write(f"{{X[i,j]}},{{Y[i,j]}},0,0,0\\n")

    print("Generated solution.csv")

except ImportError:
    print("MASA not installed. Install with: pip install masa")
    print("Or clone: https://github.com/manufactured-solutions/MASA")
'''
        os.makedirs(os.path.join(target_dir, "scripts"), exist_ok=True)
        with open(os.path.join(target_dir, "scripts", "generate_masa.py"), "w") as f:
            f.write(gen_script)

        with open(os.path.join(target_dir, "README.md"), "w", encoding="utf-8") as f:
            f.write(f"""# {info['title']}

Imported from MASA (Manufactured Analytical Solution Abstraction).

**Source:** https://github.com/manufactured-solutions/MASA

## Setup

```bash
pip install masa
python scripts/generate_masa.py
```
""")
        print(f"  Imported: {target_dir} (MASA template)")
        return target_dir


# ---------- ExactPack (LANL) --------------------------------------
class ExactPackImporter(BaseImporter):
    """ExactPack — exact solutions for code verification (LANL).
    
    Install: pip install exactpack
    """

    CASES = {
        "sod": {
            "title": "Sod Shock Tube (ExactPack)", "dim": "1D",
            "tags": ["compressible","inviscid","unsteady","riemann","euler","exactpack"],
            "notes": "Sod shock tube exact solution from LANL ExactPack.",
            "quants": [{"name":"rho","type":"profile","location":"domain","norm":"L2"},{"name":"u","type":"profile","location":"domain","norm":"L2"},{"name":"p","type":"profile","location":"domain","norm":"L2"}],
        },
        "noh": {
            "title": "Noh Problem (ExactPack)", "dim": "1D",
            "tags": ["compressible","inviscid","unsteady","shock","euler","exactpack"],
            "notes": "Noh implosion problem. Infinite-strength shock converging to origin.",
            "quants": [{"name":"rho","type":"profile","location":"domain","norm":"L2"}],
        },
        "sedov": {
            "title": "Sedov Blast Wave (ExactPack)", "dim": "1D",
            "tags": ["compressible","inviscid","unsteady","blast","euler","exactpack"],
            "notes": "Sedov-Taylor point blast. Self-similar solution.",
            "quants": [{"name":"rho","type":"profile","location":"domain","norm":"L2"},{"name":"p","type":"profile","location":"domain","norm":"L2"}],
        },
    }

    def name(self): return "exactpack"
    def list_cases(self): return list(self.CASES.keys())

    def import_case(self, case_id, target_dir):
        info = self.CASES[case_id]
        os.makedirs(target_dir, exist_ok=True)

        _write_case_yaml(target_dir, f"exactpack-{case_id}", info["title"],
            info["dim"], info["tags"],
            "https://github.com/lanl/ExactPack",
            info["notes"], info["quants"])

        gen_script = f'''"""Generate ExactPack {case_id} solution. Requires: pip install exactpack"""

try:
    import exactpack
    import numpy as np

    print(f"ExactPack available. Classes:", [c for c in dir(exactpack) if not c.startswith("_")])

    # ExactPack API varies by problem — example:
    # from exactpack.sod import Sod
    # solver = Sod()
    # x = np.linspace(0, 1, 200)
    # rho, u, p, e = solver(x, t=0.2)

    n = 200
    x = np.linspace(0, 1, n)

    with open("solution.csv", "w") as f:
        f.write("x,rho,u,p\\n")

    print("See https://github.com/lanl/ExactPack for usage examples.")

except ImportError:
    print("ExactPack not installed. Install with: pip install exactpack")
    print("Or clone: https://github.com/lanl/ExactPack")
'''
        os.makedirs(os.path.join(target_dir, "scripts"), exist_ok=True)
        with open(os.path.join(target_dir, "scripts", "generate_exactpack.py"), "w") as f:
            f.write(gen_script)

        with open(os.path.join(target_dir, "README.md"), "w", encoding="utf-8") as f:
            f.write(f"""# {info['title']}

Imported from ExactPack (LANL).

**Source:** https://github.com/lanl/ExactPack

```bash
pip install exactpack
python scripts/generate_exactpack.py
```
""")
        print(f"  Imported: {target_dir} (ExactPack template)")
        return target_dir


# ---------- CFDBench ------------------------------------------------
class CfdBenchImporter(BaseImporter):
    BASE = "https://raw.githubusercontent.com/ricardodpcosta/CFDBench/main"

    CASES = {
        "poiseuille": {
            "title": "Poiseuille Flow (CFDBench)", "dim": "2D",
            "tags": ["newtonian","laminar","steady","channel","analytical","cfdbench"],
            "path": "incompressible/poiseuille_2d",
            "notes": "Plane Poiseuille analytical solution.",
            "quants": [{"name":"u","type":"profile","location":"channel","norm":"L2"}],
        },
        "couette": {
            "title": "Couette Flow (CFDBench)", "dim": "2D",
            "tags": ["newtonian","laminar","steady","channel","analytical","cfdbench"],
            "path": "incompressible/couette_2d",
            "notes": "Plane Couette analytical solution.",
            "quants": [{"name":"u","type":"profile","location":"channel","norm":"L2"}],
        },
        "lid-cavity": {
            "title": "Lid-Driven Cavity (CFDBench)", "dim": "2D",
            "tags": ["newtonian","laminar","steady","cavity","analytical","cfdbench"],
            "path": "incompressible/lid_driven_cavity",
            "notes": "Lid-driven cavity at Re=100,400,1000. Ghia et al. reference.",
            "quants": [{"name":"u","type":"profile","location":"centerline","norm":"L2"},{"name":"v","type":"profile","location":"centerline","norm":"L2"}],
        },
        "backstep": {
            "title": "Backward-Facing Step (CFDBench)", "dim": "2D",
            "tags": ["newtonian","laminar","steady","separation","analytical","cfdbench"],
            "path": "incompressible/backward_facing_step",
            "notes": "Laminar backward-facing step. Reattachment length.",
            "quants": [{"name":"xr_h","type":"scalar","location":"reattachment","norm":"Relative_L2"}],
        },
        "natural-convection": {
            "title": "Natural Convection (CFDBench)", "dim": "2D",
            "tags": ["newtonian","laminar","steady","buoyancy","analytical","cfdbench"],
            "path": "heat_transfer/natural_convection_square_cavity",
            "notes": "Natural convection in square cavity. de Vahl Davis benchmark.",
            "quants": [{"name":"Nu","type":"scalar","location":"hot wall","norm":"Relative_L2"}],
        },
    }

    def name(self): return "cfdbench"
    def list_cases(self): return list(self.CASES.keys())

    def import_case(self, case_id, target_dir):
        info = self.CASES[case_id]
        os.makedirs(target_dir, exist_ok=True)
        try:
            readme_url = f"{self.BASE}/{info['path']}/README.md"
            _urlretrieve(readme_url, os.path.join(target_dir, "CFDBENCH_README.md"))
        except Exception:
            pass  # optional — network may be unavailable
        _write_case_yaml(target_dir, f"cfdbench-{case_id}", info["title"],
            info["dim"], info["tags"], "https://github.com/ricardodpcosta/CFDBench",
            info["notes"], info["quants"])
        with open(os.path.join(target_dir, "README.md"), "w", encoding="utf-8") as f:
            f.write(f"# {info['title']}\n\nImported from CFDBench: {self.BASE}/{info['path']}\n")
        print(f"  Imported: {target_dir}")
        return target_dir


# ---------- Registry ------------------------------------------------
_REGISTRY = {}

def _register():
    _REGISTRY["nasa-tmr"] = NasaTmrImporter()
    _REGISTRY["ercoftac"] = ErcoftacImporter()
    _REGISTRY["jhtdb"] = JhtdbImporter()
    _REGISTRY["cfdbench"] = CfdBenchImporter()
    _REGISTRY["masa"] = MasaImporter()
    _REGISTRY["exactpack"] = ExactPackImporter()

_register()


def list_sources():
    return {s: imp.list_cases() for s, imp in _REGISTRY.items()}


def list_all_cases():
    result = []
    for src, imp in _REGISTRY.items():
        for cid in imp.list_cases():
            result.append((cid, src, imp))
    return sorted(result, key=lambda x: x[0])


def find_case(case_id: str):
    for src, imp in _REGISTRY.items():
        if case_id in imp.list_cases():
            return src, imp
    return None, None


def import_case(source: str, case_id: str, target_parent: str) -> str:
    imp = _REGISTRY.get(source)
    if not imp:
        raise ValueError(f"Unknown source '{source}'. Available: {list(_REGISTRY.keys())}")
    target = os.path.join(target_parent, f"{source}-{case_id}")
    return imp.import_case(case_id, target)
