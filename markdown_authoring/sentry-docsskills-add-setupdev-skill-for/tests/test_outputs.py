"""Behavioral checks for sentry-docsskills-add-setupdev-skill-for (markdown_authoring task).

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
    text = _read('.agents/skills/setup-dev/SKILL.md')
    assert '**AL MCP**: If the `al` MCP server is available, use `al_search_docs` and `al_read_doc` for detailed troubleshooting. The AL docs cover devenv, devservices, and common issues in depth. The AL server i' in text, "expected to find: " + '**AL MCP**: If the `al` MCP server is available, use `al_search_docs` and `al_read_doc` for detailed troubleshooting. The AL docs cover devenv, devservices, and common issues in depth. The AL server i'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/setup-dev/SKILL.md')
    assert 'description: Set up and manage the Sentry development environment using devenv. Handles fresh setup, updating existing environments, starting dev services, and troubleshooting. Use when asked to "set ' in text, "expected to find: " + 'description: Set up and manage the Sentry development environment using devenv. Handles fresh setup, updating existing environments, starting dev services, and troubleshooting. Use when asked to "set '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/setup-dev/SKILL.md')
    assert 'Walk the user through getting Sentry running locally. The full process from a bare machine takes **30-45 minutes** — most of that is downloading dependencies and Docker images. Set expectations clearl' in text, "expected to find: " + 'Walk the user through getting Sentry running locally. The full process from a bare machine takes **30-45 minutes** — most of that is downloading dependencies and Docker images. Set expectations clearl'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/setup-dev/references/orbstack-fix.md')
    assert "The `check_docker_daemon_running()` function checks for a Docker socket at a hardcoded Colima path. When using OrbStack, that path doesn't exist, so it falls through to the error message telling the u" in text, "expected to find: " + "The `check_docker_daemon_running()` function checks for a Docker socket at a hardcoded Colima path. When using OrbStack, that path doesn't exist, so it falls through to the error message telling the u"[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/setup-dev/references/orbstack-fix.md')
    assert 'When `devservices serve` or `sentry devserver` fails with "Make sure colima is running" for OrbStack users, the issue is in `src/sentry/runner/commands/devservices.py`.' in text, "expected to find: " + 'When `devservices serve` or `sentry devserver` fails with "Make sure colima is running" for OrbStack users, the issue is in `src/sentry/runner/commands/devservices.py`.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/setup-dev/references/orbstack-fix.md')
    assert 'Then update `check_docker_daemon_running()` to use `_find_docker_socket()` and update the error message:' in text, "expected to find: " + 'Then update `check_docker_daemon_running()` to use `_find_docker_socket()` and update the error message:'[:80]

