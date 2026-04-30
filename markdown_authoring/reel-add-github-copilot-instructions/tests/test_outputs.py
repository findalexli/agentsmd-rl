"""Behavioral checks for reel-add-github-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/reel")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Reel is a native, cross-platform media player application written in Rust that brings your Plex and Jellyfin libraries to the desktop with a premium, Netflix-like experience. The project uses:' in text, "expected to find: " + 'Reel is a native, cross-platform media player application written in Rust that brings your Plex and Jellyfin libraries to the desktop with a premium, Netflix-like experience. The project uses:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert "1. **Don't mention AI tools in regular commit messages** - Use descriptive, technical commit messages (exception: setup/configuration commits related to AI tool integration)" in text, "expected to find: " + "1. **Don't mention AI tools in regular commit messages** - Use descriptive, technical commit messages (exception: setup/configuration commits related to AI tool integration)"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**Important**: Always use `cargo check` or `cargo build` to verify compilation. The last line of output shows the actual number of errors/warnings.' in text, "expected to find: " + '**Important**: Always use `cargo check` or `cargo build` to verify compilation. The last line of output shows the actual number of errors/warnings.'[:80]

