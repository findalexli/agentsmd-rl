"""Behavioral checks for desktop-rename-claudemd-to-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/desktop")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**ComfyUI Desktop** (@comfyorg/comfyui-electron) is an Electron-based desktop application that packages ComfyUI with a user-friendly interface. It\'s "the best modular GUI to run AI diffusion models" a' in text, "expected to find: " + '**ComfyUI Desktop** (@comfyorg/comfyui-electron) is an Electron-based desktop application that packages ComfyUI with a user-friendly interface. It\'s "the best modular GUI to run AI diffusion models" a'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'We have testing configured with Vitest. Use vitest to create any tests you need. Do not attempt to custom code your own testing infrastructure, as that is pointless and will do nothing but derail you.' in text, "expected to find: " + 'We have testing configured with Vitest. Use vitest to create any tests you need. Do not attempt to custom code your own testing infrastructure, as that is pointless and will do nothing but derail you.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This is a sophisticated Electron application with comprehensive testing, automated CI/CD, cross-platform support, and professional development practices.' in text, "expected to find: " + 'This is a sophisticated Electron application with comprehensive testing, automated CI/CD, cross-platform support, and professional development practices.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('tests/integration/AGENTS.md')
    assert '# Integration testing guide' in text, "expected to find: " + '# Integration testing guide'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('tests/integration/CLAUDE.md')
    assert '@tests/integration/AGENTS.md' in text, "expected to find: " + '@tests/integration/AGENTS.md'[:80]

