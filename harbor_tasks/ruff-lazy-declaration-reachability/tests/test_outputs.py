"""
Task: ruff-lazy-declaration-reachability
Repo: ruff @ 770cca65a1dc44241b503df7b1064a784f970499
PR:   24451

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/ruff"

USE_DEF = Path(REPO) / "crates/ty_python_semantic/src/semantic_index/use_def.rs"
STATIC_LITERAL = Path(REPO) / "crates/ty_python_semantic/src/types/class/static_literal.rs"
ENUMS = Path(REPO) / "crates/ty_python_semantic/src/types/enums.rs"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — repo CI checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_compilation():
    """Crate ty_python_semantic must compile without errors."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty_python_semantic"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"cargo check failed:\n{r.stderr.decode()[-2000:]}"
    )


# [repo_tests] pass_to_pass
def test_repo_fmt():
    """Repo code must be formatted according to rustfmt standards (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--all", "--check"],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"cargo fmt check failed (formatting issues found):\n{r.stdout.decode()[-500:]}"
    )


# [repo_tests] pass_to_pass
def test_repo_clippy():
    """Repo code must pass clippy linting for ty_python_semantic (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "ty_python_semantic", "--all-targets", "--all-features", "--", "-D", "warnings"],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"cargo clippy failed:\n{r.stderr.decode()[-1000:]}"
    )


# [repo_tests] pass_to_pass
def test_repo_unit_tests():
    """ty_python_semantic library unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_python_semantic", "--lib", "--no-fail-fast"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"Unit tests failed:\n{r.stderr.decode()[-1000:]}"
    )


# [repo_tests] pass_to_pass
def test_repo_class_mdtests():
    """Class-related mdtests pass — covers static_literal.rs call site (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_python_semantic", "--test", "mdtest", "--", "mdtest::class"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"Class mdtests failed:\n{r.stderr.decode()[-1000:]}"
    )


# [repo_tests] pass_to_pass
def test_repo_enum_mdtests():
    """Enum-related mdtests pass — covers enums.rs call site (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_python_semantic", "--test", "mdtest", "--", "mdtest::enums"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"Enum mdtests failed:\n{r.stderr.decode()[-1000:]}"
    )


# [repo_tests] pass_to_pass
def test_repo_corpus_tests():
    """Corpus tests (no-panic tests on real-world code) pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_python_semantic", "--test", "corpus"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"Corpus tests failed:\n{r.stderr.decode()[-1000:]}"
    )


# [repo_tests] pass_to_pass
def test_repo_ruff_db_unit_tests():
    """ruff_db library unit tests pass — foundational crate for ty_python_semantic (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ruff_db", "--lib", "--no-fail-fast"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"ruff_db unit tests failed:\n{r.stderr.decode()[-1000:]}"
    )


# [repo_tests] pass_to_pass
def test_repo_ty_unit_tests():
    """ty library unit tests pass — consumer of ty_python_semantic (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty", "--lib", "--no-fail-fast"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"ty unit tests failed:\n{r.stderr.decode()[-1000:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — method rename and logic restructure
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_any_reachable_method_exists():
    """DeclarationsIterator must have an any_reachable method (renamed from all_reachable)."""
    src = USE_DEF.read_text()
    # Method definition must exist
    assert re.search(r"fn\s+any_reachable\b", src), (
        "Expected fn any_reachable in use_def.rs"
    )
    # Old method name must NOT exist as a definition
    assert not re.search(r"fn\s+all_reachable\b", src), (
        "Old fn all_reachable should not exist in use_def.rs"
    )


# [pr_diff] fail_to_pass
def test_lazy_evaluation_pattern():
    """any_reachable must evaluate predicate before reachability (lazy evaluation)."""
    src = USE_DEF.read_text()

    # Find the any_reachable method body
    match = re.search(
        r"fn\s+any_reachable\b.*?\n\s*\}(?=\s*\n\s*\})",
        src,
        re.DOTALL,
    )
    assert match, "Could not find any_reachable method body"
    body = match.group(0)

    # Must NOT use the old filter-then-all pattern (evaluates reachability for ALL decls first)
    has_filter_all = ".filter(" in body and ".all(" in body
    assert not has_filter_all, (
        "any_reachable should not use .filter().all() — "
        "predicate must be checked before reachability for lazy evaluation"
    )

    # The predicate must be checked before reachability evaluation (cheap before expensive)
    pred_pos = body.find("predicate(")
    eval_pos = body.find(".evaluate(")
    assert pred_pos != -1, "predicate() call not found in any_reachable"
    assert eval_pos != -1, ".evaluate() call not found in any_reachable"
    assert pred_pos < eval_pos, (
        "predicate must be checked BEFORE reachability .evaluate() for lazy evaluation"
    )


# [pr_diff] fail_to_pass
def test_call_sites_updated():
    """Both call sites must use any_reachable with is_defined_and (De Morgan transform)."""
    for fpath, label in [
        (STATIC_LITERAL, "static_literal.rs"),
        (ENUMS, "enums.rs"),
    ]:
        src = fpath.read_text()
        assert ".any_reachable(" in src, (
            f"{label} must call .any_reachable(), not .all_reachable()"
        )
        assert ".all_reachable(" not in src, (
            f"{label} still has old .all_reachable() call"
        )
        assert "is_defined_and(" in src, (
            f"{label} must use is_defined_and() (De Morgan dual of is_undefined_or)"
        )


# [pr_diff] fail_to_pass
def test_no_stale_all_reachable_calls():
    """No remaining .all_reachable( calls in the crate source."""
    r = subprocess.run(
        ["grep", "-rn", r"\.all_reachable(", "crates/ty_python_semantic/src/"],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    # grep returns 0 if matches found, 1 if no matches
    assert r.returncode != 0, (
        f"Stale .all_reachable() calls found:\n{r.stdout.decode()}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_any_reachable_not_stub():
    """any_reachable method must have real logic, not just a stub."""
    src = USE_DEF.read_text()
    match = re.search(
        r"fn\s+any_reachable\b.*?\n\s*\}(?=\s*\n\s*\})",
        src,
        re.DOTALL,
    )
    assert match, "Could not find any_reachable method body"
    body = match.group(0)

    # Must contain key logic elements: predicates, reachability_constraints, evaluate
    assert "predicates" in body, "Method body must reference predicates"
    assert "reachability_constraints" in body, "Method body must reference reachability_constraints"
    assert ".evaluate(" in body, "Method body must call .evaluate()"
    assert "is_always_false" in body, "Method body must check is_always_false()"
    # Must have meaningful length (not just `todo!()` or `unimplemented!()`)
    lines = [l.strip() for l in body.split("\n") if l.strip() and not l.strip().startswith("//")]
    assert len(lines) >= 8, f"Method body too short ({len(lines)} lines) — likely a stub"
