"""Generate MASA ns-2d solution. Requires: pip install masa"""

try:
    import masa
    import numpy as np

    print(f"MASA version: {masa.__version__}")
    print("Available solutions:", dir(masa))

    # Initialize MASA for ns-2d
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
        f.write("x,y,u,v,p\n")
        for i in range(n):
            for j in range(n):
                f.write(f"{X[i,j]},{Y[i,j]},0,0,0\n")

    print("Generated solution.csv")

except ImportError:
    print("MASA not installed. Install with: pip install masa")
    print("Or clone: https://github.com/manufactured-solutions/MASA")
