"""Behavioral checks for ledger-live-chorewalletcli-update-skill-session-view (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ledger-live")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/ledger-wallet-cli/SKILL.md')
    assert '> **Session first:** When invoked without a specific task, **immediately run `session view`** — do not ask the user what to do first. Show the result, then ask what to do next. If labels exist, skip `' in text, "expected to find: " + '> **Session first:** When invoked without a specific task, **immediately run `session view`** — do not ask the user what to do first. Show the result, then ask what to do next. If labels exist, skip `'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/ledger-wallet-cli/SKILL.md')
    assert '> **Sandbox:** `account discover`, `receive`, `send` **must** use `dangerouslyDisableSandbox: true` — sandbox blocks USB (causes `Timeout has occurred`). Other commands are fine in sandbox.' in text, "expected to find: " + '> **Sandbox:** `account discover`, `receive`, `send` **must** use `dangerouslyDisableSandbox: true` — sandbox blocks USB (causes `Timeout has occurred`). Other commands are fine in sandbox.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/ledger-wallet-cli/SKILL.md')
    assert '**Solana flags:** `--mode send|stake.createAccount|stake.delegate|stake.undelegate|stake.withdraw`, `--validator <addr>`, `--stake-account <addr>`, `--memo <text>`' in text, "expected to find: " + '**Solana flags:** `--mode send|stake.createAccount|stake.delegate|stake.undelegate|stake.withdraw`, `--validator <addr>`, `--stake-account <addr>`, `--memo <text>`'[:80]

