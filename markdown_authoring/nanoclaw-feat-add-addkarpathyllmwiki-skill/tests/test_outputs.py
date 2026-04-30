"""Behavioral checks for nanoclaw-feat-add-addkarpathyllmwiki-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nanoclaw")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-karpathy-llm-wiki/SKILL.md')
    assert 'Based on the source types the user plans to ingest (discussed in Step 3), check whether the agent can already handle those formats — some are supported natively, others need a skill (e.g. `/add-image-' in text, "expected to find: " + 'Based on the source types the user plans to ingest (discussed in Step 3), check whether the agent can already handle those formats — some are supported natively, others need a skill (e.g. `/add-image-'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-karpathy-llm-wiki/SKILL.md')
    assert "Create a `container/skills/wiki/SKILL.md` tailored to this user's wiki. This is the schema layer from the pattern — it tells the agent how to maintain the wiki. Base it on the pattern's Operations sec" in text, "expected to find: " + "Create a `container/skills/wiki/SKILL.md` tailored to this user's wiki. This is the schema layer from the pattern — it tells the agent how to maintain the wiki. Base it on the pattern's Operations sec"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-karpathy-llm-wiki/SKILL.md')
    assert 'claude has built-in `WebFetch`, but it returns a summary, not the full document. For wiki ingestion of a URL where the full text matters, the container skill and CLAUDE.md should instruct claude to us' in text, "expected to find: " + 'claude has built-in `WebFetch`, but it returns a summary, not the full document. For wiki ingestion of a URL where the full text matters, the container skill and CLAUDE.md should instruct claude to us'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-karpathy-llm-wiki/llm-wiki.md')
    assert 'This document intentionally remains abstract, describing the idea rather than specific implementation. Directory structure, schema conventions, page formats, tooling—all depend on domain, preferences,' in text, "expected to find: " + 'This document intentionally remains abstract, describing the idea rather than specific implementation. Directory structure, schema conventions, page formats, tooling—all depend on domain, preferences,'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-karpathy-llm-wiki/llm-wiki.md')
    assert 'The concept here differs fundamentally. Rather than just retrieving from raw documents, the LLM incrementally builds and maintains a persistent wiki — a structured, interlinked markdown collection sit' in text, "expected to find: " + 'The concept here differs fundamentally. Rather than just retrieving from raw documents, the LLM incrementally builds and maintains a persistent wiki — a structured, interlinked markdown collection sit'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-karpathy-llm-wiki/llm-wiki.md')
    assert 'At scale, small tools help the LLM operate more efficiently. Search engine over wiki pages is most obvious—at small scale the index suffices, but as the wiki grows, proper search becomes necessary. qm' in text, "expected to find: " + 'At scale, small tools help the LLM operate more efficiently. Search engine over wiki pages is most obvious—at small scale the index suffices, but as the wiki grows, proper search becomes necessary. qm'[:80]

