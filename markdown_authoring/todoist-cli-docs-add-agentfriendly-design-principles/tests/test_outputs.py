"""Behavioral checks for todoist-cli-docs-add-agentfriendly-design-principles (markdown_authoring task).

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
    text = _read('.agents/skills/add-command/SKILL.md')
    assert '7. **Bounded, high-signal responses** — List commands use `paginate()` from `src/lib/pagination.ts` with `--limit <n>`, `--cursor`, and `--all` flags. When results are truncated, `formatNextCursorFoot' in text, "expected to find: " + '7. **Bounded, high-signal responses** — List commands use `paginate()` from `src/lib/pagination.ts` with `--limit <n>`, `--cursor`, and `--all` flags. When results are truncated, `formatNextCursorFoot'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-command/SKILL.md')
    assert '6. **Composable and predictable structure** — Use consistent subcommand verbs (`list`/`view`/`create`/`update`/`delete`/`browse`). Use consistent flag names across entities (`--project <ref>`, `--json' in text, "expected to find: " + '6. **Composable and predictable structure** — Use consistent subcommand verbs (`list`/`view`/`create`/`update`/`delete`/`browse`). Use consistent flag names across entities (`--project <ref>`, `--json'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/add-command/SKILL.md')
    assert '4. **Safe retries and explicit mutation boundaries** — Mutating commands support `--dry-run`. Destructive + irreversible commands require `--yes`. Create commands return the entity ID (use `isQuiet()`' in text, "expected to find: " + '4. **Safe retries and explicit mutation boundaries** — Mutating commands support `--dry-run`. Destructive + irreversible commands require `--yes`. Create commands return the entity ID (use `isQuiet()`'[:80]

