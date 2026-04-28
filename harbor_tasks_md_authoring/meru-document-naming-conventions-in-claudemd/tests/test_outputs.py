"""Behavioral checks for meru-document-naming-conventions-in-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/meru")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Name files by the domain/topic they cover, not by the single function they currently contain. Prefer generic, higher-level names (`lib/linux.ts`, `lib/fs.ts`) over function-specific ones (`lib/linux' in text, "expected to find: " + '- Name files by the domain/topic they cover, not by the single function they currently contain. Prefer generic, higher-level names (`lib/linux.ts`, `lib/fs.ts`) over function-specific ones (`lib/linux'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "- Avoid generic/contextless names even when they're full words — pick a name that carries the domain. `raw`, `data`, `parsed`, `record`, `result`, `value`, `item`, `obj`, `tmp` are all red flags on th" in text, "expected to find: " + "- Avoid generic/contextless names even when they're full words — pick a name that carries the domain. `raw`, `data`, `parsed`, `record`, `result`, `value`, `item`, `obj`, `tmp` are all red flags on th"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "- Name boolean-returning functions with the bare predicate prefix — `is`, `has`, `can`, `should`, `did`, `will` — matching Node.js, Lodash, React, and typescript-eslint's `naming-convention` rule (e.g" in text, "expected to find: " + "- Name boolean-returning functions with the bare predicate prefix — `is`, `has`, `can`, `should`, `did`, `will` — matching Node.js, Lodash, React, and typescript-eslint's `naming-convention` rule (e.g"[:80]

