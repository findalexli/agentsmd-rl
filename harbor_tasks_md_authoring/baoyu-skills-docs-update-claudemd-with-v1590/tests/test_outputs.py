"""Behavioral checks for baoyu-skills-docs-update-claudemd-with-v1590 (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/baoyu-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Claude Code marketplace plugin providing AI-powered content generation skills. Current version: **1.59.0**. Skills use official AI APIs (OpenAI, Google, DashScope, Replicate) or the reverse-engineered' in text, "expected to find: " + 'Claude Code marketplace plugin providing AI-powered content generation skills. Current version: **1.59.0**. Skills use official AI APIs (OpenAI, Google, DashScope, Replicate) or the reverse-engineered'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**Batch Parallel Generation** (`baoyu-image-gen` only): supports concurrent workers with per-provider throttling. Configure via `batch.max_workers` and `batch.provider_limits` in EXTEND.md. Default: s' in text, "expected to find: " + '**Batch Parallel Generation** (`baoyu-image-gen` only): supports concurrent workers with per-provider throttling. Configure via `batch.max_workers` and `batch.provider_limits` in EXTEND.md. Default: s'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '> **Note**: The path variable was renamed from `SKILL_DIR` / `${SKILL_DIR}` to `baseDir` / `{baseDir}` (no `${}` wrapper) in v1.57.0. All existing SKILL.md files use `{baseDir}`.' in text, "expected to find: " + '> **Note**: The path variable was renamed from `SKILL_DIR` / `${SKILL_DIR}` to `baseDir` / `{baseDir}` (no `${}` wrapper) in v1.57.0. All existing SKILL.md files use `{baseDir}`.'[:80]

