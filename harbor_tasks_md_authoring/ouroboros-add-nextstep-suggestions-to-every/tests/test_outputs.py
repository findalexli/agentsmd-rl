"""Behavioral checks for ouroboros-add-nextstep-suggestions-to-every (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ouroboros")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/evaluate/SKILL.md')
    assert '- **REJECTED at Stage 1** (mechanical): `📍 Next: Fix the build/test failures above, then ooo evaluate — or ooo ralph for automated fix loop`' in text, "expected to find: " + '- **REJECTED at Stage 1** (mechanical): `📍 Next: Fix the build/test failures above, then ooo evaluate — or ooo ralph for automated fix loop`'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/evaluate/SKILL.md')
    assert '- **REJECTED at Stage 3** (consensus): `📍 Next: ooo interview to re-examine requirements — or ooo unstuck to challenge assumptions`' in text, "expected to find: " + '- **REJECTED at Stage 3** (consensus): `📍 Next: ooo interview to re-examine requirements — or ooo unstuck to challenge assumptions`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/evaluate/SKILL.md')
    assert '- **REJECTED at Stage 2** (semantic): `📍 Next: ooo run to re-execute with fixes — or ooo evolve for iterative refinement`' in text, "expected to find: " + '- **REJECTED at Stage 2** (semantic): `📍 Next: ooo run to re-execute with fixes — or ooo evolve for iterative refinement`'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/evolve/SKILL.md')
    assert '- `stagnated`: `📍 Next: ooo unstuck to break through, then ooo evolve --status <lineage_id> to resume`' in text, "expected to find: " + '- `stagnated`: `📍 Next: ooo unstuck to break through, then ooo evolve --status <lineage_id> to resume`'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/evolve/SKILL.md')
    assert '- `failed`: `📍 Next: Check the error above. ooo status to inspect session, or ooo unstuck if blocked`' in text, "expected to find: " + '- `failed`: `📍 Next: Check the error above. ooo status to inspect session, or ooo unstuck if blocked`'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/evolve/SKILL.md')
    assert '- `exhausted`: `📍 Next: ooo evaluate to check best result — or ooo unstuck to try a new approach`' in text, "expected to find: " + '- `exhausted`: `📍 Next: ooo evaluate to check best result — or ooo unstuck to try a new approach`'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/interview/SKILL.md')
    assert '`📍 Next: ooo seed to crystallize these requirements into a specification`' in text, "expected to find: " + '`📍 Next: ooo seed to crystallize these requirements into a specification`'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/interview/SKILL.md')
    assert '📍 Next: `ooo seed` to crystallize these requirements into a specification' in text, "expected to find: " + '📍 Next: `ooo seed` to crystallize these requirements into a specification'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/interview/SKILL.md')
    assert '5. After completion, suggest the next step in `📍 Next:` format:' in text, "expected to find: " + '5. After completion, suggest the next step in `📍 Next:` format:'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ralph/SKILL.md')
    assert '- **Max iterations reached**: `📍 Next: ooo interview to re-examine the problem — or ooo unstuck to try a different approach`' in text, "expected to find: " + '- **Max iterations reached**: `📍 Next: ooo interview to re-examine the problem — or ooo unstuck to try a different approach`'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ralph/SKILL.md')
    assert '- **Success** (QA passed): `📍 Next: ooo evaluate for formal 3-stage verification`' in text, "expected to find: " + '- **Success** (QA passed): `📍 Next: ooo evaluate for formal 3-stage verification`'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ralph/SKILL.md')
    assert '📍 Next: `ooo evaluate` for formal 3-stage verification' in text, "expected to find: " + '📍 Next: `ooo evaluate` for formal 3-stage verification'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/run/SKILL.md')
    assert '- **REVISE**: Show differences/suggestions, then `📍 Next: Fix the issues above, then ooo run to retry — or ooo unstuck if blocked`' in text, "expected to find: " + '- **REVISE**: Show differences/suggestions, then `📍 Next: Fix the issues above, then ooo run to retry — or ooo unstuck if blocked`'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/run/SKILL.md')
    assert '- **FAIL/ESCALATE**: `📍 Next: Review failures above, then ooo run to retry — or ooo unstuck if blocked`' in text, "expected to find: " + '- **FAIL/ESCALATE**: `📍 Next: Review failures above, then ooo run to retry — or ooo unstuck if blocked`'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/run/SKILL.md')
    assert '- **PASS**: `📍 Next: ooo evaluate <session_id> for formal 3-stage verification`' in text, "expected to find: " + '- **PASS**: `📍 Next: ooo evaluate <session_id> for formal 3-stage verification`'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/seed/SKILL.md')
    assert '📍 Next: `ooo run` to execute this seed (requires `ooo setup` first)' in text, "expected to find: " + '📍 Next: `ooo run` to execute this seed (requires `ooo setup` first)'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/seed/SKILL.md')
    assert 'Your seed has been crystallized!' in text, "expected to find: " + 'Your seed has been crystallized!'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/status/SKILL.md')
    assert '- Drift > 0.3: `📍 Warning: significant drift detected. Consider ooo interview to re-clarify, or ooo evolve to course-correct`' in text, "expected to find: " + '- Drift > 0.3: `📍 Warning: significant drift detected. Consider ooo interview to re-clarify, or ooo evolve to course-correct`'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/status/SKILL.md')
    assert '- No drift measured: `📍 Session active — say "am I drifting?" to measure drift, or continue with ooo run`' in text, "expected to find: " + '- No drift measured: `📍 Session active — say "am I drifting?" to measure drift, or continue with ooo run`'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/status/SKILL.md')
    assert '- Drift ≤ 0.3: `📍 On track — continue with ooo run or ooo evaluate when ready`' in text, "expected to find: " + '- Drift ≤ 0.3: `📍 On track — continue with ooo run or ooo evaluate when ready`'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/unstuck/SKILL.md')
    assert '📍 Next: Try the approach above, then `ooo run` to execute — or `ooo interview` to re-examine the problem' in text, "expected to find: " + '📍 Next: Try the approach above, then `ooo run` to execute — or `ooo interview` to re-examine the problem'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/unstuck/SKILL.md')
    assert '- Suggest concrete next steps with a `📍 Next:` action routing back to the workflow' in text, "expected to find: " + '- Suggest concrete next steps with a `📍 Next:` action routing back to the workflow'[:80]

