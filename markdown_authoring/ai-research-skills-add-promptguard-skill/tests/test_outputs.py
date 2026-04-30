"""Behavioral checks for ai-research-skills-add-promptguard-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ai-research-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('07-safety-alignment/prompt-guard/SKILL.md')
    assert "description: Meta's 86M prompt injection and jailbreak detector. Filters malicious prompts and third-party data for LLM apps. 99%+ TPR, <1% FPR. Fast (<2ms GPU). Multilingual (8 languages). Deploy wit" in text, "expected to find: " + "description: Meta's 86M prompt injection and jailbreak detector. Filters malicious prompts and third-party data for LLM apps. 99%+ TPR, <1% FPR. Fast (<2ms GPU). Multilingual (8 languages). Deploy wit"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('07-safety-alignment/prompt-guard/SKILL.md')
    assert '- **Tutorial**: https://github.com/meta-llama/llama-cookbook/blob/main/getting-started/responsible_ai/prompt_guard/prompt_guard_tutorial.ipynb' in text, "expected to find: " + '- **Tutorial**: https://github.com/meta-llama/llama-cookbook/blob/main/getting-started/responsible_ai/prompt_guard/prompt_guard_tutorial.ipynb'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('07-safety-alignment/prompt-guard/SKILL.md')
    assert '- **Inference Code**: https://github.com/meta-llama/llama-cookbook/blob/main/getting-started/responsible_ai/prompt_guard/inference.py' in text, "expected to find: " + '- **Inference Code**: https://github.com/meta-llama/llama-cookbook/blob/main/getting-started/responsible_ai/prompt_guard/inference.py'[:80]

