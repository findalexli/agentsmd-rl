"""Behavioral checks for firebase-ios-sdk-ai-agentsmd-update (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/firebase-ios-sdk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/AGENTS.md')
    assert "- **`GenerativeModelSession.swift`**: Defines the `GenerativeModelSession` class, which provides a simplified interface for single-turn interactions with a generative model. It's particularly useful f" in text, "expected to find: " + "- **`GenerativeModelSession.swift`**: Defines the `GenerativeModelSession` class, which provides a simplified interface for single-turn interactions with a generative model. It's particularly useful f"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Extensions/Internal/AGENTS.md')
    assert '-   **`GenerationSchema+Gemini.swift`**: This file extends `GenerationSchema` to provide a `toGeminiJSONSchema()` method. This method transforms the schema into a format that is compatible with the Ge' in text, "expected to find: " + '-   **`GenerationSchema+Gemini.swift`**: This file extends `GenerationSchema` to provide a `toGeminiJSONSchema()` method. This method transforms the schema into a format that is compatible with the Ge'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Extensions/Internal/AGENTS.md')
    assert 'This directory contains internal extensions to data models and other types. These extensions provide functionality that is specific to the internal workings of the Firebase AI SDK and are not part of ' in text, "expected to find: " + 'This directory contains internal extensions to data models and other types. These extensions provide functionality that is specific to the internal workings of the Firebase AI SDK and are not part of '[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('FirebaseAI/Sources/Extensions/Internal/AGENTS.md')
    assert '# Internal Extensions' in text, "expected to find: " + '# Internal Extensions'[:80]

