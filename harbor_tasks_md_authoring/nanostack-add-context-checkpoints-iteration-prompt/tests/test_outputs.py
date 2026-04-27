"""Behavioral checks for nanostack-add-context-checkpoints-iteration-prompt (markdown_authoring task).

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
    text = _read('compound/SKILL.md')
    assert "bin/save-artifact.sh compound '<json with phase, summary including solutions_created, solutions_updated, total_solutions, context_checkpoint including summary, key_files, decisions_made, open_question" in text, "expected to find: " + "bin/save-artifact.sh compound '<json with phase, summary including solutions_created, solutions_updated, total_solutions, context_checkpoint including summary, key_files, decisions_made, open_question"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('compound/SKILL.md')
    assert 'The `context_checkpoint` is mandatory. Summarize how many solutions were created/updated and their types.' in text, "expected to find: " + 'The `context_checkpoint` is mandatory. Summarize how many solutions were created/updated and their types.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plan/SKILL.md')
    assert "After build completes, run `/review`, `/security` and `/qa` **in parallel** using three Agent tool calls in a single message. These three phases are all read-only (they analyze code but don't modify i" in text, "expected to find: " + "After build completes, run `/review`, `/security` and `/qa` **in parallel** using three Agent tool calls in a single message. These three phases are all read-only (they analyze code but don't modify i"[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('plan/SKILL.md')
    assert 'The `context_checkpoint` is mandatory. Summarize the plan scope, list planned files, and document key decisions (e.g., "small scope, 2 files" or "chose X over Y because Z").' in text, "expected to find: " + 'The `context_checkpoint` is mandatory. Summarize the plan scope, list planned files, and document key decisions (e.g., "small scope, 2 files" or "chose X over Y because Z").'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('plan/SKILL.md')
    assert "bin/save-artifact.sh plan '<json with phase, summary including planned_files array, context_checkpoint including summary, key_files, decisions_made, open_questions>'" in text, "expected to find: " + "bin/save-artifact.sh plan '<json with phase, summary including planned_files array, context_checkpoint including summary, key_files, decisions_made, open_questions>'"[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('qa/SKILL.md')
    assert '**If AUTOPILOT is active and running as a parallel sub-agent:** Save the artifact and return your summary to the parent agent. Do not proceed to the next skill — the parent orchestrates the sequence.' in text, "expected to find: " + '**If AUTOPILOT is active and running as a parallel sub-agent:** Save the artifact and return your summary to the parent agent. Do not proceed to the next skill — the parent orchestrates the sequence.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('qa/SKILL.md')
    assert "bin/save-artifact.sh qa '<json with phase, mode, summary including wtf_likelihood, findings, context_checkpoint including summary, key_files, decisions_made, open_questions>'" in text, "expected to find: " + "bin/save-artifact.sh qa '<json with phase, mode, summary including wtf_likelihood, findings, context_checkpoint including summary, key_files, decisions_made, open_questions>'"[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('qa/SKILL.md')
    assert '**If AUTOPILOT is active and running sequentially (no parallel):** Proceed to `/ship`. Show: `Autopilot: qa passed (X tests, 0 failed). Running /ship...`' in text, "expected to find: " + '**If AUTOPILOT is active and running sequentially (no parallel):** Proceed to `/ship`. Show: `Autopilot: qa passed (X tests, 0 failed). Running /ship...`'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('review/SKILL.md')
    assert '**If AUTOPILOT is active and running sequentially (no parallel):** Proceed to the next pending skill (`/security` or `/qa`). Show: `Autopilot: review complete (X findings, 0 blocking). Running /securi' in text, "expected to find: " + '**If AUTOPILOT is active and running sequentially (no parallel):** Proceed to the next pending skill (`/security` or `/qa`). Show: `Autopilot: review complete (X findings, 0 blocking). Running /securi'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('review/SKILL.md')
    assert '**If AUTOPILOT is active and running as a parallel sub-agent:** Save the artifact and return your summary to the parent agent. Do not proceed to the next skill — the parent orchestrates the sequence.' in text, "expected to find: " + '**If AUTOPILOT is active and running as a parallel sub-agent:** Save the artifact and return your summary to the parent agent. Do not proceed to the next skill — the parent orchestrates the sequence.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('review/SKILL.md')
    assert "bin/save-artifact.sh review '<json with phase, mode, summary, scope_drift, findings, conflicts, context_checkpoint including summary, key_files, decisions_made, open_questions>'" in text, "expected to find: " + "bin/save-artifact.sh review '<json with phase, mode, summary, scope_drift, findings, conflicts, context_checkpoint including summary, key_files, decisions_made, open_questions>'"[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('security/SKILL.md')
    assert '**If AUTOPILOT is active and running as a parallel sub-agent:** Save the artifact and return your summary to the parent agent. Do not proceed to the next skill — the parent orchestrates the sequence.' in text, "expected to find: " + '**If AUTOPILOT is active and running as a parallel sub-agent:** Save the artifact and return your summary to the parent agent. Do not proceed to the next skill — the parent orchestrates the sequence.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('security/SKILL.md')
    assert '**If AUTOPILOT is active and running sequentially (no parallel):** Proceed to next pending skill (`/qa` or `/ship`). Show: `Autopilot: security grade X (0 critical, 0 high). Running /qa...`' in text, "expected to find: " + '**If AUTOPILOT is active and running sequentially (no parallel):** Proceed to next pending skill (`/qa` or `/ship`). Show: `Autopilot: security grade X (0 critical, 0 high). Running /qa...`'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('security/SKILL.md')
    assert "bin/save-artifact.sh security '<json with phase, mode, summary, findings, conflicts, context_checkpoint including summary, key_files, decisions_made, open_questions>'" in text, "expected to find: " + "bin/save-artifact.sh security '<json with phase, mode, summary, findings, conflicts, context_checkpoint including summary, key_files, decisions_made, open_questions>'"[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('ship/SKILL.md')
    assert '**2. What could come next.** Suggest 2-3 concrete extensions based on what was built. These should be things the user can say right now to start a new sprint. Frame them as natural next steps, not fea' in text, "expected to find: " + '**2. What could come next.** Suggest 2-3 concrete extensions based on what was built. These should be things the user can say right now to start a new sprint. Frame them as natural next steps, not fea'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('ship/SKILL.md')
    assert "bin/save-artifact.sh ship '<json with phase, summary including pr_number, pr_url, title, status, ci_passed, context_checkpoint including summary, key_files, decisions_made, open_questions>'" in text, "expected to find: " + "bin/save-artifact.sh ship '<json with phase, summary including pr_number, pr_url, title, status, ci_passed, context_checkpoint including summary, key_files, decisions_made, open_questions>'"[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('ship/SKILL.md')
    assert '**1. What was built.** Summarize what the user now has in plain language. Not phase names or artifact counts. What does the thing DO, where is it, and how to use it.' in text, "expected to find: " + '**1. What was built.** Summarize what the user now has in plain language. Not phase names or artifact counts. What does the thing DO, where is it, and how to use it.'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('think/SKILL.md')
    assert "bin/save-artifact.sh think '<json with phase, summary including value_proposition, scope_mode, target_user, narrowest_wedge, key_risk, premise_validated, context_checkpoint including summary, key_file" in text, "expected to find: " + "bin/save-artifact.sh think '<json with phase, summary including value_proposition, scope_mode, target_user, narrowest_wedge, key_risk, premise_validated, context_checkpoint including summary, key_file"[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('think/SKILL.md')
    assert 'The `context_checkpoint` is mandatory. It captures the essence of this phase so downstream phases can restore context without replaying the full conversation. Write a 1-2 sentence summary, list key fi' in text, "expected to find: " + 'The `context_checkpoint` is mandatory. It captures the essence of this phase so downstream phases can restore context without replaying the full conversation. Write a 1-2 sentence summary, list key fi'[:80]

