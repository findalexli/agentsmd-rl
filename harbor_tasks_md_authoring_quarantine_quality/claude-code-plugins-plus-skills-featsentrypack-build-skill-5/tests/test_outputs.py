"""Behavioral checks for claude-code-plugins-plus-skills-featsentrypack-build-skill-5 (markdown_authoring task).

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
    text = _read('plugins/saas-packs/sentry-pack/skills/sentry-error-capture/SKILL.md')
    assert 'Capture errors and enrich them with structured context so your team can diagnose production issues in seconds instead of hours. Covers `captureException`, `captureMessage`, scoped context (`withScope`' in text, "expected to find: " + 'Capture errors and enrich them with structured context so your team can diagnose production issues in seconds instead of hours. Covers `captureException`, `captureMessage`, scoped context (`withScope`'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/saas-packs/sentry-pack/skills/sentry-error-capture/SKILL.md')
    assert "Override Sentry's default grouping to control how errors are merged into issues. Without custom fingerprints, Sentry groups by stack trace, which can split logically identical errors or merge unrelate" in text, "expected to find: " + "Override Sentry's default grouping to control how errors are merged into issues. Without custom fingerprints, Sentry groups by stack trace, which can split logically identical errors or merge unrelate"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/saas-packs/sentry-pack/skills/sentry-error-capture/SKILL.md')
    assert 'Use `withScope` (TypeScript) or `push_scope` (Python) to attach context to a single event without polluting the global scope. Context is automatically cleaned up when the scope exits.' in text, "expected to find: " + 'Use `withScope` (TypeScript) or `push_scope` (Python) to attach context to a single event without polluting the global scope. Context is automatically cleaned up when the scope exits.'[:80]

