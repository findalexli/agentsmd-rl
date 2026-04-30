"""Behavioral checks for winforms-adding-new-skills-for-build (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/winforms")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/building-code/SKILL.md')
    assert '* Visual Studio 2022 (for IDE builds) — see `WinForms.vsconfig` for required workloads.' in text, "expected to find: " + '* Visual Studio 2022 (for IDE builds) — see `WinForms.vsconfig` for required workloads.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/building-code/SKILL.md')
    assert '| `-configuration <Debug\\|Release>` | `-c` | Build configuration (default: `Debug`) |' in text, "expected to find: " + '| `-configuration <Debug\\|Release>` | `-c` | Build configuration (default: `Debug`) |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/building-code/SKILL.md')
    assert 'dotnet build src\\test\\unit\\System.Windows.Forms\\System.Windows.Forms.Tests.csproj' in text, "expected to find: " + 'dotnet build src\\test\\unit\\System.Windows.Forms\\System.Windows.Forms.Tests.csproj'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/download-sdk/SKILL.md')
    assert '| Test exe still says "framework not found" after install | Ensure the **architecture** matches (x64 vs x86); check that the test exe is looking for `Microsoft.NETCore.App` (not `Microsoft.WindowsDesk' in text, "expected to find: " + '| Test exe still says "framework not found" after install | Ensure the **architecture** matches (x64 vs x86); check that the test exe is looking for `Microsoft.NETCore.App` (not `Microsoft.WindowsDesk'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/download-sdk/SKILL.md')
    assert '| Need `Microsoft.WindowsDesktop.App` | Replace `Runtime` with `WindowsDesktop` in the URL: `https://ci.dot.net/public/WindowsDesktop/{version}/windowsdesktop-runtime-{version}-win-x64.msi` |' in text, "expected to find: " + '| Need `Microsoft.WindowsDesktop.App` | Replace `Runtime` with `WindowsDesktop` in the URL: `https://ci.dot.net/public/WindowsDesktop/{version}/windowsdesktop-runtime-{version}-win-x64.msi` |'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/download-sdk/SKILL.md')
    assert '$rc = Get-Content "artifacts\\bin\\System.Windows.Forms.Tests\\Debug\\net11.0-windows7.0\\System.Windows.Forms.Tests.runtimeconfig.json" | ConvertFrom-Json' in text, "expected to find: " + '$rc = Get-Content "artifacts\\bin\\System.Windows.Forms.Tests\\Debug\\net11.0-windows7.0\\System.Windows.Forms.Tests.runtimeconfig.json" | ConvertFrom-Json'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/running-tests/SKILL.md')
    assert '| `[Collection("Sequential")]` | Tests that must **not** run in parallel (e.g. clipboard, drag-and-drop, global state) |' in text, "expected to find: " + '| `[Collection("Sequential")]` | Tests that must **not** run in parallel (e.g. clipboard, drag-and-drop, global state) |'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/running-tests/SKILL.md')
    assert '| `[WinFormsFact]` / `[WinFormsTheory]` | Tests involving UI controls or requiring a synchronization context |' in text, "expected to find: " + '| `[WinFormsFact]` / `[WinFormsTheory]` | Tests involving UI controls or requiring a synchronization context |'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/running-tests/SKILL.md')
    assert '([Collecting User-Mode Dumps](https://learn.microsoft.com/windows/win32/wer/collecting-user-mode-dumps)),' in text, "expected to find: " + '([Collecting User-Mode Dumps](https://learn.microsoft.com/windows/win32/wer/collecting-user-mode-dumps)),'[:80]

