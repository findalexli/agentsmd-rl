"""Behavioral checks for shippie-add-agentsmd-comprehensive-agent-guide (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/shippie")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- The CLI entrypoint is `src/index.ts`; `src/review` contains agent logic and prompts, `src/configure` handles project setup, and `src/common` holds shared platform, API, and utility code.' in text, "expected to find: " + '- The CLI entrypoint is `src/index.ts`; `src/review` contains agent logic and prompts, `src/configure` handles project setup, and `src/common` holds shared platform, API, and utility code.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Do update entries in `docs/` and `templates/` whenever CLI flags or defaults change; do not alter workflow inputs or secrets without mirroring updates in `.github/workflows/`.' in text, "expected to find: " + '- Do update entries in `docs/` and `templates/` whenever CLI flags or defaults change; do not alter workflow inputs or secrets without mirroring updates in `.github/workflows/`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- When updating workflow templates in `templates/`, verify the generated `dist/*.yml` matches the published action expectations and adjust documentation in `docs/` accordingly.' in text, "expected to find: " + '- When updating workflow templates in `templates/`, verify the generated `dist/*.yml` matches the published action expectations and adjust documentation in `docs/` accordingly.'[:80]

