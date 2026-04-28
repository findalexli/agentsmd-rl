"""Behavioral checks for stripe-react-native-rework-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/stripe-react-native")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-native-feature/SKILL.md')
    assert 'This guide explains how to add new features that require communication between React Native (JavaScript) and native code (iOS/Android). Use this when adding new native functionality, payment methods, ' in text, "expected to find: " + 'This guide explains how to add new features that require communication between React Native (JavaScript) and native code (iOS/Android). Use this when adding new native functionality, payment methods, '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-native-feature/SKILL.md')
    assert 'when_to_use: Use when adding new native functionality, payment methods, extending components with platform-specific capabilities, implementing native-to-JS event communication, or adding new parameter' in text, "expected to find: " + 'when_to_use: Use when adding new native functionality, payment methods, extending components with platform-specific capabilities, implementing native-to-JS event communication, or adding new parameter'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add-native-feature/SKILL.md')
    assert 'description: Step-by-step guide for adding features requiring JS-to-native bridge communication in the Stripe React Native SDK. Covers TypeScript types, Android Kotlin, iOS Swift, event emitters, bidi' in text, "expected to find: " + 'description: Step-by-step guide for adding features requiring JS-to-native bridge communication in the Stripe React Native SDK. Covers TypeScript types, Android Kotlin, iOS Swift, event emitters, bidi'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'When searching issues, always use `--state all` to include closed/resolved issues. Check GitHub issues for similar problems before investigating user reports.' in text, "expected to find: " + 'When searching issues, always use `--state all` to include closed/resolved issues. Check GitHub issues for similar problems before investigating user reports.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "IMPORTANT: Always set `GH_HOST=github.com` for all `gh` commands. Without it, `gh` defaults to Stripe's GHE instance." in text, "expected to find: " + "IMPORTANT: Always set `GH_HOST=github.com` for all `gh` commands. Without it, `gh` defaults to Stripe's GHE instance."[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Example: `GH_HOST=github.com gh pr create --repo stripe/stripe-react-native --title [...]`' in text, "expected to find: " + 'Example: `GH_HOST=github.com gh pr create --repo stripe/stripe-react-native --title [...]`'[:80]

