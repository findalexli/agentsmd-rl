"""Behavioral checks for winget-cli-add-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/winget-cli")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'This is the Windows Package Manager (WinGet) CLI client - a native Windows application for discovering and installing packages. The codebase consists of:' in text, "expected to find: " + 'This is the Windows Package Manager (WinGet) CLI client - a native Windows application for discovering and installing packages. The codebase consists of:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **ExecutionContext**: State container that flows through workflows. Contains arguments, reporter, flags, and data (ExecutionContextData.h)' in text, "expected to find: " + '- **ExecutionContext**: State container that flows through workflows. Contains arguments, reporter, flags, and data (ExecutionContextData.h)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Open `src\\AppInstallerCLI.sln` in Visual Studio and build the solution (Ctrl+Shift+B) or use msbuild.exe to build from the command line.' in text, "expected to find: " + 'Open `src\\AppInstallerCLI.sln` in Visual Studio and build the solution (Ctrl+Shift+B) or use msbuild.exe to build from the command line.'[:80]

