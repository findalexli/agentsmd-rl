"""Behavioral checks for ignition-opencodeskills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ignition")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/add-platform-support/SKILL.md')
    assert 'This skill automates adding support for a new cloud provider or platform to Ignition, following the exact pattern from commits like [ef142f33](https://github.com/coreos/ignition/commit/ef142f33) (Hetz' in text, "expected to find: " + 'This skill automates adding support for a new cloud provider or platform to Ignition, following the exact pattern from commits like [ef142f33](https://github.com/coreos/ignition/commit/ef142f33) (Hetz'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/add-platform-support/SKILL.md')
    assert '- `description`: Custom description (default: "Ignition will read its configuration from the instance userdata. Cloud SSH keys are handled separately.")' in text, "expected to find: " + '- `description`: Custom description (default: "Ignition will read its configuration from the instance userdata. Cloud SSH keys are handled separately.")'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/add-platform-support/SKILL.md')
    assert '/add-platform-support --id hetzner --name "Hetzner Cloud" --url "http://169.254.169.254/hetzner/v1/userdata" --docs "https://www.hetzner.com/cloud"' in text, "expected to find: " + '/add-platform-support --id hetzner --name "Hetzner Cloud" --url "http://169.254.169.254/hetzner/v1/userdata" --docs "https://www.hetzner.com/cloud"'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/release_note_update/SKILL.md')
    assert 'This skill automates the Ignition release process, handling version bumps and release notes updates following the established conventions from [PR #2181](https://github.com/coreos/ignition/pull/2181).' in text, "expected to find: " + 'This skill automates the Ignition release process, handling version bumps and release notes updates following the established conventions from [PR #2181](https://github.com/coreos/ignition/pull/2181).'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/release_note_update/SKILL.md')
    assert '1. Moving unreleased items from the "Unreleased" section to a new version section in `docs/release-notes.md`' in text, "expected to find: " + '1. Moving unreleased items from the "Unreleased" section to a new version section in `docs/release-notes.md`'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/release_note_update/SKILL.md')
    assert '- [Release Notes Documentation](https://github.com/coreos/ignition/blob/main/docs/release-notes.md)' in text, "expected to find: " + '- [Release Notes Documentation](https://github.com/coreos/ignition/blob/main/docs/release-notes.md)'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/stabilize-spec/SKILL.md')
    assert 'This skill automates the complete Ignition config spec stabilization process following the exact 8-commit structure from [PR #2202](https://github.com/coreos/ignition/pull/2202).' in text, "expected to find: " + 'This skill automates the complete Ignition config spec stabilization process following the exact 8-commit structure from [PR #2202](https://github.com/coreos/ignition/pull/2202).'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/stabilize-spec/SKILL.md')
    assert 'This skill completes all items from the [stabilization checklist](https://github.com/coreos/ignition/blob/main/.github/ISSUE_TEMPLATE/stabilize-checklist.md):' in text, "expected to find: " + 'This skill completes all items from the [stabilization checklist](https://github.com/coreos/ignition/blob/main/.github/ISSUE_TEMPLATE/stabilize-checklist.md):'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.opencode/skills/stabilize-spec/SKILL.md')
    assert '- [Stabilization Template](https://github.com/coreos/ignition/blob/main/.github/ISSUE_TEMPLATE/stabilize-checklist.md)' in text, "expected to find: " + '- [Stabilization Template](https://github.com/coreos/ignition/blob/main/.github/ISSUE_TEMPLATE/stabilize-checklist.md)'[:80]

