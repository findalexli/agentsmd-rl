"""Behavioral checks for antigravity-awesome-skills-feat-add-kotler-and-osterwalder (markdown_authoring task).

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
    text = _read('skills/kotler-macro-analyzer/SKILL.md')
    assert 'This skill transforms the agent into a senior strategic consultant specializing in Philip Kotler’s macro-marketing environment analysis. It systematically evaluates PESTEL factors and synthesizes them' in text, "expected to find: " + 'This skill transforms the agent into a senior strategic consultant specializing in Philip Kotler’s macro-marketing environment analysis. It systematically evaluates PESTEL factors and synthesizes them'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kotler-macro-analyzer/SKILL.md')
    assert '"Conduct a Kotler-style strategic audit for a renewable energy startup planning to enter the Eastern European market in 2026. Focus on regulatory shifts and green energy subsidies."' in text, "expected to find: " + '"Conduct a Kotler-style strategic audit for a renewable energy startup planning to enter the Eastern European market in 2026. Focus on regulatory shifts and green energy subsidies."'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kotler-macro-analyzer/SKILL.md')
    assert '- **Data Freshness**: The quality of the output depends on the real-time availability of data from search tools; results may vary in rapidly shifting economic environments.' in text, "expected to find: " + '- **Data Freshness**: The quality of the output depends on the real-time availability of data from search tools; results may vary in rapidly shifting economic environments.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/osterwalder-canvas-architect/SKILL.md')
    assert 'A specialized architectural tool for designing and auditing business models using Alexander Osterwalder’s 9-block framework. It focuses on the internal logical "lock" between value propositions, custo' in text, "expected to find: " + 'A specialized architectural tool for designing and auditing business models using Alexander Osterwalder’s 9-block framework. It focuses on the internal logical "lock" between value propositions, custo'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/osterwalder-canvas-architect/SKILL.md')
    assert '"Draft a Business Model Canvas for an AI-powered agri-tech platform that provides soil analysis for large-scale farmers on a subscription basis. Focus on how the Key Resources (IoT/AI) drive the Cost ' in text, "expected to find: " + '"Draft a Business Model Canvas for an AI-powered agri-tech platform that provides soil analysis for large-scale farmers on a subscription basis. Focus on how the Key Resources (IoT/AI) drive the Cost '[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/osterwalder-canvas-architect/SKILL.md')
    assert '"Analyze the consistency of a direct-to-consumer organic dairy brand. Ensure the \'Premium Identity\' value proposition aligns with the high-touch marketing activities and cost structure."' in text, "expected to find: " + '"Analyze the consistency of a direct-to-consumer organic dairy brand. Ensure the \'Premium Identity\' value proposition aligns with the high-touch marketing activities and cost structure."'[:80]

