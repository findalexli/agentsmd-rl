"""Behavioral checks for claude-code-templates-feat-add-bright-data-local (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-code-templates")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('cli-tool/components/skills/development/brightdata-local-search/SKILL.md')
    assert "Run powerful web searches locally using Bright Data's SERP API. This skill sets up the [unfancy-search](https://github.com/yaronbeen/unfancy-search) pipeline — a local search engine with query expansi" in text, "expected to find: " + "Run powerful web searches locally using Bright Data's SERP API. This skill sets up the [unfancy-search](https://github.com/yaronbeen/unfancy-search) pipeline — a local search engine with query expansi"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('cli-tool/components/skills/development/brightdata-local-search/SKILL.md')
    assert 'description: Set up and run local web searches using Bright Data SERP API with the unfancy-search pipeline (query expansion, SERP retrieval, RRF reranking).' in text, "expected to find: " + 'description: Set up and run local web searches using Bright Data SERP API with the unfancy-search pipeline (query expansion, SERP retrieval, RRF reranking).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('cli-tool/components/skills/development/brightdata-local-search/SKILL.md')
    assert '1. Ensure the local server is running (`docker compose up -d` in the unfancy-search directory)' in text, "expected to find: " + '1. Ensure the local server is running (`docker compose up -d` in the unfancy-search directory)'[:80]

