"""Behavioral checks for documentation-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/documentation")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'This is the official Strapi documentation repository, built with Docusaurus 3. The main documentation website is hosted at [docs.strapi.io](https://docs.strapi.io). This repository contains only docum' in text, "expected to find: " + 'This is the official Strapi documentation repository, built with Docusaurus 3. The main documentation website is hosted at [docs.strapi.io](https://docs.strapi.io). This repository contains only docum'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "This repository includes a comprehensive AI-powered documentation workflow system. **Start with `AGENTS.md`** - it's the main entry point and directory for the entire system." in text, "expected to find: " + "This repository includes a comprehensive AI-powered documentation workflow system. **Start with `AGENTS.md`** - it's the main entry point and directory for the entire system."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **No Strapi codebase in this repo** - Code verification requires access to the separate [strapi/strapi](https://github.com/strapi/strapi) repository' in text, "expected to find: " + '- **No Strapi codebase in this repo** - Code verification requires access to the separate [strapi/strapi](https://github.com/strapi/strapi) repository'[:80]

