"""Behavioral checks for cherry-studio-docs-expand-claudemd-with-comprehensive (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cherry-studio")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '> **IMPORTANT**: Feature PRs that change Redux data models or IndexedDB schemas are **temporarily blocked** until v2.0.0 releases. Only bug fixes, performance improvements, docs, and non-data-model fe' in text, "expected to find: " + '> **IMPORTANT**: Feature PRs that change Redux data models or IndexedDB schemas are **temporarily blocked** until v2.0.0 releases. Only bug fixes, performance improvements, docs, and non-data-model fe'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Supports: OpenAI, Anthropic, Google, Azure, Mistral, Bedrock, Vertex, Ollama, Perplexity, xAI, HuggingFace, Cerebras, OpenRouter, Copilot, and more' in text, "expected to find: " + '- Supports: OpenAI, Anthropic, Google, Azure, Mistral, Bedrock, Vertex, Ollama, Perplexity, xAI, HuggingFace, Cerebras, OpenRouter, Copilot, and more'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Tables: `files`, `topics`, `settings`, `knowledge_notes`, `translate_history`, `quick_phrases`, `message_blocks`, `translate_languages`' in text, "expected to find: " + '- Tables: `files`, `topics`, `settings`, `knowledge_notes`, `translate_history`, `quick_phrases`, `message_blocks`, `translate_languages`'[:80]

