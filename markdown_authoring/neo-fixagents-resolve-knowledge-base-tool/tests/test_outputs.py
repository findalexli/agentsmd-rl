"""Behavioral checks for neo-fixagents-resolve-knowledge-base-tool (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/neo")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "**Action:** Use the `ask_knowledge_base` tool to synthesize answers regarding relevant source code, guides, and examples from the framework's knowledge base. This will give you the correct implementat" in text, "expected to find: " + "**Action:** Use the `ask_knowledge_base` tool to synthesize answers regarding relevant source code, guides, and examples from the framework's knowledge base. This will give you the correct implementat"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '2.  **`query_documents` (Secondary):** The file discovery engine. Use this **only** when you need exhaustive path enumeration (e.g., "list all files implementing Grid selection") where LLM synthesis i' in text, "expected to find: " + '2.  **`query_documents` (Secondary):** The file discovery engine. Use this **only** when you need exhaustive path enumeration (e.g., "list all files implementing Grid selection") where LLM synthesis i'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '1.  **`ask_knowledge_base` (Primary):** The embedded RAG sub-agent. Use this for all conceptual understanding, API syntax verification, and "how does X work?" questions. It synthesizes answers directl' in text, "expected to find: " + '1.  **`ask_knowledge_base` (Primary):** The embedded RAG sub-agent. Use this for all conceptual understanding, API syntax verification, and "how does X work?" questions. It synthesizes answers directl'[:80]

