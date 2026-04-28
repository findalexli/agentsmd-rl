"""Behavioral checks for awesome-japanese-llm-add-guidelines-for-models-derived (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/awesome-japanese-llm")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- If the base model is a Japanese continual pre-training model (e.g., Swallow, ELYZA, Nekomata, youko), the derived model belongs in the **継続事前学習 (Continual Pre-training)** section, NOT 事後学習のみ' in text, "expected to find: " + '- If the base model is a Japanese continual pre-training model (e.g., Swallow, ELYZA, Nekomata, youko), the derived model belongs in the **継続事前学習 (Continual Pre-training)** section, NOT 事後学習のみ'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Base model column**: Record the **original architecture** (e.g., "Llama 3.1"), NOT the intermediate Japanese model name (e.g., NOT "Llama 3.1 Swallow")' in text, "expected to find: " + '- **Base model column**: Record the **original architecture** (e.g., "Llama 3.1"), NOT the intermediate Japanese model name (e.g., NOT "Llama 3.1 Swallow")'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Example: A model fine-tuned on "Llama-3.1-Swallow-8B-Instruct" → place in 継続事前学習 → ドメイン特化型, because Swallow itself is a continual pre-training model' in text, "expected to find: " + '- Example: A model fine-tuned on "Llama-3.1-Swallow-8B-Instruct" → place in 継続事前学習 → ドメイン特化型, because Swallow itself is a continual pre-training model'[:80]

