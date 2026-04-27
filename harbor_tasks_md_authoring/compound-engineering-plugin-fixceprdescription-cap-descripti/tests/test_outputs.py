"""Behavioral checks for compound-engineering-plugin-fixceprdescription-cap-descripti (markdown_authoring task).

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
    text = _read('plugins/compound-engineering/skills/ce-commit-push-pr/SKILL.md')
    assert '2. **Preview and confirm.** Read the first two sentences of the Summary from the body file, plus the total line count. Ask the user (per the "Asking the user" convention at the top of this skill): "Ne' in text, "expected to find: " + '2. **Preview and confirm.** Read the first two sentences of the Summary from the body file, plus the total line count. Ask the user (per the "Asking the user" convention at the top of this skill): "Ne'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-commit-push-pr/SKILL.md')
    assert '**Steering discipline.** Pass only what the diff cannot reveal: a user focus ("emphasize the performance win"), a specific framing concern ("this needs to read as a migration not a feature"), or a poi' in text, "expected to find: " + '**Steering discipline.** Pass only what the diff cannot reveal: a user focus ("emphasize the performance win"), a specific framing concern ("this needs to read as a migration not a feature"), or a poi'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-commit-push-pr/SKILL.md')
    assert "3. If confirmed, apply the returned title and body file yourself. This is this skill's responsibility, not the delegated skill's. Substitute `<TITLE>` and `<BODY_FILE>` verbatim from the return block;" in text, "expected to find: " + "3. If confirmed, apply the returned title and body file yourself. This is this skill's responsibility, not the delegated skill's. Substitute `<TITLE>` and `<BODY_FILE>` verbatim from the return block;"[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-commit/SKILL.md')
    assert '**In Claude Code**, the five labeled sections below (Git status, Working tree diff, Current branch, Recent commits, Remote default branch) contain pre-populated data. Use them directly throughout this' in text, "expected to find: " + '**In Claude Code**, the five labeled sections below (Git status, Working tree diff, Current branch, Recent commits, Remote default branch) contain pre-populated data. Use them directly throughout this'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-commit/SKILL.md')
    assert '**On platforms other than Claude Code**, skip to the "Context fallback" section below and run the command there to gather context.' in text, "expected to find: " + '**On platforms other than Claude Code**, skip to the "Context fallback" section below and run the command there to gather context.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-commit/SKILL.md')
    assert '**In Claude Code, skip this section — the data above is already available.**' in text, "expected to find: " + '**In Claude Code, skip this section — the data above is already available.**'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-pr-description/SKILL.md')
    assert '| Large or architecturally significant | Narrative frame + up to 3-5 design-decision callouts + 1-2 sentence test summary + key docs links. Target ~100 lines, cap ~150. For PRs with many mechanisms, u' in text, "expected to find: " + '| Large or architecturally significant | Narrative frame + up to 3-5 design-decision callouts + 1-2 sentence test summary + key docs links. Target ~100 lines, cap ~150. For PRs with many mechanisms, u'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-pr-description/SKILL.md')
    assert "**The return block is a hand-off, not task completion.** When invoked by a parent skill (e.g., `ce-commit-push-pr`), emit the return block and then continue executing the parent's remaining steps (typ" in text, "expected to find: " + "**The return block is a hand-off, not task completion.** When invoked by a parent skill (e.g., `ce-commit-push-pr`), emit the return block and then continue executing the parent's remaining steps (typ"[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/compound-engineering/skills/ce-pr-description/SKILL.md')
    assert '**Value-lead check.** Re-read the first sentence of the Summary. If it describes what was moved around, renamed, or added ("This PR introduces three-tier autofix..."), rewrite to lead with what\'s now ' in text, "expected to find: " + '**Value-lead check.** Re-read the first sentence of the Summary. If it describes what was moved around, renamed, or added ("This PR introduces three-tier autofix..."), rewrite to lead with what\'s now '[:80]

