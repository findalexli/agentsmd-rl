"""Behavioral checks for everything-claude-code-featskills-add-reposcan-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/everything-claude-code")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/repo-scan/SKILL.md')
    assert 'description: Cross-stack source code asset audit — classifies every file, detects embedded third-party libraries, and delivers actionable four-level verdicts per module with interactive HTML reports.' in text, "expected to find: " + 'description: Cross-stack source code asset audit — classifies every file, detects embedded third-party libraries, and delivers actionable four-level verdicts per module with interactive HTML reports.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/repo-scan/SKILL.md')
    assert "> Every ecosystem has its own dependency manager, but no tool looks across C++, Android, iOS, and Web to tell you: how much code is actually yours, what's third-party, and what's dead weight." in text, "expected to find: " + "> Every ecosystem has its own dependency manager, but no tool looks across C++, Android, iOS, and Web to tell you: how much code is actually yours, what's third-party, and what's dead weight."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/repo-scan/SKILL.md')
    assert '4. **Highlight structural risks**: call out dead-weight artifacts, duplicated wrappers, outdated vendored code, and modules that should be extracted, rebuilt, or deprecated.' in text, "expected to find: " + '4. **Highlight structural risks**: call out dead-weight artifacts, duplicated wrappers, outdated vendored code, and modules that should be extracted, rebuilt, or deprecated.'[:80]

