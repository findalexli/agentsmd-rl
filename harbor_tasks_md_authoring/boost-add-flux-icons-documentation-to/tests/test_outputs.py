"""Behavioral checks for boost-add-flux-icons-documentation-to (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/boost")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.ai/fluxui-free/skill/fluxui-development/SKILL.md')
    assert 'Flux includes [Heroicons](https://heroicons.com/) as its default icon set. Search for exact icon names on the Heroicons site - do not guess or invent icon names.' in text, "expected to find: " + 'Flux includes [Heroicons](https://heroicons.com/) as its default icon set. Search for exact icon names on the Heroicons site - do not guess or invent icon names.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.ai/fluxui-free/skill/fluxui-development/SKILL.md')
    assert 'For icons not available in Heroicons, use [Lucide](https://lucide.dev/). Import the icons you need with the Artisan command:' in text, "expected to find: " + 'For icons not available in Heroicons, use [Lucide](https://lucide.dev/). Import the icons you need with the Artisan command:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.ai/fluxui-free/skill/fluxui-development/SKILL.md')
    assert '<flux:button icon="arrow-down-tray">Export</flux:button>' in text, "expected to find: " + '<flux:button icon="arrow-down-tray">Export</flux:button>'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.ai/fluxui-pro/skill/fluxui-development/SKILL.md')
    assert 'Flux includes [Heroicons](https://heroicons.com/) as its default icon set. Search for exact icon names on the Heroicons site - do not guess or invent icon names.' in text, "expected to find: " + 'Flux includes [Heroicons](https://heroicons.com/) as its default icon set. Search for exact icon names on the Heroicons site - do not guess or invent icon names.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.ai/fluxui-pro/skill/fluxui-development/SKILL.md')
    assert 'For icons not available in Heroicons, use [Lucide](https://lucide.dev/). Import the icons you need with the Artisan command:' in text, "expected to find: " + 'For icons not available in Heroicons, use [Lucide](https://lucide.dev/). Import the icons you need with the Artisan command:'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.ai/fluxui-pro/skill/fluxui-development/SKILL.md')
    assert '<flux:button icon="arrow-down-tray">Export</flux:button>' in text, "expected to find: " + '<flux:button icon="arrow-down-tray">Export</flux:button>'[:80]

