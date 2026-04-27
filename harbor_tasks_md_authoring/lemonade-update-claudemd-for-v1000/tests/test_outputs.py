"""Behavioral checks for lemonade-update-claudemd-for-v1000 (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/lemonade")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '`Router` (`src/cpp/server/router.cpp`) manages a vector of `WrappedServer` instances. Routes requests based on model recipe, maintains LRU caches per model type (LLM, embedding, reranking, audio, imag' in text, "expected to find: " + '`Router` (`src/cpp/server/router.cpp`) manages a vector of `WrappedServer` instances. Routes requests based on model recipe, maintains LRU caches per model type (LLM, embedding, reranking, audio, imag'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Lemonade is a local LLM server (v10.0.0) providing GPU and NPU acceleration for running large language models on consumer hardware. It exposes OpenAI-compatible, Ollama-compatible, and Anthropic-compa' in text, "expected to find: " + 'Lemonade is a local LLM server (v10.0.0) providing GPU and NPU acceleration for running large language models on consumer hardware. It exposes OpenAI-compatible, Ollama-compatible, and Anthropic-compa'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '`WrappedServer` (`src/cpp/include/lemon/wrapped_server.h`) is the abstract base class. Each backend inherits it and implements `load()`, `unload()`, `chat_completion()`, `completion()`, `responses()`,' in text, "expected to find: " + '`WrappedServer` (`src/cpp/include/lemon/wrapped_server.h`) is the abstract base class. Each backend inherits it and implements `load()`, `unload()`, `chat_completion()`, `completion()`, `responses()`,'[:80]

