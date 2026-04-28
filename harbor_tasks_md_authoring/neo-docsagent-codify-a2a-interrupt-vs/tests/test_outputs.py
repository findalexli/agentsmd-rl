"""Behavioral checks for neo-docsagent-codify-a2a-interrupt-vs (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/neo")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/session-sunset/references/session-sunset-workflow.md')
    assert 'To preserve "hot" thread visibility across sessions (Option B), agents do NOT `mark_read` messages immediately during active processing. Now that handovers are drafted (and have read your inbox state)' in text, "expected to find: " + 'To preserve "hot" thread visibility across sessions (Option B), agents do NOT `mark_read` messages immediately during active processing. Now that handovers are drafted (and have read your inbox state)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/session-sunset/references/session-sunset-workflow.md')
    assert 'This is the final and most critical step. You MUST invoke `add_memory` to persist a rich "Sandman memory" node. This memory should encapsulate the entire Sunset Protocol payload (Steps 1-8). The resul' in text, "expected to find: " + 'This is the final and most critical step. You MUST invoke `add_memory` to persist a rich "Sandman memory" node. This memory should encapsulate the entire Sunset Protocol payload (Steps 1-8). The resul'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agent/skills/session-sunset/references/session-sunset-workflow.md')
    assert "You MUST use the `add_message` MCP tool to send an A2A message to your own agent identity (e.g., `to: '@me'` or your explicit handle). The body of this message MUST contain the **full Sunset Protocol " in text, "expected to find: " + "You MUST use the `add_message` MCP tool to send an A2A message to your own agent identity (e.g., `to: '@me'` or your explicit handle). The body of this message MUST contain the **full Sunset Protocol "[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Option B (Sunset explicit mark_read):** Do NOT immediately call `mark_read` after reading. Preserving `readAt: null` during your active session is vital so future agents can find "hot" threads as ' in text, "expected to find: " + '- **Option B (Sunset explicit mark_read):** Do NOT immediately call `mark_read` after reading. Preserving `readAt: null` during your active session is vital so future agents can find "hot" threads as '[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Session `bf59d6c4-e250-44a2-b4b2-5bffae40ab5f` (2026-04-27):** 3 wake events fired in a single turn-arc due to queued harness inputs. By treating the wake as an interrupt and polling `list_message' in text, "expected to find: " + '- **Session `bf59d6c4-e250-44a2-b4b2-5bffae40ab5f` (2026-04-27):** 3 wake events fired in a single turn-arc due to queued harness inputs. By treating the wake as an interrupt and polling `list_message'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Session `aaf22f06-cc5c-4dff-aa2f-7d5efb3a6343` (2026-04-26):** 6+ instances of inbound A2A messages requiring explicit human-prompted nudges before being read by the receiving agent. Pattern recur' in text, "expected to find: " + '- **Session `aaf22f06-cc5c-4dff-aa2f-7d5efb3a6343` (2026-04-26):** 6+ instances of inbound A2A messages requiring explicit human-prompted nudges before being read by the receiving agent. Pattern recur'[:80]

