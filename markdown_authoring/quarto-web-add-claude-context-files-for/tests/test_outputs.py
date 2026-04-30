"""Behavioral checks for quarto-web-add-claude-context-files-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/quarto-web")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/docs-authoring.md')
    assert 'Shows a pre-release callout before X.Y ships, disappears automatically after — never remove them manually. For blog posts use `type="blog"`. For URLs use `{{< prerelease-docs-url X.Y >}}`. See `_exten' in text, "expected to find: " + 'Shows a pre-release callout before X.Y ships, disappears automatically after — never remove them manually. For blog posts use `type="blog"`. For URLs use `{{< prerelease-docs-url X.Y >}}`. See `_exten'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/docs-authoring.md')
    assert 'When documenting a feature introduced in a specific Quarto version, add at the top of the section:' in text, "expected to find: " + 'When documenting a feature introduced in a specific Quarto version, add at the top of the section:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/docs-authoring.md')
    assert '{{< prerelease-callout X.Y >}}' in text, "expected to find: " + '{{< prerelease-callout X.Y >}}'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('_extensions/prerelease/CLAUDE.md')
    assert 'See `prerelease.lua` for implementation and #1961 for design rationale.' in text, "expected to find: " + 'See `prerelease.lua` for implementation and #1961 for design rationale.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('_extensions/prerelease/CLAUDE.md')
    assert '# Prerelease Extension' in text, "expected to find: " + '# Prerelease Extension'[:80]

