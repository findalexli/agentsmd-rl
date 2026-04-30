"""Behavioral checks for shelf.nu-chore-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/shelf.nu")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This repository hosts **Shelf.nu**, an asset management platform built with Remix, React, TypeScript, and PostgreSQL. Follow the instructions below when working anywhere in this repository.' in text, "expected to find: " + 'This repository hosts **Shelf.nu**, an asset management platform built with Remix, React, TypeScript, and PostgreSQL. Follow the instructions below when working anywhere in this repository.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `npm run validate` – Run the full validation pipeline (Prisma generation, ESLint, Prettier, TypeScript, unit tests, and E2E tests). Run this before committing substantive code changes.' in text, "expected to find: " + '- `npm run validate` – Run the full validation pipeline (Prisma generation, ESLint, Prettier, TypeScript, unit tests, and E2E tests). Run this before committing substantive code changes.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Routes live under `app/routes/` (organized with remix-flat-routes; notable groups include `_layout+/`, `_auth+/`, `_welcome+/`, `api+/`, and `qr+/`).' in text, "expected to find: " + '- Routes live under `app/routes/` (organized with remix-flat-routes; notable groups include `_layout+/`, `_auth+/`, `_welcome+/`, `api+/`, and `qr+/`).'[:80]

