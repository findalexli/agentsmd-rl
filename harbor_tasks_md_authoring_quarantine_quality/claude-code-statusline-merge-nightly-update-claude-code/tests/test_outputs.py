"""Behavioral checks for claude-code-statusline-merge-nightly-update-claude-code (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-code-statusline")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'echo \'{"workspace":{"current_dir":"\'$(pwd)\'"},"model":{"display_name":"Claude Opus 4.5"},"context_window":{"used_percentage":12},"cost":{"total_cost_usd":0.45,"total_lines_added":120,"total_lines_remo' in text, "expected to find: " + 'echo \'{"workspace":{"current_dir":"\'$(pwd)\'"},"model":{"display_name":"Claude Opus 4.5"},"context_window":{"used_percentage":12},"cost":{"total_cost_usd":0.45,"total_lines_added":120,"total_lines_remo'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'The statusline reads JSON from stdin (`input=$(cat)`), exported as `STATUSLINE_INPUT_JSON` for all components. Only `workspace.current_dir` is required; all other fields are optional with graceful fal' in text, "expected to find: " + 'The statusline reads JSON from stdin (`input=$(cat)`), exported as `STATUSLINE_INPUT_JSON` for all components. Only `workspace.current_dir` is required; all other fields are optional with graceful fal'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**macOS Note**: Requires bash 4+ (`brew install bash`). Settings.json should use `/opt/homebrew/bin/bash` (Apple Silicon) or `/usr/local/bin/bash` (Intel) instead of `bash`.' in text, "expected to find: " + '**macOS Note**: Requires bash 4+ (`brew install bash`). Settings.json should use `/opt/homebrew/bin/bash` (Apple Silicon) or `/usr/local/bin/bash` (Intel) instead of `bash`.'[:80]

