"""Behavioral checks for hermes-agent-docsobliteratus-link-youtube-video-guide (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/hermes-agent")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/mlops/inference/obliteratus/SKILL.md')
    assert 'https://www.youtube.com/watch?v=8fG9BrNTeHs ("OBLITERATUS: An AI Agent Removed Gemma 4\'s Safety Guardrails")' in text, "expected to find: " + 'https://www.youtube.com/watch?v=8fG9BrNTeHs ("OBLITERATUS: An AI Agent Removed Gemma 4\'s Safety Guardrails")'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/mlops/inference/obliteratus/SKILL.md')
    assert 'Useful when the user wants a visual overview of the end-to-end workflow before running it themselves.' in text, "expected to find: " + 'Useful when the user wants a visual overview of the end-to-end workflow before running it themselves.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/mlops/inference/obliteratus/SKILL.md')
    assert 'Walkthrough of OBLITERATUS used by a Hermes agent to abliterate Gemma:' in text, "expected to find: " + 'Walkthrough of OBLITERATUS used by a Hermes agent to abliterate Gemma:'[:80]

