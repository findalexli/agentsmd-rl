"""Behavioral checks for qtpass-chore-add-claude-code-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/qtpass")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/qtpass-docs/SKILL.md')
    assert 'See [qtpass-localization](../qtpass-localization/SKILL.md) skill for comprehensive guide.' in text, "expected to find: " + 'See [qtpass-localization](../qtpass-localization/SKILL.md) skill for comprehensive guide.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/qtpass-docs/SKILL.md')
    assert 'description: Documentation guide for QtPass - README, FAQ, localization' in text, "expected to find: " + 'description: Documentation guide for QtPass - README, FAQ, localization'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/qtpass-docs/SKILL.md')
    assert '| File               | Purpose                                     |' in text, "expected to find: " + '| File               | Purpose                                     |'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/qtpass-fixing/SKILL.md')
    assert 'This enables clangd/LSP to provide accurate completions and catch real issues. Without it, the LSP shows false positives about missing Qt headers.' in text, "expected to find: " + 'This enables clangd/LSP to provide accurate completions and catch real issues. Without it, the LSP shows false positives about missing Qt headers.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/qtpass-fixing/SKILL.md')
    assert 'When showing an error dialog followed by `reject()` in a constructor, add `return` to prevent the constructor from continuing with invalid state:' in text, "expected to find: " + 'When showing an error dialog followed by `reject()` in a constructor, add `return` to prevent the constructor from continuing with invalid state:'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/qtpass-fixing/SKILL.md')
    assert '**Note:** LSP suggestions are just that - suggestions. Always verify the fix makes sense before applying, especially for complex refactoring.' in text, "expected to find: " + '**Note:** LSP suggestions are just that - suggestions. Always verify the fix makes sense before applying, especially for complex refactoring.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/qtpass-github/SKILL.md')
    assert 'gh api graphql -f query=\'{ repository(owner: "OWNER", name: "REPO") { pullRequest(number: N) { id reviewThreads(first: 20) { nodes { id isResolved } } } } }\' | jq -r \'.data.repository.pullRequest.revi' in text, "expected to find: " + 'gh api graphql -f query=\'{ repository(owner: "OWNER", name: "REPO") { pullRequest(number: N) { id reviewThreads(first: 20) { nodes { id isResolved } } } } }\' | jq -r \'.data.repository.pullRequest.revi'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/qtpass-github/SKILL.md')
    assert 'gh api "repos/OWNER/REPO/pulls/N/reviews" -X POST -f "body"="All issues addressed in recent commits" -f "event"="COMMENT"' in text, "expected to find: " + 'gh api "repos/OWNER/REPO/pulls/N/reviews" -X POST -f "body"="All issues addressed in recent commits" -f "event"="COMMENT"'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/qtpass-github/SKILL.md')
    assert 'gh api graphql -f query="mutation { resolveReviewThread(input: {threadId: \\"$THREAD_ID\\"}) { thread { isResolved } } }"' in text, "expected to find: " + 'gh api graphql -f query="mutation { resolveReviewThread(input: {threadId: \\"$THREAD_ID\\"}) { thread { isResolved } } }"'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/qtpass-linting/SKILL.md')
    assert 'For proper code completion and analysis in editors like Visual Studio Code with clangd, generate `compile_commands.json`:' in text, "expected to find: " + 'For proper code completion and analysis in editors like Visual Studio Code with clangd, generate `compile_commands.json`:'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/qtpass-linting/SKILL.md')
    assert 'The `install-qt-action` may fail in local act due to missing downloads. This is expected - real CI works fine.' in text, "expected to find: " + 'The `install-qt-action` may fail in local act due to missing downloads. This is expected - real CI works fine.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/qtpass-linting/SKILL.md')
    assert '**Note:** Prettier catches most issues. act is recommended but may fail on new branches (see below).' in text, "expected to find: " + '**Note:** Prettier catches most issues. act is recommended but may fail on new branches (see below).'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/qtpass-localization/SKILL.md')
    assert 'Currently includes: af_ZA, ar_MA, bg_BG, ca_ES, cs_CZ, cy_GB, da_DK, de_DE, de_LU, el_GR, en_GB, en_US, es_ES, et_EE, fi_FI, fr_BE, fr_FR, fr_LU, gl_ES, he_IL, hr_HR, hu_HU, it_IT, ja_JP, ko_KR, lb_LU' in text, "expected to find: " + 'Currently includes: af_ZA, ar_MA, bg_BG, ca_ES, cs_CZ, cy_GB, da_DK, de_DE, de_LU, el_GR, en_GB, en_US, es_ES, et_EE, fi_FI, fr_BE, fr_FR, fr_LU, gl_ES, he_IL, hr_HR, hu_HU, it_IT, ja_JP, ko_KR, lb_LU'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/qtpass-localization/SKILL.md')
    assert "QtPass uses Weblate for translations. Don't manually edit `.ts` files for translations - let Weblate handle it. Only run `qmake6` locally to update source references." in text, "expected to find: " + "QtPass uses Weblate for translations. Don't manually edit `.ts` files for translations - let Weblate handle it. Only run `qmake6` locally to update source references."[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/qtpass-localization/SKILL.md')
    assert 'When source strings change, translations are marked "unfinished" but may still appear correct. Always check:' in text, "expected to find: " + 'When source strings change, translations are marked "unfinished" but may still appear correct. Always check:'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/qtpass-releasing/SKILL.md')
    assert 'For scripts that modify remote state (uploading releases, signing files), add a `--dryrun` flag to enable testing without making changes:' in text, "expected to find: " + 'For scripts that modify remote state (uploading releases, signing files), add a `--dryrun` flag to enable testing without making changes:'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/qtpass-releasing/SKILL.md')
    assert 'When iterating over files matched by a glob pattern, use array assignment to handle the case where no files match:' in text, "expected to find: " + 'When iterating over files matched by a glob pattern, use array assignment to handle the case where no files match:'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/qtpass-releasing/SKILL.md')
    assert "**NOTE:** `qtpass.appdata.xml` and `appdmg.json` don't have version fields to update." in text, "expected to find: " + "**NOTE:** `qtpass.appdata.xml` and `appdmg.json` don't have version fields to update."[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/qtpass-testing/SKILL.md')
    assert "Tests that modify QtPass settings can pollute the user's live config. This is especially problematic on Windows where settings use the registry." in text, "expected to find: " + "Tests that modify QtPass settings can pollute the user's live config. This is especially problematic on Windows where settings use the registry."[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/qtpass-testing/SKILL.md')
    assert 'Windows uses backslashes (`\\`) while Unix uses forward slashes (`/`). When comparing paths, use `QDir::cleanPath()` to normalize:' in text, "expected to find: " + 'Windows uses backslashes (`\\`) while Unix uses forward slashes (`/`). When comparing paths, use `QDir::cleanPath()` to normalize:'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/qtpass-testing/SKILL.md')
    assert "Data-driven tests work well for simple bool/int/string settings. Compound types like `PasswordConfiguration` often don't fit:" in text, "expected to find: " + "Data-driven tests work well for simple bool/int/string settings. Compound types like `PasswordConfiguration` often don't fit:"[:80]

