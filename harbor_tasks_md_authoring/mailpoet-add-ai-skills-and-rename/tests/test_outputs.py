"""Behavioral checks for mailpoet-add-ai-skills-and-rename (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mailpoet")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.ai/skills/creating-pull-requests/SKILL.md')
    assert '3. **Check for changelog** — if the branch has user-facing changes and no changelog entry exists yet, use the `writing-changelog` skill to create one before proceeding' in text, "expected to find: " + '3. **Check for changelog** — if the branch has user-facing changes and no changelog entry exists yet, use the `writing-changelog` skill to create one before proceeding'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.ai/skills/creating-pull-requests/SKILL.md')
    assert '| Missing changelog entry            | Check for changelog before creating the PR. Use the `writing-changelog` skill       |' in text, "expected to find: " + '| Missing changelog entry            | Check for changelog before creating the PR. Use the `writing-changelog` skill       |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.ai/skills/creating-pull-requests/SKILL.md')
    assert '5. **Follow template sections exactly** - Not all sections are mandatory, use `_N/A_` for non-applicable ones' in text, "expected to find: " + '5. **Follow template sections exactly** - Not all sections are mandatory, use `_N/A_` for non-applicable ones'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.ai/skills/writing-changelog/SKILL.md')
    assert 'User-facing changes MUST have a changelog entry. Each entry is a small Markdown file created by the `./do changelog:add` command. Follow the steps below in order.' in text, "expected to find: " + 'User-facing changes MUST have a changelog entry. Each entry is a small Markdown file created by the `./do changelog:add` command. Follow the steps below in order.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.ai/skills/writing-changelog/SKILL.md')
    assert "description: 'Use when adding a changelog entry for a branch. Use after completing work on a feature, fix, or improvement that is user-facing.'" in text, "expected to find: " + "description: 'Use when adding a changelog entry for a branch. Use after completing work on a feature, fix, or improvement that is user-facing.'"[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.ai/skills/writing-changelog/SKILL.md')
    assert 'Pick **one** valid type that best describes the change: `Added`, `Improved`, `Fixed`, `Changed`, `Updated`, `Removed`' in text, "expected to find: " + 'Pick **one** valid type that best describes the change: `Added`, `Improved`, `Fixed`, `Changed`, `Updated`, `Removed`'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**CRITICAL:** `lib/WP/Functions.php` wraps WordPress functions for testability. MUST use `$this->wp->functionName()` (or the injected `WPFunctions` service) instead of calling WordPress functions like' in text, "expected to find: " + '**CRITICAL:** `lib/WP/Functions.php` wraps WordPress functions for testability. MUST use `$this->wp->functionName()` (or the injected `WPFunctions` service) instead of calling WordPress functions like'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Third-party PHP dependencies are prefixed with `MailPoetVendor\\` namespace and stored in `vendor-prefixed/`. This prevents conflicts with other plugins that may include the same libraries. NEVER edit ' in text, "expected to find: " + 'Third-party PHP dependencies are prefixed with `MailPoetVendor\\` namespace and stored in `vendor-prefixed/`. This prevents conflicts with other plugins that may include the same libraries. NEVER edit '[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'MailPoet is a WordPress email marketing plugin that lets users create, send, and manage newsletters and automated emails from the WordPress dashboard. It integrates deeply with WordPress and WooCommer' in text, "expected to find: " + 'MailPoet is a WordPress email marketing plugin that lets users create, send, and manage newsletters and automated emails from the WordPress dashboard. It integrates deeply with WordPress and WooCommer'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

