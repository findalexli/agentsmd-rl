"""
Task: lotti-fix-flickering-projects-page
Repo: matthiasn/lotti @ 33bd45088097cadb36fbc6930f611513cef0ba2e
PR:   2882

Verify: (1) skipLoadingOnReload added to prevent flicker on project detail page,
        (2) feature README documents the live-refresh behavior.
All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/lotti"

DETAIL_PAGE = Path(REPO) / "lib/features/projects/ui/pages/project_details_page.dart"
README = Path(REPO) / "lib/features/projects/README.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Dart file has balanced braces and parentheses."""
    src = DETAIL_PAGE.read_text()
    assert src.count("{") == src.count("}"), "Unbalanced braces in project_details_page.dart"
    assert src.count("(") == src.count(")"), "Unbalanced parentheses in project_details_page.dart"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral fix
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_skip_loading_on_reload():
    """recordAsync.when() must set skipLoadingOnReload to true."""
    src = DETAIL_PAGE.read_text()
    assert "skipLoadingOnReload" in src, \
        "project_details_page.dart should use skipLoadingOnReload on the async .when() call"
    assert re.search(r"skipLoadingOnReload\s*:\s*true", src), \
        "skipLoadingOnReload must be set to true to preserve content during reloads"


# [pr_diff] fail_to_pass
def test_skip_loading_inside_when_call():
    """skipLoadingOnReload appears within the recordAsync.when() invocation context."""
    src = DETAIL_PAGE.read_text()
    when_match = re.search(r"recordAsync\.when\(", src)
    assert when_match, "recordAsync.when() call must exist"
    # The skipLoadingOnReload param should appear between .when( and the loading: callback
    when_block = src[when_match.start():when_match.start() + 200]
    assert "skipLoadingOnReload" in when_block, \
        "skipLoadingOnReload should be a parameter of the recordAsync.when() call"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — README documents live-refresh behavior
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Agent-config (agent_config) — AGENTS.md rule compliance
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass
