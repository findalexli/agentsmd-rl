"""Behavioral checks for claude-code-toolkit-refactorsapccaudit-decompose-skillmd-int (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-code-toolkit")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/sapcc-audit/SKILL.md')
    assert 'Read `references/phase-2-dispatch-agents.md` for the full dispatch prompt (11 review areas: over-engineering, dead code, error messages, constructors, interface contracts, copy-paste, HTTP handlers, d' in text, "expected to find: " + 'Read `references/phase-2-dispatch-agents.md` for the full dispatch prompt (11 review areas: over-engineering, dead code, error messages, constructors, interface contracts, copy-paste, HTTP handlers, d'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/sapcc-audit/SKILL.md')
    assert '| Not an sapcc project | Stop immediately. Print: "This does not appear to be an SAP CC Go project (no sapcc imports in go.mod)." |' in text, "expected to find: " + '| Not an sapcc project | Stop immediately. Print: "This does not appear to be an SAP CC Go project (no sapcc imports in go.mod)." |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/sapcc-audit/SKILL.md')
    assert '| Phase 2 begins | `references/phase-2-dispatch-agents.md` | Full dispatch prompt and per-domain review checklist (11 areas) |' in text, "expected to find: " + '| Phase 2 begins | `references/phase-2-dispatch-agents.md` | Full dispatch prompt and per-domain review checklist (11 areas) |'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/sapcc-audit/references/output-templates.md')
    assert 'Some findings may overlap (e.g., dead-code agent and architecture agent flag the same unused function). Deduplicate by `file:line`. When two agents flag the same location, keep the finding with the hi' in text, "expected to find: " + 'Some findings may overlap (e.g., dead-code agent and architecture agent flag the same unused function). Deduplicate by `file:line`. When two agents flag the same location, keep the finding with the hi'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/sapcc-audit/references/output-templates.md')
    assert '| MUST-FIX | Would block the PR: data loss, interface violation, wrong behavior | Always include; leads the report |' in text, "expected to find: " + '| MUST-FIX | Would block the PR: data loss, interface violation, wrong behavior | Always include; leads the report |'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/sapcc-audit/references/output-templates.md')
    assert '| NIT | Comment but not blocking: style, naming, minor simplification | Brief — no full code blocks needed |' in text, "expected to find: " + '| NIT | Comment but not blocking: style, naming, minor simplification | Brief — no full code blocks needed |'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/sapcc-audit/references/phase-1-discover-commands.md')
    assert 'If neither command surfaces an sapcc module path or sapcc imports, stop immediately and report: "This does not appear to be an SAP CC Go project (no sapcc imports in go.mod)."' in text, "expected to find: " + 'If neither command surfaces an sapcc module path or sapcc imports, stop immediately and report: "This does not appear to be an SAP CC Go project (no sapcc imports in go.mod)."'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/sapcc-audit/references/phase-1-discover-commands.md')
    assert '> **Purpose**: Go grep/vet detection commands for mapping the repository and validating it is an sapcc project.' in text, "expected to find: " + '> **Purpose**: Go grep/vet detection commands for mapping the repository and validating it is an sapcc project.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/sapcc-audit/references/phase-1-discover-commands.md')
    assert 'Group packages so each agent gets 5–15 files (sweet spot for thorough review). Target 5–8 agents.' in text, "expected to find: " + 'Group packages so each agent gets 5–15 files (sweet spot for thorough review). Target 5–8 agents.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/sapcc-audit/references/phase-2-dispatch-agents.md')
    assert '- **Use gopls MCP tools when available**: `go_workspace` to detect workspace structure, `go_file_context` after reading each .go file for intra-package dependency understanding, `go_symbol_references`' in text, "expected to find: " + '- **Use gopls MCP tools when available**: `go_workspace` to detect workspace structure, `go_file_context` after reading each .go file for intra-package dependency understanding, `go_symbol_references`'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/sapcc-audit/references/phase-2-dispatch-agents.md')
    assert '- **Real review, not checklists.** The primary question for every function is: "Would this pass review?" not "does it follow a checklist." A real reviewer reads code holistically and reacts to archite' in text, "expected to find: " + '- **Real review, not checklists.** The primary question for every function is: "Would this pass review?" not "does it follow a checklist." A real reviewer reads code holistically and reacts to archite'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/sapcc-audit/references/phase-2-dispatch-agents.md')
    assert '- **Segment by package, not by concern.** Dispatch agents by package groups, NOT by concern area. Each agent reviews its packages holistically (errors + architecture + patterns + tests together), exac' in text, "expected to find: " + '- **Segment by package, not by concern.** Dispatch agents by package groups, NOT by concern area. Each agent reviews its packages holistically (errors + architecture + patterns + tests together), exac'[:80]

