"""Behavioral checks for tinker-cookbook-update-claude-skills-for-tinker (markdown_authoring task).

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
    text = _read('.claude/skills/checkpoints/SKILL.md')
    assert 'Beyond saving and loading during training, you can manage checkpoints via the REST API or CLI. See `/tinker-sdk` for RestClient details and `/tinker-cli` for CLI commands.' in text, "expected to find: " + 'Beyond saving and loading during training, you can manage checkpoints via the REST API or CLI. See `/tinker-sdk` for RestClient details and `/tinker-cli` for CLI commands.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/checkpoints/SKILL.md')
    assert 'rest.set_checkpoint_ttl_from_tinker_path("tinker://...", ttl_seconds=86400)' in text, "expected to find: " + 'rest.set_checkpoint_ttl_from_tinker_path("tinker://...", ttl_seconds=86400)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/checkpoints/SKILL.md')
    assert 'rest.publish_checkpoint_from_tinker_path("tinker://...")' in text, "expected to find: " + 'rest.publish_checkpoint_from_tinker_path("tinker://...")'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/logging/SKILL.md')
    assert 'description: Guide for training outputs, metrics logging, logtree reports, tracing/profiling, and debugging training runs. Use when the user asks about training logs, metrics, debugging, tracing, prof' in text, "expected to find: " + 'description: Guide for training outputs, metrics logging, logtree reports, tracing/profiling, and debugging training runs. Use when the user asks about training logs, metrics, debugging, tracing, prof'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/logging/SKILL.md')
    assert 'Contains full text of prompts, model responses, grading details. Walk the tree recursively looking for nodes with `data.type == "conversation"` to extract conversations. See `docs/rl/rl-logging.mdx` f' in text, "expected to find: " + 'Contains full text of prompts, model responses, grading details. Walk the tree recursively looking for nodes with `data.type == "conversation"` to extract conversations. See `docs/rl/rl-logging.mdx` f'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/logging/SKILL.md')
    assert 'Open `train_iteration_NNNNNN.html` in a browser for a human-readable view of rollouts with collapsible sections. `num_groups_to_log` (default: 4) controls how many trajectory groups get detailed loggi' in text, "expected to find: " + 'Open `train_iteration_NNNNNN.html` in a browser for a human-readable view of rollouts with collapsible sections. `num_groups_to_log` (default: 4) controls how many trajectory groups get detailed loggi'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/manage-skills/SKILL.md')
    assert '**Scope:** Raw Tinker Python SDK APIs — ServiceClient, TrainingClient, SamplingClient, RestClient, types, errors, and CLI commands.' in text, "expected to find: " + '**Scope:** Raw Tinker Python SDK APIs — ServiceClient, TrainingClient, SamplingClient, RestClient, types, errors, and CLI commands.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/manage-skills/SKILL.md')
    assert '│   ├── tinker-sdk/          # ServiceClient, TrainingClient, SamplingClient, RestClient APIs' in text, "expected to find: " + '│   ├── tinker-sdk/          # ServiceClient, TrainingClient, SamplingClient, RestClient APIs'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/manage-skills/SKILL.md')
    assert '│   ├── tinker-types/        # Datum, ModelInput, TensorData, response types, error types' in text, "expected to find: " + '│   ├── tinker-types/        # Datum, ModelInput, TensorData, response types, error types'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/tinker-cli/SKILL.md')
    assert 'description: Guide for the Tinker CLI — managing training runs, checkpoints, downloading weights, and publishing to HuggingFace. Use when the user asks about CLI commands, listing runs, managing check' in text, "expected to find: " + 'description: Guide for the Tinker CLI — managing training runs, checkpoints, downloading weights, and publishing to HuggingFace. Use when the user asks about CLI commands, listing runs, managing check'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/tinker-cli/SKILL.md')
    assert 'The `tinker` CLI is installed with the Tinker Python SDK. It provides commands for managing training runs and checkpoints from the terminal.' in text, "expected to find: " + 'The `tinker` CLI is installed with the Tinker Python SDK. It provides commands for managing training runs and checkpoints from the terminal.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/tinker-cli/SKILL.md')
    assert 'Options: `--repo`, `--public`, `--revision`, `--commit-message`, `--create-pr`, `--allow-pattern`, `--ignore-pattern`, `--no-model-card`.' in text, "expected to find: " + 'Options: `--repo`, `--public`, `--revision`, `--commit-message`, `--create-pr`, `--allow-pattern`, `--ignore-pattern`, `--no-model-card`.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/tinker-sdk/SKILL.md')
    assert 'description: Guide for using the Tinker Python SDK APIs — ServiceClient, TrainingClient, SamplingClient, RestClient, forward_backward, optim_step, sampling, and async patterns. Use when the user asks ' in text, "expected to find: " + 'description: Guide for using the Tinker Python SDK APIs — ServiceClient, TrainingClient, SamplingClient, RestClient, forward_backward, optim_step, sampling, and async patterns. Use when the user asks '[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/tinker-sdk/SKILL.md')
    assert '**Key pattern:** Submit `forward_backward_async` and `optim_step_async` back-to-back before awaiting — this overlaps GPU computation with data preparation.' in text, "expected to find: " + '**Key pattern:** Submit `forward_backward_async` and `optim_step_async` back-to-back before awaiting — this overlaps GPU computation with data preparation.'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/tinker-sdk/SKILL.md')
    assert '- **Use ServiceClient** to create clients — `TrainingClient` and `SamplingClient` cannot be constructed directly' in text, "expected to find: " + '- **Use ServiceClient** to create clients — `TrainingClient` and `SamplingClient` cannot be constructed directly'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/tinker-types/SKILL.md')
    assert 'description: Reference for Tinker SDK types — Datum, ModelInput, TensorData, SamplingParams, response types, error types, and helper functions. Use when the user needs to build training data, construc' in text, "expected to find: " + 'description: Reference for Tinker SDK types — Datum, ModelInput, TensorData, SamplingParams, response types, error types, and helper functions. Use when the user needs to build training data, construc'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/tinker-types/SKILL.md')
    assert '- **`APIError`** → **`APIStatusError`**: `BadRequestError` (400), `AuthenticationError` (401), `PermissionDeniedError` (403), `NotFoundError` (404), `ConflictError` (409), `UnprocessableEntityError` (' in text, "expected to find: " + '- **`APIError`** → **`APIStatusError`**: `BadRequestError` (400), `AuthenticationError` (401), `PermissionDeniedError` (403), `NotFoundError` (404), `ConflictError` (409), `UnprocessableEntityError` ('[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/tinker-types/SKILL.md')
    assert '- `tinker_cookbook.supervised.common.datum_from_model_input_weights(model_input, weights, max_length)` — from ModelInput + weights' in text, "expected to find: " + '- `tinker_cookbook.supervised.common.datum_from_model_input_weights(model_input, weights, max_length)` — from ModelInput + weights'[:80]

