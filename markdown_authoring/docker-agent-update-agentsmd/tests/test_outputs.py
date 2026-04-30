"""Behavioral checks for docker-agent-update-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/docker-agent")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `task cross` - Build binaries for multiple platforms (linux/amd64, linux/arm64, darwin/amd64, darwin/arm64, windows/amd64, windows/arm64)' in text, "expected to find: " + '- `task cross` - Build binaries for multiple platforms (linux/amd64, linux/arm64, darwin/amd64, darwin/arm64, windows/amd64, windows/arm64)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '3. **Use `t.Context()` for test contexts** - Never use `context.Background()` or `context.TODO()` (enforced by linter)' in text, "expected to find: " + '3. **Use `t.Context()` for test contexts** - Never use `context.Background()` or `context.TODO()` (enforced by linter)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '4. **transfer_task auto-approved**: Unlike other tools, `transfer_task` always executes without confirmation' in text, "expected to find: " + '4. **transfer_task auto-approved**: Unlike other tools, `transfer_task` always executes without confirmation'[:80]

