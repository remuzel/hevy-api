"""Hevy API client library."""

__version__ = "0.1.0"

# Import main client class
from . import models
from .client import HevyClient

__all__ = [
    # Client
    "HevyClient",
    # Models
    "models",
    # Version
    "__version__",
]
