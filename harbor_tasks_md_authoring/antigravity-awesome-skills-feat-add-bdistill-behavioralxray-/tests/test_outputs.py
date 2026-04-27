"""Behavioral checks for antigravity-awesome-skills-feat-add-bdistill-behavioralxray- (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-awesome-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/bdistill-behavioral-xray/SKILL.md')
    assert "bdistill's Behavioral X-Ray runs 30 carefully designed probe questions across 6 dimensions, auto-tags each response with behavioral metadata, and compiles results into a styled HTML report with radar " in text, "expected to find: " + "bdistill's Behavioral X-Ray runs 30 carefully designed probe questions across 6 dimensions, auto-tags each response with behavioral metadata, and compiles results into a styled HTML report with radar "[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/bdistill-behavioral-xray/SKILL.md')
    assert 'description: "X-ray any AI model\'s behavioral patterns — refusal boundaries, hallucination tendencies, reasoning style, formatting defaults. No API key needed."' in text, "expected to find: " + 'description: "X-ray any AI model\'s behavioral patterns — refusal boundaries, hallucination tendencies, reasoning style, formatting defaults. No API key needed."'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/bdistill-behavioral-xray/SKILL.md')
    assert "Systematically probe an AI model's behavioral patterns and generate a visual report. The AI agent probes *itself* — no API key or external setup needed." in text, "expected to find: " + "Systematically probe an AI model's behavioral patterns and generate a visual report. The AI agent probes *itself* — no API key or external setup needed."[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/bdistill-knowledge-extraction/SKILL.md')
    assert 'bdistill turns your AI subscription sessions into a compounding knowledge base. The agent answers targeted domain questions, bdistill structures and quality-scores the responses, and the output accumu' in text, "expected to find: " + 'bdistill turns your AI subscription sessions into a compounding knowledge base. The agent answers targeted domain questions, bdistill structures and quality-scores the responses, and the output accumu'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/bdistill-knowledge-extraction/SKILL.md')
    assert 'Extract structured, quality-scored domain knowledge from any AI model — in-session from closed models (no API key) or locally from open-source models via Ollama.' in text, "expected to find: " + 'Extract structured, quality-scored domain knowledge from any AI model — in-session from closed models (no API key) or locally from open-source models via Ollama.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/bdistill-knowledge-extraction/SKILL.md')
    assert "Adversarial mode challenges the agent's claims — forcing evidence, corrections, and acknowledged limitations — producing validated knowledge entries." in text, "expected to find: " + "Adversarial mode challenges the agent's claims — forcing evidence, corrections, and acknowledged limitations — producing validated knowledge entries."[:80]

