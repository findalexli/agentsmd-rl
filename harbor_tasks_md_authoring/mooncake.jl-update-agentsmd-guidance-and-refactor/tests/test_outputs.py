"""Behavioral checks for mooncake.jl-update-agentsmd-guidance-and-refactor (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mooncake.jl")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/inspect/SKILL.md')
    assert "Inspects Mooncake's internal AD pipeline only. For allocation, world-age, or compiler-boundary debugging, see `docs/src/developer_documentation/advanced_debugging.md`." in text, "expected to find: " + "Inspects Mooncake's internal AD pipeline only. For allocation, world-age, or compiler-boundary debugging, see `docs/src/developer_documentation/advanced_debugging.md`."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/inspect/SKILL.md')
    assert 'description: Inspect the AD pipeline IR for a Julia function at each Mooncake compilation stage.' in text, "expected to find: " + 'description: Inspect the AD pipeline IR for a Julia function at each Mooncake compilation stage.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/inspect/SKILL.md')
    assert '3. **What to view** — all stages, a specific stage, a diff between two stages, or world age info' in text, "expected to find: " + '3. **What to view** — all stages, a specific stage, a diff between two stages, or world age info'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/ir-inspect/SKILL.md')
    assert '.claude/skills/ir-inspect/SKILL.md' in text, "expected to find: " + '.claude/skills/ir-inspect/SKILL.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/minimise/SKILL.md')
    assert 'description: Prune a bug fix or new tests down to the smallest correct diff through multiple elimination passes. Use before committing any fix or test addition.' in text, "expected to find: " + 'description: Prune a bug fix or new tests down to the smallest correct diff through multiple elimination passes. Use before committing any fix or test addition.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/minimise/SKILL.md')
    assert '- A new test case added to an existing `@testset` is better than a new `@testset`.' in text, "expected to find: " + '- A new test case added to an existing `@testset` is better than a new `@testset`.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/minimise/SKILL.md')
    assert '- Comments and blank lines added alongside a fix are not load-bearing; remove them' in text, "expected to find: " + '- Comments and blank lines added alongside a fix are not load-bearing; remove them'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Use the canonical test utilities: `Mooncake.TestUtils.test_rule` for new differentiation rules; `TestUtils.test_tangent_splitting` on a concrete value (add constructors to `src/test_resources.jl`) f' in text, "expected to find: " + '- Use the canonical test utilities: `Mooncake.TestUtils.test_rule` for new differentiation rules; `TestUtils.test_tangent_splitting` on a concrete value (add constructors to `src/test_resources.jl`) f'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- When fixing bugs or performance issues (allocations, type instability), prefer minimal inline fixes over new helper functions; make multiple pruning passes before committing to arrive at the smalles' in text, "expected to find: " + '- When fixing bugs or performance issues (allocations, type instability), prefer minimal inline fixes over new helper functions; make multiple pruning passes before committing to arrive at the smalles'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Before adding a new test or test helper, check whether the behaviour is already covered; prefer extending an existing case over introducing a new one, make multiple pruning passes, and keep addition' in text, "expected to find: " + '- Before adding a new test or test helper, check whether the behaviour is already covered; prefer extending an existing case over introducing a new one, make multiple pruning passes, and keep addition'[:80]

