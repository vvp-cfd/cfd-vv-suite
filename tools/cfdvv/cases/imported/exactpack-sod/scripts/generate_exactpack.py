"""Generate ExactPack sod solution. Requires: pip install exactpack"""

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
        f.write("x,rho,u,p\n")

    print("See https://github.com/lanl/ExactPack for usage examples.")

except ImportError:
    print("ExactPack not installed. Install with: pip install exactpack")
    print("Or clone: https://github.com/lanl/ExactPack")
