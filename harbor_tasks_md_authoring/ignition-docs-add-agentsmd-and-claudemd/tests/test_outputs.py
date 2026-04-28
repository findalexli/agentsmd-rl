"""Behavioral checks for ignition-docs-add-agentsmd-and-claudemd (markdown_authoring task).

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
    text = _read('AGENTS.md')
    assert 'First-boot provisioning utility for immutable Linux (Fedora CoreOS, RHEL CoreOS, Flatcar). Partitions disks, formats filesystems, writes files, configures users during initramfs.' in text, "expected to find: " + 'First-boot provisioning utility for immutable Linux (Fedora CoreOS, RHEL CoreOS, Flatcar). Partitions disks, formats filesystems, writes files, configures users during initramfs.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '1. **Frontend is stable API** -- `config/` is used by external programs. API changes require bumping Ignition major version.' in text, "expected to find: " + '1. **Frontend is stable API** -- `config/` is used by external programs. API changes require bumping Ignition major version.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '7. **Execution stages are fixed** (fetch-offline, fetch, disks, mount, files, umount). External projects hardcode this list.' in text, "expected to find: " + '7. **Execution stages are fixed** (fetch-offline, fetch, disks, mount, files, umount). External projects hardcode this list.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Run `./test` before committing any changes. This validates license headers, gofmt, govet, unit tests, and documentation.' in text, "expected to find: " + 'Run `./test` before committing any changes. This validates license headers, gofmt, govet, unit tests, and documentation.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "- Use the **Explore** agent for broad codebase searches when simple Grep/Glob isn't enough" in text, "expected to find: " + "- Use the **Explore** agent for broad codebase searches when simple Grep/Glob isn't enough"[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'When working on multi-step tasks, use TodoWrite to break down work and track progress.' in text, "expected to find: " + 'When working on multi-step tasks, use TodoWrite to break down work and track progress.'[:80]

