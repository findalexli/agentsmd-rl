"""Behavioral checks for agentsys-fix-replace-hardcoded-usersavifen-path (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agentsys")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.kiro/skills/web-auth/SKILL.md')
    assert 'node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js session auth <session-name> --url <login-url> [--success-url <url>] [--success-selector <selector>] [--timeout <seconds>]' in text, "expected to find: " + 'node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js session auth <session-name> --url <login-url> [--success-url <url>] [--success-selector <selector>] [--timeout <seconds>]'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.kiro/skills/web-auth/SKILL.md')
    assert 'node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js session auth myapp --url "https://myapp.com/login" --success-url "https://myapp.com/dashboard"' in text, "expected to find: " + 'node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js session auth myapp --url "https://myapp.com/login" --success-url "https://myapp.com/dashboard"'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.kiro/skills/web-auth/SKILL.md')
    assert 'node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js session auth <session-name> --provider my-corp --providers-file ./custom-providers.json' in text, "expected to find: " + 'node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js session auth <session-name> --provider my-corp --providers-file ./custom-providers.json'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.kiro/skills/web-browse/SKILL.md')
    assert 'node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> goto <url> [--no-auth-wall-detect] [--no-content-block-detect] [--no-auto-recover] [--ensure-auth] [--wait-loaded]' in text, "expected to find: " + 'node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> goto <url> [--no-auth-wall-detect] [--no-content-block-detect] [--no-auto-recover] [--ensure-auth] [--wait-loaded]'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.kiro/skills/web-browse/SKILL.md')
    assert 'node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> form-fill --fields \'{"Email": "user@example.com", "Name": "Jane"}\' [--submit] [--submit-text <text>]' in text, "expected to find: " + 'node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> form-fill --fields \'{"Email": "user@example.com", "Name": "Jane"}\' [--submit] [--submit-text <text>]'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.kiro/skills/web-browse/SKILL.md')
    assert 'node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> extract --selector <css-selector> [--fields f1,f2,...] [--max-items N] [--max-field-length N]' in text, "expected to find: " + 'node ~/.agentsys/plugins/web-ctl/scripts/web-ctl.js run <session> extract --selector <css-selector> [--fields f1,f2,...] [--max-items N] [--max-field-length N]'[:80]

