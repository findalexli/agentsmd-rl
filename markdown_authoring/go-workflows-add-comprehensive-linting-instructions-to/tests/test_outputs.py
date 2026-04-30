"""Behavioral checks for go-workflows-add-comprehensive-linting-instructions-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/go-workflows")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The project uses golangci-lint v2 with a custom analyzer plugin for workflow code validation. There are multiple ways to run the linter:' in text, "expected to find: " + 'The project uses golangci-lint v2 with a custom analyzer plugin for workflow code validation. There are multiple ways to run the linter:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Note:** The project uses golangci-lint v2.4.0 configuration. Version v1.x will not work with the `.golangci.yml` configuration file.' in text, "expected to find: " + '**Note:** The project uses golangci-lint v2.4.0 configuration. Version v1.x will not work with the `.golangci.yml` configuration file.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '3. **Linting:** `make lint` or `golangci-lint run --timeout=5m` - Should pass with no new violations' in text, "expected to find: " + '3. **Linting:** `make lint` or `golangci-lint run --timeout=5m` - Should pass with no new violations'[:80]

