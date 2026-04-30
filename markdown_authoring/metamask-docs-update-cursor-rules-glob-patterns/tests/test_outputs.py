"""Behavioral checks for metamask-docs-update-cursor-rules-glob-patterns (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/metamask-docs")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/content-types.mdc')
    assert 'globs: **/*.md,**/*.mdx' in text, "expected to find: " + 'globs: **/*.md,**/*.mdx'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/editorial-voice.mdc')
    assert '- Do not use em dashes (—) to set off extra information. Use commas, parentheses, semicolons, or rephrase the sentence.' in text, "expected to find: " + '- Do not use em dashes (—) to set off extra information. Use commas, parentheses, semicolons, or rephrase the sentence.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/editorial-voice.mdc')
    assert '- For emphasis in exceptional cases such as critical security warnings when an admonition is not enough.' in text, "expected to find: " + '- For emphasis in exceptional cases such as critical security warnings when an admonition is not enough.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/editorial-voice.mdc')
    assert '- In general, do not use bold to emphasize words in a paragraph. Use bold sparingly:' in text, "expected to find: " + '- In general, do not use bold to emphasize words in a paragraph. Use bold sparingly:'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/markdown-formatting.mdc')
    assert 'globs: **/*.md,**/*.mdx' in text, "expected to find: " + 'globs: **/*.md,**/*.mdx'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/product-embedded-wallets.mdc')
    assert 'globs: embedded-wallets/**/*.md,embedded-wallets/**/*.mdx' in text, "expected to find: " + 'globs: embedded-wallets/**/*.md,embedded-wallets/**/*.mdx'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/product-metamask-connect.mdc')
    assert 'globs: metamask-connect/**/*.md,metamask-connect/**/*.mdx' in text, "expected to find: " + 'globs: metamask-connect/**/*.md,metamask-connect/**/*.mdx'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/product-services.mdc')
    assert 'globs: services/**/*.md,services/**/*.mdx' in text, "expected to find: " + 'globs: services/**/*.md,services/**/*.mdx'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/product-smart-accounts-kit.mdc')
    assert 'globs: smart-accounts-kit/**/*.md,smart-accounts-kit/**/*.mdx,src/lib/glossary.json' in text, "expected to find: " + 'globs: smart-accounts-kit/**/*.md,smart-accounts-kit/**/*.mdx,src/lib/glossary.json'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/product-snaps.mdc')
    assert 'globs: snaps/**/*.md,snaps/**/*.mdx' in text, "expected to find: " + 'globs: snaps/**/*.md,snaps/**/*.mdx'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/terminology.mdc')
    assert 'globs: **/*.md,**/*.mdx' in text, "expected to find: " + 'globs: **/*.md,**/*.mdx'[:80]

