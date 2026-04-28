"""Behavioral checks for afterburn-docs-add-agentsmd-and-claudemd (markdown_authoring task).

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
    text = _read('AGENTS.md')
    assert 'One-shot agent for cloud-like platforms. Retrieves instance metadata (attributes, SSH keys, hostname, network config) from provider-specific endpoints and applies it to the local system. Used on Fedor' in text, "expected to find: " + 'One-shot agent for cloud-like platforms. Retrieves instance metadata (attributes, SSH keys, hostname, network config) from provider-specific endpoints and applies it to the local system. Used on Fedor'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Each provider implements the `MetadataProvider` trait (`src/providers/mod.rs`) with default no-op methods for: `attributes()`, `hostname()`, `ssh_keys()`, `networks()`, `boot_checkin()`, etc.' in text, "expected to find: " + 'Each provider implements the `MetadataProvider` trait (`src/providers/mod.rs`) with default no-op methods for: `attributes()`, `hostname()`, `ssh_keys()`, `networks()`, `boot_checkin()`, etc.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Style**: Subject max 70 chars, body wrapped at 80 chars. Imperative tense preferred. Lowercase subsystem, capitalized description.' in text, "expected to find: " + '**Style**: Subject max 70 chars, body wrapped at 80 chars. Imperative tense preferred. Lowercase subsystem, capitalized description.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Each provider lives in `src/providers/<name>/` and implements the `MetadataProvider` trait from `src/providers/mod.rs`. See existing providers (e.g., `src/providers/hetzner/`) for the pattern. Registe' in text, "expected to find: " + 'Each provider lives in `src/providers/<name>/` and implements the `MetadataProvider` trait from `src/providers/mod.rs`. See existing providers (e.g., `src/providers/hetzner/`) for the pattern. Registe'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Do NOT modify `.github/workflows/*.yml` or `.copr/Makefile` -- these are synced from `coreos/repo-templates`.' in text, "expected to find: " + 'Do NOT modify `.github/workflows/*.yml` or `.copr/Makefile` -- these are synced from `coreos/repo-templates`.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'cargo clippy --all-targets -- -D warnings' in text, "expected to find: " + 'cargo clippy --all-targets -- -D warnings'[:80]

