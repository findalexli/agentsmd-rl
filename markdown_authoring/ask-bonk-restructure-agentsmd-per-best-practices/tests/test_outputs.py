"""Behavioral checks for ask-bonk-restructure-agentsmd-per-best-practices (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ask-bonk")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "**`/webhooks` - GitHub Actions Mode**: Webhook events trigger GitHub Actions workflows via the composite action in `github/`. OpenCode runs inside the workflow, not in Bonk's infrastructure. The `Repo" in text, "expected to find: " + "**`/webhooks` - GitHub Actions Mode**: Webhook events trigger GitHub Actions workflows via the composite action in `github/`. OpenCode runs inside the workflow, not in Bonk's infrastructure. The `Repo"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'All domain errors are `TaggedError` subclasses defined in `src/errors.ts`: `OIDCValidationError`, `AuthorizationError`, `InstallationNotFoundError`, `ValidationError`, `NotFoundError`, `GitHubAPIError' in text, "expected to find: " + 'All domain errors are `TaggedError` subclasses defined in `src/errors.ts`: `OIDCValidationError`, `AuthorizationError`, `InstallationNotFoundError`, `ValidationError`, `NotFoundError`, `GitHubAPIError'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**`/ask` - Direct Sandbox Mode**: Runs OpenCode directly in Cloudflare Sandbox for programmatic API access. Requires bearer auth (`ASK_SECRET`). Returns SSE stream.' in text, "expected to find: " + '**`/ask` - Direct Sandbox Mode**: Runs OpenCode directly in Cloudflare Sandbox for programmatic API access. Requires bearer auth (`ASK_SECRET`). Returns SSE stream.'[:80]

