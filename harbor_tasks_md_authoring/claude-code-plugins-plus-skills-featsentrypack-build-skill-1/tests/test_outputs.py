"""Behavioral checks for claude-code-plugins-plus-skills-featsentrypack-build-skill-1 (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-code-plugins-plus-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/saas-packs/sentry-pack/skills/sentry-reference-architecture/SKILL.md')
    assert 'Enterprise Sentry architecture patterns for multi-service organizations. Covers centralized configuration, project topology, team-based alert routing, distributed tracing, error middleware, source map' in text, "expected to find: " + 'Enterprise Sentry architecture patterns for multi-service organizations. Covers centralized configuration, project topology, team-based alert routing, distributed tracing, error middleware, source map'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/saas-packs/sentry-pack/skills/sentry-reference-architecture/SKILL.md')
    assert '**Pattern B: Shared Project (< 3 services, single team)** — one project with `Environment` tags (production/staging/dev). Simpler setup; outgrow when alert noise exceeds one team.' in text, "expected to find: " + '**Pattern B: Shared Project (< 3 services, single team)** — one project with `Environment` tags (production/staging/dev). Simpler setup; outgrow when alert noise exceeds one team.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/saas-packs/sentry-pack/skills/sentry-reference-architecture/SKILL.md')
    assert '**HTTP (automatic):** SDK v8 auto-propagates `sentry-trace` + `baggage` headers on fetch/http. All services in the same org link automatically.' in text, "expected to find: " + '**HTTP (automatic):** SDK v8 auto-propagates `sentry-trace` + `baggage` headers on fetch/http. All services in the same org link automatically.'[:80]

