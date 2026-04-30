"""Behavioral checks for flow-cli-docs-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/flow-cli")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `make generate` — `go generate ./...`; run before `lint`, `ci`, or any test touching generated code' in text, "expected to find: " + '- `make generate` — `go generate ./...`; run before `lint`, `ci`, or any test touching generated code'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'eight command groups (super, resources, interactions, tools, project, security, manager, schedule).' in text, "expected to find: " + 'eight command groups (super, resources, interactions, tools, project, security, manager, schedule).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `flowkit/` top-level directory — legacy stub; real code lives in `github.com/onflow/flowkit/v2`.' in text, "expected to find: " + '- `flowkit/` top-level directory — legacy stub; real code lives in `github.com/onflow/flowkit/v2`.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

