"""Behavioral checks for systemd-add-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/systemd")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **clangd**: Use `mkosi.clangd` script to start a C/C++ LSP server for navigating C source and header files. Run `mkosi -f box -- meson setup build && mkosi -f box -- meson compile -C build gensource' in text, "expected to find: " + '- **clangd**: Use `mkosi.clangd` script to start a C/C++ LSP server for navigating C source and header files. Run `mkosi -f box -- meson setup build && mkosi -f box -- meson compile -C build gensource'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'systemd is a system and service manager for Linux, written in C (GNU17 with extensions). The project is built with Meson and consists of ~140 components including PID 1, journald, udevd, networkd, and' in text, "expected to find: " + 'systemd is a system and service manager for Linux, written in C (GNU17 with extensions). The project is built with Meson and consists of ~140 components including PID 1, journald, udevd, networkd, and'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Per project policy: If you use AI code generation tools, you **must disclose** this in commit messages and PR descriptions. All AI-generated output requires thorough human review before submission.' in text, "expected to find: " + 'Per project policy: If you use AI code generation tools, you **must disclose** this in commit messages and PR descriptions. All AI-generated output requires thorough human review before submission.'[:80]

