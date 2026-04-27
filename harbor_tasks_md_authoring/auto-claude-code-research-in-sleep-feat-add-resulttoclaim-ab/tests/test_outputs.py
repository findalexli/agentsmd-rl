"""Behavioral checks for auto-claude-code-research-in-sleep-feat-add-resulttoclaim-ab (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/auto-claude-code-research-in-sleep")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ablation-planner/SKILL.md')
    assert "description: Use when main results pass result-to-claim (claim_supported=yes or partial) and ablation studies are needed for paper submission. Codex designs ablations from a reviewer's perspective, CC" in text, "expected to find: " + "description: Use when main results pass result-to-claim (claim_supported=yes or partial) and ablation studies are needed for paper submission. Codex designs ablations from a reviewer's perspective, CC"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ablation-planner/SKILL.md')
    assert 'Systematically design ablation studies that answer the questions reviewers will ask. Codex leads the design (reviewer perspective), CC reviews feasibility and implements.' in text, "expected to find: " + 'Systematically design ablation studies that answer the questions reviewers will ask. Codex leads the design (reviewer perspective), CC reviews feasibility and implements.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ablation-planner/SKILL.md')
    assert '- **Codex leads the design. CC does not pre-filter or bias the ablation list** before Codex sees it. Codex thinks like a reviewer; CC thinks like an engineer.' in text, "expected to find: " + '- **Codex leads the design. CC does not pre-filter or bias the ablation list** before Codex sees it. Codex thinks like a reviewer; CC thinks like an engineer.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/result-to-claim/SKILL.md')
    assert "description: Use when experiments complete to judge what claims the results support, what they don't, and what evidence is still missing. Codex MCP evaluates results against intended claims and routes" in text, "expected to find: " + "description: Use when experiments complete to judge what claims the results support, what they don't, and what evidence is still missing. Codex MCP evaluates results against intended claims and routes"[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/result-to-claim/SKILL.md')
    assert 'Experiments produce numbers; this gate decides what those numbers *mean*. Collect results from available sources, get a Codex judgment, then auto-route based on the verdict.' in text, "expected to find: " + 'Experiments produce numbers; this gate decides what those numbers *mean*. Collect results from available sources, get a Codex judgment, then auto-route based on the verdict.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/result-to-claim/SKILL.md')
    assert '5. **Multiple rounds of `partial` on the same claim** → record analysis in findings.md, consider whether to narrow the claim scope or switch ideas' in text, "expected to find: " + '5. **Multiple rounds of `partial` on the same claim** → record analysis in findings.md, consider whether to narrow the claim scope or switch ideas'[:80]

