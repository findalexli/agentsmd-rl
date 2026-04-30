"""Behavioral checks for skills-refskills-enforce-skill-independence (markdown_authoring task).

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
    text = _read('skills/commit/SKILL.md')
    assert "**If you're on `main` or `master`, you MUST create a feature branch first** — unless the user explicitly asked to commit to main. Do not ask the user whether to create a branch; just proceed with bran" in text, "expected to find: " + "**If you're on `main` or `master`, you MUST create a feature branch first** — unless the user explicitly asked to commit to main. Do not ask the user whether to create a branch; just proceed with bran"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/pr-writer/SKILL.md')
    assert 'If on `main` or `master`, create a feature branch and move any uncommitted changes onto it before committing — a PR cannot be opened from the default branch against itself. If there are uncommitted ch' in text, "expected to find: " + 'If on `main` or `master`, create a feature branch and move any uncommitted changes onto it before committing — a PR cannot be opened from the default branch against itself. If there are uncommitted ch'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/pr-writer/SKILL.md')
    assert 'Before creating a PR, ensure all changes are committed **to a feature branch**, not to the default branch.' in text, "expected to find: " + 'Before creating a PR, ensure all changes are committed **to a feature branch**, not to the default branch.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/pr-writer/SKILL.md')
    assert '# Check current branch and for uncommitted changes' in text, "expected to find: " + '# Check current branch and for uncommitted changes'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skill-writer/EVAL.md')
    assert 'Synthesize a new skill named `pi-agent-integration-eval` for working with `@mariozechner/pi-agent-core` as a consumer in downstream libraries.' in text, "expected to find: " + 'Synthesize a new skill named `pi-agent-integration-eval` for working with `@mariozechner/pi-agent-core` as a consumer in downstream libraries.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skill-writer/references/design-principles.md')
    assert "A skill's runtime behavior must not depend on another skill being present. Do not instruct the agent to invoke another skill by name (`run the X skill`, `use \\`sentry-skills:Y\\``, `hand off to Z`), an" in text, "expected to find: " + "A skill's runtime behavior must not depend on another skill being present. Do not instruct the agent to invoke another skill by name (`run the X skill`, `use \\`sentry-skills:Y\\``, `hand off to Z`), an"[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skill-writer/references/design-principles.md')
    assert "Mentioning another skill's name in non-runtime content — provenance logs, audit allowlists, eval prompts meant to be copy-pasted by a human — is fine. The rule targets runtime behavior, not any mentio" in text, "expected to find: " + "Mentioning another skill's name in non-runtime content — provenance logs, audit allowlists, eval prompts meant to be copy-pasted by a human — is fine. The rule targets runtime behavior, not any mentio"[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/skill-writer/references/design-principles.md')
    assert '| "If there are uncommitted changes, commit them first." | "Run the `sentry-skills:commit` skill before proceeding." |' in text, "expected to find: " + '| "If there are uncommitted changes, commit them first." | "Run the `sentry-skills:commit` skill before proceeding." |'[:80]

