"""Behavioral checks for ouroboros-fixskills-load-deferred-mcp-tools (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ouroboros")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/evaluate/SKILL.md')
    assert "**IMPORTANT**: Do NOT skip this step. Do NOT assume MCP tools are unavailable just because they don't appear in your immediate tool list. They are almost always available as deferred tools that need t" in text, "expected to find: " + "**IMPORTANT**: Do NOT skip this step. Do NOT assume MCP tools are unavailable just because they don't appear in your immediate tool list. They are almost always available as deferred tools that need t"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/evaluate/SKILL.md')
    assert '2. The tool will typically be named `mcp__plugin_ouroboros_ouroboros__ouroboros_evaluate` (with a plugin prefix). After ToolSearch returns, the tool becomes callable.' in text, "expected to find: " + '2. The tool will typically be named `mcp__plugin_ouroboros_ouroboros__ouroboros_evaluate` (with a plugin prefix). After ToolSearch returns, the tool becomes callable.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/evaluate/SKILL.md')
    assert 'The Ouroboros MCP tools are often registered as **deferred tools** that must be explicitly loaded before use. **You MUST perform this step before proceeding.**' in text, "expected to find: " + 'The Ouroboros MCP tools are often registered as **deferred tools** that must be explicitly loaded before use. **You MUST perform this step before proceeding.**'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/evolve/SKILL.md')
    assert '2. The tools will typically be named with prefix `mcp__plugin_ouroboros_ouroboros__` (e.g., `ouroboros_evolve_step`, `ouroboros_interview`, `ouroboros_generate_seed`). After ToolSearch returns, the to' in text, "expected to find: " + '2. The tools will typically be named with prefix `mcp__plugin_ouroboros_ouroboros__` (e.g., `ouroboros_evolve_step`, `ouroboros_interview`, `ouroboros_generate_seed`). After ToolSearch returns, the to'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/evolve/SKILL.md')
    assert "**IMPORTANT**: Do NOT skip this step. Do NOT assume MCP tools are unavailable just because they don't appear in your immediate tool list. They are almost always available as deferred tools that need t" in text, "expected to find: " + "**IMPORTANT**: Do NOT skip this step. Do NOT assume MCP tools are unavailable just because they don't appear in your immediate tool list. They are almost always available as deferred tools that need t"[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/evolve/SKILL.md')
    assert 'The Ouroboros MCP tools are often registered as **deferred tools** that must be explicitly loaded before use. **You MUST perform this step before deciding between Path A and Path B.**' in text, "expected to find: " + 'The Ouroboros MCP tools are often registered as **deferred tools** that must be explicitly loaded before use. **You MUST perform this step before deciding between Path A and Path B.**'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/interview/SKILL.md')
    assert "**IMPORTANT**: Do NOT skip this step. Do NOT assume MCP tools are unavailable just because they don't appear in your immediate tool list. They are almost always available as deferred tools that need t" in text, "expected to find: " + "**IMPORTANT**: Do NOT skip this step. Do NOT assume MCP tools are unavailable just because they don't appear in your immediate tool list. They are almost always available as deferred tools that need t"[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/interview/SKILL.md')
    assert 'The Ouroboros MCP tools are often registered as **deferred tools** that must be explicitly loaded before use. **You MUST perform this step before deciding between Path A and Path B.**' in text, "expected to find: " + 'The Ouroboros MCP tools are often registered as **deferred tools** that must be explicitly loaded before use. **You MUST perform this step before deciding between Path A and Path B.**'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/interview/SKILL.md')
    assert '2. The tool will typically be named `mcp__plugin_ouroboros_ouroboros__ouroboros_interview` (with a plugin prefix). After ToolSearch returns, the tool becomes callable.' in text, "expected to find: " + '2. The tool will typically be named `mcp__plugin_ouroboros_ouroboros__ouroboros_interview` (with a plugin prefix). After ToolSearch returns, the tool becomes callable.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/run/SKILL.md')
    assert "**IMPORTANT**: Do NOT skip this step. Do NOT assume MCP tools are unavailable just because they don't appear in your immediate tool list. They are almost always available as deferred tools that need t" in text, "expected to find: " + "**IMPORTANT**: Do NOT skip this step. Do NOT assume MCP tools are unavailable just because they don't appear in your immediate tool list. They are almost always available as deferred tools that need t"[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/run/SKILL.md')
    assert '2. The tools will typically be named with prefix `mcp__plugin_ouroboros_ouroboros__` (e.g., `ouroboros_execute_seed`, `ouroboros_session_status`). After ToolSearch returns, the tools become callable.' in text, "expected to find: " + '2. The tools will typically be named with prefix `mcp__plugin_ouroboros_ouroboros__` (e.g., `ouroboros_execute_seed`, `ouroboros_session_status`). After ToolSearch returns, the tools become callable.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/run/SKILL.md')
    assert 'The Ouroboros MCP tools are often registered as **deferred tools** that must be explicitly loaded before use. **You MUST perform this step before proceeding.**' in text, "expected to find: " + 'The Ouroboros MCP tools are often registered as **deferred tools** that must be explicitly loaded before use. **You MUST perform this step before proceeding.**'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/seed/SKILL.md')
    assert "**IMPORTANT**: Do NOT skip this step. Do NOT assume MCP tools are unavailable just because they don't appear in your immediate tool list. They are almost always available as deferred tools that need t" in text, "expected to find: " + "**IMPORTANT**: Do NOT skip this step. Do NOT assume MCP tools are unavailable just because they don't appear in your immediate tool list. They are almost always available as deferred tools that need t"[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/seed/SKILL.md')
    assert 'The Ouroboros MCP tools are often registered as **deferred tools** that must be explicitly loaded before use. **You MUST perform this step before deciding between Path A and Path B.**' in text, "expected to find: " + 'The Ouroboros MCP tools are often registered as **deferred tools** that must be explicitly loaded before use. **You MUST perform this step before deciding between Path A and Path B.**'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/seed/SKILL.md')
    assert '2. The tool will typically be named `mcp__plugin_ouroboros_ouroboros__ouroboros_generate_seed` (with a plugin prefix). After ToolSearch returns, the tool becomes callable.' in text, "expected to find: " + '2. The tool will typically be named `mcp__plugin_ouroboros_ouroboros__ouroboros_generate_seed` (with a plugin prefix). After ToolSearch returns, the tool becomes callable.'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/status/SKILL.md')
    assert "**IMPORTANT**: Do NOT skip this step. Do NOT assume MCP tools are unavailable just because they don't appear in your immediate tool list. They are almost always available as deferred tools that need t" in text, "expected to find: " + "**IMPORTANT**: Do NOT skip this step. Do NOT assume MCP tools are unavailable just because they don't appear in your immediate tool list. They are almost always available as deferred tools that need t"[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/status/SKILL.md')
    assert '2. The tools will typically be named with prefix `mcp__plugin_ouroboros_ouroboros__` (e.g., `ouroboros_session_status`, `ouroboros_measure_drift`). After ToolSearch returns, the tools become callable.' in text, "expected to find: " + '2. The tools will typically be named with prefix `mcp__plugin_ouroboros_ouroboros__` (e.g., `ouroboros_session_status`, `ouroboros_measure_drift`). After ToolSearch returns, the tools become callable.'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/status/SKILL.md')
    assert 'The Ouroboros MCP tools are often registered as **deferred tools** that must be explicitly loaded before use. **You MUST perform this step before proceeding.**' in text, "expected to find: " + 'The Ouroboros MCP tools are often registered as **deferred tools** that must be explicitly loaded before use. **You MUST perform this step before proceeding.**'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/unstuck/SKILL.md')
    assert "**IMPORTANT**: Do NOT skip this step. Do NOT assume MCP tools are unavailable just because they don't appear in your immediate tool list. They are almost always available as deferred tools that need t" in text, "expected to find: " + "**IMPORTANT**: Do NOT skip this step. Do NOT assume MCP tools are unavailable just because they don't appear in your immediate tool list. They are almost always available as deferred tools that need t"[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/unstuck/SKILL.md')
    assert '2. The tool will typically be named `mcp__plugin_ouroboros_ouroboros__ouroboros_lateral_think` (with a plugin prefix). After ToolSearch returns, the tool becomes callable.' in text, "expected to find: " + '2. The tool will typically be named `mcp__plugin_ouroboros_ouroboros__ouroboros_lateral_think` (with a plugin prefix). After ToolSearch returns, the tool becomes callable.'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/unstuck/SKILL.md')
    assert 'The Ouroboros MCP tools are often registered as **deferred tools** that must be explicitly loaded before use. **You MUST perform this step before proceeding.**' in text, "expected to find: " + 'The Ouroboros MCP tools are often registered as **deferred tools** that must be explicitly loaded before use. **You MUST perform this step before proceeding.**'[:80]

