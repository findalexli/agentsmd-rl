"""Behavioral checks for todoist-cli-docs-add-agentsmd-with-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/todoist-cli")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The file `src/lib/skills/content.ts` exports `SKILL_CONTENT` — a comprehensive command reference that gets installed into AI agent skill directories via `td skill install`. This is the source of truth' in text, "expected to find: " + 'The file `src/lib/skills/content.ts` exports `SKILL_CONTENT` — a comprehensive command reference that gets installed into AI agent skill directories via `td skill install`. This is the source of truth'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Whenever commands, subcommands, flags, or options are added, updated, or removed in `src/commands/`, the `SKILL_CONTENT` in `src/lib/skills/content.ts` must be updated to match.** This includes:' in text, "expected to find: " + '**Whenever commands, subcommands, flags, or options are added, updated, or removed in `src/commands/`, the `SKILL_CONTENT` in `src/lib/skills/content.ts` must be updated to match.** This includes:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **ID references**: All explicit IDs use `id:` prefix. Use `requireIdRef()` for ID-only args, `isIdRef()`/`extractId()` for mixed refs (fuzzy name + explicit ID)' in text, "expected to find: " + '- **ID references**: All explicit IDs use `id:` prefix. Use `requireIdRef()` for ID-only args, `isIdRef()`/`extractId()` for mixed refs (fuzzy name + explicit ID)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'See [AGENTS.md](./AGENTS.md) for all project guidelines and development instructions.' in text, "expected to find: " + 'See [AGENTS.md](./AGENTS.md) for all project guidelines and development instructions.'[:80]

