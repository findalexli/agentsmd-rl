"""Behavioral checks for latchkey-add-openclaw-support (markdown_authoring task).

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
    assert '5. **If necessary, ask the user to configure credentials first.** Tell the user to run `latchkey auth set` on the machine where latchkey is installed (using the setCredentialsExample from the `service' in text, "expected to find: " + '5. **If necessary, ask the user to configure credentials first.** Tell the user to run `latchkey auth set` on the machine where latchkey is installed (using the setCredentialsExample from the `service'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('integrations/SKILL.md')
    assert '6. **Alternatively, let the user log in with the browser.** If supported for the given service, run `latchkey auth browser <service_name>` to open a browser login pop-up window.' in text, "expected to find: " + '6. **Alternatively, let the user log in with the browser.** If supported for the given service, run `latchkey auth browser <service_name>` to open a browser login pop-up window.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('integrations/SKILL.md')
    assert "8. **Do not initiate a new login if the credentials status is `valid` or `unknown`** - the user might just not have the necessary permissions for the action you're trying to do." in text, "expected to find: " + "8. **Do not initiate a new login if the credentials status is `valid` or `unknown`** - the user might just not have the necessary permissions for the action you're trying to do."[:80]

