"""Behavioral checks for vscode-docs-docs-fix-release-note-writer (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vscode-docs")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/release-note-writer/SKILL.md')
    assert '2. **Stable Release Notes**: These notes summarize the key features and improvements in a stable release of VS Code. They follow a more structured format with predefined sections for different feature' in text, "expected to find: " + '2. **Stable Release Notes**: These notes summarize the key features and improvements in a stable release of VS Code. They follow a more structured format with predefined sections for different feature'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/release-note-writer/SKILL.md')
    assert 'Stable release notes summarize the key features and improvements in a stable release of VS Code. They follow a more structured format with predefined sections for different feature areas. The release ' in text, "expected to find: " + 'Stable release notes summarize the key features and improvements in a stable release of VS Code. They follow a more structured format with predefined sections for different feature areas. The release '[:80]

