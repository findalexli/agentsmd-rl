"""Behavioral checks for geo-optimizer-skill-docs-rewrite-skillmd-as-operational (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/geo-optimizer-skill")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '> Make websites visible and citable by AI search engines (ChatGPT Search, Perplexity, Claude, Gemini AI Overviews). Implements the GEO audit framework plus a 47-method citability engine based on Princ' in text, "expected to find: " + '> Make websites visible and citable by AI search engines (ChatGPT Search, Perplexity, Claude, Gemini AI Overviews). Implements the GEO audit framework plus a 47-method citability engine based on Princ'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert 'Plugins implement the `AuditCheck` protocol (`name`, `description`, `max_score`, `run()`). Plugin results appear in the audit output but do not affect the base score.' in text, "expected to find: " + 'Plugins implement the `AuditCheck` protocol (`name`, `description`, `max_score`, `run()`). Plugin results appear in the audit output but do not affect the base score.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert 'To allow citations while blocking training: `Disallow: /` for `GPTBot` and `anthropic-ai`, but keep `Allow: /` for `OAI-SearchBot`, `ClaudeBot`, `PerplexityBot`.' in text, "expected to find: " + 'To allow citations while blocking training: `Disallow: /` for `GPTBot` and `anthropic-ai`, but keep `Allow: /` for `OAI-SearchBot`, `ClaudeBot`, `PerplexityBot`.'[:80]

