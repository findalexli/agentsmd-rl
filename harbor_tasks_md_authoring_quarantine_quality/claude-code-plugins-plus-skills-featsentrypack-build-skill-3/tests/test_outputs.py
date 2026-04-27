"""Behavioral checks for claude-code-plugins-plus-skills-featsentrypack-build-skill-3 (markdown_authoring task).

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
    text = _read('plugins/saas-packs/sentry-pack/skills/sentry-local-dev-loop/SKILL.md')
    assert 'Configure Sentry for local development with environment-aware DSN routing, debug-mode verbosity, full-capture sample rates, `beforeSend` inspection, Sentry Spotlight for offline event viewing, and `se' in text, "expected to find: " + 'Configure Sentry for local development with environment-aware DSN routing, debug-mode verbosity, full-capture sample rates, `beforeSend` inspection, Sentry Spotlight for offline event viewing, and `se'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/saas-packs/sentry-pack/skills/sentry-local-dev-loop/SKILL.md')
    assert "The `spotlight: true` option in Step 1's `Sentry.init()` routes events to the local sidecar. This gives you a full Sentry-style event viewer without sending anything to `sentry.io`." in text, "expected to find: " + "The `spotlight: true` option in Step 1's `Sentry.init()` routes events to the local sidecar. This gives you a full Sentry-style event viewer without sending anything to `sentry.io`."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/saas-packs/sentry-pack/skills/sentry-local-dev-loop/SKILL.md')
    assert "Sentry Spotlight runs a local sidecar that intercepts Sentry events and displays them in a browser UI at `http://localhost:8969` (Spotlight's default port) — no network required:" in text, "expected to find: " + "Sentry Spotlight runs a local sidecar that intercepts Sentry events and displays them in a browser UI at `http://localhost:8969` (Spotlight's default port) — no network required:"[:80]

