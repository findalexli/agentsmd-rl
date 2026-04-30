"""Behavioral checks for compound-engineering-plugin-fixplan-remove-deprecated-techni (markdown_authoring task).

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
    text = _read('plugins/compound-engineering/skills/ce-plan/SKILL.md')
    assert '6. **Start `/ce:work` on remote** - Begin implementing in Claude Code on the web (use `&` to run in background)' in text, "expected to find: " + '6. **Start `/ce:work` on remote** - Begin implementing in Claude Code on the web (use `&` to run in background)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-plan/SKILL.md')
    assert 'Loop back to options after Simplify or Other changes until user selects `/ce:work` or another action.' in text, "expected to find: " + 'Loop back to options after Simplify or Other changes until user selects `/ce:work` or another action.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-plan/SKILL.md')
    assert '3. **Review and refine** - Improve the document through structured self-review' in text, "expected to find: " + '3. **Review and refine** - Improve the document through structured self-review'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/deepen-plan/SKILL.md')
    assert '3. **Deepen further** - Run another round of research on specific sections' in text, "expected to find: " + '3. **Deepen further** - Run another round of research on specific sections'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/deepen-plan/SKILL.md')
    assert '2. **Start `/ce:work`** - Begin implementing this enhanced plan' in text, "expected to find: " + '2. **Start `/ce:work`** - Begin implementing this enhanced plan'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/deepen-plan/SKILL.md')
    assert '4. **Revert** - Restore original plan (if backup exists)' in text, "expected to find: " + '4. **Revert** - Restore original plan (if backup exists)'[:80]

