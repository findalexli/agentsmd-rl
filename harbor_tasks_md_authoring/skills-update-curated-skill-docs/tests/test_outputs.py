"""Behavioral checks for skills-update-curated-skill-docs (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/.curated/figma-code-connect-components/SKILL.md')
    assert 'After successful login, the user will have to restart codex. You should finish your answer and tell them so when they try again they can continue with Step 1.' in text, "expected to find: " + 'After successful login, the user will have to restart codex. You should finish your answer and tell them so when they try again they can continue with Step 1.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/.curated/figma-code-connect-components/SKILL.md')
    assert '- Set `[features].rmcp_client = true` in `config.toml` **or** run `codex --enable rmcp_client`' in text, "expected to find: " + '- Set `[features].rmcp_client = true` in `config.toml` **or** run `codex --enable rmcp_client`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/.curated/figma-code-connect-components/SKILL.md')
    assert 'If any MCP call fails because Figma MCP is not connected, pause and set it up:' in text, "expected to find: " + 'If any MCP call fails because Figma MCP is not connected, pause and set it up:'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/.curated/figma-create-design-system-rules/SKILL.md')
    assert 'After successful login, the user will have to restart codex. You should finish your answer and tell them so when they try again they can continue with Step 1.' in text, "expected to find: " + 'After successful login, the user will have to restart codex. You should finish your answer and tell them so when they try again they can continue with Step 1.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/.curated/figma-create-design-system-rules/SKILL.md')
    assert '- Set `[features].rmcp_client = true` in `config.toml` **or** run `codex --enable rmcp_client`' in text, "expected to find: " + '- Set `[features].rmcp_client = true` in `config.toml` **or** run `codex --enable rmcp_client`'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/.curated/figma-create-design-system-rules/SKILL.md')
    assert 'If any MCP call fails because Figma MCP is not connected, pause and set it up:' in text, "expected to find: " + 'If any MCP call fails because Figma MCP is not connected, pause and set it up:'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/.curated/figma-implement-design/SKILL.md')
    assert 'After successful login, the user will have to restart codex. You should finish your answer and tell them so when they try again they can continue with Step 1.' in text, "expected to find: " + 'After successful login, the user will have to restart codex. You should finish your answer and tell them so when they try again they can continue with Step 1.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/.curated/figma-implement-design/SKILL.md')
    assert '- Set `[features].rmcp_client = true` in `config.toml` **or** run `codex --enable rmcp_client`' in text, "expected to find: " + '- Set `[features].rmcp_client = true` in `config.toml` **or** run `codex --enable rmcp_client`'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/.curated/figma-implement-design/SKILL.md')
    assert 'If any MCP call fails because Figma MCP is not connected, pause and set it up:' in text, "expected to find: " + 'If any MCP call fails because Figma MCP is not connected, pause and set it up:'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/.curated/notion-knowledge-capture/SKILL.md')
    assert '- `reference/` — database schemas and templates (e.g., `team-wiki-database.md`, `how-to-guide-database.md`, `faq-database.md`, `decision-log-database.md`, `documentation-database.md`, `learning-databa' in text, "expected to find: " + '- `reference/` — database schemas and templates (e.g., `team-wiki-database.md`, `how-to-guide-database.md`, `faq-database.md`, `decision-log-database.md`, `documentation-database.md`, `learning-databa'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/.curated/notion-knowledge-capture/SKILL.md')
    assert 'description: Capture conversations and decisions into structured Notion pages; use when turning chats/notes into wiki entries, how-tos, decisions, or FAQs with proper linking.' in text, "expected to find: " + 'description: Capture conversations and decisions into structured Notion pages; use when turning chats/notes into wiki entries, how-tos, decisions, or FAQs with proper linking.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/.curated/notion-knowledge-capture/SKILL.md')
    assert 'After successful login, the user will have to restart codex. You should finish your answer and tell them so when they try again they can continue with Step 1.' in text, "expected to find: " + 'After successful login, the user will have to restart codex. You should finish your answer and tell them so when they try again they can continue with Step 1.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/.curated/notion-meeting-intelligence/SKILL.md')
    assert '- `reference/` — template picker and meeting templates (e.g., `template-selection-guide.md`, `status-update-template.md`, `decision-meeting-template.md`, `sprint-planning-template.md`, `one-on-one-tem' in text, "expected to find: " + '- `reference/` — template picker and meeting templates (e.g., `template-selection-guide.md`, `status-update-template.md`, `decision-meeting-template.md`, `sprint-planning-template.md`, `one-on-one-tem'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/.curated/notion-meeting-intelligence/SKILL.md')
    assert 'description: Prepare meeting materials with Notion context and Codex research; use when gathering context, drafting agendas/pre-reads, and tailoring materials to attendees.' in text, "expected to find: " + 'description: Prepare meeting materials with Notion context and Codex research; use when gathering context, drafting agendas/pre-reads, and tailoring materials to attendees.'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/.curated/notion-meeting-intelligence/SKILL.md')
    assert 'After successful login, the user will have to restart codex. You should finish your answer and tell them so when they try again they can continue with Step 1.' in text, "expected to find: " + 'After successful login, the user will have to restart codex. You should finish your answer and tell them so when they try again they can continue with Step 1.'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/.curated/notion-research-documentation/SKILL.md')
    assert '- `reference/` — search tactics, format selection, templates, and citation rules (e.g., `advanced-search.md`, `format-selection-guide.md`, `research-summary-template.md`, `comparison-template.md`, `ci' in text, "expected to find: " + '- `reference/` — search tactics, format selection, templates, and citation rules (e.g., `advanced-search.md`, `format-selection-guide.md`, `research-summary-template.md`, `comparison-template.md`, `ci'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/.curated/notion-research-documentation/SKILL.md')
    assert 'description: Research across Notion and synthesize into structured documentation; use when gathering info from multiple Notion sources to produce briefs, comparisons, or reports with citations.' in text, "expected to find: " + 'description: Research across Notion and synthesize into structured documentation; use when gathering info from multiple Notion sources to produce briefs, comparisons, or reports with citations.'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/.curated/notion-research-documentation/SKILL.md')
    assert 'After successful login, the user will have to restart codex. You should finish your answer and tell them so when they try again they can continue with Step 1.' in text, "expected to find: " + 'After successful login, the user will have to restart codex. You should finish your answer and tell them so when they try again they can continue with Step 1.'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/.curated/notion-spec-to-implementation/SKILL.md')
    assert '- Create the plan via `Notion:notion-create-pages`, include: overview, linked spec, requirements summary, phases, dependencies/risks, and success criteria. Link back to the spec.' in text, "expected to find: " + '- Create the plan via `Notion:notion-create-pages`, include: overview, linked spec, requirements summary, phases, dependencies/risks, and success criteria. Link back to the spec.'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/.curated/notion-spec-to-implementation/SKILL.md')
    assert '- `reference/` — parsing patterns, plan/task templates, progress cadence (e.g., `spec-parsing.md`, `standard-implementation-plan.md`, `task-creation.md`, `progress-tracking.md`).' in text, "expected to find: " + '- `reference/` — parsing patterns, plan/task templates, progress cadence (e.g., `spec-parsing.md`, `standard-implementation-plan.md`, `task-creation.md`, `progress-tracking.md`).'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/.curated/notion-spec-to-implementation/SKILL.md')
    assert '- Fetch the page (`Notion:notion-fetch`) and scan for requirements, acceptance criteria, constraints, and priorities. See `reference/spec-parsing.md` for extraction patterns.' in text, "expected to find: " + '- Fetch the page (`Notion:notion-fetch`) and scan for requirements, acceptance criteria, constraints, and priorities. See `reference/spec-parsing.md` for extraction patterns.'[:80]

