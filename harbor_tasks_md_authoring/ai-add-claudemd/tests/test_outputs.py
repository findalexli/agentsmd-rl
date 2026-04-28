"""Behavioral checks for ai-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ai")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'TanStack AI is a type-safe, provider-agnostic AI SDK for building AI-powered applications. The repository is a **pnpm monorepo** managed with **Nx** that includes TypeScript, PHP, and Python packages,' in text, "expected to find: " + 'TanStack AI is a type-safe, provider-agnostic AI SDK for building AI-powered applications. The repository is a **pnpm monorepo** managed with **Nx** that includes TypeScript, PHP, and Python packages,'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'The library uses a **tree-shakeable adapter architecture** where each provider (OpenAI, Anthropic, Gemini, Ollama) exports multiple specialized adapters:' in text, "expected to find: " + 'The library uses a **tree-shakeable adapter architecture** where each provider (OpenAI, Anthropic, Gemini, Ollama) exports multiple specialized adapters:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'When adding new functionality to provider adapters, create separate adapters rather than adding to monolithic ones. Export from `/adapters` subpath.' in text, "expected to find: " + 'When adding new functionality to provider adapters, create separate adapters rather than adding to monolithic ones. Export from `/adapters` subpath.'[:80]

