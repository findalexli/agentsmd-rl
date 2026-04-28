"""Behavioral checks for operately-chore-create-agentsmd-to-enable (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/operately")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- One-shot tests: `make test` (Elixir + Jest). Targeted: `make test FILE=app/test/some_test.exs` or `make test FILE=assets/js/path.spec.ts`.' in text, "expected to find: " + '- One-shot tests: `make test` (Elixir + Jest). Targeted: `make test FILE=app/test/some_test.exs` or `make test FILE=assets/js/path.spec.ts`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- TypeScript/JS: Prettier (`printWidth: 120`, `trailingComma: all`). Check: `npm --prefix app run prettier:check`; fix: `make js.fmt.fix`.' in text, "expected to find: " + '- TypeScript/JS: Prettier (`printWidth: 120`, `trailingComma: all`). Check: `npm --prefix app run prettier:check`; fix: `make js.fmt.fix`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Backend (Elixir/Phoenix): `app/` with `lib/` (Elixir code), `config/`, `priv/`, and `test/` (plus `ee/` enterprise code and tests).' in text, "expected to find: " + '- Backend (Elixir/Phoenix): `app/` with `lib/` (Elixir code), `config/`, `priv/`, and `test/` (plus `ee/` enterprise code and tests).'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('turboui/AGENTS.md')
    assert "This document captures the architecture principles, patterns, and workflow for developing components in the turboui library - a React-based component system for Operately's work management software, f" in text, "expected to find: " + "This document captures the architecture principles, patterns, and workflow for developing components in the turboui library - a React-based component system for Operately's work management software, f"[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('turboui/AGENTS.md')
    assert '- **Always examine reference implementations first**: If the user mentions "like [ComponentA]" or "similar to [ComponentB]", immediately examine those components for reusable patterns, shared componen' in text, "expected to find: " + '- **Always examine reference implementations first**: If the user mentions "like [ComponentA]" or "similar to [ComponentB]", immediately examine those components for reusable patterns, shared componen'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('turboui/AGENTS.md')
    assert '- **Copy exact patterns**: Don\'t recreate; copy the exact component structure, class names (`font-bold`, `mt-2`, `size=\\"xxs\\"`), spacing, and interaction patterns from the referenced examples' in text, "expected to find: " + '- **Copy exact patterns**: Don\'t recreate; copy the exact component structure, class names (`font-bold`, `mt-2`, `size=\\"xxs\\"`), spacing, and interaction patterns from the referenced examples'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('turboui/CLAUDE.md')
    assert 'This document has moved. See [AGENTS.md](./AGENTS.md).' in text, "expected to find: " + 'This document has moved. See [AGENTS.md](./AGENTS.md).'[:80]

