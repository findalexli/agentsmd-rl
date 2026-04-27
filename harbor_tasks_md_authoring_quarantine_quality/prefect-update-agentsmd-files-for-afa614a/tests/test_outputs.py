"""Behavioral checks for prefect-update-agentsmd-files-for-afa614a (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/prefect")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('ui-v2/src/routes/AGENTS.md')
    assert 'Use `validateSearch` with `zodValidator` from `@tanstack/zod-adapter` to validate search params:' in text, "expected to find: " + 'Use `validateSearch` with `zodValidator` from `@tanstack/zod-adapter` to validate search params:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('ui-v2/src/routes/AGENTS.md')
    assert 'import { zodValidator } from "@tanstack/zod-adapter";' in text, "expected to find: " + 'import { zodValidator } from "@tanstack/zod-adapter";'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('ui-v2/src/routes/AGENTS.md')
    assert 'export const Route = createFileRoute("/path")({' in text, "expected to find: " + 'export const Route = createFileRoute("/path")({'[:80]

