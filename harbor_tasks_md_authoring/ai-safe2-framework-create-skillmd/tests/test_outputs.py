"""Behavioral checks for ai-safe2-framework-create-skillmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ai-safe2-framework")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skill.md')
    assert '**You are the AI SAFE² Secure Build Copilot**, a specialized security and governance assistant that implements the [AI SAFE² Framework v2.1](https://github.com/CyberStrategyInstitute/ai-safe2-framewor' in text, "expected to find: " + '**You are the AI SAFE² Secure Build Copilot**, a specialized security and governance assistant that implements the [AI SAFE² Framework v2.1](https://github.com/CyberStrategyInstitute/ai-safe2-framewor'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skill.md')
    assert 'Your purpose is to help developers, security architects, GRC officers, and AI automation builders ship **secure-by-design AI systems** that embed governance and compliance from the first commit — not ' in text, "expected to find: " + 'Your purpose is to help developers, security architects, GRC officers, and AI automation builders ship **secure-by-design AI systems** that embed governance and compliance from the first commit — not '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skill.md')
    assert '"description": "The OpenAI API key is directly embedded in the prompt template string, making it visible in logs and potentially exposed to the LLM context.",' in text, "expected to find: " + '"description": "The OpenAI API key is directly embedded in the prompt template string, making it visible in logs and potentially exposed to the LLM context.",'[:80]

