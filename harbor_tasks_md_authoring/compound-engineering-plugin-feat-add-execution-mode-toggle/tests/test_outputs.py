"""Behavioral checks for compound-engineering-plugin-feat-add-execution-mode-toggle (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/compound-engineering-plugin")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Scratch Space:** When authoring or editing skills and agents that need repo-local scratch space, instruct them to use `.context/` for ephemeral collaboration artifacts. Namespace compound-engineer' in text, "expected to find: " + '- **Scratch Space:** When authoring or editing skills and agents that need repo-local scratch space, instruct them to use `.context/` for ephemeral collaboration artifacts. Namespace compound-engineer'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/deepen-plan-beta/SKILL.md')
    assert '3. **Prefer the simplest execution mode** - Use direct agent synthesis by default. Switch to artifact-backed research only when the selected research scope is large enough that returning all findings ' in text, "expected to find: " + '3. **Prefer the simplest execution mode** - Use direct agent synthesis by default. Switch to artifact-backed research only when the selected research scope is large enough that returning all findings '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/deepen-plan-beta/SKILL.md')
    assert 'Use a per-run scratch directory under `.context/compound-engineering/deepen-plan-beta/`, for example `.context/compound-engineering/deepen-plan-beta/<run-id>/` or `.context/compound-engineering/deepen' in text, "expected to find: " + 'Use a per-run scratch directory under `.context/compound-engineering/deepen-plan-beta/`, for example `.context/compound-engineering/deepen-plan-beta/<run-id>/` or `.context/compound-engineering/deepen'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/deepen-plan-beta/SKILL.md')
    assert '6. **Respect product boundaries** - Do not invent new product requirements. If deepening reveals a product-level gap, surface it as an open question or route back to `ce:brainstorm`.' in text, "expected to find: " + '6. **Respect product boundaries** - Do not invent new product requirements. If deepening reveals a product-level gap, surface it as an open question or route back to `ce:brainstorm`.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/resolve-pr-parallel/SKILL.md')
    assert '- Require each resolver agent to return a short status summary to the parent: comment/thread handled, files changed, tests run or skipped, any blocker that still needs human attention, and for questio' in text, "expected to find: " + '- Require each resolver agent to return a short status summary to the parent: comment/thread handled, files changed, tests run or skipped, any blocker that still needs human attention, and for questio'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/resolve-pr-parallel/SKILL.md')
    assert 'If the PR is large enough that even batched short returns are likely to get noisy, use a per-run scratch directory such as `.context/compound-engineering/resolve-pr-parallel/<run-id>/`:' in text, "expected to find: " + 'If the PR is large enough that even batched short returns are likely to get noisy, use a per-run scratch directory such as `.context/compound-engineering/resolve-pr-parallel/<run-id>/`:'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/resolve-pr-parallel/SKILL.md')
    assert '- Re-read only the artifacts that are needed to resolve threads, answer reviewer questions, or summarize the batch' in text, "expected to find: " + '- Re-read only the artifacts that are needed to resolve threads, answer reviewer questions, or summarize the batch'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/resolve-todo-parallel/SKILL.md')
    assert 'If the todo set is large enough that even batched short returns are likely to get noisy, use a per-run scratch directory such as `.context/compound-engineering/resolve-todo-parallel/<run-id>/`:' in text, "expected to find: " + 'If the todo set is large enough that even batched short returns are likely to get noisy, use a per-run scratch directory such as `.context/compound-engineering/resolve-todo-parallel/<run-id>/`:'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/resolve-todo-parallel/SKILL.md')
    assert '- Require each resolver agent to return only a short status summary to the parent: todo handled, files changed, tests run or skipped, and any blocker that still needs follow-up' in text, "expected to find: " + '- Require each resolver agent to return only a short status summary to the parent: todo handled, files changed, tests run or skipped, and any blocker that still needs follow-up'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/resolve-todo-parallel/SKILL.md')
    assert '- Re-read only the artifacts that are needed to summarize outcomes, document learnings, or decide whether a todo is truly resolved' in text, "expected to find: " + '- Re-read only the artifacts that are needed to summarize outcomes, document learnings, or decide whether a todo is truly resolved'[:80]

