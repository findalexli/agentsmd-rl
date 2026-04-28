"""Behavioral checks for moloch-add-comprehensive-copilot-instructions-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/moloch")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Moloch is a LaTeX Beamer presentation theme package. It is a minimalistic fork of the Metropolis theme, distributed via CTAN (Comprehensive TeX Archive Network). The repository consists of:' in text, "expected to find: " + 'Moloch is a LaTeX Beamer presentation theme package. It is a minimalistic fork of the Metropolis theme, distributed via CTAN (Comprehensive TeX Archive Network). The repository consists of:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**IMPORTANT**: This project requires Nix for building and testing. The LaTeX environment is managed through Nix flakes. Do NOT attempt to use system LaTeX tools directly.' in text, "expected to find: " + '**IMPORTANT**: This project requires Nix for building and testing. The LaTeX environment is managed through Nix flakes. Do NOT attempt to use system LaTeX tools directly.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '1. **Trust these instructions**: Only search for additional information if these instructions are incomplete or incorrect. The build process is fully documented above.' in text, "expected to find: " + '1. **Trust these instructions**: Only search for additional information if these instructions are incomplete or incorrect. The build process is fully documented above.'[:80]

