"""Behavioral checks for claude-code-templates-feat-add-scoped-clauderules-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-code-templates")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/cli-tool.md')
    assert 'This is the npm package `claude-code-templates`. A Node.js CLI for installing Claude Code components.' in text, "expected to find: " + 'This is the npm package `claude-code-templates`. A Node.js CLI for installing Claude Code components.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/cli-tool.md')
    assert 'Always check `npm view claude-code-templates version` before publishing to avoid version conflicts.' in text, "expected to find: " + 'Always check `npm view claude-code-templates version` before publishing to avoid version conflicts.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/cli-tool.md')
    assert '1. Run `python scripts/generate_components_json.py` to regenerate catalog' in text, "expected to find: " + '1. Run `python scripts/generate_components_json.py` to regenerate catalog'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/cloudflare.md')
    assert '- **pulse**: Weekly KPI report (GitHub, Discord, Supabase, Vercel, GA) every Sunday 14:00 UTC via Telegram' in text, "expected to find: " + '- **pulse**: Weekly KPI report (GitHub, Discord, Supabase, Vercel, GA) every Sunday 14:00 UTC via Telegram'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/cloudflare.md')
    assert '- **docs-monitor**: Monitors code.claude.com/docs changes hourly, sends Telegram notifications' in text, "expected to find: " + '- **docs-monitor**: Monitors code.claude.com/docs changes hourly, sends Telegram notifications'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/cloudflare.md')
    assert '- Secrets managed via Cloudflare dashboard / `wrangler secret put`' in text, "expected to find: " + '- Secrets managed via Cloudflare dashboard / `wrangler secret put`'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/dashboard.md')
    assert 'Always use the `deployer` agent. Never deploy manually. Node pinned to 22.x (v24 breaks Vercel builds).' in text, "expected to find: " + 'Always use the `deployer` agent. Never deploy manually. Node pinned to 22.x (v24 breaks Vercel builds).'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/dashboard.md')
    assert 'Astro 5 + React islands + Tailwind v4 application. Single Vercel project serving both domains.' in text, "expected to find: " + 'Astro 5 + React islands + Tailwind v4 application. Single Vercel project serving both domains.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/dashboard.md')
    assert '- `dashboard/src/lib/constants.ts` — `FEATURED_ITEMS` array (metadata, install command, links)' in text, "expected to find: " + '- `dashboard/src/lib/constants.ts` — `FEATURED_ITEMS` array (metadata, install command, links)'[:80]

