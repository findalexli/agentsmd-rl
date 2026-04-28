"""Behavioral checks for python-openai-demos-add-comprehensive-agentsmd-documentation (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/python-openai-demos")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This repository contains a collection of Python scripts that demonstrate how to use the OpenAI API (and compatible APIs like Azure OpenAI, GitHub Models, and Ollama) to generate chat completions. The ' in text, "expected to find: " + 'This repository contains a collection of Python scripts that demonstrate how to use the OpenAI API (and compatible APIs like Azure OpenAI, GitHub Models, and Ollama) to generate chat completions. The '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Models that support function calling:** `gpt-4o`, `gpt-4o-mini`, `o3-mini`, `AI21-Jamba-1.5-Large`, `AI21-Jamba-1.5-Mini`, `Codestral-2501`, `Cohere-command-r`, `Ministral-3B`, `Mistral-Large-2411`,' in text, "expected to find: " + '**Models that support function calling:** `gpt-4o`, `gpt-4o-mini`, `o3-mini`, `AI21-Jamba-1.5-Large`, `AI21-Jamba-1.5-Mini`, `Codestral-2501`, `Cohere-command-r`, `Ministral-3B`, `Mistral-Large-2411`,'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'All example scripts are located in the root directory. They follow a consistent pattern of setting up an OpenAI client based on environment variables, then demonstrating specific API features.' in text, "expected to find: " + 'All example scripts are located in the root directory. They follow a consistent pattern of setting up an OpenAI client based on environment variables, then demonstrating specific API features.'[:80]

