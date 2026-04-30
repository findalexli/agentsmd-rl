"""Behavioral checks for prime-rl-chore-overhaul-skills-and-clean (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/prime-rl")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Minimal try/except**: let errors propagate — silent failures hide bugs. Only catch exceptions for intentional fault tolerance (retries, robustness).' in text, "expected to find: " + '- **Minimal try/except**: let errors propagate — silent failures hide bugs. Only catch exceptions for intentional fault tolerance (retries, robustness).'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- **Targeted comments**: don't explain your work process or reference old code. Use targeted comments sparingly to clarify ambiguous logic." in text, "expected to find: " + "- **Targeted comments**: don't explain your work process or reference old code. Use targeted comments sparingly to clarify ambiguous logic."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Adding dependencies**: add to `pyproject.toml` and run `uv sync --all-extras` to install and lock them.' in text, "expected to find: " + '- **Adding dependencies**: add to `pyproject.toml` and run `uv sync --all-extras` to install and lock them.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/config/SKILL.md')
    assert '- **Fail early**: incompatible option combinations (e.g. CP requires flash attention, NCCL broadcast requires async level 1) should raise in `model_validator` at config resolution time, not at runtime' in text, "expected to find: " + '- **Fail early**: incompatible option combinations (e.g. CP requires flash attention, NCCL broadcast requires async level 1) should raise in `model_validator` at config resolution time, not at runtime'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/config/SKILL.md')
    assert '- **Deprecation**: when renaming or removing config fields, emit a deprecation warning with a clear migration path (e.g. "field X is deprecated, use Y instead"). Do not silently drop fields — help use' in text, "expected to find: " + '- **Deprecation**: when renaming or removing config fields, emit a deprecation warning with a clear migration path (e.g. "field X is deprecated, use Y instead"). Do not silently drop fields — help use'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/config/SKILL.md')
    assert 'description: How the prime-rl config system works — TOML files, CLI, config composition, and special patterns. Use when creating configs, debugging config errors, or overriding values via CLI.' in text, "expected to find: " + 'description: How the prime-rl config system works — TOML files, CLI, config composition, and special patterns. Use when creating configs, debugging config errors, or overriding values via CLI.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/entrypoints/SKILL.md')
    assert 'description: All available prime-rl entrypoints — what they do, how to launch them, and which config class they use. Use when running commands, launching training, or starting servers.' in text, "expected to find: " + 'description: All available prime-rl entrypoints — what they do, how to launch them, and which config class they use. Use when running commands, launching training, or starting servers.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/entrypoints/SKILL.md')
    assert 'All entrypoints are run via `uv run <command>` and accept TOML configs via `@ path/to/config.toml` with CLI overrides. See the `config` skill for config system details.' in text, "expected to find: " + 'All entrypoints are run via `uv run <command>` and accept TOML configs via `@ path/to/config.toml` with CLI overrides. See the `config` skill for config system details.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/entrypoints/SKILL.md')
    assert 'Orchestrates the complete RL loop: launches inference server, orchestrator, and trainer as subprocesses.' in text, "expected to find: " + 'Orchestrates the complete RL loop: launches inference server, orchestrator, and trainer as subprocesses.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/inference-server/SKILL.md')
    assert 'skills/inference-server/SKILL.md' in text, "expected to find: " + 'skills/inference-server/SKILL.md'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/installation/SKILL.md')
    assert 'uv sync --all-extras # recommended: includes flash-attn, flash-attn-cute, etc.' in text, "expected to find: " + 'uv sync --all-extras # recommended: includes flash-attn, flash-attn-cute, etc.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/installation/SKILL.md')
    assert 'uv sync --group dev  # dev tools: pytest, ruff, pre-commit' in text, "expected to find: " + 'uv sync --group dev  # dev tools: pytest, ruff, pre-commit'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/installation/SKILL.md')
    assert 'uv sync              # core dependencies only' in text, "expected to find: " + 'uv sync              # core dependencies only'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/monitor-run/SKILL.md')
    assert '- **Active task distribution**: check if tasks are distributed as expected across workers per-env and across envs. uneven distribution suggests some workers/envs are slower. heavily skewed distributio' in text, "expected to find: " + '- **Active task distribution**: check if tasks are distributed as expected across workers per-env and across envs. uneven distribution suggests some workers/envs are slower. heavily skewed distributio'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/monitor-run/SKILL.md')
    assert 'The exact split is controlled by `deployment.num_infer_gpus`, `deployment.num_train_gpus`, and `deployment.num_teacher_gpus`. The orchestrator runs as a separate process (no GPU). Check the resolved c' in text, "expected to find: " + 'The exact split is controlled by `deployment.num_infer_gpus`, `deployment.num_train_gpus`, and `deployment.num_teacher_gpus`. The orchestrator runs as a separate process (no GPU). Check the resolved c'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/monitor-run/SKILL.md')
    assert 'description: How to monitor ongoing training runs — find output directories, check logs, diagnose performance, and inspect SLURM jobs. Use when asked to check on a run, debug training issues, or inves' in text, "expected to find: " + 'description: How to monitor ongoing training runs — find output directories, check logs, diagnose performance, and inspect SLURM jobs. Use when asked to check on a run, debug training issues, or inves'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/release/SKILL.md')
    assert '5. **Highlights**: group related PRs under a single highlight. Use `##` subsections when a highlight contains multiple items (e.g. Performance & Parallelism). Keep the top highlights for the most impa' in text, "expected to find: " + '5. **Highlights**: group related PRs under a single highlight. Use `##` subsections when a highlight contains multiple items (e.g. Performance & Parallelism). Keep the top highlights for the most impa'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/release/SKILL.md')
    assert '7. **Links**: use clickable links for docs (`[docs/foo.md](https://github.com/PrimeIntellect-ai/prime-rl/blob/main/docs/foo.md)`) and PR references (`[#1234](https://github.com/PrimeIntellect-ai/prime' in text, "expected to find: " + '7. **Links**: use clickable links for docs (`[docs/foo.md](https://github.com/PrimeIntellect-ai/prime-rl/blob/main/docs/foo.md)`) and PR references (`[#1234](https://github.com/PrimeIntellect-ai/prime'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/release/SKILL.md')
    assert '8. **Contributors**: list all contributors ranked by number of commits, using their GitHub `@username`. Get usernames via the GitHub API, not git author names (which can be inconsistent).' in text, "expected to find: " + '8. **Contributors**: list all contributors ranked by number of commits, using their GitHub `@username`. Get usernames via the GitHub API, not git author names (which can be inconsistent).'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/toml-config/SKILL.md')
    assert 'skills/toml-config/SKILL.md' in text, "expected to find: " + 'skills/toml-config/SKILL.md'[:80]

