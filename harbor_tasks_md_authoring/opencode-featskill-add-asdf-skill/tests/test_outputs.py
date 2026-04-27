"""Behavioral checks for opencode-featskill-add-asdf-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/opencode")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('opencode/skill/asdf/SKILL.md')
    assert 'description: Use this skill whenever the user wants to install, configure, or use asdf (asdf-vm), the universal version manager. Trigger for any mention of asdf, .tool-versions files, managing runtime' in text, "expected to find: " + 'description: Use this skill whenever the user wants to install, configure, or use asdf (asdf-vm), the universal version manager. Trigger for any mention of asdf, .tool-versions files, managing runtime'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('opencode/skill/asdf/SKILL.md')
    assert 'asdf is a universal CLI version manager — one tool to replace nvm, pyenv, rbenv, tfenv, goenv and more. It manages per-project versions via `.tool-versions` files and switches versions automatically a' in text, "expected to find: " + 'asdf is a universal CLI version manager — one tool to replace nvm, pyenv, rbenv, tfenv, goenv and more. It manages per-project versions via `.tool-versions` files and switches versions automatically a'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('opencode/skill/asdf/SKILL.md')
    assert '> **Note**: `asdf set` replaced the older `asdf local` / `asdf global` commands in asdf v0.15+. Both still work but `asdf set` is the modern API.' in text, "expected to find: " + '> **Note**: `asdf set` replaced the older `asdf local` / `asdf global` commands in asdf v0.15+. Both still work but `asdf set` is the modern API.'[:80]

