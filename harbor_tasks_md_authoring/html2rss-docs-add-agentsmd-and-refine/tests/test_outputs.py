"""Behavioral checks for html2rss-docs-add-agentsmd-and-refine (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/html2rss")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '1. **Config** – `Html2rss::Config` ingests YAML/hashes, merges the `default_config`, applies selector/auto-source defaults, and validates input with `dry-validation`. All defaults—including headers, s' in text, "expected to find: " + '1. **Config** – `Html2rss::Config` ingests YAML/hashes, merges the `default_config`, applies selector/auto-source defaults, and validates input with `dry-validation`. All defaults—including headers, s'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Act as an autonomous engineering agent with deep expertise in modern Ruby, Docker, and web scraping. Operate with a privacy-first mindset, lean on open standards, and reach for proven tooling when it ' in text, "expected to find: " + 'Act as an autonomous engineering agent with deep expertise in modern Ruby, Docker, and web scraping. Operate with a privacy-first mindset, lean on open standards, and reach for proven tooling when it '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '3. **Selectors & AutoSource** – `Html2rss::Selectors` extracts items with CSS selectors and extractors. `Html2rss::AutoSource` inspects structured HTML/JSON to augment or replace selectors when auto-d' in text, "expected to find: " + '3. **Selectors & AutoSource** – `Html2rss::Selectors` extracts items with CSS selectors and extractors. `Html2rss::AutoSource` inspects structured HTML/JSON to augment or replace selectors when auto-d'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- When process or decision updates are required, extend `.github/copilot-instructions.md`; this file should remain the primary location for evolving guidance.' in text, "expected to find: " + '- When process or decision updates are required, extend `.github/copilot-instructions.md`; this file should remain the primary location for evolving guidance.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Read and follow the instructions defined in `.github/copilot-instructions.md` for all work within this repository.' in text, "expected to find: " + '- Read and follow the instructions defined in `.github/copilot-instructions.md` for all work within this repository.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This repository uses `.github/copilot-instructions.md` as the canonical set of agent guidelines.' in text, "expected to find: " + 'This repository uses `.github/copilot-instructions.md` as the canonical set of agent guidelines.'[:80]

