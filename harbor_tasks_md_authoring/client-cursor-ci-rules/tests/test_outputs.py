"""Behavioral checks for client-cursor-ci-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/client")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert 'User reports: "TestStatRoot failed, logs at: curl -s -o - https://ci-fail-logs.s3.amazonaws.com/citogo-PR_28719-4-kbfs_libdokan-TestStatRoot-puco3td7mech4ilrcdhabhsklm25vgk2.gz | zcat -d | less"' in text, "expected to find: " + 'User reports: "TestStatRoot failed, logs at: curl -s -o - https://ci-fail-logs.s3.amazonaws.com/citogo-PR_28719-4-kbfs_libdokan-TestStatRoot-puco3td7mech4ilrcdhabhsklm25vgk2.gz | zcat -d | less"'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert 'command: "curl -s -o TestStatRoot-failure.gz https://ci-fail-logs.s3.amazonaws.com/citogo-PR_28719-4-kbfs_libdokan-TestStatRoot-puco3td7mech4ilrcdhabhsklm25vgk2.gz",' in text, "expected to find: " + 'command: "curl -s -o TestStatRoot-failure.gz https://ci-fail-logs.s3.amazonaws.com/citogo-PR_28719-4-kbfs_libdokan-TestStatRoot-puco3td7mech4ilrcdhabhsklm25vgk2.gz",'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert 'curl -s -o - https://ci-fail-logs.s3.amazonaws.com/citogo-PR_28719-4-kbfs_libdokan-TestStatRoot-puco3td7mech4ilrcdhabhsklm25vgk2.gz | zcat -d | less' in text, "expected to find: " + 'curl -s -o - https://ci-fail-logs.s3.amazonaws.com/citogo-PR_28719-4-kbfs_libdokan-TestStatRoot-puco3td7mech4ilrcdhabhsklm25vgk2.gz | zcat -d | less'[:80]

