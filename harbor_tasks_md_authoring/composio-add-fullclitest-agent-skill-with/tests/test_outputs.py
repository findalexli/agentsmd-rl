"""Behavioral checks for composio-add-fullclitest-agent-skill-with (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/composio")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/cli-test-with-bundling/SKILL.md')
    assert 'Read the version from `ts/packages/cli/package.json` and append a beta prerelease suffix so the build is always treated as a beta release. This prevents accidental production releases and marks the Gi' in text, "expected to find: " + 'Read the version from `ts/packages/cli/package.json` and append a beta prerelease suffix so the build is always treated as a beta release. This prevents accidental production releases and marks the Gi'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/cli-test-with-bundling/SKILL.md')
    assert 'This ensures the CI workflow creates a **prerelease** GitHub release (the workflow auto-detects `beta` in the version string).' in text, "expected to find: " + 'This ensures the CI workflow creates a **prerelease** GitHub release (the workflow auto-detects `beta` in the version string).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/cli-test-with-bundling/SKILL.md')
    assert 'Then download from the release. The workflow creates a GitHub release tagged `@composio/cli@<beta-version>`:' in text, "expected to find: " + 'Then download from the release. The workflow creates a GitHub release tagged `@composio/cli@<beta-version>`:'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/full-cli-test/SKILL.md')
    assert 'This test validates `execute()`, `experimental_subAgent()`, and end-to-end Slack connectivity. It must be run in **both Phase 2 and Phase 3** to ensure it works with both the locally-built and CI-bund' in text, "expected to find: " + 'This test validates `execute()`, `experimental_subAgent()`, and end-to-end Slack connectivity. It must be run in **both Phase 2 and Phase 3** to ensure it works with both the locally-built and CI-bund'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/full-cli-test/SKILL.md')
    assert "- The Slack user tag `<@cryogenicplanet>` should resolve to the correct user in your workspace. If the mention doesn't resolve, find the Slack user ID first and use `<@U_XXXXX>` format." in text, "expected to find: " + "- The Slack user tag `<@cryogenicplanet>` should resolve to the correct user in your workspace. If the mention doesn't resolve, find the Slack user ID first and use `<@U_XXXXX>` format."[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/full-cli-test/SKILL.md')
    assert '1. Read the version from `ts/packages/cli/package.json` and append a `-beta.<timestamp>` suffix (e.g. `1.2.3-beta.20260331143022`) — **always trigger as a beta release**' in text, "expected to find: " + '1. Read the version from `ts/packages/cli/package.json` and append a `-beta.<timestamp>` suffix (e.g. `1.2.3-beta.20260331143022`) — **always trigger as a beta release**'[:80]

