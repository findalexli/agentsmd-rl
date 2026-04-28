"""Behavioral checks for phoenix-featskills-add-session-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/phoenix")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/phoenix-tracing/SKILL.md')
    assert '- **Custom Spans**: `setup-{lang}` → `instrumentation-manual-{lang}` → `span-{type}`' in text, "expected to find: " + '- **Custom Spans**: `setup-{lang}` → `instrumentation-manual-{lang}` → `span-{type}`'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/phoenix-tracing/SKILL.md')
    assert '- **Quick Start**: `setup-{lang}` → `instrumentation-auto-{lang}` → Check Phoenix' in text, "expected to find: " + '- **Quick Start**: `setup-{lang}` → `instrumentation-auto-{lang}` → Check Phoenix'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/phoenix-tracing/SKILL.md')
    assert '- **Session Tracking**: `sessions-{lang}` for conversation grouping patterns' in text, "expected to find: " + '- **Session Tracking**: `sessions-{lang}` for conversation grouping patterns'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/phoenix-tracing/rules/sessions-typescript.md')
    assert 'Track multi-turn conversations by grouping traces with session IDs. **Use `withSpan` directly from `@arizeai/openinference-core`** - no wrappers or custom utilities needed.' in text, "expected to find: " + 'Track multi-turn conversations by grouping traces with session IDs. **Use `withSpan` directly from `@arizeai/openinference-core`** - no wrappers or custom utilities needed.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/phoenix-tracing/rules/sessions-typescript.md')
    assert 'For web servers or complex async flows where you need to propagate session IDs through middleware, you can use the Context API:' in text, "expected to find: " + 'For web servers or complex async flows where you need to propagate session IDs through middleware, you can use the Context API:'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/phoenix-tracing/rules/sessions-typescript.md')
    assert 'The `session.id` is only set on the **root span**. Child spans are automatically grouped by the trace hierarchy.' in text, "expected to find: " + 'The `session.id` is only set on the **root span**. Child spans are automatically grouped by the trace hierarchy.'[:80]

