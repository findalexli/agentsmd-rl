"""Behavioral checks for powershell-add-comprehensive-github-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/powershell")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**PnP PowerShell** is a .NET 8 based PowerShell Module providing over 750 cmdlets that work with Microsoft 365 environments such as SharePoint Online, Microsoft Teams, Microsoft Project, Security & Co' in text, "expected to find: " + '**PnP PowerShell** is a .NET 8 based PowerShell Module providing over 750 cmdlets that work with Microsoft 365 environments such as SharePoint Online, Microsoft Teams, Microsoft Project, Security & Co'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'This is a cross-platform module (Windows, macOS, Linux) that requires PowerShell 7.4.0 or newer and is based on .NET 8.0. It is the successor of the PnP-PowerShell module which only worked on Windows ' in text, "expected to find: " + 'This is a cross-platform module (Windows, macOS, Linux) that requires PowerShell 7.4.0 or newer and is based on .NET 8.0. It is the successor of the PnP-PowerShell module which only worked on Windows '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '9. **Backward Compatibility**: When renaming a cmdlet or fixing a typo in a cmdlet name, always add an `[Alias()]` attribute with the old cmdlet name to maintain backward compatibility. Example:' in text, "expected to find: " + '9. **Backward Compatibility**: When renaming a cmdlet or fixing a typo in a cmdlet name, always add an `[Alias()]` attribute with the old cmdlet name to maintain backward compatibility. Example:'[:80]

