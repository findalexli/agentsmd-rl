"""Behavioral checks for mcp-use-feat-add-claudemd-files-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mcp-use")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**mcp-use** is a full-stack MCP (Model Context Protocol) framework providing clients, agents, and servers in both Python and TypeScript. This is a widely-used open-source library.' in text, "expected to find: " + '**mcp-use** is a full-stack MCP (Model Context Protocol) framework providing clients, agents, and servers in both Python and TypeScript. This is a widely-used open-source library.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'See language-specific CLAUDE.md files in `libraries/python/` and `libraries/typescript/` for detailed guidance.' in text, "expected to find: " + 'See language-specific CLAUDE.md files in `libraries/python/` and `libraries/typescript/` for detailed guidance.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Let the user decide - often breaking changes are acceptable and preferred over code duplication' in text, "expected to find: " + '- Let the user decide - often breaking changes are acceptable and preferred over code duplication'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('libraries/python/CLAUDE.md')
    assert '**IMPORTANT:** Read the root `/CLAUDE.md` first for critical workflow requirements around planning, breaking changes, and testing standards.' in text, "expected to find: " + '**IMPORTANT:** Read the root `/CLAUDE.md` first for critical workflow requirements around planning, breaking changes, and testing standards.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('libraries/python/CLAUDE.md')
    assert 'This file provides guidance for working with the Python implementation of mcp-use.' in text, "expected to find: " + 'This file provides guidance for working with the Python implementation of mcp-use.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('libraries/python/CLAUDE.md')
    assert '**Tests are MANDATORY for new functionality. See root CLAUDE.md for standards.**' in text, "expected to find: " + '**Tests are MANDATORY for new functionality. See root CLAUDE.md for standards.**'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('libraries/typescript/CLAUDE.md')
    assert 'The TypeScript library is a **pnpm workspace monorepo** containing multiple packages for MCP clients, agents, servers, and tooling.' in text, "expected to find: " + 'The TypeScript library is a **pnpm workspace monorepo** containing multiple packages for MCP clients, agents, servers, and tooling.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('libraries/typescript/CLAUDE.md')
    assert 'This file provides guidance for working with the TypeScript implementation of mcp-use.' in text, "expected to find: " + 'This file provides guidance for working with the TypeScript implementation of mcp-use.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('libraries/typescript/CLAUDE.md')
    assert 'Select affected packages, choose semver bump (patch/minor/major), write summary.' in text, "expected to find: " + 'Select affected packages, choose semver bump (patch/minor/major), write summary.'[:80]

