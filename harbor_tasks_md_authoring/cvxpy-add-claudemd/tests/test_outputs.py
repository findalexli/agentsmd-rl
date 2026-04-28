"""Behavioral checks for cvxpy-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cvxpy")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Always use the PR template in `.github/` when opening PRs. Fill out all sections. **Never check an item in the Contribution Checklist that has not actually been done.**' in text, "expected to find: " + 'Always use the PR template in `.github/` when opening PRs. Fill out all sections. **Never check an item in the Contribution Checklist that has not actually been done.**'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Backends are critical to performance. They handle matrix construction during `ConeMatrixStuffing`. Located in `cvxpy/lin_ops/backends/`.' in text, "expected to find: " + 'Backends are critical to performance. They handle matrix construction during `ConeMatrixStuffing`. Located in `cvxpy/lin_ops/backends/`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '6. **Forgetting to update documentation** - new features need docs at [cvxpy.org](https://www.cvxpy.org/) (see `doc/` folder)' in text, "expected to find: " + '6. **Forgetting to update documentation** - new features need docs at [cvxpy.org](https://www.cvxpy.org/) (see `doc/` folder)'[:80]

