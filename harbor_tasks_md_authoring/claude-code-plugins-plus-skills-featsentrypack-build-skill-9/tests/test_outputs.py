"""Behavioral checks for claude-code-plugins-plus-skills-featsentrypack-build-skill-9 (markdown_authoring task).

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
    text = _read('plugins/saas-packs/sentry-pack/skills/sentry-rate-limits/SKILL.md')
    assert 'Manage Sentry rate limits, sampling strategies, and quota usage to control costs without losing visibility into critical errors. Covers client-side sampling, `beforeSend` filtering, server-side inboun' in text, "expected to find: " + 'Manage Sentry rate limits, sampling strategies, and quota usage to control costs without losing visibility into critical errors. Covers client-side sampling, `beforeSend` filtering, server-side inboun'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/saas-packs/sentry-pack/skills/sentry-rate-limits/SKILL.md')
    assert 'When your project exceeds its quota, Sentry returns `429 Too Many Requests` with a `Retry-After` header. The SDK automatically stops sending events until the cooldown expires. Events generated during ' in text, "expected to find: " + 'When your project exceeds its quota, Sentry returns `429 Too Many Requests` with a `Retry-After` header. The SDK automatically stops sending events until the cooldown expires. Events generated during '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/saas-packs/sentry-pack/skills/sentry-rate-limits/SKILL.md')
    assert 'Spike protection is auto-enabled on Team and Business plans. It detects sudden event volume increases and temporarily rate-limits the project to prevent quota exhaustion from error storms.' in text, "expected to find: " + 'Spike protection is auto-enabled on Team and Business plans. It detects sudden event volume increases and temporarily rate-limits the project to prevent quota exhaustion from error storms.'[:80]

