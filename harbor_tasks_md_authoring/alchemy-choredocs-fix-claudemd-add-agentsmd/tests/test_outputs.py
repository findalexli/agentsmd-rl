"""Behavioral checks for alchemy-choredocs-fix-claudemd-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/alchemy")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '> If the Resource is mostly headless infrastructure like a database or some other service, you should use Cloudflare Workers as the runtime to "round off" the example package e.g. for a Neon Provider,' in text, "expected to find: " + '> If the Resource is mostly headless infrastructure like a database or some other service, you should use Cloudflare Workers as the runtime to "round off" the example package e.g. for a Neon Provider,'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '> In these cases, you should instead opt to represent this as `{resource}: string | {Resource}`, e.g. `table: string | Table`. This "lifts" the Resource into the Alchemy abstraction without sacrificin' in text, "expected to find: " + '> In these cases, you should instead opt to represent this as `{resource}: string | {Resource}`, e.g. `table: string | Table`. This "lifts" the Resource into the Alchemy abstraction without sacrificin'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'When submitting a Pull Request with a change, always include a code snippet that shows how the new feature/fix is used. It is not enough to just describe it with text and bullet points.' in text, "expected to find: " + 'When submitting a Pull Request with a change, always include a code snippet that shows how the new feature/fix is used. It is not enough to just describe it with text and bullet points.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '> If the Resource is mostly headless infrastructure like a database or some other service, you should use Cloudflare Workers as the runtime to "round off" the example package e.g. for a Neon Provider,' in text, "expected to find: " + '> If the Resource is mostly headless infrastructure like a database or some other service, you should use Cloudflare Workers as the runtime to "round off" the example package e.g. for a Neon Provider,'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '> In these cases, you should instead opt to represent this as `{resource}: string | {Resource}`, e.g. `table: string | Table`. This "lifts" the Resource into the Alchemy abstraction without sacrificin' in text, "expected to find: " + '> In these cases, you should instead opt to represent this as `{resource}: string | {Resource}`, e.g. `table: string | Table`. This "lifts" the Resource into the Alchemy abstraction without sacrificin'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Please provide a comprehensive document of all the Resources for this provider with relevant links to documentation. This is effectively the design and internal documentation.' in text, "expected to find: " + 'Please provide a comprehensive document of all the Resources for this provider with relevant links to documentation. This is effectively the design and internal documentation.'[:80]

