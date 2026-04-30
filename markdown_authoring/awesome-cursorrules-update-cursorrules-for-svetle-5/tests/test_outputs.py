"""Behavioral checks for awesome-cursorrules-update-cursorrules-for-svetle-5 (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/awesome-cursorrules")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('rules/svelte-5-vs-svelte-4-cursorrules-prompt-file/.cursorrules')
    assert 'In Svelte 5, event handlers are treated as standard HTML properties rather than Svelte-specific directives, simplifying their use and integrating them more closely with the rest of the properties in t' in text, "expected to find: " + 'In Svelte 5, event handlers are treated as standard HTML properties rather than Svelte-specific directives, simplifying their use and integrating them more closely with the rest of the properties in t'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('rules/svelte-5-vs-svelte-4-cursorrules-prompt-file/.cursorrules')
    assert "This creates clearer, more maintainable components compared to Svelte 4's previous syntax by making reactivity explicit and using standardized web platform features." in text, "expected to find: " + "This creates clearer, more maintainable components compared to Svelte 4's previous syntax by making reactivity explicit and using standardized web platform features."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('rules/svelte-5-vs-svelte-4-cursorrules-prompt-file/.cursorrules')
    assert "- All runes must be imported from 'svelte': `import { $state, $effect, $derived, $props, $slots } from 'svelte';`" in text, "expected to find: " + "- All runes must be imported from 'svelte': `import { $state, $effect, $derived, $props, $slots } from 'svelte';`"[:80]

