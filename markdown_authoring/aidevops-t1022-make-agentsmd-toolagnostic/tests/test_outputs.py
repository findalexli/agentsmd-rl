"""Behavioral checks for aidevops-t1022-make-agentsmd-toolagnostic (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/aidevops")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/AGENTS.md')
    assert '**Session memory monitoring + respawn** (t264, t264.1): Long-running Claude Code/Bun sessions accumulate WebKit malloc dirty pages that are never returned to the OS (25GB+ observed). Phase 11 of the p' in text, "expected to find: " + '**Session memory monitoring + respawn** (t264, t264.1): Long-running Claude Code/Bun sessions accumulate WebKit malloc dirty pages that are never returned to the OS (25GB+ observed). Phase 11 of the p'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/AGENTS.md')
    assert '**Supported tools:** [Claude Code](https://Claude.ai/) (TUI, Desktop, and Extension for Zed/VSCode) is the only tested and supported AI coding tool for aidevops. The `Claude` CLI is used for headless ' in text, "expected to find: " + '**Supported tools:** [Claude Code](https://Claude.ai/) (TUI, Desktop, and Extension for Zed/VSCode) is the only tested and supported AI coding tool for aidevops. The `Claude` CLI is used for headless '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/AGENTS.md')
    assert '**Runtime identity**: You are an AI DevOps agent powered by the aidevops framework. When asked about your identity, use the app name from the version check output - do not guess or assume based on sys' in text, "expected to find: " + '**Runtime identity**: You are an AI DevOps agent powered by the aidevops framework. When asked about your identity, use the app name from the version check output - do not guess or assume based on sys'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Primary: `~/.config/Claude/Claude.json`, `~/.config/Claude/agent/`' in text, "expected to find: " + '- Primary: `~/.config/Claude/Claude.json`, `~/.config/Claude/agent/`'[:80]

