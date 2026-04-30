"""Behavioral checks for cultivation-world-simulator-featdev-add-claudecompatible-ski (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cultivation-world-simulator")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/git-pr/SKILL.md')
    assert 'gh pr create --head <github-username>/<branch-name> --base main --title "<type>: <description>" --body "<body>"' in text, "expected to find: " + 'gh pr create --head <github-username>/<branch-name> --base main --title "<type>: <description>" --body "<body>"'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/git-pr/SKILL.md')
    assert '# git remote set-url origin https://github.com/AI-Cultivation/cultivation-world-simulator.git' in text, "expected to find: " + '# git remote set-url origin https://github.com/AI-Cultivation/cultivation-world-simulator.git'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/git-pr/SKILL.md')
    assert 'description: Create a pull request with proper remote handling' in text, "expected to find: " + 'description: Create a pull request with proper remote handling'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/test-validate/SKILL.md')
    assert 'description: Run Python tests using the project venv' in text, "expected to find: " + 'description: Run Python tests using the project venv'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/test-validate/SKILL.md')
    assert '.venv/bin/python src/server/main.py --dev' in text, "expected to find: " + '.venv/bin/python src/server/main.py --dev'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/test-validate/SKILL.md')
    assert '.venv/bin/pytest tests/test_<name>.py -v' in text, "expected to find: " + '.venv/bin/pytest tests/test_<name>.py -v'[:80]

