"""
Task: prql-refactor-remove-2nd-person-from
Repo: PRQL/prql @ efff1bad5f42a6f6cdd10514502028fe41b75db4
PR:   5567

Remove 2nd person pronouns from error messages and add style guidelines to CLAUDE.md.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

from pathlib import Path

REPO = "/workspace/prql"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — error message refactoring
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_ast_expand_no_second_person():
    """ast_expand.rs error messages must not use 2nd person pronouns."""
    content = Path(f"{REPO}/prqlc/prqlc/src/semantic/ast_expand.rs").read_text()
    # The base commit has "you can only use column names with self-equality operator"
    # and "you cannot use namespace prefix with self-equality operator"
    assert "you can only" not in content.lower(), \
        "ast_expand.rs still contains 'you can only'"
    assert "you cannot" not in content.lower(), \
        "ast_expand.rs still contains 'you cannot'"
    # Anti-stub: error messages about self-equality must still exist
    assert "self-equality" in content.lower() or "self_equality" in content.lower(), \
        "Error about self-equality operator was deleted instead of reworded"
    assert "column name" in content.lower(), \
        "Error message should still reference column names"
    assert "namespace" in content.lower(), \
        "Error message should still reference namespace prefix"


# [pr_diff] fail_to_pass
def test_lowering_no_second_person():
    """lowering.rs hint messages must not use 2nd person pronouns."""
    content = Path(f"{REPO}/prqlc/prqlc/src/semantic/lowering.rs").read_text()
    # The base commit has "are you missing `from` statement?" and
    # "did you forget to specify the column name?"
    assert "are you missing" not in content.lower(), \
        "lowering.rs still contains 'are you missing'"
    assert "did you forget" not in content.lower(), \
        "lowering.rs still contains 'did you forget'"
    # Anti-stub: hint messages must still exist with meaningful content
    assert "from" in content and "missing" in content.lower(), \
        "Hint about missing from statement was deleted instead of reworded"
    assert "column name" in content.lower(), \
        "Hint about column name was deleted instead of reworded"


# [pr_diff] fail_to_pass
def test_types_no_second_person():
    """resolver/types.rs hint message must not use 2nd person pronouns."""
    content = Path(f"{REPO}/prqlc/prqlc/src/semantic/resolver/types.rs").read_text()
    # The base commit has "Have you forgotten an argument"
    assert "have you forgotten" not in content.lower(), \
        "types.rs still contains 'Have you forgotten'"
    # Anti-stub: hint about missing argument must still exist
    assert "argument" in content.lower() and "missing" in content.lower(), \
        "Hint about missing argument was deleted instead of reworded"


# [pr_diff] fail_to_pass


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — CLAUDE.md update
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass


# [static] pass_to_pass
def test_source_files_exist():
    """All modified source files must still exist."""
    files = [
        "prqlc/prqlc/src/semantic/ast_expand.rs",
        "prqlc/prqlc/src/semantic/lowering.rs",
        "prqlc/prqlc/src/semantic/resolver/types.rs",
        "prqlc/prqlc/tests/integration/bad_error_messages.rs",
        "prqlc/prqlc/tests/integration/sql.rs",
        "CLAUDE.md",
    ]
    for f in files:
        assert Path(f"{REPO}/{f}").exists(), f"Required file {f} is missing"
