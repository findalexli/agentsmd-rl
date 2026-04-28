"""Behavioral checks for tensorrt-llm-nonechore-introduce-flashinferupgrade-skill-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/tensorrt-llm")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/flashinfer-upgrade/SKILL.md')
    assert '| `security_scanning/poetry.lock` | Update `version = "OLD"` → `version = "NEW"` under `[[package]] name = "flashinfer-python"`, and update the `files` list with new hashes |' in text, "expected to find: " + '| `security_scanning/poetry.lock` | Update `version = "OLD"` → `version = "NEW"` under `[[package]] name = "flashinfer-python"`, and update the `files` list with new hashes |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/flashinfer-upgrade/SKILL.md')
    assert 'git stash push -m "flashinfer-upgrade-wip" -- requirements.txt security_scanning/pyproject.toml security_scanning/poetry.lock ATTRIBUTIONS-Python.md' in text, "expected to find: " + 'git stash push -m "flashinfer-upgrade-wip" -- requirements.txt security_scanning/pyproject.toml security_scanning/poetry.lock ATTRIBUTIONS-Python.md'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/flashinfer-upgrade/SKILL.md')
    assert '- Updated version pins in requirements.txt, security_scanning/pyproject.toml, security_scanning/poetry.lock, and ATTRIBUTIONS-Python.md' in text, "expected to find: " + '- Updated version pins in requirements.txt, security_scanning/pyproject.toml, security_scanning/poetry.lock, and ATTRIBUTIONS-Python.md'[:80]

