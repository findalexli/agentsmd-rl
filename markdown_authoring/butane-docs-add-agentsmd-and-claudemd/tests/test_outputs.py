"""Behavioral checks for butane-docs-add-agentsmd-and-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/butane")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Butane** translates human-readable Butane Configs into machine-readable [Ignition](https://github.com/coreos/ignition) Configs for CoreOS-based operating systems.' in text, "expected to find: " + '**Butane** translates human-readable Butane Configs into machine-readable [Ignition](https://github.com/coreos/ignition) Configs for CoreOS-based operating systems.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Stabilizing**: Use `/stabilize-spec` or follow [stabilization checklist](https://github.com/coreos/butane/issues/new?template=stabilize-checklist.md)' in text, "expected to find: " + '**Stabilizing**: Use `/stabilize-spec` or follow [stabilization checklist](https://github.com/coreos/butane/issues/new?template=stabilize-checklist.md)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Preferred**: Config merging via `baseutil.MergeTranslatedConfigs()` - desugared struct is merge parent, user config is child (allows user overrides)' in text, "expected to find: " + '**Preferred**: Config merging via `baseutil.MergeTranslatedConfigs()` - desugared struct is merge parent, user config is child (allows user overrides)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This file imports the main repository specification from AGENTS.md and adds Claude Code-specific instructions.' in text, "expected to find: " + 'This file imports the main repository specification from AGENTS.md and adds Claude Code-specific instructions.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Always run `./test` before committing - this is non-negotiable and enforced by the repository.' in text, "expected to find: " + 'Always run `./test` before committing - this is non-negotiable and enforced by the repository.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "- Use the **Explore** agent for broad codebase searches when simple Grep/Glob isn't enough" in text, "expected to find: " + "- Use the **Explore** agent for broad codebase searches when simple Grep/Glob isn't enough"[:80]

