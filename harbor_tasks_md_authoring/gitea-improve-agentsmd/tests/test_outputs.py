"""Behavioral checks for gitea-improve-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/gitea")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- Run single go unit tests with `go test -tags 'sqlite sqlite_unlock_notify' -run '^TestName$' ./modulepath/`" in text, "expected to find: " + "- Run single go unit tests with `go test -tags 'sqlite sqlite_unlock_notify' -run '^TestName$' ./modulepath/`"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- Run single playwright e2e test files with `GITEA_TEST_E2E_FLAGS='<filepath>' make test-e2e`" in text, "expected to find: " + "- Run single playwright e2e test files with `GITEA_TEST_E2E_FLAGS='<filepath>' make test-e2e`"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- Run single go integration tests with `make 'test-sqlite#TestName/Subtest'`" in text, "expected to find: " + "- Run single go integration tests with `make 'test-sqlite#TestName/Subtest'`"[:80]

