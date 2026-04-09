"""
Task: ruff-ty-remove-all-definitely-bound
Repo: astral-sh/ruff @ 55f667ba3924e8f44b1f4acdabfb0b5c0cfffe12
PR:   24482

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/ruff"
INFER_RS = "crates/ty_python_semantic/src/types/infer.rs"
BUILDER_RS = "crates/ty_python_semantic/src/types/infer/builder.rs"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — dead code removal verification
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_all_definitely_bound_in_infer_rs():
    """The unused all_definitely_bound field must be completely removed from infer.rs."""
    r = subprocess.run(
        ["grep", "-c", "all_definitely_bound", INFER_RS],
        cwd=REPO, capture_output=True, text=True,
    )
    # grep -c returns exit 1 when no matches found (desired state)
    count = int(r.stdout.strip()) if r.returncode == 0 else 0
    assert count == 0, (
        f"Found {count} reference(s) to all_definitely_bound in infer.rs — "
        "the dead field must be fully removed"
    )


# [pr_diff] fail_to_pass
def test_no_all_definitely_bound_in_builder_rs():
    """The unused all_definitely_bound field must be completely removed from builder.rs."""
    r = subprocess.run(
        ["grep", "-c", "all_definitely_bound", BUILDER_RS],
        cwd=REPO, capture_output=True, text=True,
    )
    count = int(r.stdout.strip()) if r.returncode == 0 else 0
    assert count == 0, (
        f"Found {count} reference(s) to all_definitely_bound in builder.rs — "
        "the dead field must be fully removed"
    )


# [pr_diff] fail_to_pass
def test_no_all_definitely_bound_condition():
    """The !all_definitely_bound condition must be removed from the extra construction."""
    r = subprocess.run(
        ["grep", "-n", "!all_definitely_bound", BUILDER_RS],
        cwd=REPO, capture_output=True, text=True,
    )
    assert r.returncode != 0, (
        f"Found !all_definitely_bound condition still present in builder.rs:\n{r.stdout}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — compilation + regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_cargo_check():
    """ty_python_semantic must compile cleanly after dead code removal."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty_python_semantic"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_cargo_clippy():
    """No clippy warnings on the affected package after removal."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "ty_python_semantic", "--", "-D", "warnings"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"clippy reported warnings:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_cargo_check_ty():
    """ty crate compiles cleanly (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"cargo check -p ty failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_cargo_fmt_check():
    """All code is properly formatted (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--all", "--check"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"cargo fmt check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_ty_python_semantic_unit():
    """ty_python_semantic unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_python_semantic", "--lib"],
        cwd=REPO, capture_output=True, text=True, timeout=600,
    )
    assert r.returncode == 0, f"unit tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_ty_python_semantic_infer():
    """ty_python_semantic type inference tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_python_semantic", "--lib", "--", "types::infer"],
        cwd=REPO, capture_output=True, text=True, timeout=600,
    )
    assert r.returncode == 0, f"infer tests failed:\n{r.stderr[-500:]}"
