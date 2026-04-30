"""Behavioral checks for xurl-fixskill-harden-xurl-skillmd-against (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/xurl")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert 'Tokens are persisted to `~/.xurl` in YAML format. Each app has its own isolated tokens. Do not read this file through the agent/LLM. Once authenticated, every command below will auto‑attach the right ' in text, "expected to find: " + 'Tokens are persisted to `~/.xurl` in YAML format. Each app has its own isolated tokens. Do not read this file through the agent/LLM. Once authenticated, every command below will auto‑attach the right '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '- Sensitive flags that must never be used in agent commands: `--bearer-token`, `--consumer-key`, `--consumer-secret`, `--access-token`, `--token-secret`, `--client-id`, `--client-secret`.' in text, "expected to find: " + '- Sensitive flags that must never be used in agent commands: `--bearer-token`, `--consumer-key`, `--consumer-secret`, `--access-token`, `--token-secret`, `--client-id`, `--client-secret`.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '- **Multiple apps:** Each app has its own isolated credentials and tokens. Configure credentials manually outside agent/LLM context, then switch with `xurl auth default` or `--app`.' in text, "expected to find: " + '- **Multiple apps:** Each app has its own isolated credentials and tokens. Configure credentials manually outside agent/LLM context, then switch with `xurl auth default` or `--app`.'[:80]

