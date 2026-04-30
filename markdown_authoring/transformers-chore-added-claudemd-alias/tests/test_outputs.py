"""Behavioral checks for transformers-chore-added-claudemd-alias (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/transformers")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '2) The newer method is to add a file named `modular_<name>.py` in the model directory. `modular` files **can** inherit from other models. `make fix-repo` will copy code to generate standalone `modelin' in text, "expected to find: " + '2) The newer method is to add a file named `modular_<name>.py` in the model directory. `modular` files **can** inherit from other models. `make fix-repo` will copy code to generate standalone `modelin'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '1) The older method is to mark classes or functions with `# Copied from ...`. Copies are kept in sync by `make fix-repo`. Do not edit a `# Copied from` block, as it will be reverted by `make fix-repo`' in text, "expected to find: " + '1) The older method is to mark classes or functions with `# Copied from ...`. Copies are kept in sync by `make fix-repo`. Do not edit a `# Copied from` block, as it will be reverted by `make fix-repo`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'We try to avoid direct inheritance between model-specific files in `src/transformers/models/`. We have two mechanisms to manage the resulting code duplication:' in text, "expected to find: " + 'We try to avoid direct inheritance between model-specific files in `src/transformers/models/`. We have two mechanisms to manage the resulting code duplication:'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

