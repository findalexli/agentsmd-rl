"""Behavioral checks for gomodel-docs-update-claudemd-to-reflect (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/gomodel")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**Startup:** Config load (defaults → YAML → env vars) → Register providers with factory → Init providers (cache → async model load → background refresh → router) → Init audit logging → Init usage trac' in text, "expected to find: " + '**Startup:** Config load (defaults → YAML → env vars) → Register providers with factory → Init providers (cache → async model load → background refresh → router) → Init audit logging → Init usage trac'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- `internal/guardrails/` — Pluggable guardrails pipeline. `GuardedProvider` wraps a `RoutableProvider` and applies guardrails *before* routing. Guardrails operate on normalized `[]Message` DTOs decoup' in text, "expected to find: " + '- `internal/guardrails/` — Pluggable guardrails pipeline. `GuardedProvider` wraps a `RoutableProvider` and applies guardrails *before* routing. Guardrails operate on normalized `[]Message` DTOs decoup'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- `internal/core/interfaces.go` — `Provider` interface (ChatCompletion, StreamChatCompletion, ListModels, Responses, StreamResponses). `RoutableProvider` adds `Supports()` and `GetProviderType()`. `Av' in text, "expected to find: " + '- `internal/core/interfaces.go` — `Provider` interface (ChatCompletion, StreamChatCompletion, ListModels, Responses, StreamResponses). `RoutableProvider` adds `Supports()` and `GetProviderType()`. `Av'[:80]

