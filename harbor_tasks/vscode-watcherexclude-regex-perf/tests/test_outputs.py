"""
Task: vscode-watcherexclude-regex-perf
Repo: microsoft/vscode @ 002f2d99e814b4068447558eef47ac8977d1c05a
PR:   306224

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Fix summary:
  - files.contribution.ts: Replace '**/.git/objects/**' glob patterns with
    '.git/objects/**' + '*/.git/objects/**' to avoid pathological RegExp in
    large workspaces. Add explanatory comment.
  - configuration.contribution.ts (sessions): Remove duplicate files.watcherExclude
    block (session override was applying the same pathological patterns).
"""

from pathlib import Path

REPO = Path("/workspace/vscode")
FC_FILE = REPO / "src/vs/workbench/contrib/files/browser/files.contribution.ts"
SC_FILE = REPO / "src/vs/sessions/contrib/configuration/browser/configuration.contribution.ts"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_optimized_patterns_present():
    """New non-pathological watcherExclude patterns added to workbench config default.

    The fix replaces '**/.git/objects/**' (causes pathological regex) with two
    simpler patterns: '.git/objects/**' (root-level) and '*/.git/objects/**'
    (one-level-deep). All three directories must have both variants.
    """
    content = FC_FILE.read_text()

    # Root-level patterns (no leading glob)
    assert "'.git/objects/**': true" in content, \
        "Missing '.git/objects/**' pattern — root-level git objects not excluded"
    assert "'.git/subtree-cache/**': true" in content, \
        "Missing '.git/subtree-cache/**' pattern"
    assert "'.hg/store/**': true" in content, \
        "Missing '.hg/store/**' pattern"

    # One-level-deep patterns (covers subdirectory workspaces)
    assert "'*/.git/objects/**': true" in content, \
        "Missing '*/.git/objects/**' pattern — nested git objects not excluded"
    assert "'*/.git/subtree-cache/**': true" in content, \
        "Missing '*/.git/subtree-cache/**' pattern"
    assert "'*/.hg/store/**': true" in content, \
        "Missing '*/.hg/store/**' pattern"


# [pr_diff] fail_to_pass
def test_pathological_patterns_removed():
    """Old '**/' prefix patterns removed — they generate catastrophically complex RegExp.

    A '**/' prefix followed by another '**' creates an exponential-time regex
    matcher that stalls the file watcher on large repos (issue #305923).
    """
    content = FC_FILE.read_text()

    assert "'**/.git/objects/**': true" not in content, \
        "Old pathological pattern '**/.git/objects/**' still present"
    assert "'**/.git/subtree-cache/**': true" not in content, \
        "Old pathological pattern '**/.git/subtree-cache/**' still present"
    assert "'**/.hg/store/**': true" not in content, \
        "Old pathological pattern '**/.hg/store/**' still present"


# [pr_diff] fail_to_pass
def test_performance_comment_present():
    """Explanatory comment documenting why '**' prefix patterns are avoided."""
    content = FC_FILE.read_text()

    assert "Avoiding a '**' pattern here" in content, \
        "Missing comment: \"Avoiding a '**' pattern here which results in a very complex\""
    assert "slow things down significantly" in content, \
        "Missing performance explanation in comment"


# [pr_diff] fail_to_pass
def test_session_config_duplicate_removed():
    """Duplicate files.watcherExclude removed from sessions configuration.

    The sessions contrib was overriding files.watcherExclude with the same
    pathological patterns, defeating any workbench-level fix.
    """
    content = SC_FILE.read_text()

    assert "'files.watcherExclude':" not in content, \
        "Duplicate files.watcherExclude still present in sessions configuration.contribution.ts"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_watcher_exclude_still_in_workbench():
    """watcherExclude configuration is still defined in the workbench files config.

    The fix replaces the default value; it must NOT remove the setting entirely.
    """
    content = FC_FILE.read_text()

    assert "watcherExclude" in content, \
        "watcherExclude key missing — configuration was removed instead of patched"
    assert "'default':" in content, \
        "'default' section missing from watcherExclude configuration"


# [static] pass_to_pass
def test_config_files_still_register():
    """Both TypeScript files still call their respective registration APIs."""
    fc_content = FC_FILE.read_text()
    sc_content = SC_FILE.read_text()

    assert "registerConfiguration" in fc_content, \
        "files.contribution.ts no longer calls registerConfiguration"
    assert "registerDefaultConfigurations" in sc_content, \
        "configuration.contribution.ts no longer calls registerDefaultConfigurations"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from .github/copilot-instructions.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — .github/copilot-instructions.md:112 @ 002f2d99e814b4068447558eef47ac8977d1c05a
def test_tab_indentation_in_files_contribution():
    """files.contribution.ts uses tabs (not spaces) for indentation per VS Code style guide."""
    content = FC_FILE.read_text()
    lines = content.splitlines()

    tab_indented = sum(1 for line in lines if line.startswith("\t"))
    # 4-space indented lines (would indicate wrong style)
    space_indented = sum(1 for line in lines if line.startswith("    ") and not line.startswith("\t"))

    assert tab_indented > 10, \
        f"Expected tab-indented lines, found only {tab_indented} — file may use spaces"
    assert space_indented < 5, \
        f"Found {space_indented} space-indented lines; file must use tabs per copilot-instructions.md:112"
