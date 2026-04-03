"""
Task: vscode-enable-testsh-scripts-to-take
Repo: vscode @ 73b0fb29377f401a4e2b792b9065e77b9fa19e9e
PR:   microsoft/vscode#306039

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/vscode"
INDEX_JS = Path(REPO) / "test" / "unit" / "electron" / "index.js"
SKILL_MD = Path(REPO) / ".github" / "skills" / "unit-tests" / "SKILL.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified JS file must parse without syntax errors."""
    r = subprocess.run(
        ["node", "--check", str(INDEX_JS)],
        capture_output=True, timeout=30,
    )
    assert r.returncode == 0, (
        f"Syntax error in index.js:\n{r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_help_text_shows_file_positional_usage():
    """Help text must show that bare file paths can be passed as positional args."""
    content = INDEX_JS.read_text()
    # The help text should indicate files can be passed as positional args
    # Look for [file...] in the usage line or mention of positional arguments
    assert "[file" in content or "positional argument" in content.lower(), (
        "Help text should indicate that file paths can be passed as positional arguments"
    )
    # Help should mention the connection between bare files and --run
    content_lower = content.lower()
    has_run_explanation = (
        "--run arguments" in content
        or "--run values" in content
        or ("--run" in content_lower and "positional" in content_lower)
        or ("treated as" in content_lower and "--run" in content)
    )
    assert has_run_explanation, (
        "Help text should explain that bare files are treated as --run arguments"
    )


# [pr_diff] fail_to_pass


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — SKILL.md documentation update
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_existing_run_flag_preserved():
    """The existing --run flag handling must still be present."""
    content = INDEX_JS.read_text()
    # The minimist config must still declare 'run' as a string option
    assert "'run'" in content or '"run"' in content, (
        "minimist config should still include 'run' as a string option"
    )
    # The --run option should still be documented in the help text
    assert "--run" in content, (
        "Help text should still document the --run flag"
    )
