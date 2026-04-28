"""Behavioral checks for qpdf-add-copilotinstructionsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/qpdf")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '1. **Assertions**: Test code should include `qpdf/assert_test.h` first. Debug code should include `qpdf/assert_debug.h` and use `qpdf_assert_debug` instead of `assert`. Use `qpdf_expect`, `qpdf_ensure' in text, "expected to find: " + '1. **Assertions**: Test code should include `qpdf/assert_test.h` first. Debug code should include `qpdf/assert_debug.h` and use `qpdf_assert_debug` instead of `assert`. Use `qpdf_expect`, `qpdf_ensure'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Global options and limits are qpdf-wide settings in the `qpdf::global` namespace that affect behavior across all operations. See `README-maintainer.md` section "HOW TO ADD A GLOBAL OPTION OR LIMIT" fo' in text, "expected to find: " + 'Global options and limits are qpdf-wide settings in the `qpdf::global` namespace that affect behavior across all operations. See `README-maintainer.md` section "HOW TO ADD A GLOBAL OPTION OR LIMIT" fo'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'qpdf is a command-line tool and C++ library that performs content-preserving transformations on PDF files. It supports linearization, encryption, page splitting/merging, and PDF file inspection. Versi' in text, "expected to find: " + 'qpdf is a command-line tool and C++ library that performs content-preserving transformations on PDF files. It supports linearization, encryption, page splitting/merging, and PDF file inspection. Versi'[:80]

