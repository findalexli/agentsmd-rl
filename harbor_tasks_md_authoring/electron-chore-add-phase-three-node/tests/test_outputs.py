"""Behavioral checks for electron-chore-add-phase-three-node (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/electron")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/electron-node-upgrade/SKILL.md')
    assert 'description: Guide for performing Node.js version upgrades in the Electron project. Use when working on the roller/node/main branch to fix patch conflicts during `e sync --3`. Covers the patch applica' in text, "expected to find: " + 'description: Guide for performing Node.js version upgrades in the Electron project. Use when working on the roller/node/main branch to fix patch conflicts during `e sync --3`. Covers the patch applica'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/electron-node-upgrade/SKILL.md')
    assert "Electron runs a subset of Node.js's upstream test suite using a custom runner (`script/node-spec-runner.js`). Tests are executed with the built Electron binary via `ELECTRON_RUN_AS_NODE=true`. Many te" in text, "expected to find: " + "Electron runs a subset of Node.js's upstream test suite using a custom runner (`script/node-spec-runner.js`). Tests are executed with the built Electron binary via `ELECTRON_RUN_AS_NODE=true`. Many te"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/electron-node-upgrade/SKILL.md')
    assert "Only add a test to `script/node-disabled-tests.json` as a **last resort** — when the test is fundamentally incompatible with Electron's architecture (not just a BoringSSL difference that can be guarde" in text, "expected to find: " + "Only add a test to `script/node-disabled-tests.json` as a **last resort** — when the test is fundamentally incompatible with Electron's architecture (not just a BoringSSL difference that can be guarde"[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/electron-node-upgrade/references/phase-three-commit-guidelines.md')
    assert "Group related test fixes into a single commit when they address the same root cause (e.g., multiple crypto tests all needing BoringSSL guards for the same missing cipher). Don't create one commit per " in text, "expected to find: " + "Group related test fixes into a single commit when they address the same root cause (e.g., multiple crypto tests all needing BoringSSL guards for the same missing cipher). Don't create one commit per "[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/electron-node-upgrade/references/phase-three-commit-guidelines.md')
    assert 'Always include a `Co-Authored-By` trailer identifying the AI model that assisted (e.g., `Co-Authored-By: <AI model attribution>`).' in text, "expected to find: " + 'Always include a `Co-Authored-By` trailer identifying the AI model that assisted (e.g., `Co-Authored-By: <AI model attribution>`).'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/electron-node-upgrade/references/phase-three-commit-guidelines.md')
    assert '**Titles** follow the 60/80-character guideline: simple changes fit within 60 characters, otherwise the limit is 80 characters.' in text, "expected to find: " + '**Titles** follow the 60/80-character guideline: simple changes fit within 60 characters, otherwise the limit is 80 characters.'[:80]

