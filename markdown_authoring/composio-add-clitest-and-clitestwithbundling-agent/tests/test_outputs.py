"""Behavioral checks for composio-add-clitest-and-clitestwithbundling-agent (markdown_authoring task).

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
    text = _read('.agents/skills/cli-test-with-bundling/SKILL.md')
    assert '../../../.claude/skills/cli-test-with-bundling/SKILL.md' in text, "expected to find: " + '../../../.claude/skills/cli-test-with-bundling/SKILL.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/cli-test/SKILL.md')
    assert '../../../.claude/skills/cli-test/SKILL.md' in text, "expected to find: " + '../../../.claude/skills/cli-test/SKILL.md'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/cli-test-with-bundling/SKILL.md')
    assert '`composio run` and `experimental_subAgent()` inside `run` have complex bundling — they spawn child Bun processes using companion modules that live outside the compiled binary. These are the most likel' in text, "expected to find: " + '`composio run` and `experimental_subAgent()` inside `run` have complex bundling — they spawn child Bun processes using companion modules that live outside the compiled binary. These are the most likel'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/cli-test-with-bundling/SKILL.md')
    assert 'Trigger the `Build CLI Binaries` workflow on GitHub Actions, wait for it to complete, download the built binary for the current platform, and test it locally.' in text, "expected to find: " + 'Trigger the `Build CLI Binaries` workflow on GitHub Actions, wait for it to complete, download the built binary for the current platform, and test it locally.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/cli-test-with-bundling/SKILL.md')
    assert 'If either of these fails, the companion module bundling is broken — check `ts/packages/cli/scripts/build-binary.ts` and the `buildCompanionModules` function.' in text, "expected to find: " + 'If either of these fails, the companion module bundling is broken — check `ts/packages/cli/scripts/build-binary.ts` and the `buildCompanionModules` function.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/cli-test/SKILL.md')
    assert 'By default the binary uses your existing Composio CLI auth (stored in `~/.composio/user-config.json`). No extra setup needed — just build and run.' in text, "expected to find: " + 'By default the binary uses your existing Composio CLI auth (stored in `~/.composio/user-config.json`). No extra setup needed — just build and run.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/cli-test/SKILL.md')
    assert 'description: Build the CLI binary from source and test it locally by running commands against the built binary.' in text, "expected to find: " + 'description: Build the CLI binary from source and test it locally by running commands against the built binary.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/cli-test/SKILL.md')
    assert 'To test against staging instead of production, export these env vars before running the binary:' in text, "expected to find: " + 'To test against staging instead of production, export these env vars before running the binary:'[:80]

