"""Behavioral checks for agenc-chore-add-cursor-rules-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agenc")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/anchor.mdc')
    assert '- `SlashReason`: ProofFailed, ProofTimeout, InvalidResult' in text, "expected to find: " + '- `SlashReason`: ProofFailed, ProofTimeout, InvalidResult'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/anchor.mdc')
    assert 'description: Rules for Anchor/Solana program development' in text, "expected to find: " + 'description: Rules for Anchor/Solana program development'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/anchor.mdc')
    assert '// Calculate exact size: 8 (discriminator) + field sizes' in text, "expected to find: " + '// Calculate exact size: 8 (discriminator) + field sizes'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/runtime.mdc')
    assert 'const deferral = new ProofDeferralManager(config, graph, ledger);' in text, "expected to find: " + 'const deferral = new ProofDeferralManager(config, graph, ledger);'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/runtime.mdc')
    assert 'const pipeline = new ProofPipeline({ maxConcurrentProofs: 5 });' in text, "expected to find: " + 'const pipeline = new ProofPipeline({ maxConcurrentProofs: 5 });'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/runtime.mdc')
    assert 'const rollback = new RollbackController(config, graph, ledger);' in text, "expected to find: " + 'const rollback = new RollbackController(config, graph, ledger);'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/speculation.mdc')
    assert 'When modifying speculation code, always verify this invariant is maintained.' in text, "expected to find: " + 'When modifying speculation code, always verify this invariant is maintained.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/speculation.mdc')
    assert '**NEVER submit a proof until all ancestor proofs are confirmed on-chain.**' in text, "expected to find: " + '**NEVER submit a proof until all ancestor proofs are confirmed on-chain.**'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/speculation.mdc')
    assert 'description: Rules for working with the speculative execution system' in text, "expected to find: " + 'description: Rules for working with the speculative execution system'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert 'AgenC is a privacy-preserving AI agent coordination protocol built on Solana. It enables decentralized task coordination with zero-knowledge proofs for private task completions.' in text, "expected to find: " + 'AgenC is a privacy-preserving AI agent coordination protocol built on Solana. It enables decentralized task coordination with zero-knowledge proofs for private task completions.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert 'The runtime includes a complete speculative execution system for overlapping task execution with proof generation.' in text, "expected to find: " + 'The runtime includes a complete speculative execution system for overlapping task execution with proof generation.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert '| SpeculationMetricsCollector | speculation-metrics.ts | Observability metrics |' in text, "expected to find: " + '| SpeculationMetricsCollector | speculation-metrics.ts | Observability metrics |'[:80]

