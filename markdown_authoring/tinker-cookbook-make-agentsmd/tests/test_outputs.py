"""Behavioral checks for tinker-cookbook-make-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/tinker-cookbook")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Loss plumbing:** every `tinker.Datum` bundles a `model_input` plus `loss_fn_inputs` (`TensorData`). Use helpers such as `conversation_to_datum`, `datum_from_tokens_weights`, and `_remove_mask` ins' in text, "expected to find: " + '- **Loss plumbing:** every `tinker.Datum` bundles a `model_input` plus `loss_fn_inputs` (`TensorData`). Use helpers such as `conversation_to_datum`, `datum_from_tokens_weights`, and `_remove_mask` ins'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Main loop:** `tinker_cookbook/rl/train.py`. Steps: build dataset (`RLDatasetBuilder`), get groups of envs (`EnvGroupBuilder`), collect rollouts (`do_group_rollout`), compute advantages (`compute_a' in text, "expected to find: " + '- **Main loop:** `tinker_cookbook/rl/train.py`. Steps: build dataset (`RLDatasetBuilder`), get groups of envs (`EnvGroupBuilder`), collect rollouts (`do_group_rollout`), compute advantages (`compute_a'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Subscripts:** `_P` (problems/prompts), `_G` (groups of rollouts sharing metadata), `_T` (tokens/time), `_D` (datums), with flattened forms like `_PG`. Example: `tokens_P_G_T[p][g][t]` indexes toke' in text, "expected to find: " + '- **Subscripts:** `_P` (problems/prompts), `_G` (groups of rollouts sharing metadata), `_T` (tokens/time), `_D` (datums), with flattened forms like `_PG`. Example: `tokens_P_G_T[p][g][t]` indexes toke'[:80]

