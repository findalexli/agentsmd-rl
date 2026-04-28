"""Behavioral checks for llmgateway-docs-update-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/llmgateway")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'When running curl commands against the local API, you can use `test-token` as authentication.' in text, "expected to find: " + 'When running curl commands against the local API, you can use `test-token` as authentication.'[:80]

