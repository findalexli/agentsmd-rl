"""Behavioral checks for skills-fix-address-clawhub-security-scanner (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('heygen-video/SKILL.md')
    assert '> **`auto_proceed: true` is intentional.** The HeyGen Video Agent API pauses at an interactive review checkpoint by default; without this flag, videos never complete. This is a known API behavior, not' in text, "expected to find: " + '> **`auto_proceed: true` is intentional.** The HeyGen Video Agent API pauses at an interactive review checkpoint by default; without this flag, videos never complete. This is a known API behavior, not'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('heygen-video/SKILL.md')
    assert 'Do not `source` the config file. If still unset, tell the user to run `./setup` or `export HEYGEN_API_KEY=<key>`.' in text, "expected to find: " + 'Do not `source` the config file. If still unset, tell the user to run `./setup` or `export HEYGEN_API_KEY=<key>`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('heygen-video/SKILL.md')
    assert "export HEYGEN_API_KEY=$(grep -m1 '^HEYGEN_API_KEY=' ~/.heygen/config 2>/dev/null | cut -d= -f2-)" in text, "expected to find: " + "export HEYGEN_API_KEY=$(grep -m1 '^HEYGEN_API_KEY=' ~/.heygen/config 2>/dev/null | cut -d= -f2-)"[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('platforms/nanoclaw/heygen/SKILL.md')
    assert '-H "X-Api-Key: $HEYGEN_API_KEY" | jq \'.data.avatar_list[:5] | .[] | {avatar_id: .avatar_group_id, avatar_name}\'' in text, "expected to find: " + '-H "X-Api-Key: $HEYGEN_API_KEY" | jq \'.data.avatar_list[:5] | .[] | {avatar_id: .avatar_group_id, avatar_name}\''[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('platforms/nanoclaw/heygen/SKILL.md')
    assert 'curl -s -X GET "https://api.heygen.com/v3/avatars" \\' in text, "expected to find: " + 'curl -s -X GET "https://api.heygen.com/v3/avatars" \\'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('platforms/nanoclaw/heygen/SKILL.md')
    assert 'curl -s -X GET "https://api.heygen.com/v3/voices" \\' in text, "expected to find: " + 'curl -s -X GET "https://api.heygen.com/v3/voices" \\'[:80]

