"""Behavioral checks for openhands-infra-docsworkflow-enhance-githubworkflow-skill-wi (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/openhands-infra")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/github-workflow/SKILL.md')
    assert 'description: This skill should be used when the user asks to "create a PR", "address review comments", "resolve review threads", "retrigger Q review", "/q review", "respond to Amazon Q", "/codex revie' in text, "expected to find: " + 'description: This skill should be used when the user asks to "create a PR", "address review comments", "resolve review threads", "retrigger Q review", "/q review", "respond to Amazon Q", "/codex revie'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/github-workflow/SKILL.md')
    assert 'When creating a PR, include this checklist in the description. Update it as each step completes:' in text, "expected to find: " + 'When creating a PR, include this checklist in the description. Update it as each step completes:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/github-workflow/SKILL.md')
    assert '5. **Retrigger review** - Comment with appropriate trigger (e.g., `/q review`, `/codex review`)' in text, "expected to find: " + '5. **Retrigger review** - Comment with appropriate trigger (e.g., `/q review`, `/codex review`)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/github-workflow/references/review-commands.md')
    assert '--jq \'[.[] | select(.user.login == "codex[bot]")] | .[-1] | {id: .id, submitted_at: .submitted_at}\'' in text, "expected to find: " + '--jq \'[.[] | select(.user.login == "codex[bot]")] | .[-1] | {id: .id, submitted_at: .submitted_at}\''[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/github-workflow/references/review-commands.md')
    assert '6. **Iterate until no new positive findings** - If new findings appear, repeat from step 1' in text, "expected to find: " + '6. **Iterate until no new positive findings** - If new findings appear, repeat from step 1'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/github-workflow/references/review-commands.md')
    assert '--jq \'[.[] | select(.user.login == "codex[bot]")] | .[-1]\'' in text, "expected to find: " + '--jq \'[.[] | select(.user.login == "codex[bot]")] | .[-1]\''[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **GitHub workflow**: Use `.claude/skills/github-workflow/` for PR creation, review comments, reviewer bots' in text, "expected to find: " + '- **GitHub workflow**: Use `.claude/skills/github-workflow/` for PR creation, review comments, reviewer bots'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**CRITICAL**: All feature development and bug fixes MUST strictly follow the `github-workflow` skill.' in text, "expected to find: " + '**CRITICAL**: All feature development and bug fixes MUST strictly follow the `github-workflow` skill.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Steps 6-7: Address ALL reviewer bot findings (Q, Codex, etc.) and iterate until no new findings' in text, "expected to find: " + '- Steps 6-7: Address ALL reviewer bot findings (Q, Codex, etc.) and iterate until no new findings'[:80]

