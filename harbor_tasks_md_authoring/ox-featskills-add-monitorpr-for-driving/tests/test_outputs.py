"""Behavioral checks for ox-featskills-add-monitorpr-for-driving (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ox")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/monitor-pr/SKILL.md')
    assert "`jq -s` and iterate across pages (e.g. `jq -s '[.[].data.repository.pullRequest.reviewThreads.nodes[]] | ...'`)." in text, "expected to find: " + "`jq -s` and iterate across pages (e.g. `jq -s '[.[].data.repository.pullRequest.reviewThreads.nodes[]] | ...'`)."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/monitor-pr/SKILL.md')
    assert 'failing=$(jq \'[.[] | select(.bucket=="fail" or .bucket=="cancel")] | length\' <<<"$checks")' in text, "expected to find: " + 'failing=$(jq \'[.[] | select(.bucket=="fail" or .bucket=="cancel")] | length\' <<<"$checks")'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/monitor-pr/SKILL.md')
    assert 'if [ "$failing" = "0" ] && [ "$pending" = "0" ] && [ "$unresolved" = "0" ]; then' in text, "expected to find: " + 'if [ "$failing" = "0" ] && [ "$pending" = "0" ] && [ "$unresolved" = "0" ]; then'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**PR review feedback:** Use the `/monitor-pr` skill to watch an open PR and drive it to green. It streams state via the `Monitor` tool, triages each unresolved thread (including CodeRabbit nitpicks an' in text, "expected to find: " + '**PR review feedback:** Use the `/monitor-pr` skill to watch an open PR and drive it to green. It streams state via the `Monitor` tool, triages each unresolved thread (including CodeRabbit nitpicks an'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- **`ox-*` skill files** (shipped by `ox init` as wrappers for `ox` CLI commands) must be thin relays — agent behavioral guidance belongs in the command's JSON output (`guidance` field), not duplicate" in text, "expected to find: " + "- **`ox-*` skill files** (shipped by `ox init` as wrappers for `ox` CLI commands) must be thin relays — agent behavioral guidance belongs in the command's JSON output (`guidance` field), not duplicate"[:80]

