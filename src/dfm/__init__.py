import importlib.metadata

# Fetches the version of the package as defined in pyproject.toml
__version__ = importlib.metadata.version(__package__)
