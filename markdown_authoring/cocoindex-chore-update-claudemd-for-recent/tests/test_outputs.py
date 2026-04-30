"""Behavioral checks for cocoindex-chore-update-claudemd-for-recent (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cocoindex")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**Processing Component** — The unit of execution that owns a set of target states. Created by `mount()` or `mount_run()` at a specific component path. When a component finishes, its target states sync' in text, "expected to find: " + '**Processing Component** — The unit of execution that owns a set of target states. Created by `mount()` or `mount_run()` at a specific component path. When a component finishes, its target states sync'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**Context** — React-style provider mechanism for sharing resources. Define keys with `ContextKey[T]`, provide values in lifespan via `builder.provide()`, use in functions via `coco.use_context(key)`.' in text, "expected to find: " + '**Context** — React-style provider mechanism for sharing resources. Define keys with `ContextKey[T]`, provide values in lifespan via `builder.provide()`, use in functions via `coco.use_context(key)`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**Component Path** — Stable identifier for a processing component across runs. Created via `coco.component_subpath("process", filename)`. CocoIndex uses component paths to:' in text, "expected to find: " + '**Component Path** — Stable identifier for a processing component across runs. Created via `coco.component_subpath("process", filename)`. CocoIndex uses component paths to:'[:80]

