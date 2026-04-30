"""Behavioral checks for dotnet-skills-clarify-cqrs-pattern-and-structural (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dotnet-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/data/database-performance/SKILL.md')
    assert '**Read and write models are fundamentally different - they have different shapes, columns, and purposes.** Don\'t create a single "User" entity and reuse it everywhere.' in text, "expected to find: " + '**Read and write models are fundamentally different - they have different shapes, columns, and purposes.** Don\'t create a single "User" entity and reuse it everywhere.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/data/database-performance/SKILL.md')
    assert '- **Read models** are denormalized, optimized for query efficiency, and return multiple projection types (UserProfile, UserSummary, UserDetailForAdmin)' in text, "expected to find: " + '- **Read models** are denormalized, optimized for query efficiency, and return multiple projection types (UserProfile, UserSummary, UserDetailForAdmin)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/data/database-performance/SKILL.md')
    assert '- **Write models** are normalized, validation-focused, and accept strongly-typed commands (CreateUserCommand, UpdateUserCommand)' in text, "expected to find: " + '- **Write models** are normalized, validation-focused, and accept strongly-typed commands (CreateUserCommand, UpdateUserCommand)'[:80]

