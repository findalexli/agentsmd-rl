"""Behavioral checks for simorgh-first-stab-at-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/simorgh")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'A core part of what makes Simorgh unique is that each service (e.g. `arabic`, `mundo`, `portuguese`) can have different requirements: editorial priorities, layouts, translations, feature toggles, anal' in text, "expected to find: " + 'A core part of what makes Simorgh unique is that each service (e.g. `arabic`, `mundo`, `portuguese`) can have different requirements: editorial priorities, layouts, translations, feature toggles, anal'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Always be **service-aware**: many behaviours are service-specific (e.g. features, translations, routes, branding, analytics). When reading or writing code, think about which service(s) it affects, a' in text, "expected to find: " + '- Always be **service-aware**: many behaviours are service-specific (e.g. features, translations, routes, branding, analytics). When reading or writing code, think about which service(s) it affects, a'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The Simorgh repository is made up of 2 React applications, one powered by a custom Express server and the other powered by Next.js, that serve a variety of web pages for multiple languages, such as ht' in text, "expected to find: " + 'The Simorgh repository is made up of 2 React applications, one powered by a custom Express server and the other powered by Next.js, that serve a variety of web pages for multiple languages, such as ht'[:80]

