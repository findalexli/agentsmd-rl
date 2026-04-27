"""Behavioral checks for agent-skills-docsskills-wave-a-securityprivacy-guardrails (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agent-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('prompts/munger-observer/SKILL.md')
    assert '- Do not copy or forward personal excerpts outside the current workspace/session without explicit user instruction.' in text, "expected to find: " + '- Do not copy or forward personal excerpts outside the current workspace/session without explicit user instruction.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('prompts/munger-observer/SKILL.md')
    assert '- Exclude credentials, financial account numbers, health data, and private identifiers from outputs.' in text, "expected to find: " + '- Exclude credentials, financial account numbers, health data, and private identifiers from outputs.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('prompts/munger-observer/SKILL.md')
    assert '- Analyze only the minimum required memory/session span for the requested review.' in text, "expected to find: " + '- Analyze only the minimum required memory/session span for the requested review.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/context-recovery/SKILL.md')
    assert '- In DMs/private channels, require explicit user confirmation before broad history scans.' in text, "expected to find: " + '- In DMs/private channels, require explicit user confirmation before broad history scans.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/context-recovery/SKILL.md')
    assert '- last 24h or last 50 messages (whichever is smaller), unless user asks for more.' in text, "expected to find: " + '- last 24h or last 50 messages (whichever is smaller), unless user asks for more.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/context-recovery/SKILL.md')
    assert '- Never include secrets/tokens in recovered summaries; replace with `[REDACTED]`.' in text, "expected to find: " + '- Never include secrets/tokens in recovered summaries; replace with `[REDACTED]`.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/google-ads/SKILL.md')
    assert '- Any mutating action (pause/enable/edit bids/budgets) requires explicit confirmation listing impacted entities first.' in text, "expected to find: " + '- Any mutating action (pause/enable/edit bids/budgets) requires explicit confirmation listing impacted entities first.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/google-ads/SKILL.md')
    assert '- Protect `~/.google-ads.yaml` permissions and never echo tokens/secrets in terminal output.' in text, "expected to find: " + '- Protect `~/.google-ads.yaml` permissions and never echo tokens/secrets in terminal output.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/google-ads/SKILL.md')
    assert '- Browser mode must be user-attended for account-affecting actions.' in text, "expected to find: " + '- Browser mode must be user-attended for account-affecting actions.'[:80]

