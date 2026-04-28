"""Behavioral checks for sentry-featskills-add-djangomodels-agent-skill (markdown_authoring task).

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
    text = _read('.agents/skills/django-models/SKILL.md')
    assert 'description: Design Django ORM models for Sentry following architectural conventions for silos, replication, relocation, and foreign keys. Use when adding a new Django model, designing a model for a f' in text, "expected to find: " + 'description: Design Django ORM models for Sentry following architectural conventions for silos, replication, relocation, and foreign keys. Use when adding a new Django model, designing a model for a f'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/django-models/SKILL.md')
    assert '- `HybridCloudForeignKey("sentry.User", on_delete="...", ...)` — the FK target lives in the _opposite_ silo. No database constraint. Cascade is eventually consistent via outbox tombstones. `on_delete`' in text, "expected to find: " + '- `HybridCloudForeignKey("sentry.User", on_delete="...", ...)` — the FK target lives in the _opposite_ silo. No database constraint. Cascade is eventually consistent via outbox tombstones. `on_delete`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/django-models/SKILL.md')
    assert "Use `DefaultFieldsModel` for new models. It gives you `date_added` (`auto_now_add=True`) and `date_updated` (`auto_now=True`) for free, and it's almost always what you want — tables that genuinely sho" in text, "expected to find: " + "Use `DefaultFieldsModel` for new models. It gives you `date_added` (`auto_now_add=True`) and `date_updated` (`auto_now=True`) for free, and it's almost always what you want — tables that genuinely sho"[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/generate-migration/SKILL.md')
    assert "4. Apply the migration locally with `sentry django migrate <app_name>` — Sentry's migration framework runs its safety checks on apply, so this catches unsafe ops (missing `is_post_deployment`, unsafe " in text, "expected to find: " + "4. Apply the migration locally with `sentry django migrate <app_name>` — Sentry's migration framework runs its safety checks on apply, so this catches unsafe ops (missing `is_post_deployment`, unsafe "[:80]

