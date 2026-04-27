"""Behavioral checks for rulesync-refactor-rename-and-update-rulesync (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/rulesync")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.rulesync/skills/draft-release/SKILL.md')
    assert '10. Create a **draft** release using `gh release create v${new_version} --draft --title v${new_version} --notes-file ./tmp/release-notes/*.md` command on the `github.com/dyoshikawa/rulesync` repositor' in text, "expected to find: " + '10. Create a **draft** release using `gh release create v${new_version} --draft --title v${new_version} --notes-file ./tmp/release-notes/*.md` command on the `github.com/dyoshikawa/rulesync` repositor'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.rulesync/skills/draft-release/SKILL.md')
    assert '5. Update `getVersion()` function to return the ${new_version} in `src/cli/index.ts`, and run `pnpm cicheck`. If the checks fail, fix the code until pass. Then, execute `git add`, `git commit` and `gi' in text, "expected to find: " + '5. Update `getVersion()` function to return the ${new_version} in `src/cli/index.ts`, and run `pnpm cicheck`. If the checks fail, fix the code until pass. Then, execute `git add`, `git commit` and `gi'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.rulesync/skills/draft-release/SKILL.md')
    assert 'Then, from $ARGUMENTS, get the new version without v prefix, and assign it to $new_version. For example, if $ARGUMENTS is "v1.0.0", the new version is "1.0.0".' in text, "expected to find: " + 'Then, from $ARGUMENTS, get the new version without v prefix, and assign it to $new_version. For example, if $ARGUMENTS is "v1.0.0", the new version is "1.0.0".'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.rulesync/skills/post-review-comments/SKILL.md')
    assert 'name: post-review-comments' in text, "expected to find: " + 'name: post-review-comments'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.rulesync/skills/release/SKILL.md')
    assert '.rulesync/skills/release/SKILL.md' in text, "expected to find: " + '.rulesync/skills/release/SKILL.md'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.rulesync/skills/review-and-comments/SKILL.md')
    assert 'Using the review results from Step 1, run the `post-review-comments` skill with $target_pr.' in text, "expected to find: " + 'Using the review results from Step 1, run the `post-review-comments` skill with $target_pr.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.rulesync/skills/review-and-comments/SKILL.md')
    assert 'Review a PR for code quality and security issues, then post review comments on' in text, "expected to find: " + 'Review a PR for code quality and security issues, then post review comments on'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.rulesync/skills/review-and-comments/SKILL.md')
    assert 'it. Runs review-pr followed by post-review-comments sequentially.' in text, "expected to find: " + 'it. Runs review-pr followed by post-review-comments sequentially.'[:80]

