"""Behavioral checks for proxifyre-add-comprehensive-github-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/proxifyre")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert "ProxiFyre is a Windows-specific SOCKS5 proxifier application that builds upon the Windows Packet Filter's socksify demo. It consists of three main projects: ndisapi.lib (Windows Packet Filter static l" in text, "expected to find: " + "ProxiFyre is a Windows-specific SOCKS5 proxifier application that builds upon the Windows Packet Filter's socksify demo. It consists of three main projects: ndisapi.lib (Windows Packet Filter static l"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**ALWAYS reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**' in text, "expected to find: " + '**ALWAYS reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- If you are in a Linux environment: **Document that builds cannot be completed** and focus on repository navigation and structure analysis only.' in text, "expected to find: " + '- If you are in a Linux environment: **Document that builds cannot be completed** and focus on repository navigation and structure analysis only.'[:80]

