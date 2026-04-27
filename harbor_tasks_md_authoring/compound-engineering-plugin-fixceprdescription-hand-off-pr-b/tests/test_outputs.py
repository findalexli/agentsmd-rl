"""Behavioral checks for compound-engineering-plugin-fixceprdescription-hand-off-pr-b (markdown_authoring task).

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
    text = _read('plugins/compound-engineering/AGENTS.md')
    assert '- [ ] When shell is the only option (e.g., `ast-grep`, `bundle show`, git commands), instruct one simple command at a time — no action chaining (`cmd1 && cmd2`, `cmd1 ; cmd2`) and no error suppression' in text, "expected to find: " + '- [ ] When shell is the only option (e.g., `ast-grep`, `bundle show`, git commands), instruct one simple command at a time — no action chaining (`cmd1 && cmd2`, `cmd1 ; cmd2`) and no error suppression'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/AGENTS.md')
    assert "Keep rationale at the highest-level location that covers it; restate behavioral directives at the point they take effect. A 500-line skill shouldn't hinge on the agent remembering line 9 by line 400. " in text, "expected to find: " + "Keep rationale at the highest-level location that covers it; restate behavioral directives at the point they take effect. A 500-line skill shouldn't hinge on the agent remembering line 9 by line 400. "[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/AGENTS.md')
    assert "Every line in `SKILL.md` loads on every invocation. Include rationale only when it changes what the agent does at runtime — if behavior wouldn't differ without the sentence, cut it." in text, "expected to find: " + "Every line in `SKILL.md` loads on every invocation. Include rationale only when it changes what the agent does at runtime — if behavior wouldn't differ without the sentence, cut it."[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-pr-description/SKILL.md')
    assert 'description: "Write or regenerate a value-first pull-request description (title + body) for the current branch\'s commits or for a specified PR. Use when the user says \'write a PR description\', \'refres' in text, "expected to find: " + 'description: "Write or regenerate a value-first pull-request description (title + body) for the current branch\'s commits or for a specified PR. Use when the user says \'write a PR description\', \'refres'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-pr-description/SKILL.md')
    assert 'The caller decides whether to apply via `gh pr edit`, `gh pr create`, or discard, reading the body from `body_file` (e.g., `--body "$(cat "$BODY_FILE")"`). This skill does NOT call those commands itse' in text, "expected to find: " + 'The caller decides whether to apply via `gh pr edit`, `gh pr create`, or discard, reading the body from `body_file` (e.g., `--body "$(cat "$BODY_FILE")"`). This skill does NOT call those commands itse'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-pr-description/SKILL.md')
    assert 'The quoted sentinel `\'__CE_PR_BODY_END__\'` keeps `$VAR`, backticks, `${...}`, and any literal `EOF` inside the body from being expanded or clashing with the terminator. Keep `echo "$BODY_FILE"` chaine' in text, "expected to find: " + 'The quoted sentinel `\'__CE_PR_BODY_END__\'` keeps `$VAR`, backticks, `${...}`, and any literal `EOF` inside the body from being expanded or clashing with the terminator. Keep `echo "$BODY_FILE"` chaine'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md')
    assert '`ce-pr-description` returns a `{title, body_file}` block (body in an OS temp file). It applies the value-first writing principles, commit classification, sizing, narrative framing, writing voice, visu' in text, "expected to find: " + '`ce-pr-description` returns a `{title, body_file}` block (body in an OS temp file). It applies the value-first writing principles, commit classification, sizing, narrative framing, writing voice, visu'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md')
    assert '**Generate the updated title and body** — load the `ce-pr-description` skill with the PR URL from DU-2 (e.g., `https://github.com/owner/repo/pull/123`). The URL preserves repo/PR identity even when in' in text, "expected to find: " + '**Generate the updated title and body** — load the `ce-pr-description` skill with the PR URL from DU-2 (e.g., `https://github.com/owner/repo/pull/123`). The URL preserves repo/PR identity even when in'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/git-commit-push-pr/SKILL.md')
    assert 'If the PR check returned `state: OPEN`, note the URL -- this is the existing-PR flow. Continue to Step 4 and 5 (commit any pending work and push), then go to Step 7 to ask whether to rewrite the descr' in text, "expected to find: " + 'If the PR check returned `state: OPEN`, note the URL -- this is the existing-PR flow. Continue to Step 4 and 5 (commit any pending work and push), then go to Step 7 to ask whether to rewrite the descr'[:80]

