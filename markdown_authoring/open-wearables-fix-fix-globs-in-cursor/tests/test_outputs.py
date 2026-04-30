"""Behavioral checks for open-wearables-fix-fix-globs-in-cursor (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/open-wearables")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('backend/.cursor/rules/models.mdc')
    assert 'globs: backend/app/models/**,backend/app/database.py,backend/app/mappings.py,backend/app/utils/mappings_meta.py' in text, "expected to find: " + 'globs: backend/app/models/**,backend/app/database.py,backend/app/mappings.py,backend/app/utils/mappings_meta.py'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('backend/.cursor/rules/repositories.mdc')
    assert 'globs: backend/app/repositories/**' in text, "expected to find: " + 'globs: backend/app/repositories/**'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('backend/.cursor/rules/routes.mdc')
    assert 'globs: backend/app/api/routes/**' in text, "expected to find: " + 'globs: backend/app/api/routes/**'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('backend/.cursor/rules/schemas.mdc')
    assert 'globs: backend/app/schemas/**' in text, "expected to find: " + 'globs: backend/app/schemas/**'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('backend/.cursor/rules/services.mdc')
    assert 'globs: backend/app/services/**,backend/app/utils/exceptions.py' in text, "expected to find: " + 'globs: backend/app/services/**,backend/app/utils/exceptions.py'[:80]

