"""Behavioral checks for openwebui-extensions-create-copilotinstructionsmd-with-plugi (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/openwebui-extensions")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'This document defines the standard conventions and best practices for OpenWebUI plugin development. Copilot should follow these guidelines when generating code or documentation.' in text, "expected to find: " + 'This document defines the standard conventions and best practices for OpenWebUI plugin development. Copilot should follow these guidelines when generating code or documentation.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'def _get_user_context(self, __user__: Optional[Dict[str, Any]]) -> Dict[str, str]:' in text, "expected to find: " + 'def _get_user_context(self, __user__: Optional[Dict[str, Any]]) -> Dict[str, str]:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'GitHub: [Fu-Jie/awesome-openwebui](https://github.com/Fu-Jie/awesome-openwebui)' in text, "expected to find: " + 'GitHub: [Fu-Jie/awesome-openwebui](https://github.com/Fu-Jie/awesome-openwebui)'[:80]

