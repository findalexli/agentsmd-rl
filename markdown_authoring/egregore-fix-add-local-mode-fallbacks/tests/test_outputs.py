"""Behavioral checks for egregore-fix-add-local-mode-fallbacks (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/egregore")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add/SKILL.md')
    assert '**Local mode** (`mode === "local"`): Skip ALL `bin/graph.sh` calls — do NOT run them. Do NOT show any graph-related messaging ("Graph offline", "will sync", Neo4j, etc.).' in text, "expected to find: " + '**Local mode** (`mode === "local"`): Skip ALL `bin/graph.sh` calls — do NOT run them. Do NOT show any graph-related messaging ("Graph offline", "will sync", Neo4j, etc.).'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add/SKILL.md')
    assert '6. Create Artifact node in Neo4j via `bash bin/graph.sh query "..."` (never MCP, suppress raw output — capture in variable, only show status) — **CONNECTED MODE ONLY**' in text, "expected to find: " + '6. Create Artifact node in Neo4j via `bash bin/graph.sh query "..."` (never MCP, suppress raw output — capture in variable, only show status) — **CONNECTED MODE ONLY**'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/add/SKILL.md')
    assert '- Steps 1-5 (fetch, type, quests, topics, file creation) work normally — quest matching reads from `memory/quests/` directory instead of graph query.' in text, "expected to find: " + '- Steps 1-5 (fetch, type, quests, topics, file creation) work normally — quest matching reads from `memory/quests/` directory instead of graph query.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/issue/SKILL.md')
    assert "- **Create mode**: Step 0 context capture — run Bash call 1 (git identity + state) normally; skip Bash call 2's `bin/graph.sh test` line (keep the memory-symlink and egregore.json checks); skip the Ne" in text, "expected to find: " + "- **Create mode**: Step 0 context capture — run Bash call 1 (git identity + state) normally; skip Bash call 2's `bin/graph.sh test` line (keep the memory-symlink and egregore.json checks); skip the Ne"[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/issue/SKILL.md')
    assert '**Local mode** (`mode === "local"`): Skip ALL `bin/graph.sh` and `bin/notify.sh` calls — do NOT run them. Do NOT show any graph-related messaging ("Graph offline", "will sync", Neo4j, etc.).' in text, "expected to find: " + '**Local mode** (`mode === "local"`): Skip ALL `bin/graph.sh` and `bin/notify.sh` calls — do NOT run them. Do NOT show any graph-related messaging ("Graph offline", "will sync", Neo4j, etc.).'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/issue/SKILL.md')
    assert '- **List mode**: Read issues from `memory/knowledge/issues/` directory — parse frontmatter for id, title, status, recipient, created, topics. Render same TUI.' in text, "expected to find: " + '- **List mode**: Read issues from `memory/knowledge/issues/` directory — parse frontmatter for id, title, status, recipient, created, topics. Render same TUI.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/todo/SKILL.md')
    assert '- **Add**: Ensure directory and file exist (see initialization above). Parse text, determine priority, check `memory/quests/` for quest matching (read frontmatter `status: active` from quest files). G' in text, "expected to find: " + '- **Add**: Ensure directory and file exist (see initialization above). Parse text, determine priority, check `memory/quests/` for quest matching (read frontmatter `status: active` from quest files). G'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/todo/SKILL.md')
    assert '- **Done/Cancel**: Read file, filter to active items (status `open`, `blocked`, `deferred`), sort by priority desc then created desc (same order as List display). Positional references (e.g., `todo do' in text, "expected to find: " + '- **Done/Cancel**: Read file, filter to active items (status `open`, `blocked`, `deferred`), sort by priority desc then created desc (same order as List display). Positional references (e.g., `todo do'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/todo/SKILL.md')
    assert '**Local mode** (`mode === "local"`): Skip ALL `bin/graph.sh` calls — do NOT run them. Do NOT show any graph-related messaging ("Graph offline", "will sync", Neo4j, etc.).' in text, "expected to find: " + '**Local mode** (`mode === "local"`): Skip ALL `bin/graph.sh` calls — do NOT run them. Do NOT show any graph-related messaging ("Graph offline", "will sync", Neo4j, etc.).'[:80]

