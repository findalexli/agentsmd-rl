"""Behavioral checks for everything-claude-code-feat-add-agentpaymentx402-skill-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/everything-claude-code")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/agent-payment-x402/SKILL.md')
    assert '> **Note**: Spending policy is set by the **orchestrator** before delegating to the agent — not by the agent itself. This prevents agents from escalating their own spending limits. Configure policy vi' in text, "expected to find: " + '> **Note**: Spending policy is set by the **orchestrator** before delegating to the agent — not by the agent itself. This prevents agents from escalating their own spending limits. Configure policy vi'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/agent-payment-x402/SKILL.md')
    assert 'Use when: your agent needs to pay for an API call, purchase a service, settle with another agent, enforce per-task spending limits, or manage a non-custodial wallet. Pairs naturally with cost-aware-ll' in text, "expected to find: " + 'Use when: your agent needs to pay for an API call, purchase a service, settle with another agent, enforce per-task spending limits, or manage a non-custodial wallet. Pairs naturally with cost-aware-ll'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/agent-payment-x402/SKILL.md')
    assert "x402 extends HTTP 402 (Payment Required) into a machine-negotiable flow. When a server returns `402`, the agent's payment tool automatically negotiates price, checks budget, signs a transaction, and r" in text, "expected to find: " + "x402 extends HTTP 402 (Payment Required) into a machine-negotiable flow. When a server returns `402`, the agent's payment tool automatically negotiates price, checks budget, signs a transaction, and r"[:80]

