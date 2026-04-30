"""Behavioral checks for claude-skills-update-console-example-in-symfonypatterns (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/php-pro/references/symfony-patterns.md')
    assert '$user = $this->userService->createUser($email, $password, $isAdmin);' in text, "expected to find: " + '$user = $this->userService->createUser($email, $password, $isAdmin);'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/php-pro/references/symfony-patterns.md')
    assert "$io->success(sprintf('User created with ID: %d', $user->getId()));" in text, "expected to find: " + "$io->success(sprintf('User created with ID: %d', $user->getId()));"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/php-pro/references/symfony-patterns.md')
    assert 'return Command::SUCCESS;' in text, "expected to find: " + 'return Command::SUCCESS;'[:80]

