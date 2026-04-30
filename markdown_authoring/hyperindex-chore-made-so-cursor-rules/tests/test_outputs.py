"""Behavioral checks for hyperindex-chore-made-so-cursor-rules (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/hyperindex")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/subgraph-migration.mdc')
    assert '**🚨 CRITICAL: This is the final step to ensure complete migration accuracy. NO TODOs should remain - absolutely everything must be implemented, regardless of complexity.**' in text, "expected to find: " + '**🚨 CRITICAL: This is the final step to ensure complete migration accuracy. NO TODOs should remain - absolutely everything must be implemented, regardless of complexity.**'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/subgraph-migration.mdc')
    assert '3. **Consult Envio documentation** at https://docs.envio.dev/docs/HyperIndex-LLM/hyperindex-complete for correct implementation patterns' in text, "expected to find: " + '3. **Consult Envio documentation** at https://docs.envio.dev/docs/HyperIndex-LLM/hyperindex-complete for correct implementation patterns'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/subgraph-migration.mdc')
    assert '**⚠️ IMPORTANT: Read all steps in this checklist before beginning so you know to wait and check output, not get stuck indefinitely**' in text, "expected to find: " + '**⚠️ IMPORTANT: Read all steps in this checklist before beginning so you know to wait and check output, not get stuck indefinitely**'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('codegenerator/cli/templates/static/shared/.cursor/rules/subgraph-migration.mdc')
    assert 'description: Made to assist in migrating from subgraph to HyperIndex. Includes both step by step instructions for cursor based migration as well as common migration patters. (Note: if doing a full mig' in text, "expected to find: " + 'description: Made to assist in migrating from subgraph to HyperIndex. Includes both step by step instructions for cursor based migration as well as common migration patters. (Note: if doing a full mig'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('codegenerator/cli/templates/static/shared/.cursor/rules/subgraph-migration.mdc')
    assert "12. **🚨 CRITICAL: Check entity type mismatches and database schema compatibility** - ALWAYS verify that the types you're setting in code match the schema entity property types exactly, and ensure data" in text, "expected to find: " + "12. **🚨 CRITICAL: Check entity type mismatches and database schema compatibility** - ALWAYS verify that the types you're setting in code match the schema entity property types exactly, and ensure data"[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('codegenerator/cli/templates/static/shared/.cursor/rules/subgraph-migration.mdc')
    assert '**IMPORTANT: After completing each step, ALWAYS run the Quality Check Checklist (see section 21) before proceeding to the next step. This prevents common issues from accumulating and makes debugging m' in text, "expected to find: " + '**IMPORTANT: After completing each step, ALWAYS run the Quality Check Checklist (see section 21) before proceeding to the next step. This prevents common issues from accumulating and makes debugging m'[:80]

