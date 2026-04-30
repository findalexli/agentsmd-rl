"""Behavioral checks for antigravity-awesome-skills-feat-add-progressivewebapp-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-awesome-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/progressive-web-app/SKILL.md')
    assert 'description: "Build Progressive Web Apps (PWAs) with offline support, installability, and caching strategies. Trigger whenever the user mentions PWA, service workers, web app manifests, Workbox, \'add ' in text, "expected to find: " + 'description: "Build Progressive Web Apps (PWAs) with offline support, installability, and caching strategies. Trigger whenever the user mentions PWA, service workers, web app manifests, Workbox, \'add '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/progressive-web-app/SKILL.md')
    assert "For production apps, consider [Workbox](https://developer.chrome.com/docs/workbox) (Google's PWA library) instead of hand-rolling strategies. It handles edge cases, cache expiry, and versioning automa" in text, "expected to find: " + "For production apps, consider [Workbox](https://developer.chrome.com/docs/workbox) (Google's PWA library) instead of hand-rolling strategies. It handles edge cases, cache expiry, and versioning automa"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/progressive-web-app/SKILL.md')
    assert 'A Progressive Web App is a web application that uses modern browser capabilities to deliver a fast, reliable, and installable experience — even on unreliable networks. The three required pillars are:' in text, "expected to find: " + 'A Progressive Web App is a web application that uses modern browser capabilities to deliver a fast, reliable, and installable experience — even on unreliable networks. The three required pillars are:'[:80]

