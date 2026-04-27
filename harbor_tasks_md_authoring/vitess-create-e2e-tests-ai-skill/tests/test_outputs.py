"""Behavioral checks for vitess-create-e2e-tests-ai-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/vitess")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/e2e-tests/SKILL.md')
    assert 'Tests invoke binaries from `$VTROOT/bin/`. If source code for the binaries has changed, rebuild before running tests. Rebuilding is not needed if only test code under `go/test/endtoend/` has changed, ' in text, "expected to find: " + 'Tests invoke binaries from `$VTROOT/bin/`. If source code for the binaries has changed, rebuild before running tests. Rebuilding is not needed if only test code under `go/test/endtoend/` has changed, '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/e2e-tests/SKILL.md')
    assert 'End-to-end tests spin up real Vitess binaries (vtgate, vttablet, vtctld, mysqlctl, etcd, vtorc) and real MySQL instances on the local machine. They exercise the full production stack: topology, replic' in text, "expected to find: " + 'End-to-end tests spin up real Vitess binaries (vtgate, vttablet, vtctld, mysqlctl, etcd, vtorc) and real MySQL instances on the local machine. They exercise the full production stack: topology, replic'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/e2e-tests/SKILL.md')
    assert 'Use `-timeout` generously. End-to-end tests start entire clusters (etcd, MySQL, vttablet, vtgate) and can take minutes. Default 10m is safe for most tests. `-count=1` disables caching, which is essent' in text, "expected to find: " + 'Use `-timeout` generously. End-to-end tests start entire clusters (etcd, MySQL, vttablet, vtgate) and can take minutes. Default 10m is safe for most tests. `-count=1` disables caching, which is essent'[:80]

