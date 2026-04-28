"""Behavioral checks for flint-chore-add-initial-githubcopilotinstructionsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/flint")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Example: instead of messages like _"Octal escape sequences should not be used in string literals."_, use messages like _"Prefer hexadecimal or Unicode escape sequences over legacy octal escape sequenc' in text, "expected to find: " + 'Example: instead of messages like _"Octal escape sequences should not be used in string literals."_, use messages like _"Prefer hexadecimal or Unicode escape sequences over legacy octal escape sequenc'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert "If you see failures in things you didn't touch, such as cross-rule unit test failures when you only changed one rule, it's probably that your dev environment isn't on Node.js 24 and/or you didn't buil" in text, "expected to find: " + "If you see failures in things you didn't touch, such as cross-rule unit test failures when you only changed one rule, it's probably that your dev environment isn't on Node.js 24 and/or you didn't buil"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'All `package.json` scripts that will be run in CI should pass: `pnpm build`, `pnpm lint`, `pnpm flint`, `pnpm lint:knip`, `pnpm lint:md`, `pnpm lint:packages`, and `pnpm lint:spelling`.' in text, "expected to find: " + 'All `package.json` scripts that will be run in CI should pass: `pnpm build`, `pnpm lint`, `pnpm flint`, `pnpm lint:knip`, `pnpm lint:md`, `pnpm lint:packages`, and `pnpm lint:spelling`.'[:80]

