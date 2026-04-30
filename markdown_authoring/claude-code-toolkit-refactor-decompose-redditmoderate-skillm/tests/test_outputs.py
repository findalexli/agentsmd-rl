"""Behavioral checks for claude-code-toolkit-refactor-decompose-redditmoderate-skillm (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-code-toolkit")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/reddit-moderate/SKILL.md')
    assert '| **Auto** | `/loop 10m /reddit-moderate --auto` | Fetch queue, classify, auto-action high-confidence items, flag rest |' in text, "expected to find: " + '| **Auto** | `/loop 10m /reddit-moderate --auto` | Fetch queue, classify, auto-action high-confidence items, flag rest |'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/reddit-moderate/SKILL.md')
    assert '| Per-item classification steps, repeat offender check, mass-report detection | `references/classification-prompt.md` |' in text, "expected to find: " + '| Per-item classification steps, repeat offender check, mass-report detection | `references/classification-prompt.md` |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/reddit-moderate/SKILL.md')
    assert '| Prompt template, untrusted content handling, prompt injection defense | `references/classification-prompt.md` |' in text, "expected to find: " + '| Prompt template, untrusted content handling, prompt injection defense | `references/classification-prompt.md` |'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/reddit-moderate/references/classification-prompt.md')
    assert "The classification prompt is the core of reddit-moderate's LLM-powered moderation. It assembles subreddit context (rules, mod log, moderator notes, repeat offenders) with untrusted Reddit content into" in text, "expected to find: " + "The classification prompt is the core of reddit-moderate's LLM-powered moderation. It assembles subreddit context (rules, mod log, moderator notes, repeat offenders) with untrusted Reddit content into"[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/reddit-moderate/references/classification-prompt.md')
    assert '2. **Mass-report detection** (deterministic, not LLM) -- If `num_reports > 10 AND distinct_report_categories >= 3`, flag the item as a `MASS_REPORT_ABUSE` candidate. This heuristic runs before LLM cla' in text, "expected to find: " + '2. **Mass-report detection** (deterministic, not LLM) -- If `num_reports > 10 AND distinct_report_categories >= 3`, flag the item as a `MASS_REPORT_ABUSE` candidate. This heuristic runs before LLM cla'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/reddit-moderate/references/classification-prompt.md')
    assert '> **Scope**: LLM classification prompt template, category definitions, confidence thresholds, action mapping, and per-subreddit config.json format. Does NOT cover workflow phases or script commands.' in text, "expected to find: " + '> **Scope**: LLM classification prompt template, category definitions, confidence thresholds, action mapping, and per-subreddit config.json format. Does NOT cover workflow phases or script commands.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/reddit-moderate/references/context-loading.md')
    assert 'Before classifying any items, the skill loads subreddit-specific context from `reddit-data/{subreddit}/`. This context enables accurate classification by providing rules, historical patterns, communit' in text, "expected to find: " + 'Before classifying any items, the skill loads subreddit-specific context from `reddit-data/{subreddit}/`. This context enables accurate classification by providing rules, historical patterns, communit'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/reddit-moderate/references/context-loading.md')
    assert 'After setup, create or edit `moderator-notes.md` to add community-specific context that automated tools cannot extract (known spam patterns, cultural norms, which accounts are known bad actors).' in text, "expected to find: " + 'After setup, create or edit `moderator-notes.md` to add community-specific context that automated tools cannot extract (known spam patterns, cultural norms, which accounts are known bad actors).'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/reddit-moderate/references/context-loading.md')
    assert '> **Scope**: Subreddit data directory structure, file purposes, setup flow, and context loading sequence. Does NOT cover the classification prompt itself or script command flags.' in text, "expected to find: " + '> **Scope**: Subreddit data directory structure, file purposes, setup flow, and context loading sequence. Does NOT cover the classification prompt itself or script command flags.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/reddit-moderate/references/script-commands.md')
    assert '`reddit_mod.py` is the deterministic backbone of reddit-moderate. It handles Reddit API calls via PRAW, outputs structured data for LLM classification, and executes mod actions. The script never calls' in text, "expected to find: " + '`reddit_mod.py` is the deterministic backbone of reddit-moderate. It handles Reddit API calls via PRAW, outputs structured data for LLM classification, and executes mod actions. The script never calls'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/reddit-moderate/references/script-commands.md')
    assert 'The `--classify` flag on scan builds classification prompts internally (same `build_classification_prompt()` as the classify subcommand). Without `--json`, scan shows a summary with a note to use `--j' in text, "expected to find: " + 'The `--classify` flag on scan builds classification prompts internally (same `build_classification_prompt()` as the classify subcommand). Without `--json`, scan shows a summary with a note to use `--j'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/reddit-moderate/references/script-commands.md')
    assert '> **Scope**: All reddit_mod.py subcommands, flags, usage examples, and exit codes. Does NOT cover classification logic or workflow phases.' in text, "expected to find: " + '> **Scope**: All reddit_mod.py subcommands, flags, usage examples, and exit codes. Does NOT cover classification logic or workflow phases.'[:80]

