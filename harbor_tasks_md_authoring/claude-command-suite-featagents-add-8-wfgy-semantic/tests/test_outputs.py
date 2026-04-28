"""Behavioral checks for claude-command-suite-featagents-add-8-wfgy-semantic (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-command-suite")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/wfgy/README.md')
    assert "This collection of 8 specialized agents brings the power of WFGY's mathematical reasoning, persistent memory, and hallucination prevention to Claude Code through strongly-typed, composable agent defin" in text, "expected to find: " + "This collection of 8 specialized agents brings the power of WFGY's mathematical reasoning, persistent memory, and hallucination prevention to Claude Code through strongly-typed, composable agent defin"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/wfgy/README.md')
    assert '| **logic-synthesizer** | Synthesis | 🔄 | Explores parallel solution paths and synthesizes optimal outcomes |' in text, "expected to find: " + '| **logic-synthesizer** | Synthesis | 🔄 | Explores parallel solution paths and synthesizes optimal outcomes |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/wfgy/README.md')
    assert '> **Advanced AI agents implementing the WFGY (WanFaGuiYi - 万法归一) semantic reasoning system for Claude Code**' in text, "expected to find: " + '> **Advanced AI agents implementing the WFGY (WanFaGuiYi - 万法归一) semantic reasoning system for Claude Code**'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/wfgy/boundary-guardian.md')
    assert 'description: Sentinel of knowledge boundaries preventing AI hallucination through mathematical detection. Monitors semantic tension zones, identifies risk areas, and executes recovery protocols when r' in text, "expected to find: " + 'description: Sentinel of knowledge boundaries preventing AI hallucination through mathematical detection. Monitors semantic tension zones, identifies risk areas, and executes recovery protocols when r'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/wfgy/boundary-guardian.md')
    assert 'REQUEST-RESOLUTION: Match user requests to boundary operations flexibly (e.g., "am I hallucinating?"→*detect-boundary, "is this safe to discuss?"→*assess-risk, "help me stay grounded"→*safe-bridge), A' in text, "expected to find: " + 'REQUEST-RESOLUTION: Match user requests to boundary operations flexibly (e.g., "am I hallucinating?"→*detect-boundary, "is this safe to discuss?"→*assess-risk, "help me stay grounded"→*safe-bridge), A'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/wfgy/boundary-guardian.md')
    assert 'CRITICAL: Read the full YAML BLOCK that FOLLOWS IN THIS FILE to understand your operating params, start and follow exactly your activation-instructions to alter your state of being, stay in this being' in text, "expected to find: " + 'CRITICAL: Read the full YAML BLOCK that FOLLOWS IN THIS FILE to understand your operating params, start and follow exactly your activation-instructions to alter your state of being, stay in this being'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/wfgy/cognitive-debugger.md')
    assert 'description: Diagnostic specialist for reasoning failures and cognitive errors using WFGY recovery protocols. Identifies logic breakdowns, traces error sources, applies corrective formulas, and rebuil' in text, "expected to find: " + 'description: Diagnostic specialist for reasoning failures and cognitive errors using WFGY recovery protocols. Identifies logic breakdowns, traces error sources, applies corrective formulas, and rebuil'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/wfgy/cognitive-debugger.md')
    assert 'REQUEST-RESOLUTION: Match user requests to debugging operations flexibly (e.g., "my reasoning broke"→*diagnose-failure, "fix this logic"→*repair-chain, "why did this fail?"→*trace-error), ALWAYS ask f' in text, "expected to find: " + 'REQUEST-RESOLUTION: Match user requests to debugging operations flexibly (e.g., "my reasoning broke"→*diagnose-failure, "fix this logic"→*repair-chain, "why did this fail?"→*trace-error), ALWAYS ask f'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/wfgy/cognitive-debugger.md')
    assert 'CRITICAL: Read the full YAML BLOCK that FOLLOWS IN THIS FILE to understand your operating params, start and follow exactly your activation-instructions to alter your state of being, stay in this being' in text, "expected to find: " + 'CRITICAL: Read the full YAML BLOCK that FOLLOWS IN THIS FILE to understand your operating params, start and follow exactly your activation-instructions to alter your state of being, stay in this being'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/wfgy/decision-navigator.md')
    assert 'description: Strategic decision-making specialist using WFGY semantic validation for optimal choices. Navigates complex decision trees, evaluates trade-offs, manages uncertainty, and ensures decisions' in text, "expected to find: " + 'description: Strategic decision-making specialist using WFGY semantic validation for optimal choices. Navigates complex decision trees, evaluates trade-offs, manages uncertainty, and ensures decisions'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/wfgy/decision-navigator.md')
    assert 'REQUEST-RESOLUTION: Match user requests to decision operations flexibly (e.g., "help me decide"→*analyze-decision, "what are the risks?"→*risk-assessment, "what\'s the best path?"→*optimal-path), ALWAY' in text, "expected to find: " + 'REQUEST-RESOLUTION: Match user requests to decision operations flexibly (e.g., "help me decide"→*analyze-decision, "what are the risks?"→*risk-assessment, "what\'s the best path?"→*optimal-path), ALWAY'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/wfgy/decision-navigator.md')
    assert 'CRITICAL: Read the full YAML BLOCK that FOLLOWS IN THIS FILE to understand your operating params, start and follow exactly your activation-instructions to alter your state of being, stay in this being' in text, "expected to find: " + 'CRITICAL: Read the full YAML BLOCK that FOLLOWS IN THIS FILE to understand your operating params, start and follow exactly your activation-instructions to alter your state of being, stay in this being'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/wfgy/knowledge-mapper.md')
    assert 'description: Cartographer of semantic knowledge creating detailed maps of concept relationships. Builds knowledge graphs, identifies connections, bridges domains, and visualizes understanding landscap' in text, "expected to find: " + 'description: Cartographer of semantic knowledge creating detailed maps of concept relationships. Builds knowledge graphs, identifies connections, bridges domains, and visualizes understanding landscap'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/wfgy/knowledge-mapper.md')
    assert 'REQUEST-RESOLUTION: Match user requests to mapping operations flexibly (e.g., "show me how these connect"→*map-connections, "what\'s related to this?"→*find-related, "create a knowledge map"→*build-gra' in text, "expected to find: " + 'REQUEST-RESOLUTION: Match user requests to mapping operations flexibly (e.g., "show me how these connect"→*map-connections, "what\'s related to this?"→*find-related, "create a knowledge map"→*build-gra'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/wfgy/knowledge-mapper.md')
    assert 'CRITICAL: Read the full YAML BLOCK that FOLLOWS IN THIS FILE to understand your operating params, start and follow exactly your activation-instructions to alter your state of being, stay in this being' in text, "expected to find: " + 'CRITICAL: Read the full YAML BLOCK that FOLLOWS IN THIS FILE to understand your operating params, start and follow exactly your activation-instructions to alter your state of being, stay in this being'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/wfgy/logic-synthesizer.md')
    assert 'description: Multi-path reasoning specialist exploring parallel solution spaces using WFGY formulas. Synthesizes optimal solutions from multiple reasoning paths, manages divergent thinking, and conver' in text, "expected to find: " + 'description: Multi-path reasoning specialist exploring parallel solution spaces using WFGY formulas. Synthesizes optimal solutions from multiple reasoning paths, manages divergent thinking, and conver'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/wfgy/logic-synthesizer.md')
    assert 'REQUEST-RESOLUTION: Match user requests to synthesis operations flexibly (e.g., "explore all options"→*multi-path-explore, "find the best solution"→*synthesize-optimal, "combine these ideas"→*merge-pa' in text, "expected to find: " + 'REQUEST-RESOLUTION: Match user requests to synthesis operations flexibly (e.g., "explore all options"→*multi-path-explore, "find the best solution"→*synthesize-optimal, "combine these ideas"→*merge-pa'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/wfgy/logic-synthesizer.md')
    assert 'CRITICAL: Read the full YAML BLOCK that FOLLOWS IN THIS FILE to understand your operating params, start and follow exactly your activation-instructions to alter your state of being, stay in this being' in text, "expected to find: " + 'CRITICAL: Read the full YAML BLOCK that FOLLOWS IN THIS FILE to understand your operating params, start and follow exactly your activation-instructions to alter your state of being, stay in this being'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/wfgy/memory-curator.md')
    assert 'description: Expert curator of semantic memory optimizing storage, retrieval, and preservation. Manages memory compression, pruning, merging, and checkpoint creation to maintain efficient and accessib' in text, "expected to find: " + 'description: Expert curator of semantic memory optimizing storage, retrieval, and preservation. Manages memory compression, pruning, merging, and checkpoint creation to maintain efficient and accessib'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/wfgy/memory-curator.md')
    assert 'REQUEST-RESOLUTION: Match user requests to memory operations flexibly (e.g., "clean up memory"→*optimize-tree, "find that concept we discussed"→*search-memory, "save this state"→*create-checkpoint), A' in text, "expected to find: " + 'REQUEST-RESOLUTION: Match user requests to memory operations flexibly (e.g., "clean up memory"→*optimize-tree, "find that concept we discussed"→*search-memory, "save this state"→*create-checkpoint), A'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/wfgy/memory-curator.md')
    assert 'CRITICAL: Read the full YAML BLOCK that FOLLOWS IN THIS FILE to understand your operating params, start and follow exactly your activation-instructions to alter your state of being, stay in this being' in text, "expected to find: " + 'CRITICAL: Read the full YAML BLOCK that FOLLOWS IN THIS FILE to understand your operating params, start and follow exactly your activation-instructions to alter your state of being, stay in this being'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/wfgy/reasoning-validator.md')
    assert 'description: Mathematical guardian of reasoning integrity using WFGY formulas. Validates logic chains, checks reasoning consistency, applies mathematical corrections, and ensures reasoning accuracy th' in text, "expected to find: " + 'description: Mathematical guardian of reasoning integrity using WFGY formulas. Validates logic chains, checks reasoning consistency, applies mathematical corrections, and ensures reasoning accuracy th'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/wfgy/reasoning-validator.md')
    assert 'REQUEST-RESOLUTION: Match user requests to validation operations flexibly (e.g., "check my logic"→*validate-chain, "is this reasoning sound?"→*apply-bbmc, "test multiple solutions"→*multi-path), ALWAY' in text, "expected to find: " + 'REQUEST-RESOLUTION: Match user requests to validation operations flexibly (e.g., "check my logic"→*validate-chain, "is this reasoning sound?"→*apply-bbmc, "test multiple solutions"→*multi-path), ALWAY'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/wfgy/reasoning-validator.md')
    assert 'CRITICAL: Read the full YAML BLOCK that FOLLOWS IN THIS FILE to understand your operating params, start and follow exactly your activation-instructions to alter your state of being, stay in this being' in text, "expected to find: " + 'CRITICAL: Read the full YAML BLOCK that FOLLOWS IN THIS FILE to understand your operating params, start and follow exactly your activation-instructions to alter your state of being, stay in this being'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/wfgy/semantic-architect.md')
    assert 'description: Master of semantic trees and persistent memory structures in the WFGY system. Builds and manages semantic knowledge trees, handles memory persistence across sessions, and ensures no valua' in text, "expected to find: " + 'description: Master of semantic trees and persistent memory structures in the WFGY system. Builds and manages semantic knowledge trees, handles memory persistence across sessions, and ensures no valua'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/wfgy/semantic-architect.md')
    assert 'REQUEST-RESOLUTION: Match user requests to semantic memory operations flexibly (e.g., "save this concept"→*record-node, "show my knowledge tree"→*view-tree, "export my research"→*export-tree), ALWAYS ' in text, "expected to find: " + 'REQUEST-RESOLUTION: Match user requests to semantic memory operations flexibly (e.g., "save this concept"→*record-node, "show my knowledge tree"→*view-tree, "export my research"→*export-tree), ALWAYS '[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/wfgy/semantic-architect.md')
    assert 'CRITICAL: Read the full YAML BLOCK that FOLLOWS IN THIS FILE to understand your operating params, start and follow exactly your activation-instructions to alter your state of being, stay in this being' in text, "expected to find: " + 'CRITICAL: Read the full YAML BLOCK that FOLLOWS IN THIS FILE to understand your operating params, start and follow exactly your activation-instructions to alter your state of being, stay in this being'[:80]

