"""Behavioral checks for codex-add-code-review-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/codex")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/code-review-breaking-changes/SKILL.md')
    assert 'Do not stop after finding one issue; analyze all possible ways breaking changes can happen.' in text, "expected to find: " + 'Do not stop after finding one issue; analyze all possible ways breaking changes can happen.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/code-review-breaking-changes/SKILL.md')
    assert 'Search for breaking changes in external integration surfaces:' in text, "expected to find: " + 'Search for breaking changes in external integration surfaces:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/code-review-breaking-changes/SKILL.md')
    assert '- resuming sessions from existing rollouts' in text, "expected to find: " + '- resuming sessions from existing rollouts'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/code-review-change-size/SKILL.md')
    assert 'If the change is larger, explain whether it can be split into reviewable stages and identify the smallest coherent stage to land first.' in text, "expected to find: " + 'If the change is larger, explain whether it can be split into reviewable stages and identify the smallest coherent stage to land first.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/code-review-change-size/SKILL.md')
    assert 'Unless the change is mechanical the total number of changed lines should not exceed 800 lines.' in text, "expected to find: " + 'Unless the change is mechanical the total number of changed lines should not exceed 800 lines.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/code-review-change-size/SKILL.md')
    assert 'Base the staging suggestion on the actual diff, dependencies, and affected call sites.' in text, "expected to find: " + 'Base the staging suggestion on the actual diff, dependencies, and affected call sites.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/code-review-context/SKILL.md')
    assert '5. Highlight new individual items that can cross >1k tokens as P0. These need an additional manual review.' in text, "expected to find: " + '5. Highlight new individual items that can cross >1k tokens as P0. These need an additional manual review.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/code-review-context/SKILL.md')
    assert '3. No unbounded items - everything injected in the model context must have a bounded size and a hard cap.' in text, "expected to find: " + '3. No unbounded items - everything injected in the model context must have a bounded size and a hard cap.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/code-review-context/SKILL.md')
    assert 'Codex maintains a context (history of messages) that is sent to the model in inference requests.' in text, "expected to find: " + 'Codex maintains a context (history of messages) that is sent to the model in inference requests.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/code-review-testing/SKILL.md')
    assert 'For agent changes prefer integration tests over unit tests. Integration tests are under `core/suite` and use `test_codex` to set up a test instance of codex.' in text, "expected to find: " + 'For agent changes prefer integration tests over unit tests. Integration tests are under `core/suite` and use `test_codex` to set up a test instance of codex.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/code-review-testing/SKILL.md')
    assert '- Provide a list of major logic changes and user-facing behaviors that need to be tested.' in text, "expected to find: " + '- Provide a list of major logic changes and user-facing behaviors that need to be tested.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/code-review-testing/SKILL.md')
    assert 'Check whether there are existing helpers to make tests more streamlined and readable.' in text, "expected to find: " + 'Check whether there are existing helpers to make tests more streamlined and readable.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/code-review/SKILL.md')
    assert 'Use subagents to review code using all code-review-* skills in this repository other than this orchestrator. One subagent per skill. Pass full skill path to subagents. Use xhigh reasoning.' in text, "expected to find: " + 'Use subagents to review code using all code-review-* skills in this repository other than this orchestrator. One subagent per skill. Pass full skill path to subagents. Use xhigh reasoning.'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/code-review/SKILL.md')
    assert 'If the GitHub user running the review is the owner of the pull request add a `code-reviewed` label.' in text, "expected to find: " + 'If the GitHub user running the review is the owner of the pull request add a `code-reviewed` label.'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.codex/skills/code-review/SKILL.md')
    assert 'Make sure to return every single issue. You can return an unlimited number of findings.' in text, "expected to find: " + 'Make sure to return every single issue. You can return an unlimited number of findings.'[:80]

