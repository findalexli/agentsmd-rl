"""Behavioral checks for opensandbox-docs-add-agentmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/opensandbox")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Naming: classes `PascalCase`, functions `snake_case` (Python) / `camelCase` (Go/Kotlin), constants `UPPER_SNAKE_CASE`.' in text, "expected to find: " + '- Naming: classes `PascalCase`, functions `snake_case` (Python) / `camelCase` (Go/Kotlin), constants `UPPER_SNAKE_CASE`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- PRs should include summary, testing status, and linked issues; follow the template in `CONTRIBUTING.md`.' in text, "expected to find: " + '- PRs should include summary, testing status, and linked issues; follow the template in `CONTRIBUTING.md`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Local server config lives in `~/.sandbox.toml` (copied from `server/example.config.toml`).' in text, "expected to find: " + '- Local server config lives in `~/.sandbox.toml` (copied from `server/example.config.toml`).'[:80]

