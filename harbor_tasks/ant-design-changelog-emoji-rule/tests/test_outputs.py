"""Behavioral tests for ant-design PR #57321 (markdown_authoring task).

The PR:
1. Adds a rule to CLAUDE.md banning multi-emoji stacking on changelog entries.
2. Applies that rule by removing the stacked `♿` from the unreleased changelog
   entry referencing PR #57266 in both English and Chinese changelogs.

Tests use subprocess.run() to perform real file IO checks (greps and parses)
on the ant-design repo at /workspace/ant-design — there is no JS/TS build to
exercise here, only markdown content correctness.
"""

import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/ant-design")
CLAUDE_MD = REPO / "CLAUDE.md"
CHANGELOG_EN = REPO / "CHANGELOG.en-US.md"
CHANGELOG_ZH = REPO / "CHANGELOG.zh-CN.md"


def _read(path: Path) -> str:
    r = subprocess.run(["cat", str(path)], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, f"failed to read {path}: {r.stderr}"
    return r.stdout


def test_claude_md_has_single_emoji_rule():
    """CLAUDE.md must state that each changelog entry uses only one emoji.

    This is the core agent-instruction edit from the PR.
    """
    content = _read(CLAUDE_MD)
    assert "每条 Changelog 仅选择一个 Emoji，不要在同一条目中叠加多个 Emoji。" in content, (
        "CLAUDE.md must contain the new rule forbidding emoji stacking on "
        "changelog entries (the exact Chinese sentence from the PR)."
    )


def test_claude_md_rule_in_changelog_section():
    """The new rule must live inside the Changelog规范 section, not a random spot.

    The PR places it between the Emoji table and the existing 'reference existing
    entries' guidance — i.e. inside the Changelog conventions block.
    """
    content = _read(CLAUDE_MD)
    rule = "每条 Changelog 仅选择一个 Emoji"
    section_marker = "## Changelog 规范"
    assert section_marker in content, f"expected section header {section_marker!r}"
    rule_pos = content.find(rule)
    section_pos = content.find(section_marker)
    assert rule_pos > section_pos, (
        "the single-emoji rule must appear after the '## Changelog 规范' header"
    )
    # And it must precede the next top-level section ("## 参考资源" or similar).
    next_section = re.search(r"\n## (?!Changelog)", content[section_pos + 1 :])
    assert next_section is not None, "expected a section after Changelog 规范"
    next_section_abs = section_pos + 1 + next_section.start()
    assert rule_pos < next_section_abs, (
        "the single-emoji rule must be inside the Changelog 规范 section"
    )


def test_changelog_en_pr_57266_entry_has_single_emoji():
    """In CHANGELOG.en-US.md, the entry for PR #57266 must use exactly one emoji.

    The base commit had `⌨️ ♿`; the PR removes the redundant `♿` to comply with
    the new single-emoji rule.
    """
    content = _read(CHANGELOG_EN)
    lines = [ln for ln in content.splitlines() if "/pull/57266)" in ln]
    assert lines, "expected at least one line referencing pull/57266"
    target = lines[0]
    assert "⌨️" in target, f"expected keyboard emoji in entry, got: {target!r}"
    assert "♿" not in target, (
        "the wheelchair (accessibility) emoji must be removed from the #57266 "
        f"entry; got: {target!r}"
    )


def test_changelog_zh_pr_57266_entry_has_single_emoji():
    """In CHANGELOG.zh-CN.md, the entry for PR #57266 must use exactly one emoji."""
    content = _read(CHANGELOG_ZH)
    lines = [ln for ln in content.splitlines() if "/pull/57266)" in ln]
    assert lines, "expected at least one line referencing pull/57266"
    target = lines[0]
    assert "⌨️" in target, f"expected keyboard emoji in entry, got: {target!r}"
    assert "♿" not in target, (
        "the wheelchair (accessibility) emoji must be removed from the #57266 "
        f"entry; got: {target!r}"
    )


def test_changelog_en_pr_57266_text_unchanged():
    """The body text of the #57266 entry (after the emoji) must match the gold.

    Guards against agents who 'comply' by deleting the entry or rewriting it.
    """
    content = _read(CHANGELOG_EN)
    expected = (
        "- ⌨️ Improve App link `:focus-visible` outline to enhance keyboard "
        "accessibility. [#57266](https://github.com/ant-design/ant-design/pull/57266) "
        "[@ug-hero](https://github.com/ug-hero)"
    )
    assert expected in content, (
        "the English changelog entry for #57266 must match the gold text "
        f"(only the leading emojis change). Expected to find:\n{expected}"
    )


def test_changelog_zh_pr_57266_text_unchanged():
    """The body text of the #57266 entry (Chinese) must match the gold."""
    content = _read(CHANGELOG_ZH)
    expected = (
        "- ⌨️ 优化 App 链接的 `:focus-visible` 外框样式，提升键盘可访问性。"
        "[#57266](https://github.com/ant-design/ant-design/pull/57266) "
        "[@ug-hero](https://github.com/ug-hero)"
    )
    assert expected in content, (
        "the Chinese changelog entry for #57266 must match the gold text "
        f"(only the leading emojis change). Expected to find:\n{expected}"
    )


def test_only_unreleased_section_was_modified():
    """Older (already-released) changelog entries with ♿ must remain unchanged.

    The base commit has multiple older `⌨️ ♿` entries (e.g. #56902, #56521,
    #56716). The PR explicitly preserves them — only entries in the current
    unreleased section (above the first `## ` version header) are cleaned up.

    This test asserts that at least some `⌨️ ♿` lines still exist in the file,
    so an agent that did a wholesale find-and-replace fails.
    """
    en = _read(CHANGELOG_EN)
    zh = _read(CHANGELOG_ZH)
    en_remaining = [ln for ln in en.splitlines() if "⌨️ ♿" in ln]
    zh_remaining = [ln for ln in zh.splitlines() if "⌨️ ♿" in ln]
    assert en_remaining, (
        "older released CHANGELOG.en-US.md entries that used ⌨️ ♿ must NOT be "
        "modified; the rule applies only to the current unreleased section."
    )
    assert zh_remaining, (
        "older released CHANGELOG.zh-CN.md entries that used ⌨️ ♿ must NOT be "
        "modified; the rule applies only to the current unreleased section."
    )


def test_no_unintended_changelog_changes():
    """Beyond the #57266 entries, no other unreleased-section lines should change.

    Use `git diff` against the base commit to count modified lines in the
    changelog files. The PR touches exactly 1 line per changelog file.
    """
    r = subprocess.run(
        ["git", "diff", "--numstat", "HEAD", "--", "CHANGELOG.en-US.md", "CHANGELOG.zh-CN.md"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"git diff failed: {r.stderr}"
    for line in r.stdout.strip().splitlines():
        if not line.strip():
            continue
        added, removed, _path = line.split(maxsplit=2)
        # Each changelog should have exactly 1 line added, 1 line removed.
        assert added == "1" and removed == "1", (
            f"unexpected changelog churn in {_path}: +{added} -{removed} "
            "(should be +1 -1)"
        )


def test_repo_git_status_clean_of_unstaged_other_files():
    """Sanity p2p: git command works in the repo (the working tree exists)."""
    r = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"git rev-parse failed: {r.stderr}"
    assert len(r.stdout.strip()) == 40, "expected a 40-char SHA"


if __name__ == "__main__":
    import sys
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
