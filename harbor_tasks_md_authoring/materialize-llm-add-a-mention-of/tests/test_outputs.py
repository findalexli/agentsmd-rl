"""Behavioral checks for materialize-llm-add-a-mention-of (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/materialize")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/mz-test/SKILL.md')
    assert 'Some compositions (e.g. platform-checks, upgrade, pg-cdc multi-version) run the' in text, "expected to find: " + 'Some compositions (e.g. platform-checks, upgrade, pg-cdc multi-version) run the'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/mz-test/SKILL.md')
    assert 'version-sensitive output (e.g. the result of a `SHOW`, a system-catalog query,' in text, "expected to find: " + 'version-sensitive output (e.g. the result of a `SHOW`, a system-catalog query,'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/mz-test/SKILL.md')
    assert 'The `[version...]` guard goes immediately after the directive sigil (`>` for a' in text, "expected to find: " + 'The `[version...]` guard goes immediately after the directive sigil (`>` for a'[:80]

