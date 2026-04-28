"""Behavioral checks for webcomponents-docs-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/webcomponents")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '1. `yarn generate` - Generates `.ts` files (in `src/generated`) from `.css` and `.properties` files. Run once on clean state, or when these files change. The dev server runs this in watch mode automat' in text, "expected to find: " + '1. `yarn generate` - Generates `.ts` files (in `src/generated`) from `.css` and `.properties` files. Run once on clean state, or when these files change. The dev server runs this in watch mode automat'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Use `<!-- playground-fold -->` and `<!-- playground-fold-end -->` to hide boilerplate code in the interactive playground. Only the component usage (between fold comments) is shown to users.' in text, "expected to find: " + 'Use `<!-- playground-fold -->` and `<!-- playground-fold-end -->` to hide boilerplate code in the interactive playground. Only the component usage (between fold comments) is shown to users.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "UI5 Web Components is an enterprise-grade, framework-agnostic web components library implementing SAP Fiori design. It's a Yarn-based monorepo using Lerna and Yarn Workspaces." in text, "expected to find: " + "UI5 Web Components is an enterprise-grade, framework-agnostic web components library implementing SAP Fiori design. It's a Yarn-based monorepo using Lerna and Yarn Workspaces."[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/base/AGENTS.md')
    assert '> **Working in the ui5-webcomponents monorepo?** See the [root AGENTS.md](../../AGENTS.md) for repository commands, build flow, and commit guidelines.' in text, "expected to find: " + '> **Working in the ui5-webcomponents monorepo?** See the [root AGENTS.md](../../AGENTS.md) for repository commands, build flow, and commit guidelines.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/base/AGENTS.md')
    assert '# AGENTS.md - UI5 Web Components Development Guide' in text, "expected to find: " + '# AGENTS.md - UI5 Web Components Development Guide'[:80]

