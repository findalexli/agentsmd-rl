"""Behavioral checks for directxtex-update-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/directxtex")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Code Style**: The project uses an .editorconfig file to enforce coding standards. Follow the rules defined in `.editorconfig` for indentation, line endings, and other formatting. Additional inform' in text, "expected to find: " + '- **Code Style**: The project uses an .editorconfig file to enforce coding standards. Follow the rules defined in `.editorconfig` for indentation, line endings, and other formatting. Additional inform'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- All public function declarations are prefixed with `DIRECTX_TEX_API`, which wraps `__declspec(dllexport)` / `__declspec(dllimport)` (or the MinGW `__attribute__` equivalent) when the `DIRECTX_TEX_EX' in text, "expected to find: " + '- All public function declarations are prefixed with `DIRECTX_TEX_API`, which wraps `__declspec(dllexport)` / `__declspec(dllimport)` (or the MinGW `__attribute__` equivalent) when the `DIRECTX_TEX_EX'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'All public API functions must use SAL annotations on every parameter. Use `_Use_decl_annotations_` at the top of each implementation that has SAL in the header declaration — never repeat the annotatio' in text, "expected to find: " + 'All public API functions must use SAL annotations on every parameter. Use `_Use_decl_annotations_` at the top of each implementation that has SAL in the header declaration — never repeat the annotatio'[:80]

