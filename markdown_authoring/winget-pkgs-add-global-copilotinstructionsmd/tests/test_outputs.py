"""Behavioral checks for winget-pkgs-add-global-copilotinstructionsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/winget-pkgs")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'This is the **Windows Package Manager (WinGet) community repository** — a manifest-only repo containing ~415,000+ YAML files describing how to install Windows applications via `winget`. There is no ap' in text, "expected to find: " + 'This is the **Windows Package Manager (WinGet) community repository** — a manifest-only repo containing ~415,000+ YAML files describing how to install Windows applications via `winget`. There is no ap'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**Never recursively scan or search the `manifests/` directory.** It contains hundreds of thousands of files and will cause severe performance issues. Only search within the specific package folder bei' in text, "expected to find: " + '**Never recursively scan or search the `manifests/` directory.** It contains hundreds of thousands of files and will cause severe performance issues. Only search within the specific package folder bei'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- PRs to `manifests/` trigger an Azure DevOps validation pipeline that runs file validation, URL scanning, SmartScreen checks, manifest policy checks, installation verification, and installer metadata' in text, "expected to find: " + '- PRs to `manifests/` trigger an Azure DevOps validation pipeline that runs file validation, URL scanning, SmartScreen checks, manifest policy checks, installation verification, and installer metadata'[:80]

