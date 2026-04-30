"""Behavioral checks for openvino.genai-agentic-skills-update-documentation-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/openvino.genai")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/update-docs/SKILL.md')
    assert "- **Name**: use the existing `models.ts` as the source of truth for naming style. The `name` is usually the marketing / family name grouping related versions under one entry (e.g. `name: 'Phi3'` cover" in text, "expected to find: " + "- **Name**: use the existing `models.ts` as the source of truth for naming style. The `name` is usually the marketing / family name grouping related versions under one entry (e.g. `name: 'Phi3'` cover"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/update-docs/SKILL.md')
    assert 'description: "Update OpenVINO GenAI site documentation for API or feature changes. Use when: new pipelines, models, or use-cases are introduced; site docs need to reflect new capabilities."' in text, "expected to find: " + 'description: "Update OpenVINO GenAI site documentation for API or feature changes. Use when: new pipelines, models, or use-cases are introduced; site docs need to reflect new capabilities."'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/update-docs/SKILL.md')
    assert '- **Architecture** (optional): verify the `architecture` value against the model\'s `config.json` (`"architectures"` field) or HuggingFace model card. Do not guess from the model name.' in text, "expected to find: " + '- **Architecture** (optional): verify the `architecture` value against the model\'s `config.json` (`"architectures"` field) or HuggingFace model card. Do not guess from the model name.'[:80]

