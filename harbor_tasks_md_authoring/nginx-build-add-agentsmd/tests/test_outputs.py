"""Behavioral checks for nginx-build-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nginx-build")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'CLI entrypoints sit in `nginx-build.go` and the `command/` package. Build orchestration and artifact helpers live in `builder/`, `configure/`, and `util/`. Third-party integration logic is grouped und' in text, "expected to find: " + 'CLI entrypoints sit in `nginx-build.go` and the `command/` package. Build orchestration and artifact helpers live in `builder/`, `configure/`, and `util/`. Third-party integration logic is grouped und'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Use `make nginx-build` to compile the binary with the current commit hash embedded. `./nginx-build -d work` performs a minimal fetch-and-build cycle in a sandbox directory. Run `make build-example` to' in text, "expected to find: " + 'Use `make nginx-build` to compile the binary with the current commit hash embedded. `./nginx-build -d work` performs a minimal fetch-and-build cycle in a sandbox directory. Run `make build-example` to'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Follow Conventional Commits (`fix: handle trailing comments`, `chore(ci): tighten go workflow paths`). Combine related edits; avoid mixing refactors with feature changes. Every PR should describe the ' in text, "expected to find: " + 'Follow Conventional Commits (`fix: handle trailing comments`, `chore(ci): tighten go workflow paths`). Combine related edits; avoid mixing refactors with feature changes. Every PR should describe the '[:80]

