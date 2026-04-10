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


# [static] pass_to_pass
def test_semantic_module_structure():
    """Semantic module has expected directory structure."""
    dirs = [
        "prqlc/prqlc/src/semantic",
        "prqlc/prqlc/src/semantic/resolver",
        "prqlc/prqlc/tests/integration",
    ]
    for d in dirs:
        assert Path(f"{REPO}/{d}").is_dir(), f"Required directory {d} is missing"


# [static] pass_to_pass
def test_rust_source_syntax_valid():
    """Modified Rust source files have valid basic syntax (balanced braces)."""
    files = [
        "prqlc/prqlc/src/semantic/ast_expand.rs",
        "prqlc/prqlc/src/semantic/lowering.rs",
        "prqlc/prqlc/src/semantic/resolver/types.rs",
    ]
    for f in files:
        content = Path(f"{REPO}/{f}").read_text()
        # Basic check: balanced braces (skipping string literals and comments is complex,
        # so we do a simple count which catches major syntax errors)
        open_braces = content.count("{")
        close_braces = content.count("}")
        assert open_braces == close_braces, f"{f}: Unbalanced braces ({open_braces} vs {close_braces})"
        open_parens = content.count("(")
        close_parens = content.count(")")
        assert open_parens == close_parens, f"{f}: Unbalanced parentheses"
        open_brackets = content.count("[")
        close_brackets = content.count("]")
        assert open_brackets == close_brackets, f"{f}: Unbalanced brackets"


# [static] pass_to_pass
def test_error_message_patterns_detectable():
    """Error message patterns (old and new) are detectable in source files."""
    # This test verifies that the source files have the expected structure
    # for error message detection - it passes both before and after the fix
    ast_expand = Path(f"{REPO}/prqlc/prqlc/src/semantic/ast_expand.rs").read_text()
    lowering = Path(f"{REPO}/prqlc/prqlc/src/semantic/lowering.rs").read_text()
    types_rs = Path(f"{REPO}/prqlc/prqlc/src/semantic/resolver/types.rs").read_text()

    # Check that Error::new_simple and push_hint patterns exist
    assert "Error::new_simple(" in ast_expand, "ast_expand.rs: Missing Error::new_simple calls"
    assert ".push_hint(" in lowering, "lowering.rs: Missing push_hint calls"
    assert ".push_hint(" in types_rs, "types.rs: Missing push_hint calls"

    # Check that error message strings exist (either old or new format)
    ast_has_error_msgs = (
        "you can only use column names" in ast_expand or
        "self-equality operator requires" in ast_expand
    )
    assert ast_has_error_msgs, "ast_expand.rs: No recognizable error messages found"


# [static] pass_to_pass
def test_claude_md_structure():
    """CLAUDE.md has expected structure with Development Workflow section."""
    content = Path(f"{REPO}/CLAUDE.md").read_text()

    # These sections exist in both base and fixed commits
    required_sections = [
        "## Development Workflow",
        "## Tests",
        "## Linting",
    ]
    for section in required_sections:
        assert section in content, f"CLAUDE.md missing required section: {section}"

    # Check for code blocks with shell commands
    assert "```sh" in content, "CLAUDE.md missing shell code examples"


# [static] pass_to_pass
def test_snapshot_tests_structure():
    """Snapshot test files have valid structure with insta assertions."""
    bad_error_msgs = Path(f"{REPO}/prqlc/prqlc/tests/integration/bad_error_messages.rs").read_text()
    sql_rs = Path(f"{REPO}/prqlc/prqlc/tests/integration/sql.rs").read_text()

    # Check for insta snapshot patterns
    assert "insta::" in bad_error_msgs or "@r\"" in bad_error_msgs,         "bad_error_messages.rs: Missing insta snapshot patterns"
    assert "insta::" in sql_rs or "@r\"" in sql_rs or "unwrap_err()" in sql_rs,         "sql.rs: Missing test assertions"

    # Check for Error: and Hint: patterns in test snapshots (both old and new formats)
    assert "Error:" in bad_error_msgs, "bad_error_messages.rs: Missing Error patterns"
    assert "Hint:" in bad_error_msgs or "Help:" in bad_error_msgs,         "bad_error_messages.rs: Missing Hint/Help patterns"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — real CI tooling checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_typos_on_semantic():
    """Spell check passes on semantic module files (pass_to_pass)."""
    r = subprocess.run(
        ["pip3", "install", "typos", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["typos", "prqlc/prqlc/src/semantic/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Typos check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_typos_on_tests():
    """Spell check passes on integration test files (pass_to_pass)."""
    r = subprocess.run(
        ["pip3", "install", "typos", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["typos", "prqlc/prqlc/tests/integration/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Typos check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_python_bindings():
    """Python bindings pass ruff linting (pass_to_pass)."""
    r = subprocess.run(
        ["pip3", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["ruff", "check", "prqlc/bindings/prqlc-python/python/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_shellcheck_scripts():
    """CI shell scripts pass shellcheck (pass_to_pass)."""
    # Install shellcheck first
    r = subprocess.run(
        ["apt-get", "update", "-qq"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["apt-get", "install", "-y", "-qq", "shellcheck"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(
        ["shellcheck", ".github/workflows/scripts/set_version.sh",
         ".github/workflows/scripts/util_free_space.sh"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Shellcheck failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_no_dbg_in_rust():
    """No dbg! macros in modified Rust files (pass_to_pass)."""
    r = subprocess.run(
        ["grep", "-rn", "dbg!", "prqlc/prqlc/src/semantic/ast_expand.rs",
         "prqlc/prqlc/src/semantic/lowering.rs", "prqlc/prqlc/src/semantic/resolver/types.rs"],
        capture_output=True, text=True, cwd=REPO,
    )
    # grep returns 1 when no matches (which is what we want)
    assert r.returncode == 1, f"Found dbg! macros in source:\n{r.stdout}"
