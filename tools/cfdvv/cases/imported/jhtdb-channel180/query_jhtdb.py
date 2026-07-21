
# JHTDB query script for channel180
# Install: pip install giverny
try:
    import giverny
    # Access dataset: channel
    # See: https://turbulence.idies.jhu.edu/docs/
    print("giverny installed — query the database interactively")
except ImportError:
    print("Install giverny: pip install giverny")
    print("Then query: https://turbulence.idies.jhu.edu/")
