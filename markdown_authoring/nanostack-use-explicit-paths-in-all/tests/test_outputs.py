"""Behavioral checks for nanostack-use-explicit-paths-in-all (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nanostack")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert "All skills reference scripts as `bin/save-artifact.sh`, `bin/find-artifact.sh`, etc. These paths are relative to the nanostack skill root, not to the user's project directory." in text, "expected to find: " + "All skills reference scripts as `bin/save-artifact.sh`, `bin/find-artifact.sh`, etc. These paths are relative to the nanostack skill root, not to the user's project directory."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert 'This works for all standard installations (git clone and npx). Saving artifacts is not optional — every skill must save its artifact after completing.' in text, "expected to find: " + 'This works for all standard installations (git clone and npx). Saving artifacts is not optional — every skill must save its artifact after completing.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('SKILL.md')
    assert '**When you need to run a bin/ script, prefix it with `~/.claude/skills/nanostack/`:**' in text, "expected to find: " + '**When you need to run a bin/ script, prefix it with `~/.claude/skills/nanostack/`:**'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('compound/SKILL.md')
    assert "~/.claude/skills/nanostack/bin/save-artifact.sh compound '<json with phase, summary including solutions_created, solutions_updated, total_solutions, context_checkpoint including summary, key_files, de" in text, "expected to find: " + "~/.claude/skills/nanostack/bin/save-artifact.sh compound '<json with phase, summary including solutions_created, solutions_updated, total_solutions, context_checkpoint including summary, key_files, de"[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('compound/SKILL.md')
    assert "- **Update, don't duplicate.** If ~/.claude/skills/nanostack/bin/find-solution.sh returns a close match, update that document." in text, "expected to find: " + "- **Update, don't duplicate.** If ~/.claude/skills/nanostack/bin/find-solution.sh returns a close match, update that document."[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('compound/SKILL.md')
    assert '~/.claude/skills/nanostack/bin/save-solution.sh <type> "<title>" "tag1,tag2,tag3"' in text, "expected to find: " + '~/.claude/skills/nanostack/bin/save-solution.sh <type> "<title>" "tag1,tag2,tag3"'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('plan/SKILL.md')
    assert "~/.claude/skills/nanostack/bin/save-artifact.sh plan '<json with phase, summary including planned_files array, context_checkpoint including summary, key_files, decisions_made, open_questions>'" in text, "expected to find: " + "~/.claude/skills/nanostack/bin/save-artifact.sh plan '<json with phase, summary including planned_files array, context_checkpoint including summary, key_files, decisions_made, open_questions>'"[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('plan/SKILL.md')
    assert '~/.claude/skills/nanostack/bin/find-artifact.sh think 2' in text, "expected to find: " + '~/.claude/skills/nanostack/bin/find-artifact.sh think 2'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('qa/SKILL.md')
    assert "~/.claude/skills/nanostack/bin/save-artifact.sh qa '<json with phase, mode, summary including wtf_likelihood, findings, context_checkpoint including summary, key_files, decisions_made, open_questions>" in text, "expected to find: " + "~/.claude/skills/nanostack/bin/save-artifact.sh qa '<json with phase, mode, summary including wtf_likelihood, findings, context_checkpoint including summary, key_files, decisions_made, open_questions>"[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('qa/SKILL.md')
    assert '~/.claude/skills/nanostack/bin/find-artifact.sh plan 2' in text, "expected to find: " + '~/.claude/skills/nanostack/bin/find-artifact.sh plan 2'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('review/SKILL.md')
    assert "~/.claude/skills/nanostack/bin/save-artifact.sh review '<json with phase, mode, summary, scope_drift, findings, conflicts, context_checkpoint including summary, key_files, decisions_made, open_questio" in text, "expected to find: " + "~/.claude/skills/nanostack/bin/save-artifact.sh review '<json with phase, mode, summary, scope_drift, findings, conflicts, context_checkpoint including summary, key_files, decisions_made, open_questio"[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('review/SKILL.md')
    assert '~/.claude/skills/nanostack/bin/find-solution.sh --file <changed-file-path>' in text, "expected to find: " + '~/.claude/skills/nanostack/bin/find-solution.sh --file <changed-file-path>'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('review/SKILL.md')
    assert '~/.claude/skills/nanostack/bin/find-solution.sh "<relevant-keywords>"' in text, "expected to find: " + '~/.claude/skills/nanostack/bin/find-solution.sh "<relevant-keywords>"'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('security/SKILL.md')
    assert "~/.claude/skills/nanostack/bin/save-artifact.sh security '<json with phase, mode, summary, findings, conflicts, context_checkpoint including summary, key_files, decisions_made, open_questions>'" in text, "expected to find: " + "~/.claude/skills/nanostack/bin/save-artifact.sh security '<json with phase, mode, summary, findings, conflicts, context_checkpoint including summary, key_files, decisions_made, open_questions>'"[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('security/SKILL.md')
    assert '~/.claude/skills/nanostack/bin/find-artifact.sh review 30' in text, "expected to find: " + '~/.claude/skills/nanostack/bin/find-artifact.sh review 30'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('security/SKILL.md')
    assert '~/.claude/skills/nanostack/bin/find-artifact.sh plan 2' in text, "expected to find: " + '~/.claude/skills/nanostack/bin/find-artifact.sh plan 2'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('ship/SKILL.md')
    assert "~/.claude/skills/nanostack/bin/save-artifact.sh ship '<json with phase, summary including pr_number, pr_url, title, status, ci_passed, context_checkpoint including summary, key_files, decisions_made, " in text, "expected to find: " + "~/.claude/skills/nanostack/bin/save-artifact.sh ship '<json with phase, summary including pr_number, pr_url, title, status, ci_passed, context_checkpoint including summary, key_files, decisions_made, "[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('ship/SKILL.md')
    assert '~/.claude/skills/nanostack/bin/find-artifact.sh review 2' in text, "expected to find: " + '~/.claude/skills/nanostack/bin/find-artifact.sh review 2'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('ship/SKILL.md')
    assert '~/.claude/skills/nanostack/bin/sprint-journal.sh' in text, "expected to find: " + '~/.claude/skills/nanostack/bin/sprint-journal.sh'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('think/SKILL.md')
    assert "~/.claude/skills/nanostack/bin/save-artifact.sh think '<json with phase, summary including value_proposition, scope_mode, target_user, narrowest_wedge, key_risk, premise_validated, context_checkpoint " in text, "expected to find: " + "~/.claude/skills/nanostack/bin/save-artifact.sh think '<json with phase, summary including value_proposition, scope_mode, target_user, narrowest_wedge, key_risk, premise_validated, context_checkpoint "[:80]

