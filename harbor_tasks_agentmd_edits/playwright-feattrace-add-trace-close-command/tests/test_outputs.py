"""
Task: playwright-feattrace-add-trace-close-command
Repo: playwright @ 21268964f99d52e5a48e24c04df5f6dc9e7fa0bc
PR:   39903

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/playwright"

TRACE_UTILS = Path(REPO) / "packages/playwright-core/src/tools/trace/traceUtils.ts"
TRACE_CLI = Path(REPO) / "packages/playwright-core/src/tools/trace/traceCli.ts"
SKILL_MD = Path(REPO) / "packages/playwright-core/src/tools/trace/SKILL.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files must exist and contain valid content."""
    for ts_file in [TRACE_UTILS, TRACE_CLI]:
        assert ts_file.is_file(), f"Missing: {ts_file}"
        content = ts_file.read_text()
        assert len(content) > 100, f"File too small: {ts_file}"
        assert "import" in content, f"No imports in {ts_file.name}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_close_trace_function_exported():
    """traceUtils.ts must export an async closeTrace function."""
    content = TRACE_UTILS.read_text()
    assert re.search(r'export\s+async\s+function\s+closeTrace', content), \
        "traceUtils.ts must export an async closeTrace function"


# [pr_diff] fail_to_pass
def test_close_trace_removes_directory():
    """closeTrace must remove the trace directory recursively."""
    content = TRACE_UTILS.read_text()
    # Extract the closeTrace function body
    match = re.search(
        r'export\s+async\s+function\s+closeTrace\s*\(\)\s*\{(.*?)\n\}',
        content, re.DOTALL,
    )
    assert match, "closeTrace function not found"
    body = match.group(1)
    # Must check existence and remove recursively
    assert "existsSync" in body, "closeTrace must check if directory exists before removing"
    assert "recursive" in body, "closeTrace must remove directory recursively"


# [pr_diff] fail_to_pass
def test_close_command_registered():
    """traceCli.ts must register a 'close' subcommand."""
    content = TRACE_CLI.read_text()
    assert re.search(r"\.command\(\s*['\"]close['\"]\s*\)", content), \
        "traceCli.ts must register a 'close' command"


# [pr_diff] fail_to_pass
def test_close_command_imports_close_trace():
    """The close command handler must import and call closeTrace from traceUtils."""
    content = TRACE_CLI.read_text()
    # Find the close command block — it should dynamically import closeTrace
    assert "closeTrace" in content, \
        "traceCli.ts must reference closeTrace"
    # Must import from traceUtils (dynamic or static)
    assert re.search(r"import\s*\(\s*['\"]\.\/traceUtils['\"]\s*\)", content) or \
           re.search(r"from\s+['\"]\.\/traceUtils['\"]", content), \
        "close command must import from './traceUtils'"


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Config edit tests (config_edit) — SKILL.md documentation
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
