"""
Task: tuist-server-contributor-dev-setup
Repo: tuist/tuist @ 37e098781f47d8ba89bf9afe88817671dddecfc2
PR:   9852

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/tuist"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / structure checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Elixir file has balanced defmodule/end structure."""
    ex_file = Path(REPO) / "server" / "lib" / "tuist_web" / "live" / "user_login_live.ex"
    content = ex_file.read_text()
    # Basic structural validation: defmodule present and file has balanced do/end
    assert "defmodule TuistWeb.UserLoginLive do" in content, \
        "user_login_live.ex must define TuistWeb.UserLoginLive module"
    # Check balanced do/end (rough heuristic)
    do_count = len(re.findall(r'\bdo\b', content))
    end_count = len(re.findall(r'\bend\b', content))
    assert do_count == end_count, \
        f"Unbalanced do/end: {do_count} do vs {end_count} end"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests for the code change
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_dev_environment_check_added():
    """user_login_live.ex must query the dev environment status."""
    ex_file = Path(REPO) / "server" / "lib" / "tuist_web" / "live" / "user_login_live.ex"
    content = ex_file.read_text()
    # The mount function must assign a dev environment flag
    assert "Environment.dev?" in content, \
        "user_login_live.ex should call Environment.dev?() to check dev environment"
    # It should be assigned via the pipe operator in the socket assigns
    assert re.search(r'assign\(:dev\?', content), \
        "user_login_live.ex should assign :dev? to the socket"


# [pr_diff] fail_to_pass
def test_dev_login_form_present():
    """Login page must include a form that logs in with the test user credentials."""
    ex_file = Path(REPO) / "server" / "lib" / "tuist_web" / "live" / "user_login_live.ex"
    content = ex_file.read_text()
    # The form must submit to the login endpoint
    assert '"/users/log_in"' in content or "~p\"/users/log_in\"" in content, \
        "Should have a form posting to /users/log_in"
    # Must have the test user email as a hidden input
    assert "tuistrocks@tuist.dev" in content, \
        "Form should include the test user email"
    # Must have the test user password as a hidden input
    assert 'name="user[password]"' in content, \
        "Form should include hidden password field"
    # Must have a submit button for the test user login
    assert "test user" in content.lower(), \
        "Form should have a button mentioning test user"


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — config/documentation update tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — rules from AGENTS.md / CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md global guardrails
def test_no_po_files_modified():
    """Translation .po files must not be modified (only tuistit bot edits those)."""
    import subprocess
    r = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    changed_files = r.stdout.strip().split("\n") if r.stdout.strip() else []
    po_files = [f for f in changed_files if f.endswith(".po")]
    assert len(po_files) == 0, \
        f".po files must not be modified (AGENTS.md guardrail): {po_files}"
