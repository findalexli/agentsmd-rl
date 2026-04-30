"""Behavioral checks for linguist-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/linguist")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **languages.yml**: Keep alphabetically sorted (case-sensitive, uppercase before lowercase) with the comment at the top. Use the comment at the top to determine the fields to add for a language.' in text, "expected to find: " + '- **languages.yml**: Keep alphabetically sorted (case-sensitive, uppercase before lowercase) with the comment at the top. Use the comment at the top to determine the fields to add for a language.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '2. Link to GitHub search results showing in-the-wild usage, excluding forks, for each extension being added (minimum 2000 files for common extensions, 200 for once-per-repo files or extensions).' in text, "expected to find: " + '2. Link to GitHub search results showing in-the-wild usage, excluding forks, for each extension being added (minimum 2000 files for common extensions, 200 for once-per-repo files or extensions).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Heuristics**: Write patterns to minimize false positives. Patterns must be linear, safe from ReDoS attacks, and RE2 compatible. All heuristics must have tests.' in text, "expected to find: " + '- **Heuristics**: Write patterns to minimize false positives. Patterns must be linear, safe from ReDoS attacks, and RE2 compatible. All heuristics must have tests.'[:80]

