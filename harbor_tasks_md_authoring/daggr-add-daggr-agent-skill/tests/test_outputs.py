"""Behavioral checks for daggr-add-daggr-agent-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/daggr")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/daggr/SKILL.md')
    assert 'Build DAG-based AI pipelines connecting Gradio Spaces, HuggingFace models, and Python functions into visual workflows. Use when asked to create a workflow, build a pipeline, connect AI models, chain G' in text, "expected to find: " + 'Build DAG-based AI pipelines connecting Gradio Spaces, HuggingFace models, and Python functions into visual workflows. Use when asked to create a workflow, build a pipeline, connect AI models, chain G'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/daggr/SKILL.md')
    assert '(categories: image-generation | video-generation | text-generation | speech-synthesis | music-generation | voice-cloning | image-editing | background-removal | image-upscaling | ocr | style-transfer |' in text, "expected to find: " + '(categories: image-generation | video-generation | text-generation | speech-synthesis | music-generation | voice-cloning | image-editing | background-removal | image-upscaling | ocr | style-transfer |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/daggr/SKILL.md')
    assert '**Deployed Spaces:** Users can click "Login" in the UI and paste their HF token. This enables persistence (sheets) so they can save outputs and resume work later. The token is stored in browser localS' in text, "expected to find: " + '**Deployed Spaces:** Users can click "Login" in the UI and paste their HF token. This enables persistence (sheets) so they can save outputs and resume work later. The token is stored in browser localS'[:80]

