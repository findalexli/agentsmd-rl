"""Behavioral checks for intellij-update-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/intellij")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'The workspace may include reference directories from the IntelliJ IDEA monorepo. These are **for context only** - use them to understand IntelliJ Platform APIs, research implementation patterns, or le' in text, "expected to find: " + 'The workspace may include reference directories from the IntelliJ IDEA monorepo. These are **for context only** - use them to understand IntelliJ Platform APIs, research implementation patterns, or le'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'The project is migrating from **monolithic** BUILD files (one large file per plugin) to **fine-grained** BUILD files (distributed across the codebase following package structure). This follows Bazel b' in text, "expected to find: " + 'The project is migrating from **monolithic** BUILD files (one large file per plugin) to **fine-grained** BUILD files (distributed across the codebase following package structure). This follows Bazel b'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '1. **Prefer `intellij_plugin_library`**: For plugin code, always use `intellij_plugin_library` instead of manually creating `kt_jvm_library`/`java_library` targets. It handles compilation and plugin i' in text, "expected to find: " + '1. **Prefer `intellij_plugin_library`**: For plugin code, always use `intellij_plugin_library` instead of manually creating `kt_jvm_library`/`java_library` targets. It handles compilation and plugin i'[:80]

