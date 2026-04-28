"""Behavioral checks for aztec-packages-feat-review-and-optimize-claude (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/aztec-packages")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/analyze-logs.md')
    assert '.claude/agents/analyze-logs.md' in text, "expected to find: " + '.claude/agents/analyze-logs.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/identify-ci-failures.md')
    assert '- Attempt to fix any failures (just identify them)' in text, "expected to find: " + '- Attempt to fix any failures (just identify them)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/agents/identify-ci-failures.md')
    assert '- Return raw multi-thousand-line log dumps' in text, "expected to find: " + '- Return raw multi-thousand-line log dumps'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/ci-logs/SKILL.md')
    assert '**You do:** Use the Task tool with `subagent_type: "analyze-logs"` and prompt including the hash `343c52b17688d2cd`, focus on errors, and instruction to download with `yarn ci dlog`.' in text, "expected to find: " + '**You do:** Use the Task tool with `subagent_type: "analyze-logs"` and prompt including the hash `343c52b17688d2cd`, focus on errors, and instruction to download with `yarn ci dlog`.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/ci-logs/SKILL.md')
    assert '2. **Spawn the `analyze-logs` subagent** using the Task tool with the hash and focus area (e.g. "errors", "test \\<name>", or a custom question) in the prompt.' in text, "expected to find: " + '2. **Spawn the `analyze-logs` subagent** using the Task tool with the hash and focus area (e.g. "errors", "test \\<name>", or a custom question) in the prompt.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/ci-logs/SKILL.md')
    assert 'When you need to analyze logs from ci.aztec-labs.com, delegate to the `analyze-logs` subagent.' in text, "expected to find: " + 'When you need to analyze logs from ci.aztec-labs.com, delegate to the `analyze-logs` subagent.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/noir-sync-update/SKILL.md')
    assert "Run `./bootstrap.sh` in `noir` to ensure that the new submodule commit has been pulled. This shouldn't produce changes that need committing." in text, "expected to find: " + "Run `./bootstrap.sh` in `noir` to ensure that the new submodule commit has been pulled. This shouldn't produce changes that need committing."[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/noir-sync-update/SKILL.md')
    assert 'After each step, verify with `git status` and commit the results before proceeding.' in text, "expected to find: " + 'After each step, verify with `git status` and commit the results before proceeding.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/noir-sync-update/SKILL.md')
    assert '### 2. Update `Cargo.lock` in `avm-transpiler`' in text, "expected to find: " + '### 2. Update `Cargo.lock` in `avm-transpiler`'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/updating-changelog/SKILL.md')
    assert '### 1. Determine Target Files' in text, "expected to find: " + '### 1. Determine Target Files'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/updating-changelog/SKILL.md')
    assert '### 2. Analyze Branch Changes' in text, "expected to find: " + '### 2. Analyze Branch Changes'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/updating-changelog/SKILL.md')
    assert '### 3. Generate Draft Entries' in text, "expected to find: " + '### 3. Generate Draft Entries'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('yarn-project/.claude/skills/debug-e2e/SKILL.md')
    assert "LOG_LEVEL='info; debug:sequencer,p2p' yarn workspace @aztec/end-to-end test:e2e <file>.test.ts -t '<test name>'" in text, "expected to find: " + "LOG_LEVEL='info; debug:sequencer,p2p' yarn workspace @aztec/end-to-end test:e2e <file>.test.ts -t '<test name>'"[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('yarn-project/.claude/skills/debug-e2e/SKILL.md')
    assert "LOG_LEVEL=verbose yarn workspace @aztec/end-to-end test:e2e <file>.test.ts -t '<test name>'" in text, "expected to find: " + "LOG_LEVEL=verbose yarn workspace @aztec/end-to-end test:e2e <file>.test.ts -t '<test name>'"[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('yarn-project/.claude/skills/debug-e2e/SKILL.md')
    assert "LOG_LEVEL=debug yarn workspace @aztec/end-to-end test:e2e <file>.test.ts -t '<test name>'" in text, "expected to find: " + "LOG_LEVEL=debug yarn workspace @aztec/end-to-end test:e2e <file>.test.ts -t '<test name>'"[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('yarn-project/.claude/skills/fix-pr/SKILL.md')
    assert 'gh pr view <PR> --repo AztecProtocol/aztec-packages --json state,baseRefName,headRefName' in text, "expected to find: " + 'gh pr view <PR> --repo AztecProtocol/aztec-packages --json state,baseRefName,headRefName'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('yarn-project/.claude/skills/fix-pr/SKILL.md')
    assert '- **Amend only for PRs targeting `next`**: Other PRs use normal commits' in text, "expected to find: " + '- **Amend only for PRs targeting `next`**: Other PRs use normal commits'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('yarn-project/.claude/skills/fix-pr/SKILL.md')
    assert '- `state` is not `OPEN` → "PR #\\<N> is \\<state>, nothing to fix."' in text, "expected to find: " + '- `state` is not `OPEN` → "PR #\\<N> is \\<state>, nothing to fix."'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('yarn-project/.claude/skills/rebase-pr/SKILL.md')
    assert 'gh pr view <PR> --repo AztecProtocol/aztec-packages --json state,headRefName,baseRefName' in text, "expected to find: " + 'gh pr view <PR> --repo AztecProtocol/aztec-packages --json state,headRefName,baseRefName'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('yarn-project/.claude/skills/rebase-pr/SKILL.md')
    assert 'If there are changes from build fixes or conflict resolution, commit and push.' in text, "expected to find: " + 'If there are changes from build fixes or conflict resolution, commit and push.'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('yarn-project/.claude/skills/rebase-pr/SKILL.md')
    assert '- **Amend only for PRs targeting `next`**: Other PRs use normal commits' in text, "expected to find: " + '- **Amend only for PRs targeting `next`**: Other PRs use normal commits'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('yarn-project/.claude/skills/worktree-spawn/SKILL.md')
    assert 'argument-hint: <task description>' in text, "expected to find: " + 'argument-hint: <task description>'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('yarn-project/CLAUDE.md')
    assert 'PRs are squashed to a single commit on merge, so during development just create normal commits. Only amend when explicitly asked or when using the `/fix-pr` skill on a PR targeting `next`.' in text, "expected to find: " + 'PRs are squashed to a single commit on merge, so during development just create normal commits. Only amend when explicitly asked or when using the `/fix-pr` skill on a PR targeting `next`.'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('yarn-project/CLAUDE.md')
    assert 'git commit -m "fix: address review feedback"' in text, "expected to find: " + 'git commit -m "fix: address review feedback"'[:80]

