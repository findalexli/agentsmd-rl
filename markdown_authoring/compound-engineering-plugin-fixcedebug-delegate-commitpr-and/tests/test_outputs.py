"""Behavioral checks for compound-engineering-plugin-fixcedebug-delegate-commitpr-and (markdown_authoring task).

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
    assert '- **Type selection — classify by intent, not diff shape.** Where `fix:` and `feat:` could both seem to fit, default to `fix:`: a change that remedies broken or missing behavior is `fix:` even when imp' in text, "expected to find: " + '- **Type selection — classify by intent, not diff shape.** Where `fix:` and `feat:` could both seem to fit, default to `fix:`: a change that remedies broken or missing behavior is `fix:` even when imp'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- **Never use `!` or a `BREAKING CHANGE:` footer without explicit user confirmation.** These markers trigger release-please's automatic major version bump — a decision the user may not want even when " in text, "expected to find: " + "- **Never use `!` or a `BREAKING CHANGE:` footer without explicit user confirmation.** These markers trigger release-please's automatic major version bump — a decision the user may not want even when "[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-commit-push-pr/SKILL.md')
    assert 'When using conventional commits, choose the type that most precisely describes the change. Where `fix:` and `feat:` both seem to fit, default to `fix:`: a change that remedies broken or missing behavi' in text, "expected to find: " + 'When using conventional commits, choose the type that most precisely describes the change. Where `fix:` and `feat:` both seem to fit, default to `fix:`: a change that remedies broken or missing behavi'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-commit/SKILL.md')
    assert 'When using conventional commits, choose the type that most precisely describes the change (the type list above). Where `fix:` and `feat:` both seem to fit, default to `fix:`: a change that remedies br' in text, "expected to find: " + 'When using conventional commits, choose the type that most precisely describes the change (the type list above). Where `fix:` and `feat:` both seem to fit, default to `fix:`: a change that remedies br'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-debug/SKILL.md')
    assert "- If the current branch is the default branch, ask whether to create a feature branch first using the platform's blocking question tool (see Phase 2 for the per-platform names). To detect the default " in text, "expected to find: " + "- If the current branch is the default branch, ask whether to create a feature branch first using the platform's blocking question tool (see Phase 2 for the per-platform names). To detect the default "[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-debug/SKILL.md')
    assert 'Options 1 and 2 are terminal — running either ends the skill. Options 3 and 4 are additive: after the chosen action completes, re-prompt with the remaining options (excluding the one just completed an' in text, "expected to find: " + 'Options 1 and 2 are terminal — running either ends the skill. Options 3 and 4 are additive: after the chosen action completes, re-prompt with the remaining options (excluding the one just completed an'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-debug/SKILL.md')
    assert '4. **Post findings to the issue first** — reply on the tracker with confirmed root cause, verified reproduction, relevant code references, and suggested fix direction (include only when entry came fro' in text, "expected to find: " + '4. **Post findings to the issue first** — reply on the tracker with confirmed root cause, verified reproduction, relevant code references, and suggested fix direction (include only when entry came fro'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-pr-description/SKILL.md')
    assert '- **Type** is chosen by intent, not file extension or diff shape. `feat` for new functionality, `fix` for a bug fix, `refactor` for a behavior-preserving change, `docs` for doc-only, `chore` for tooli' in text, "expected to find: " + '- **Type** is chosen by intent, not file extension or diff shape. `feat` for new functionality, `fix` for a bug fix, `refactor` for a behavior-preserving change, `docs` for doc-only, `chore` for tooli'[:80]

