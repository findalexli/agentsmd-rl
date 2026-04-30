"""Behavioral checks for aisearch-openai-rag-audio-add-agentsmd-to-repository-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/aisearch-openai-rag-audio")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'VoiceRAG is an application pattern demonstrating RAG (Retrieval Augmented Generation) with voice interfaces using Azure AI Search and the GPT-4o Realtime API for Audio. The application enables voice-b' in text, "expected to find: " + 'VoiceRAG is an application pattern demonstrating RAG (Retrieval Augmented Generation) with voice interfaces using Azure AI Search and the GPT-4o Realtime API for Audio. The application enables voice-b'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Note**: This project uses direct pip with pinned versions in `requirements.txt`. Unlike some projects that use `uv` or `pip-compile` with separate `.in` files, dependencies are managed directly in `' in text, "expected to find: " + '**Note**: This project uses direct pip with pinned versions in `requirements.txt`. Unlike some projects that use `uv` or `pip-compile` with separate `.in` files, dependencies are managed directly in `'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This file contains instructions for developers and automated coding agents working on the VoiceRAG application. It covers code layout, environment setup, testing procedures, and development convention' in text, "expected to find: " + 'This file contains instructions for developers and automated coding agents working on the VoiceRAG application. It covers code layout, environment setup, testing procedures, and development convention'[:80]

