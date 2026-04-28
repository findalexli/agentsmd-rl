"""Behavioral checks for sentry-choreai-split-image-section-in (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sentry")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('static/AGENTS.md')
    assert 'Use the core avatar components (<UserAvatar/>, <TeamAvatar/>, <ProjectAvatar/>, <OrganizationAvatar/>, <SentryAppAvatar/>, <DocIntegrationAvatar/>) from `static/app/components/core/avatar` for avatars' in text, "expected to find: " + 'Use the core avatar components (<UserAvatar/>, <TeamAvatar/>, <ProjectAvatar/>, <OrganizationAvatar/>, <SentryAppAvatar/>, <DocIntegrationAvatar/>) from `static/app/components/core/avatar` for avatars'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('static/AGENTS.md')
    assert '- Split Layout from Typography by directly using Flex, Grid, Stack or Container and Text or Heading components' in text, "expected to find: " + '- Split Layout from Typography by directly using Flex, Grid, Stack or Container and Text or Heading components'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('static/AGENTS.md')
    assert "import {UserAvatar} from 'sentry/components/core/avatar/userAvatar';" in text, "expected to find: " + "import {UserAvatar} from 'sentry/components/core/avatar/userAvatar';"[:80]

