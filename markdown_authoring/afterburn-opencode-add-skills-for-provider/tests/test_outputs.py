"""Behavioral checks for afterburn-opencode-add-skills-for-provider (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/afterburn")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/add-provider/SKILL.md')
    assert '**For config drive providers**, use the ProxmoxVE provider (`src/providers/proxmoxve/`) as reference. These are more complex and variable -- adapt based on the specific config drive format.' in text, "expected to find: " + '**For config drive providers**, use the ProxmoxVE provider (`src/providers/proxmoxve/`) as reference. These are more complex and variable -- adapt based on the specific config drive format.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/add-provider/SKILL.md')
    assert 'Based on supported features, add `ConditionKernelCommandLine=|ignition.platform.id={platform_id}` to the appropriate service files. Insert in **alphabetical order** among existing entries.' in text, "expected to find: " + 'Based on supported features, add `ConditionKernelCommandLine=|ignition.platform.id={platform_id}` to the appropriate service files. Insert in **alphabetical order** among existing entries.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/add-provider/SKILL.md')
    assert 'Scaffold a new cloud/platform provider for the Afterburn metadata agent, including the Rust implementation, mock tests, documentation, and systemd/dracut service entries.' in text, "expected to find: " + 'Scaffold a new cloud/platform provider for the Afterburn metadata agent, including the Rust implementation, mock tests, documentation, and systemd/dracut service entries.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/prepare-release/SKILL.md')
    assert 'Some release notes entries may already exist (contributors often add entries when they merge features). Preserve those and add any missing ones from the commit analysis.' in text, "expected to find: " + 'Some release notes entries may already exist (contributors often add entries when they merge features). Preserve those and add any missing ones from the commit analysis.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/prepare-release/SKILL.md')
    assert '- Minor: "Azure: fetch SSH keys from IMDS instead of deprecated certificates endpoint", "Azure: fix parsing of SharedConfig XML document with current serde-xml-rs"' in text, "expected to find: " + '- Minor: "Azure: fetch SSH keys from IMDS instead of deprecated certificates endpoint", "Azure: fix parsing of SharedConfig XML document with current serde-xml-rs"'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/prepare-release/SKILL.md')
    assert 'Automate the pre-release PR for an Afterburn release: create branch, update dependencies, draft release notes from commit history, and open the PR.' in text, "expected to find: " + 'Automate the pre-release PR for an Afterburn release: create branch, update dependencies, draft release notes from commit history, and open the PR.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/publish-release/SKILL.md')
    assert 'This is a multi-phase, interactive workflow. The skill runs what it can automatically and prompts the user at credential-gated steps. Track progress with a checklist displayed after each phase.' in text, "expected to find: " + 'This is a multi-phase, interactive workflow. The skill runs what it can automatically and prompts the user at credential-gated steps. Track progress with a checklist displayed after each phase.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/publish-release/SKILL.md')
    assert 'Guide the post-merge release process for Afterburn. This skill runs automatable steps directly and prompts the user for steps requiring credentials (GPG signing, crates.io publishing).' in text, "expected to find: " + 'Guide the post-merge release process for Afterburn. This skill runs automatable steps directly and prompts the user for steps requiring credentials (GPG signing, crates.io publishing).'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/publish-release/SKILL.md')
    assert 'Read the release notes for this version from `docs/release-notes.md`. Extract the section between `## Afterburn ${RELEASE_VER}` and the next `## ` header.' in text, "expected to find: " + 'Read the release notes for this version from `docs/release-notes.md`. Extract the section between `## Afterburn ${RELEASE_VER}` and the next `## ` header.'[:80]

