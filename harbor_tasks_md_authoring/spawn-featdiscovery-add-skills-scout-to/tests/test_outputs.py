"""Behavioral checks for spawn-featdiscovery-add-skills-scout-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/spawn")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/discovery.md')
    assert 'Research and maintain the `skills` section of `manifest.json`. Skills are agent-specific capabilities pre-installed on VMs via `--beta skills`.' in text, "expected to find: " + 'Research and maintain the `skills` section of `manifest.json`. Skills are agent-specific capabilities pre-installed on VMs via `--beta skills`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/discovery.md')
    assert '- **Agent configs** — native config files unlocking agent features (Cursor rules, OpenClaw SOUL.md)' in text, "expected to find: " + '- **Agent configs** — native config files unlocking agent features (Cursor rules, OpenClaw SOUL.md)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/discovery.md')
    assert '1. Verify the npm package exists and starts: `npm view PACKAGE version && timeout 5 npx -y PACKAGE`' in text, "expected to find: " + '1. Verify the npm package exists and starts: `npm view PACKAGE version && timeout 5 npx -y PACKAGE`'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/discovery-team-prompt.md')
    assert 'Research the best skills, MCP servers, and agent-specific configurations for each agent in manifest.json.' in text, "expected to find: " + 'Research the best skills, MCP servers, and agent-specific configurations for each agent in manifest.json.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/discovery-team-prompt.md')
    assert '2. **Popular community skills** — search GitHub for `awesome-{agent}`, `{agent}-skills`, `{agent}-rules`' in text, "expected to find: " + '2. **Popular community skills** — search GitHub for `awesome-{agent}`, `{agent}-skills`, `{agent}-rules`'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/setup-agent-team/discovery-team-prompt.md')
    assert '- Chrome/Chromium for Playwright (`npx playwright install chromium && npx playwright install-deps`)' in text, "expected to find: " + '- Chrome/Chromium for Playwright (`npx playwright install chromium && npx playwright install-deps`)'[:80]

