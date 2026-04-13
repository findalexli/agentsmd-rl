"""
Task: ruff-ty-remove-scope-reachability
Repo: astral-sh/ruff @ 5fd492a95721a158c54d60349b54e5fe4b7cd874
PR:   24457

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/ruff"
SEMANTIC_INDEX_RS = "crates/ty_python_semantic/src/semantic_index.rs"
SCOPE_RS = "crates/ty_python_semantic/src/semantic_index/scope.rs"
BUILDER_RS = "crates/ty_python_semantic/src/semantic_index/builder.rs"
IDE_SUPPORT_RS = "crates/ty_python_semantic/src/types/ide_support.rs"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — dead code removal verification
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_is_scope_reachable():
    """The is_scope_reachable method must be completely removed from semantic_index.rs."""
    r = subprocess.run(
        ["grep", "-c", "fn is_scope_reachable", SEMANTIC_INDEX_RS],
        cwd=REPO, capture_output=True, text=True,
    )
    count = int(r.stdout.strip()) if r.returncode == 0 else 0
    assert count == 0, (
        f"Found {count} definition(s) of is_scope_reachable in semantic_index.rs — "
        "the method must be fully removed"
    )


# [pr_diff] fail_to_pass
def test_no_reachability_field_in_scope():
    """The reachability field must be removed from the Scope struct in scope.rs."""
    r = subprocess.run(
        ["grep", "-c", "reachability:", SCOPE_RS],
        cwd=REPO, capture_output=True, text=True,
    )
    count = int(r.stdout.strip()) if r.returncode == 0 else 0
    assert count == 0, (
        f"Found {count} reachability field reference(s) in scope.rs — "
        "the field must be fully removed from the Scope struct"
    )


# [pr_diff] fail_to_pass
def test_is_range_reachable_uses_ancestor_scopes():
    """is_range_reachable must use ancestor_scopes iteration instead of is_scope_reachable."""
    r = subprocess.run(
        ["grep", "-c", "ancestor_scopes", SEMANTIC_INDEX_RS],
        cwd=REPO, capture_output=True, text=True,
    )
    count = int(r.stdout.strip()) if r.returncode == 0 else 0
    assert count >= 1, (
        "is_range_reachable must use ancestor_scopes to iterate parent scopes — "
        f"found {count} reference(s) to ancestor_scopes in semantic_index.rs"
    )


# [pr_diff] fail_to_pass
def test_ide_support_uses_is_range_reachable():
    """ide_support.rs must use is_range_reachable instead of is_scope_reachable."""
    r = subprocess.run(
        ["grep", "-c", "is_scope_reachable", IDE_SUPPORT_RS],
        cwd=REPO, capture_output=True, text=True,
    )
    count = int(r.stdout.strip()) if r.returncode == 0 else 0
    assert count == 0, (
        f"Found {count} reference(s) to is_scope_reachable in ide_support.rs — "
        "must be replaced with is_range_reachable"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — compilation + regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_cargo_check():
    """ty_python_semantic must compile cleanly after reachability removal."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty_python_semantic"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_cargo_clippy():
    """No clippy warnings on the affected crate after removal."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "ty_python_semantic", "--all-features", "--", "-D", "warnings"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"clippy reported warnings:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_cargo_test_lib():
    """ty_python_semantic library unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_python_semantic", "--lib", "--", "--test-threads=4"],
        cwd=REPO, capture_output=True, text=True, timeout=600,
    )
    assert r.returncode == 0, f"Library tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_cargo_test_mdtest():
    """ty_python_semantic markdown tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_python_semantic", "--test", "mdtest"],
        cwd=REPO, capture_output=True, text=True, timeout=600,
    )
    assert r.returncode == 0, f"Markdown tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_cargo_check_workspace():
    """Full workspace compiles cleanly (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "--workspace"],
        cwd=REPO, capture_output=True, text=True, timeout=600,
    )
    assert r.returncode == 0, f"Workspace check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_cargo_test_corpus():
    """Corpus integration tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_python_semantic", "--test", "corpus"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"Corpus tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_cargo_fmt_check():
    """Code formatting follows rustfmt standards (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--", "--check"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Formatting check failed:\n{r.stderr[-500:]}"
