"""Behavioral checks for git-ai-add-agentsmd-project-guide (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/git-ai")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '1. **Checkpoint**: An AI coding agent calls `git-ai checkpoint <agent>` with hook input (JSON on stdin or env var). The agent preset (`src/commands/checkpoint_agent/agent_presets.rs`) extracts edited ' in text, "expected to find: " + '1. **Checkpoint**: An AI coding agent calls `git-ai checkpoint <agent>` with hook input (JSON on stdin or env var). The agent preset (`src/commands/checkpoint_agent/agent_presets.rs`) extracts edited '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '`Config` is a global `OnceLock` singleton accessed via `Config::get()`. It reads from `~/.git-ai/config.json`. In tests, `GIT_AI_TEST_CONFIG_PATCH` env var allows overriding specific config fields wit' in text, "expected to find: " + '`Config` is a global `OnceLock` singleton accessed via `Config::get()`. It reads from `~/.git-ai/config.json`. In tests, `GIT_AI_TEST_CONFIG_PATCH` env var allows overriding specific config fields wit'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '`GitAiError` enum in `src/error.rs` -- not `thiserror`-based, uses manual `Display`/`From` impls. Variants: `GitCliError` (captures exit code + stderr + args), `IoError`, `JsonError`, `SqliteError`, `' in text, "expected to find: " + '`GitAiError` enum in `src/error.rs` -- not `thiserror`-based, uses manual `Display`/`From` impls. Variants: `GitCliError` (captures exit code + stderr + args), `IoError`, `JsonError`, `SqliteError`, `'[:80]

