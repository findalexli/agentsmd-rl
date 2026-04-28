"""Behavioral checks for flashinfer-bench-claude-update-skills-on-hugging (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/flashinfer-bench")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-reference-tests/SKILL.md')
    assert '**Note**: See [extract-kernel-definitions](../extract-kernel-definitions/SKILL.md#for-model-constants-huggingface--sglang-required) for detailed guidance on sourcing model constants from HuggingFace a' in text, "expected to find: " + '**Note**: See [extract-kernel-definitions](../extract-kernel-definitions/SKILL.md#for-model-constants-huggingface--sglang-required) for detailed guidance on sourcing model constants from HuggingFace a'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-reference-tests/SKILL.md')
    assert '#### For Model Constants: HuggingFace + SGLang (Required)' in text, "expected to find: " + '#### For Model Constants: HuggingFace + SGLang (Required)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/extract-kernel-definitions/SKILL.md')
    assert '**IMPORTANT**: Always refer to the HuggingFace model page first (`https://huggingface.co/{org}/{model-name}`) for authoritative model constants when creating definitions for new kernels. Download `con' in text, "expected to find: " + '**IMPORTANT**: Always refer to the HuggingFace model page first (`https://huggingface.co/{org}/{model-name}`) for authoritative model constants when creating definitions for new kernels. Download `con'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/extract-kernel-definitions/SKILL.md')
    assert 'Use SGLang (`tmp/sglang/python/sglang/srt/models/{model_name}.py`) for runtime-specific constants like `page_size` and tensor parallel configurations (e.g. `num_attention_heads`, `num_local_experts`).' in text, "expected to find: " + 'Use SGLang (`tmp/sglang/python/sglang/srt/models/{model_name}.py`) for runtime-specific constants like `page_size` and tensor parallel configurations (e.g. `num_attention_heads`, `num_local_experts`).'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/extract-kernel-definitions/SKILL.md')
    assert '### For Model Constants: HuggingFace + SGLang (Required)' in text, "expected to find: " + '### For Model Constants: HuggingFace + SGLang (Required)'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**IMPORTANT**: When creating definitions for new kernels, always refer to the HuggingFace model page (`https://huggingface.co/{org}/{model-name}`) to obtain authoritative model constants from `config.' in text, "expected to find: " + '**IMPORTANT**: When creating definitions for new kernels, always refer to the HuggingFace model page (`https://huggingface.co/{org}/{model-name}`) to obtain authoritative model constants from `config.'[:80]

