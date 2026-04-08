"""
Task: prql-refactor-remove-2nd-person-from
Repo: PRQL/prql @ efff1bad5f42a6f6cdd10514502028fe41b75db4
PR:   5567

Remove 2nd person pronouns from error messages and add style guidelines to CLAUDE.md.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/prql"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — error message refactoring
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_second_person_in_compiler_messages():
    """No 2nd person pronouns in compiler error/hint string literals."""
    r = subprocess.run(
        ["grep", "-rn", "-E",
         r'"[^"]*\b(you can only|you cannot|are you missing|did you forget|Have you forgotten)\b[^"]*"',
         "prqlc/prqlc/src/semantic/"],
        capture_output=True, text=True, cwd=REPO,
    )
    # grep returns 1 when no matches found (which is what we want)
    assert r.returncode == 1, (
        f"Found 2nd person pronouns in compiler source:\n{r.stdout}"
    )


# [pr_diff] fail_to_pass
def test_ast_expand_correct_replacements():
    """ast_expand.rs uses imperative error messages instead of 2nd person."""
    r = subprocess.run(
        ["python3", "-c", """
content = open('prqlc/prqlc/src/semantic/ast_expand.rs').read()
assert 'self-equality operator requires a column name' in content, \
    "Missing: 'self-equality operator requires a column name'"
assert 'self-equality operator does not support namespace prefix' in content, \
    "Missing: 'self-equality operator does not support namespace prefix'"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_lowering_correct_replacements():
    """lowering.rs uses modal verb hints instead of 2nd person."""
    r = subprocess.run(
        ["python3", "-c", """
content = open('prqlc/prqlc/src/semantic/lowering.rs').read()
assert '`from` statement might be missing?' in content, \
    "Missing hint: '`from` statement might be missing?'"
assert 'column name might be missing?' in content, \
    "Missing hint: 'column name might be missing?'"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_types_correct_replacement():
    """resolver/types.rs uses modal verb hint instead of 2nd person."""
    r = subprocess.run(
        ["python3", "-c", """
content = open('prqlc/prqlc/src/semantic/resolver/types.rs').read()
assert 'Argument might be missing' in content, \
    "Missing hint: 'Argument might be missing'"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_snapshot_tests_updated():
    """Inline snapshot strings in test files reflect the updated messages."""
    r = subprocess.run(
        ["python3", "-c", """
bem = open('prqlc/prqlc/tests/integration/bad_error_messages.rs').read()
assert 'Argument might be missing to function std.group?' in bem, \
    "Snapshot not updated: expected 'Argument might be missing to function std.group?'"
assert '`from` statement might be missing?' in bem, \
    "Snapshot not updated: expected '`from` statement might be missing?'"
assert 'Have you forgotten an argument' not in bem, \
    "Old snapshot still present: 'Have you forgotten an argument'"
assert 'are you missing `from` statement?' not in bem, \
    "Old snapshot still present: 'are you missing `from` statement?'"

sql = open('prqlc/prqlc/tests/integration/sql.rs').read()
assert 'column name might be missing?' in sql, \
    "Snapshot not updated: expected 'column name might be missing?'"
assert 'did you forget to specify the column name?' not in sql, \
    "Old snapshot still present: 'did you forget to specify the column name?'"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_claude_md_error_guidelines():
    """CLAUDE.md documents error message style guidelines."""
    r = subprocess.run(
        ["python3", "-c", """
content = open('CLAUDE.md').read()
assert '## Error Messages' in content or '## Error messages' in content, \
    "CLAUDE.md missing Error Messages section"
lower = content.lower()
assert '2nd person' in lower or 'second person' in lower or 'you/your' in lower, \
    "Guidelines don't mention avoiding 2nd person pronouns"
assert 'might' in lower, \
    "Guidelines should reference modal verb 'might' for hint rewording"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass — regression checks
# ---------------------------------------------------------------------------

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
