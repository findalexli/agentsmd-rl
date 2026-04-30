"""Behavioral checks for compound-engineering-plugin-fixcompound-remove-overly-defens (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/compound-engineering-plugin")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-compound/SKILL.md')
    assert '**Always run full mode by default.** Proceed directly to Phase 1 unless the user explicitly requests compact-safe mode (e.g., `/ce:compound --compact` or "use compact mode").' in text, "expected to find: " + '**Always run full mode by default.** Proceed directly to Phase 1 unless the user explicitly requests compact-safe mode (e.g., `/ce:compound --compact` or "use compact mode").'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-compound/SKILL.md')
    assert "Compact-safe mode exists as a lightweight alternative — see the **Compact-Safe Mode** section below. It's there if the user wants it, not something to push." in text, "expected to find: " + "Compact-safe mode exists as a lightweight alternative — see the **Compact-Safe Mode** section below. It's there if the user wants it, not something to push."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-compound/SKILL.md')
    assert '## Execution Strategy' in text, "expected to find: " + '## Execution Strategy'[:80]

