"""Behavioral checks for llama.cpp-move-copilot-instructions-to-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/llama.cpp")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'It is crucial to remind contributors that the project mandates disclosure of any AI usage in pull requests. This requirement stems from the potential for AI-generated code to include suboptimal optimi' in text, "expected to find: " + 'It is crucial to remind contributors that the project mandates disclosure of any AI usage in pull requests. This requirement stems from the potential for AI-generated code to include suboptimal optimi'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Disclose AI Usage**: Refer to the "Disclose AI Usage" earlier in this document' in text, "expected to find: " + '- **Disclose AI Usage**: Refer to the "Disclose AI Usage" earlier in this document'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Backend-related changes, such as those involving CPU, CUDA, Metal, Vulkan, etc.' in text, "expected to find: " + '- Backend-related changes, such as those involving CPU, CUDA, Metal, Vulkan, etc.'[:80]

