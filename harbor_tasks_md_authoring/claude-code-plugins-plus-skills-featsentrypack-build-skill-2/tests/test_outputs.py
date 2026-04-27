"""Behavioral checks for claude-code-plugins-plus-skills-featsentrypack-build-skill-2 (markdown_authoring task).

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
    text = _read('plugins/saas-packs/sentry-pack/skills/sentry-incident-runbook/SKILL.md')
    assert 'An alert fires: `PaymentProcessingError` with 200 events in 5 minutes. Triage reveals crash-free rate dropped to 91%. Breadcrumbs show the Stripe webhook handler receiving malformed payloads after a S' in text, "expected to find: " + 'An alert fires: `PaymentProcessingError` with 200 events in 5 minutes. Triage reveals crash-free rate dropped to 91%. Breadcrumbs show the Stripe webhook handler receiving malformed payloads after a S'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/saas-packs/sentry-pack/skills/sentry-incident-runbook/SKILL.md')
    assert 'A `TypeError: Cannot read properties of undefined` appears immediately after a release tagged `v2.4.1`. First Seen matches the deploy timestamp. Stack trace points to a renamed API response field. Sus' in text, "expected to find: " + 'A `TypeError: Cannot read properties of undefined` appears immediately after a release tagged `v2.4.1`. First Seen matches the deploy timestamp. Stack trace points to a renamed API response field. Sus'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/saas-packs/sentry-pack/skills/sentry-incident-runbook/SKILL.md')
    assert 'Sentry shows `ServiceUnavailableError` affecting 40 users/hour. Discover query reveals `count()` = 180, `count_unique(user)` = 40, `p95(transaction.duration)` = 8200ms. Breadcrumbs show the third-part' in text, "expected to find: " + 'Sentry shows `ServiceUnavailableError` affecting 40 users/hour. Discover query reveals `count()` = 180, `count_unique(user)` = 40, `p95(transaction.duration)` = 8200ms. Breadcrumbs show the third-part'[:80]

