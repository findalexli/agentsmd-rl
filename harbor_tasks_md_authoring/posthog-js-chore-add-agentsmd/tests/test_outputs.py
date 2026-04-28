"""Behavioral checks for posthog-js-chore-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/posthog-js")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Example and playground projects are independent pnpm workspaces. You can install their dependencies by running `pnpm install` inside the specific project folder. All dependencies and sub-dependencie' in text, "expected to find: " + '- Example and playground projects are independent pnpm workspaces. You can install their dependencies by running `pnpm install` inside the specific project folder. All dependencies and sub-dependencie'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This is a pnpm monorepo containing multiple PostHog JavaScript SDKs and development tooling. The repository uses Turbo for build orchestration and supports local development through tarball-based test' in text, "expected to find: " + 'This is a pnpm monorepo containing multiple PostHog JavaScript SDKs and development tooling. The repository uses Turbo for build orchestration and supports local development through tarball-based test'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The recommended workflow for testing local changes uses tarballs, which most realistically simulates how packages are installed from npm:' in text, "expected to find: " + 'The recommended workflow for testing local changes uses tarballs, which most realistically simulates how packages are installed from npm:'[:80]

