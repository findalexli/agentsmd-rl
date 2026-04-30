"""Behavioral checks for intel-xpu-backend-for-triton-enhance-copilot-code-review-cus (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/intel-xpu-backend-for-triton")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**MLIR patterns:** Use rewriter patterns for transformations, follow dialect conversion infrastructure, register and verify operations properly.' in text, "expected to find: " + '**MLIR patterns:** Use rewriter patterns for transformations, follow dialect conversion infrastructure, register and verify operations properly.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**Key principles:** Use LLVM types (`StringRef`, `ArrayRef`), express ownership clearly, follow RAII, use LLVM casting, avoid exceptions.' in text, "expected to find: " + '**Key principles:** Use LLVM types (`StringRef`, `ArrayRef`), express ownership clearly, follow RAII, use LLVM casting, avoid exceptions.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Generate code following LLVM/MLIR standards. Apply these conventions consistently for high-quality, maintainable code.' in text, "expected to find: " + 'Generate code following LLVM/MLIR standards. Apply these conventions consistently for high-quality, maintainable code.'[:80]

