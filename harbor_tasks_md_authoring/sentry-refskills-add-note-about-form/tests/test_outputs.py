"""Behavioral checks for sentry-refskills-add-note-about-form (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sentry")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/migrate-frontend-forms/SKILL.md')
    assert 'If the legacy `JsonForm` being migrated was already indexed by SettingsSearch (i.e., it had entries in `sentry/data/forms`), you **must** add a `FormSearch` wrapper to the new form so search functiona' in text, "expected to find: " + 'If the legacy `JsonForm` being migrated was already indexed by SettingsSearch (i.e., it had entries in `sentry/data/forms`), you **must** add a `FormSearch` wrapper to the new form so search functiona'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/migrate-frontend-forms/SKILL.md')
    assert 'This script (`scripts/extractFormFields.ts`) scans all TSX files, finds `<FormSearch>` components, extracts field metadata (`name`, `label`, `hintText`, `route`), and writes the generated registry to ' in text, "expected to find: " + 'This script (`scripts/extractFormFields.ts`) scans all TSX files, finds `<FormSearch>` components, extracts field metadata (`name`, `label`, `hintText`, `route`), and writes the generated registry to '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/migrate-frontend-forms/SKILL.md')
    assert '`FormSearch` is a **build-time marker component** — it has zero runtime behavior and simply renders its children unchanged. Its `route` prop is read by a static extraction script to associate form fie' in text, "expected to find: " + '`FormSearch` is a **build-time marker component** — it has zero runtime behavior and simply renders its children unchanged. Its `route` prop is read by a static extraction script to associate form fie'[:80]

