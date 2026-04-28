"""Behavioral checks for mcp-devtools-set-up-github-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mcp-devtools")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**Session span parent-child relationships**: Session spans in `internal/telemetry/tracer.go` must be ended immediately followed by `ForceFlush()` to ensure they export to the backend before child tool' in text, "expected to find: " + '**Session span parent-child relationships**: Session spans in `internal/telemetry/tracer.go` must be ended immediately followed by `ForceFlush()` to ensure they export to the backend before child tool'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- When adding new tools ensure they are registered in the list of available tools in the server (within their init function), ensure they have a basic unit test, and that they have docs/tools/<toolnam' in text, "expected to find: " + '- When adding new tools ensure they are registered in the list of available tools in the server (within their init function), ensure they have a basic unit test, and that they have docs/tools/<toolnam'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- On occasion the user may ask you to build a new tool and provide reference code or information in a provided directory such as `tmp_repo_clones/<dirname>` unless specified otherwise this should only' in text, "expected to find: " + '- On occasion the user may ask you to build a new tool and provide reference code or information in a provided directory such as `tmp_repo_clones/<dirname>` unless specified otherwise this should only'[:80]

