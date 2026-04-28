"""Behavioral checks for calcite-design-system-chorecopilotinstructions-update-commun (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/calcite-design-system")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- When helpful, prefix review comments with a label so intent is clear. Format: `<label>:`. Suggested labels:' in text, "expected to find: " + '- When helpful, prefix review comments with a label so intent is clear. Format: `<label>:`. Suggested labels:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- `blocking:` must be addressed before merge (correctness, accessibility, security, breaking API)' in text, "expected to find: " + '- `blocking:` must be addressed before merge (correctness, accessibility, security, breaking API)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- `suggestion:` optional improvement; author may adopt or explain why not' in text, "expected to find: " + '- `suggestion:` optional improvement; author may adopt or explain why not'[:80]

