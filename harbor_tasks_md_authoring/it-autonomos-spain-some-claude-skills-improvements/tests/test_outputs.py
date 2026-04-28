"""Behavioral checks for it-autonomos-spain-some-claude-skills-improvements (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/it-autonomos-spain")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/tests-local-run-local-tests/SKILL.md')
    assert '.claude/skills/tests-local-run-local-tests/SKILL.md' in text, "expected to find: " + '.claude/skills/tests-local-run-local-tests/SKILL.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/tests-local-test-and-update-internal-links/SKILL.md')
    assert 'grep -oE \'id="[^"]+"\' HTML_FILE | sed \'s/id="//;s/"$//\' | grep -v -E \'(-contact-form|^hs-script-loader$|^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$)\' | sort -u' in text, "expected to find: " + 'grep -oE \'id="[^"]+"\' HTML_FILE | sed \'s/id="//;s/"$//\' | grep -v -E \'(-contact-form|^hs-script-loader$|^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$)\' | sort -u'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/tests-local-test-and-update-internal-links/SKILL.md')
    assert '| `*-contact-form*` | Contact form element IDs (including language-suffixed variants like `-contact-form-en`) |' in text, "expected to find: " + '| `*-contact-form*` | Contact form element IDs (including language-suffixed variants like `-contact-form-en`) |'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/tests-local-test-local-site-links/SKILL.md')
    assert '.claude/skills/tests-local-test-local-site-links/SKILL.md' in text, "expected to find: " + '.claude/skills/tests-local-test-local-site-links/SKILL.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/tests-prod-run-prod-tests/SKILL.md')
    assert '.claude/skills/tests-prod-run-prod-tests/SKILL.md' in text, "expected to find: " + '.claude/skills/tests-prod-run-prod-tests/SKILL.md'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/tests-prod-test-bitly-links/SKILL.md')
    assert '.claude/skills/tests-prod-test-bitly-links/SKILL.md' in text, "expected to find: " + '.claude/skills/tests-prod-test-bitly-links/SKILL.md'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/tests-prod-test-prod-site-links/SKILL.md')
    assert '.claude/skills/tests-prod-test-prod-site-links/SKILL.md' in text, "expected to find: " + '.claude/skills/tests-prod-test-prod-site-links/SKILL.md'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/tests-run-all-tests/SKILL.md')
    assert '.claude/skills/tests-run-all-tests/SKILL.md' in text, "expected to find: " + '.claude/skills/tests-run-all-tests/SKILL.md'[:80]

