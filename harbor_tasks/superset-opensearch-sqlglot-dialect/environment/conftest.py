"""Bypass superset/__init__.py during tests.

Importing the real superset package triggers Flask app construction,
flask-appbuilder, SQLAlchemy, and many other heavy deps. The PR under test
only touches the lightweight superset.sql.* tree, so we register a stub
``superset`` package whose ``__path__`` still points at the real source
tree. Subsequent ``import superset.sql.dialects.opensearch`` then resolves
the real submodule without executing the heavy ``__init__``.
"""
from __future__ import annotations

import sys
import types
from pathlib import Path

_SUPERSET_PKG = Path(__file__).parent / "superset"

if "superset" not in sys.modules or not hasattr(sys.modules["superset"], "__path__"):
    stub = types.ModuleType("superset")
    stub.__path__ = [str(_SUPERSET_PKG)]
    sys.modules["superset"] = stub
