"""Behavioral checks for latchkey-add-a-separate-skillmd-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/latchkey")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('integrations/SKILL.md')
    assert 'integrations/SKILL.md' in text, "expected to find: " + 'integrations/SKILL.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('integrations/openclaw/SKILL.md')
    assert '5. **If necessary, ask the user to configure credentials first.** Tell the user to run `latchkey auth set` on the machine where latchkey is installed (using the setCredentialsExample from the `service' in text, "expected to find: " + '5. **If necessary, ask the user to configure credentials first.** Tell the user to run `latchkey auth set` on the machine where latchkey is installed (using the setCredentialsExample from the `service'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('integrations/openclaw/SKILL.md')
    assert 'metadata: {"openclaw":{"emoji":"🔑","requires":{"bins":["latchkey"]},"install":[{"id":"node","kind":"node","package":"latchkey","bins":["latchkey"],"label":"Install Latchkey (npm)"}]}}' in text, "expected to find: " + 'metadata: {"openclaw":{"emoji":"🔑","requires":{"bins":["latchkey"]},"install":[{"id":"node","kind":"node","package":"latchkey","bins":["latchkey"],"label":"Install Latchkey (npm)"}]}}'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('integrations/openclaw/SKILL.md')
    assert "7. **Do not initiate a new login if the credentials status is `valid` or `unknown`** - the user might just not have the necessary permissions for the action you're trying to do." in text, "expected to find: " + "7. **Do not initiate a new login if the credentials status is `valid` or `unknown`** - the user might just not have the necessary permissions for the action you're trying to do."[:80]

