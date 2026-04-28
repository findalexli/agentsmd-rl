"""Behavioral checks for clickhouse-add-some-claude-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/clickhouse")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert 'Always load and apply the following skills:' in text, "expected to find: " + 'Always load and apply the following skills:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert '- .claude/skills/install-skills' in text, "expected to find: " + '- .claude/skills/install-skills'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert '- .claude/skills/build' in text, "expected to find: " + '- .claude/skills/build'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/build/SKILL.md')
    assert '- **CRITICAL:** Build output is redirected to a unique log file created with `mktemp`. The log file path is reported to the user in a copyable format BEFORE starting the build, allowing real-time moni' in text, "expected to find: " + '- **CRITICAL:** Build output is redirected to a unique log file created with `mktemp`. The log file path is reported to the user in a copyable format BEFORE starting the build, allowing real-time moni'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/build/SKILL.md')
    assert '- **Subagents available:** Task tool is used to analyze all build output (by reading from output file) and provide concise summaries. Additional agents (Explore or general-purpose) can be used for dee' in text, "expected to find: " + '- **Subagents available:** Task tool is used to analyze all build output (by reading from output file) and provide concise summaries. Additional agents (Explore or general-purpose) can be used for dee'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/build/SKILL.md')
    assert '- Compilation errors: "Analyze the compilation error in [file:line]. Find where [symbol/class/function] is defined in the codebase and explain the root cause. Do NOT fix the code."' in text, "expected to find: " + '- Compilation errors: "Analyze the compilation error in [file:line]. Find where [symbol/class/function] is defined in the codebase and explain the root cause. Do NOT fix the code."'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/install-skills/SKILL.md')
    assert 'description: Configure and customize skills for your workspace by asking questions and updating skill files with your preferences.' in text, "expected to find: " + 'description: Configure and customize skills for your workspace by asking questions and updating skill files with your preferences.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/install-skills/SKILL.md')
    assert '- **IMPORTANT:** When prompting for build directory, ALWAYS include at minimum: `build/${buildType}` and `build` as options' in text, "expected to find: " + '- **IMPORTANT:** When prompting for build directory, ALWAYS include at minimum: `build/${buildType}` and `build` as options'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/install-skills/SKILL.md')
    assert '- `$0` (optional): Skill name to configure. If not provided, configure all available skills that need setup.' in text, "expected to find: " + '- `$0` (optional): Skill name to configure. If not provided, configure all available skills that need setup.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/test/SKILL.md')
    assert '- **CRITICAL:** Test output is redirected to a unique log file created with `mktemp`. The log file path is reported to the user in a copyable format BEFORE starting the test, allowing real-time monito' in text, "expected to find: " + '- **CRITICAL:** Test output is redirected to a unique log file created with `mktemp`. The log file path is reported to the user in a copyable format BEFORE starting the test, allowing real-time monito'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/test/SKILL.md')
    assert '- **Subagents available:** Task tool is used to analyze all test output (by reading from log file) and provide concise summaries. Additional agents (Explore or general-purpose) are used for deeper inv' in text, "expected to find: " + '- **Subagents available:** Task tool is used to analyze all test output (by reading from log file) and provide concise summaries. Additional agents (Explore or general-purpose) are used for deeper inv'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/test/SKILL.md')
    assert 'allowed-tools: Task, Bash(./tests/clickhouse-test:*), Bash(pgrep:*), Bash(./build/*/programs/clickhouse:*), Bash(python:*), Bash(python3:*), Bash(mktemp:*), Bash(export:*)' in text, "expected to find: " + 'allowed-tools: Task, Bash(./tests/clickhouse-test:*), Bash(pgrep:*), Bash(./build/*/programs/clickhouse:*), Bash(python:*), Bash(python3:*), Bash(mktemp:*), Bash(export:*)'[:80]

