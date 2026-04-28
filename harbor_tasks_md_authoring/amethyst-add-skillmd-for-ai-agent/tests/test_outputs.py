"""Behavioral checks for amethyst-add-skillmd-for-ai-agent (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/amethyst")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '[Amethyst](https://github.com/vitorpamplona/amethyst) is the premier Nostr client for Android. This skill enables you to:' in text, "expected to find: " + '[Amethyst](https://github.com/vitorpamplona/amethyst) is the premier Nostr client for Android. This skill enables you to:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert 'Edit relay configuration in `quartz/src/main/java/com/vitorpamplona/quartz/nip01Core/relay/` or the UI settings files.' in text, "expected to find: " + 'Edit relay configuration in `quartz/src/main/java/com/vitorpamplona/quartz/nip01Core/relay/` or the UI settings files.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '**⚠️ CRITICAL:** The Google Services plugin fails when you change the package name. For F-Droid builds, disable it.' in text, "expected to find: " + '**⚠️ CRITICAL:** The Google Services plugin fails when you change the package name. For F-Droid builds, disable it.'[:80]

