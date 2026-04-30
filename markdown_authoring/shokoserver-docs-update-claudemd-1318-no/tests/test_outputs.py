"""Behavioral checks for shokoserver-docs-update-claudemd-1318-no (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/shokoserver")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**API versioning**: `v0` (version-less: auth + legacy Plex webhooks + index redirect), `v1` (legacy REST, off by default), `v2` (legacy REST, can be kill-switched), `v3` (current, all new endpoints). ' in text, "expected to find: " + '**API versioning**: `v0` (version-less: auth + legacy Plex webhooks + index redirect), `v1` (legacy REST, off by default), `v2` (legacy REST, can be kill-switched), `v3` (current, all new endpoints). '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**Access pattern**: Repositories are accessed via the `RepoFactory` static class (e.g., `RepoFactory.AnimeSeries.GetByID(id)`). `RepoFactory` is DI-registered but exposes static fields for convenience' in text, "expected to find: " + '**Access pattern**: Repositories are accessed via the `RepoFactory` static class (e.g., `RepoFactory.AnimeSeries.GetByID(id)`). `RepoFactory` is DI-registered but exposes static fields for convenience'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**Serialization**: MVC uses `AddNewtonsoftJson()` (not `System.Text.Json`) with: `MaxDepth = 10`, `DefaultContractResolver`, `NullValueHandling.Include`, `DefaultValueHandling.Populate`. SignalR also ' in text, "expected to find: " + '**Serialization**: MVC uses `AddNewtonsoftJson()` (not `System.Text.Json`) with: `MaxDepth = 10`, `DefaultContractResolver`, `NullValueHandling.Include`, `DefaultValueHandling.Populate`. SignalR also '[:80]

