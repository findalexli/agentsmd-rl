"""Behavioral checks for edumips64-add-copilot-instructions-for-repository (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/edumips64")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'EduMIPS64 is a free, cross-platform visual MIPS64 CPU simulator written in Java with a web-based UI using JavaScript/React. The project aims to be an educational tool for learning MIPS64 assembly lang' in text, "expected to find: " + 'EduMIPS64 is a free, cross-platform visual MIPS64 CPU simulator written in Java with a web-based UI using JavaScript/React. The project aims to be an educational tool for learning MIPS64 assembly lang'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'The repository includes a dev container configuration (`.devcontainer/devcontainer.json`) that provides a fully configured development environment. GitHub Codespaces will use this by default.' in text, "expected to find: " + 'The repository includes a dev container configuration (`.devcontainer/devcontainer.json`) that provides a fully configured development environment. GitHub Codespaces will use this by default.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Component tests**: `ParserTest.java`, `MemoryTest.java`, etc. - Test individual components in isolation' in text, "expected to find: " + '- **Component tests**: `ParserTest.java`, `MemoryTest.java`, etc. - Test individual components in isolation'[:80]

