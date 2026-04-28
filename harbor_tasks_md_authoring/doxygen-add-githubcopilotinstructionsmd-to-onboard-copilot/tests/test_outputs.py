"""Behavioral checks for doxygen-add-githubcopilotinstructionsmd-to-onboard-copilot (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/doxygen")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Doxygen is the de facto standard tool for generating documentation from annotated source code. It supports C++, C, Objective-C, C#, PHP, Java, Python, IDL, Fortran, VHDL, and more. The project is writ' in text, "expected to find: " + 'Doxygen is the de facto standard tool for generating documentation from annotated source code. It supports C++, C, Objective-C, C#, PHP, Java, Python, IDL, Fortran, VHDL, and more. The project is writ'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Key scanners: `commentscan.l`, `commentcnv.l`, `code.l`, `configimpl.l`, `constexp.l`, `declinfo.l`, `defargs.l`, `doctokenizer.l`, `fortranscanner.l`, `pre.l`, etc.' in text, "expected to find: " + 'Key scanners: `commentscan.l`, `commentcnv.l`, `code.l`, `configimpl.l`, `constexp.l`, `declinfo.l`, `defargs.l`, `doctokenizer.l`, `fortranscanner.l`, `pre.l`, etc.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Tests are Python-driven via `testing/runtests.py`. Each test is a numbered file in `testing/` matching `NNN_*.ext`. Tests run doxygen and compare XML output.' in text, "expected to find: " + 'Tests are Python-driven via `testing/runtests.py`. Each test is a numbered file in `testing/` matching `NNN_*.ext`. Tests run doxygen and compare XML output.'[:80]

