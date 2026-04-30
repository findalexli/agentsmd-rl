"""Behavioral checks for catalyst-add-claude-skills-for-releasecatalyst (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/catalyst")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/release-catalyst/SKILL.md')
    assert 'Pulls in changes from the `@bigcommerce/catalyst-core@<version>` release. For more information about what was included in the `@bigcommerce/catalyst-core@<version>` release, see the [changelog entry](' in text, "expected to find: " + 'Pulls in changes from the `@bigcommerce/catalyst-core@<version>` release. For more information about what was included in the `@bigcommerce/catalyst-core@<version>` release, see the [changelog entry]('[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/release-catalyst/SKILL.md')
    assert '- Note: squash merging is normally disallowed on `integrations/makeswift` to preserve merge bases for sync PRs. The user may need to temporarily enable squash merging in the branch protection rules fo' in text, "expected to find: " + '- Note: squash merging is normally disallowed on `integrations/makeswift` to preserve merge bases for sync PRs. The user may need to temporarily enable squash merging in the branch protection rules fo'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/release-catalyst/SKILL.md')
    assert 'Invoke the `/sync-makeswift` skill, with one addition: during the sync (after merge, before pushing), also add a changeset for `@bigcommerce/catalyst-makeswift`:' in text, "expected to find: " + 'Invoke the `/sync-makeswift` skill, with one addition: during the sync (after merge, before pushing), also add a changeset for `@bigcommerce/catalyst-makeswift`:'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/sync-makeswift/SKILL.md')
    assert "- `core/package.json`: the `name` field MUST stay `@bigcommerce/catalyst-makeswift`. The `version` field MUST stay at the latest published `@bigcommerce/catalyst-makeswift` version (check what's on `o" in text, "expected to find: " + "- `core/package.json`: the `name` field MUST stay `@bigcommerce/catalyst-makeswift`. The `version` field MUST stay at the latest published `@bigcommerce/catalyst-makeswift` version (check what's on `o"[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/sync-makeswift/SKILL.md')
    assert 'Remove any `.changeset/*.md` files that do NOT target `@bigcommerce/catalyst-makeswift`. Read each changeset file and delete any that reference `@bigcommerce/catalyst-core` or other packages. Amend th' in text, "expected to find: " + 'Remove any `.changeset/*.md` files that do NOT target `@bigcommerce/catalyst-makeswift`. Read each changeset file and delete any that reference `@bigcommerce/catalyst-core` or other packages. Amend th'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/sync-makeswift/SKILL.md')
    assert '> **Do not squash or rebase-and-merge this PR.** Use a true merge commit or rebase locally to preserve the merge base between `canary` and `integrations/makeswift`.' in text, "expected to find: " + '> **Do not squash or rebase-and-merge this PR.** Use a true merge commit or rebase locally to preserve the merge base between `canary` and `integrations/makeswift`.'[:80]

