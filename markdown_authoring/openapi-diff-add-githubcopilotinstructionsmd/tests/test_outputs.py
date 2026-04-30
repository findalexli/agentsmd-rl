"""Behavioral checks for openapi-diff-add-githubcopilotinstructionsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/openapi-diff")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Do not modify CI/CD pipeline files (`.github/workflows/`, `azure-pipelines.yml`) unless specifically required.' in text, "expected to find: " + '- Do not modify CI/CD pipeline files (`.github/workflows/`, `azure-pipelines.yml`) unless specifically required.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'This repository contains the source code for `openapi-diff` (aka `oad`, aka `@azure/oad`), a breaking-change' in text, "expected to find: " + 'This repository contains the source code for `openapi-diff` (aka `oad`, aka `@azure/oad`), a breaking-change'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'detector tool for OpenAPI specifications. It is published as an npm package and is used internally by the' in text, "expected to find: " + 'detector tool for OpenAPI specifications. It is published as an npm package and is used internally by the'[:80]

