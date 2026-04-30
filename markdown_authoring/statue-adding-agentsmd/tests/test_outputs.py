"""Behavioral checks for statue-adding-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/statue")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This guide provides a systematic approach to transforming a statue-ssg installation into a fully customized website in a single pass. The project is already initialized with all dependencies, ESM supp' in text, "expected to find: " + 'This guide provides a systematic approach to transforming a statue-ssg installation into a fully customized website in a single pass. The project is already initialized with all dependencies, ESM supp'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "**Why this matters:** Without `handleUnseenRoutes: 'ignore'`, the build will fail if you have dynamic routes like `[directory]` or `[...slug]` that don't have corresponding markdown content." in text, "expected to find: " + "**Why this matters:** Without `handleUnseenRoutes: 'ignore'`, the build will fail if you have dynamic routes like `[directory]` or `[...slug]` that don't have corresponding markdown content."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Build warnings about unused export properties (`export let data`) or CSS optimization can be ignored. Address errors related to missing files or syntax issues.' in text, "expected to find: " + 'Build warnings about unused export properties (`export let data`) or CSS optimization can be ignored. Address errors related to missing files or syntax issues.'[:80]

