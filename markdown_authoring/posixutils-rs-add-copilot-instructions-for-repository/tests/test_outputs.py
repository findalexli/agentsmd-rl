"""Behavioral checks for posixutils-rs-add-copilot-instructions-for-repository (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/posixutils-rs")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'posixutils-rs is a suite of Rust-native core command line utilities (cp, mv, awk, make, vi, etc.) using POSIX.2024 as the baseline specification. The goal is to create clean, race-free userland utilit' in text, "expected to find: " + 'posixutils-rs is a suite of Rust-native core command line utilities (cp, mv, awk, make, vi, etc.) using POSIX.2024 as the baseline specification. The goal is to create clean, race-free userland utilit'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '1. **POSIX Compliance First**: The primary specification is POSIX.2024. Implement features according to POSIX specification before considering GNU/BSD extensions.' in text, "expected to find: " + '1. **POSIX Compliance First**: The primary specification is POSIX.2024. Implement features according to POSIX specification before considering GNU/BSD extensions.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '3. **Quick tests only in `cargo test`**: Longer tests or tests requiring root should use feature flags like `posixutils_test_all` or `requires_root`.' in text, "expected to find: " + '3. **Quick tests only in `cargo test`**: Longer tests or tests requiring root should use feature flags like `posixutils_test_all` or `requires_root`.'[:80]

