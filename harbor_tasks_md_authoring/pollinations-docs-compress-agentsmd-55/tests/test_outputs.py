"""Behavioral checks for pollinations-docs-compress-agentsmd-55 (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/pollinations")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Platforms (auto-detected; comma-separated for multi): `web` (default w/ URL), `android`, `ios` (App Store or routinehub.co), `windows`, `macos`, `desktop` (cross-platform), `cli`, `discord`, `telegram' in text, "expected to find: " + 'Platforms (auto-detected; comma-separated for multi): `web` (default w/ URL), `android`, `ios` (App Store or routinehub.co), `windows`, `macos`, `desktop` (cross-platform), `cli`, `discord`, `telegram'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Flow: user opens issue with `TIER-APP` → workflow validates + AI generates preview → bot posts `APP_REVIEW_DATA` JSON + labels `TIER-APP-REVIEW` → maintainer adds `TIER-APP-APPROVED` → workflow prepen' in text, "expected to find: " + 'Flow: user opens issue with `TIER-APP` → workflow validates + AI generates preview → bot posts `APP_REVIEW_DATA` JSON + labels `TIER-APP-REVIEW` → maintainer adds `TIER-APP-APPROVED` → workflow prepen'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Before implementing: verify assumptions on web (APIs change), read related files, check related PRs/issues, check existing utilities in `shared/` before writing new ones (auth, queue, registry, SSE ' in text, "expected to find: " + '- Before implementing: verify assumptions on web (APIs change), read related files, check related PRs/issues, check existing utilities in `shared/` before writing new ones (auth, queue, registry, SSE '[:80]

