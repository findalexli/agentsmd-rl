"""
Task: playwright-cli-split-open-goto-skill
Repo: microsoft/playwright @ 0f542ecb2d37ec5bcf4e987d20ac379ccdba9033
PR:   39164

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/playwright"
PROGRAM_TS = Path(REPO) / "packages/playwright/src/mcp/terminal/program.ts"
SKILL_MD = Path(REPO) / "packages/playwright/src/skill/SKILL.md"
CLI_TEST = Path(REPO) / "tests/mcp/cli-misc.spec.ts"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files parse without syntax errors."""
    for ts_file in [PROGRAM_TS, CLI_TEST]:
        content = ts_file.read_text()
        # Basic brace/bracket balance check — catches gross syntax errors
        opens = content.count("{") + content.count("(") + content.count("[")
        closes = content.count("}") + content.count(")") + content.count("]")
        diff = abs(opens - closes)
        assert diff < 5, f"{ts_file.name}: bracket imbalance of {diff} — likely syntax error"
        assert len(content) > 100, f"{ts_file.name}: file too short — likely truncated"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_console_output_emoji_format():
    """Console output messages in program.ts use emoji status prefixes."""
    src = PROGRAM_TS.read_text()
    # The install function should use ✅ for success messages
    assert "✅ Workspace initialized" in src, \
        "program.ts should prefix workspace init message with ✅"
    assert "✅ Skills installed" in src, \
        "program.ts should prefix skills installed message with ✅"


# [pr_diff] fail_to_pass
def test_console_output_backtick_paths():
    """Console output wraps paths in backticks for readability."""
    src = PROGRAM_TS.read_text()
    # Check that the template literal wraps cwd in backticks: `${cwd}`
    assert "`${cwd}`" in src or "\\`${cwd}\\`" in src, \
        "program.ts should wrap cwd path in backticks in workspace init message"
    # Skills installed message should wrap relative path in backticks
    assert "\\`${path.relative" in src, \
        "program.ts should wrap skill dest path in backticks"


# [pr_diff] fail_to_pass


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — SKILL.md update tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass

    # Check multi-tab example
    tab_match = re.search(
        r"## Example: Multi-tab workflow.*?```bash(.*?)```", content, re.DOTALL
    )
    assert tab_match, "SKILL.md should have a Multi-tab workflow example"
    assert "playwright-cli close" in tab_match.group(1), \
        "Multi-tab workflow example should include 'playwright-cli close'"


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub + regression
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_program_ts_not_stub():
    """program.ts install function has real logic, not just stubs."""
    src = PROGRAM_TS.read_text()
    # Verify key functional elements still exist
    assert "async function install" in src, \
        "program.ts should have an install function"
    assert "fs.promises.mkdir" in src, \
        "install function should create directories"
    assert "fs.promises.cp" in src, \
        "install function should copy skill files"
    assert "console.log" in src, \
        "install function should log output"


# [static] pass_to_pass


# [static] pass_to_pass
def test_upstream_test_matches_output():
    """Upstream test for install w/skills expects the new output format."""
    content = CLI_TEST.read_text()
    # The test should expect backtick-wrapped output
    assert "Skills installed to \\`" in content or "Skills installed to `.claude" in content, \
        "cli-misc.spec.ts should expect backtick-wrapped skill install path"
