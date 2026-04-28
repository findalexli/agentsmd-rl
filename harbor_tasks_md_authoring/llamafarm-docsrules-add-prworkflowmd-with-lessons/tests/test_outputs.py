"""Behavioral checks for llamafarm-docsrules-add-prworkflowmd-with-lessons (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/llamafarm")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/pr_workflow.md')
    assert "If the above in-place pattern isn't achievable, either (a) restructure so every filesystem operation is in a compound conditional with a fresh `commonpath` check, or (b) dismiss via API with justifica" in text, "expected to find: " + "If the above in-place pattern isn't achievable, either (a) restructure so every filesystem operation is in a compound conditional with a fresh `commonpath` check, or (b) dismiss via API with justifica"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/pr_workflow.md')
    assert "cubic, qodo, github-advanced-security, and github-code-quality re-post the same findings on every new commit with updated line numbers. The comment list is full of duplicates; don't read it as the sou" in text, "expected to find: " + "cubic, qodo, github-advanced-security, and github-code-quality re-post the same findings on every new commit with updated line numbers. The comment list is full of duplicates; don't read it as the sou"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/pr_workflow.md')
    assert "Windows' default `cp1252` console codec crashes on characters like `\\u0120` (Ġ) and `\\u010a` (Ċ) that llama.cpp's native logger emits during tokenizer loading. This must run **before** any logger is c" in text, "expected to find: " + "Windows' default `cp1252` console codec crashes on characters like `\\u0120` (Ġ) and `\\u010a` (Ċ) that llama.cpp's native logger emits during tokenizer loading. This must run **before** any logger is c"[:80]

