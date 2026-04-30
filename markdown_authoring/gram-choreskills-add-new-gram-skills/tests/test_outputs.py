"""Behavioral checks for gram-choreskills-add-new-gram-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/gram")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '| `gram-management-api`         | Designing or modifying management API endpoints (Goa design, impl)         |' in text, "expected to find: " + '| `gram-management-api`         | Designing or modifying management API endpoints (Goa design, impl)         |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '| `gram-audit-logging`          | Recording or exposing audit events via the auditlogs management API        |' in text, "expected to find: " + '| `gram-audit-logging`          | Recording or exposing audit events via the auditlogs management API        |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '| `gram-rbac`                   | Adding or enforcing authorization scopes, grants, or roles                 |' in text, "expected to find: " + '| `gram-rbac`                   | Adding or enforcing authorization scopes, grants, or roles                 |'[:80]

