"""Behavioral checks for tsgolint-docs-update-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/tsgolint")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `typescript-go/` - **[SUBMODULE]** TypeScript Go port submodule (temporary local edits are OK for testing; never commit submodule pointer changes)' in text, "expected to find: " + '- `typescript-go/` - **[SUBMODULE]** TypeScript Go port submodule (temporary local edits are OK for testing; never commit submodule pointer changes)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `typescript-go/*` - Submodule in this repo (do not commit direct submodule pointer updates; use `patches/*` for permanent changes)' in text, "expected to find: " + '- `typescript-go/*` - Submodule in this repo (do not commit direct submodule pointer updates; use `patches/*` for permanent changes)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '5. The patches are applied during project initialization (`just init`) using `git am --3way --no-gpg-sign ../patches/*.patch`' in text, "expected to find: " + '5. The patches are applied during project initialization (`just init`) using `git am --3way --no-gpg-sign ../patches/*.patch`'[:80]

