"""Behavioral checks for purl-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/purl")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Commits should use concise, imperative subjects (e.g., `Add glob support to filter`) and group related changes. Reference issues when relevant using `Fixes #123`. For pull requests, provide a short su' in text, "expected to find: " + 'Commits should use concise, imperative subjects (e.g., `Add glob support to filter`) and group related changes. Reference issues when relevant using `Fixes #123`. For pull requests, provide a short su'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Go sources live at `main.go` for the CLI entry point and under `internal/cli` for command parsing, option handling, and reusable helpers. Unit tests (`cli_test.go`, `export_test.go`) and golden inputs' in text, "expected to find: " + 'Go sources live at `main.go` for the CLI entry point and under `internal/cli` for command parsing, option handling, and reusable helpers. Unit tests (`cli_test.go`, `export_test.go`) and golden inputs'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Run `goimports` (or `goimports ./...`) before committing so imports stay organized; if `goimports` is unavailable, fall back to `gofmt`. Go tooling expects tab indentation and CamelCase identifiers fo' in text, "expected to find: " + 'Run `goimports` (or `goimports ./...`) before committing so imports stay organized; if `goimports` is unavailable, fall back to `gofmt`. Go tooling expects tab indentation and CamelCase identifiers fo'[:80]

