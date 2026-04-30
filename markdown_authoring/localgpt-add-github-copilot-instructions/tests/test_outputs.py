"""Behavioral checks for localgpt-add-github-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/localgpt")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'LocalGPT is a local-only AI assistant built in Rust with persistent markdown-based memory and optional autonomous operation via heartbeat. It runs entirely on your machine with no cloud dependency req' in text, "expected to find: " + 'LocalGPT is a local-only AI assistant built in Rust with persistent markdown-based memory and optional autonomous operation via heartbeat. It runs entirely on your machine with no cloud dependency req'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**CRITICAL**: `localgpt-core` must have zero platform-specific dependencies. It must compile cleanly for `aarch64-apple-ios` and `aarch64-linux-android`. No clap, eframe, axum, teloxide, landlock, nix' in text, "expected to find: " + '**CRITICAL**: `localgpt-core` must have zero platform-specific dependencies. It must compile cleanly for `aarch64-apple-ios` and `aarch64-linux-android`. No clap, eframe, axum, teloxide, landlock, nix'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Workspace path resolution: `LOCALGPT_WORKSPACE` env > `LOCALGPT_PROFILE` env > `memory.workspace` config > `~/.localgpt/workspace`' in text, "expected to find: " + 'Workspace path resolution: `LOCALGPT_WORKSPACE` env > `LOCALGPT_PROFILE` env > `memory.workspace` config > `~/.localgpt/workspace`'[:80]

