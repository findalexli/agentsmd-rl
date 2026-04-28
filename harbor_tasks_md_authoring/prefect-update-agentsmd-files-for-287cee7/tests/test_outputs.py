"""Behavioral checks for prefect-update-agentsmd-files-for-287cee7 (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/prefect")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('src/prefect/utilities/AGENTS.md')
    assert "- **`generate_parameter_schema` silently downgrades unsupported parameter types to `Any`.** When a parameter's type raises `ValueError`, `TypeError`, or `PydanticInvalidForJsonSchema` during JSON sche" in text, "expected to find: " + "- **`generate_parameter_schema` silently downgrades unsupported parameter types to `Any`.** When a parameter's type raises `ValueError`, `TypeError`, or `PydanticInvalidForJsonSchema` during JSON sche"[:80]

