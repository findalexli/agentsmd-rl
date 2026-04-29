"""
Task: ruff-optimize-place-from-declarations
Repo: ruff @ 398e2a79c488cf2ae59512ea31e00626d7dd8833
PR:   24444

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import re
import subprocess
from pathlib import Path

REPO = "/workspace/ruff"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check():
    """ty_python_semantic crate compiles without errors."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty_python_semantic"],
        cwd=REPO, capture_output=True, timeout=600,
    )
    assert r.returncode == 0, (
        f"cargo check failed:\n{r.stderr.decode()[-3000:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_or_else_method_semantics():
    """Truthiness::or_else lazy method exists and has correct semantics.

    Injects a Rust unit test into types.rs that exercises or_else with
    multiple Truthiness variants and verifies lazy closure invocation.
    Fails on base commit (method does not exist -> compilation error).
    """
    types_rs = Path(REPO) / "crates" / "ty_python_semantic" / "src" / "types.rs"
    original = types_rs.read_text()

    test_module = '''

// === INJECTED TEST START ===
#[cfg(test)]
mod or_else_verification_test {
    use super::Truthiness;
    use std::sync::atomic::{AtomicBool, Ordering};

    #[test]
    fn or_else_always_true_short_circuits() {
        // Use AtomicBool for interior mutability (Fn closure, not FnMut)
        let called = AtomicBool::new(false);
        let result = Truthiness::AlwaysTrue.or_else(|| {
            called.store(true, Ordering::SeqCst);
            Truthiness::AlwaysFalse
        });
        assert!(matches!(result, Truthiness::AlwaysTrue));
        assert!(!called.load(Ordering::SeqCst), "or_else must not call closure when self is AlwaysTrue");
    }

    #[test]
    fn or_else_always_false_delegates() {
        let result = Truthiness::AlwaysFalse.or_else(|| Truthiness::Ambiguous);
        assert!(matches!(result, Truthiness::Ambiguous));

        let result2 = Truthiness::AlwaysFalse.or_else(|| Truthiness::AlwaysTrue);
        assert!(matches!(result2, Truthiness::AlwaysTrue));

        let result3 = Truthiness::AlwaysFalse.or_else(|| Truthiness::AlwaysFalse);
        assert!(matches!(result3, Truthiness::AlwaysFalse));
    }

    #[test]
    fn or_else_ambiguous_propagates() {
        let result = Truthiness::Ambiguous.or_else(|| Truthiness::AlwaysTrue);
        assert!(matches!(result, Truthiness::AlwaysTrue));

        let result2 = Truthiness::Ambiguous.or_else(|| Truthiness::AlwaysFalse);
        assert!(matches!(result2, Truthiness::Ambiguous));

        let result3 = Truthiness::Ambiguous.or_else(|| Truthiness::Ambiguous);
        assert!(matches!(result3, Truthiness::Ambiguous));
    }
}
// === INJECTED TEST END ===
'''
    try:
        types_rs.write_text(original + test_module)
        r = subprocess.run(
            [
                "cargo", "test", "-p", "ty_python_semantic",
                "--", "or_else_verification_test",
            ],
            cwd=REPO, capture_output=True, timeout=600,
            env={**os.environ, "CARGO_PROFILE_DEV_OPT_LEVEL": "1"},
        )
        assert r.returncode == 0, (
            f"or_else test failed:\n{r.stderr.decode()[-3000:]}"
        )
        stdout = r.stdout.decode()
        # Verify all 3 sub-tests ran
        assert "3 passed" in stdout or "test result: ok" in stdout, (
            f"Expected 3 passing tests, got:\n{stdout[-1000:]}"
        )
    finally:
        # Restore original file
        types_rs.write_text(original)


# [pr_diff] fail_to_pass
def test_lazy_deleted_reachability_eval():
    """deleted_reachability uses or_else (lazy) instead of or (eager) in place_from_bindings_impl."""
    place_rs = Path(REPO) / "crates" / "ty_python_semantic" / "src" / "place.rs"
    content = place_rs.read_text()

    # Find the place_from_bindings_impl function and check for or_else usage
    # The fix changes: deleted_reachability = deleted_reachability.or(...)
    # to:              deleted_reachability = deleted_reachability.or_else(|| {...})
    fn_match = re.search(
        r"fn place_from_bindings_impl.*?\n\}",
        content,
        re.DOTALL,
    )
    assert fn_match is not None, "place_from_bindings_impl function not found"
    fn_body = fn_match.group(0)

    # Must use or_else for lazy evaluation of deleted reachability
    assert "deleted_reachability.or_else" in fn_body or "deleted_reachability = deleted_reachability.or_else" in content, (
        "place_from_bindings_impl should use or_else for lazy evaluation of deleted_reachability. "
        "Found eager .or() instead."
    )
    # Must NOT use the eager .or( pattern for deleted_reachability
    eager_pattern = re.search(
        r"deleted_reachability\s*=\s*deleted_reachability\.or\(\s*\n?\s*reachability_constraints\.evaluate",
        fn_body,
    )
    assert eager_pattern is None, (
        "deleted_reachability should use .or_else() (lazy), not .or() (eager)"
    )


# [pr_diff] fail_to_pass
def test_declarations_boundness_evaluator():
    """DeclarationsBoundnessEvaluator enum defined to defer reachability evaluation."""
    place_rs = Path(REPO) / "crates" / "ty_python_semantic" / "src" / "place.rs"
    content = place_rs.read_text()

    # The enum must be defined
    assert "enum DeclarationsBoundnessEvaluator" in content, (
        "DeclarationsBoundnessEvaluator enum not found in place.rs"
    )

    # It must have the two expected variants
    enum_match = re.search(
        r"enum DeclarationsBoundnessEvaluator.*?\{(.*?)\n\}",
        content,
        re.DOTALL,
    )
    assert enum_match is not None, "Could not parse DeclarationsBoundnessEvaluator enum body"
    enum_body = enum_match.group(1)
    assert "AssumeBound" in enum_body, "Missing AssumeBound variant"
    assert "BasedOnUnboundVisibility" in enum_body, "Missing BasedOnUnboundVisibility variant"

    # It must have an evaluate method
    impl_match = re.search(
        r"impl.*DeclarationsBoundnessEvaluator.*\{.*?fn evaluate\(",
        content,
        re.DOTALL,
    )
    assert impl_match is not None, (
        "DeclarationsBoundnessEvaluator must have an evaluate() method"
    )

    # The evaluator must actually be used in place_from_declarations_impl
    fn_match = re.search(
        r"fn place_from_declarations_impl.*?\n\}",
        content,
        re.DOTALL,
    )
    assert fn_match is not None, "place_from_declarations_impl not found"
    fn_body = fn_match.group(0)
    assert "boundness_evaluator" in fn_body.lower() or "DeclarationsBoundnessEvaluator" in fn_body, (
        "DeclarationsBoundnessEvaluator must be used in place_from_declarations_impl"
    )


# [pr_diff] fail_to_pass
def test_is_non_exported_standalone():
    """is_non_exported extracted as standalone function from closure."""
    place_rs = Path(REPO) / "crates" / "ty_python_semantic" / "src" / "place.rs"
    content = place_rs.read_text()

    # Must have a standalone fn is_non_exported (not just a closure)
    fn_pattern = re.search(
        r"\nfn is_non_exported[<(]",
        content,
    )
    assert fn_pattern is not None, (
        "is_non_exported must be a standalone function, not a closure. "
        "Expected 'fn is_non_exported' at module level in place.rs"
    )

    # Verify it takes db, declaration, and requires_explicit_reexport params
    fn_sig_match = re.search(
        r"fn is_non_exported.*?\(.*?db.*?declaration.*?requires_explicit_reexport.*?\)",
        content,
        re.DOTALL,
    )
    assert fn_sig_match is not None, (
        "is_non_exported should take db, declaration, and requires_explicit_reexport parameters"
    )

    # The function should be called in place_from_declarations_impl
    decl_fn = re.search(
        r"fn place_from_declarations_impl.*?\n\}",
        content,
        re.DOTALL,
    )
    assert decl_fn is not None
    assert "is_non_exported(" in decl_fn.group(0), (
        "is_non_exported() must be called in place_from_declarations_impl"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + config checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_crate_tests():
    """Existing ty_python_semantic tests still pass (focused subset)."""
    # Run the place-related tests which directly exercise the changed code
    r = subprocess.run(
        [
            "cargo", "test", "-p", "ty_python_semantic",
            "--", "place", "--test-threads=2",
        ],
        cwd=REPO, capture_output=True, timeout=600,
        env={**os.environ, "CARGO_PROFILE_DEV_OPT_LEVEL": "1"},
    )
    assert r.returncode == 0, (
        f"Existing crate tests failed:\n{r.stderr.decode()[-3000:]}"
    )


# [repo_tests] pass_to_pass
def test_cargo_fmt():
    """Repo's code formatting passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--all", "--check"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"cargo fmt check failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass
def test_cargo_clippy():
    """Repo's clippy linting passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "ty_python_semantic", "--", "-D", "warnings"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Clippy failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass
def test_cargo_doc():
    """Repo's documentation builds without warnings (pass_to_pass)."""
    env = {**os.environ, "RUSTDOCFLAGS": "-D warnings"}
    r = subprocess.run(
        ["cargo", "doc", "--no-deps", "-p", "ty_python_semantic", "--document-private-items"],
        cwd=REPO, capture_output=True, text=True, timeout=300, env=env,
    )
    assert r.returncode == 0, f"cargo doc failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass
def test_cargo_lib_tests():
    """ty_python_semantic library tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_python_semantic", "--lib", "--", "--test-threads=2"],
        cwd=REPO, capture_output=True, text=True, timeout=600,
        env={**os.environ, "CARGO_PROFILE_DEV_OPT_LEVEL": "1"},
    )
    assert r.returncode == 0, f"Library tests failed:\n{r.stderr[-2000:]}"


# [repo_tests] pass_to_pass
def test_cargo_mdtest():
    """Repo's Markdown-based tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_python_semantic", "--test", "mdtest"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
        env={**os.environ, "CARGO_PROFILE_DEV_OPT_LEVEL": "1"},
    )
    assert r.returncode == 0, f"Mdtest failed:\n{r.stderr[-1000:]}"


# [agent_config] pass_to_pass — AGENTS.md:76
def test_no_local_imports():
    """Rust imports are at the top of the file, not inside functions.

    AGENTS.md line 76: 'Rust imports should always go at the top of the file,
    never locally in functions.'
    """
    modified_files = [
        "crates/ty_python_semantic/src/place.rs",
        "crates/ty_python_semantic/src/types.rs",
        "crates/ty_python_semantic/src/semantic_index.rs",
        "crates/ty_python_semantic/src/semantic_index/use_def.rs",
    ]
    for rel_path in modified_files:
        filepath = Path(REPO) / rel_path
        if not filepath.exists():
            continue
        content = filepath.read_text()
        lines = content.split("\n")

        in_function = False
        brace_depth = 0
        fn_start_line = 0

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Track function entry (simplified: look for fn declarations)
            if re.match(r"^\s*(pub(\(crate\))?\s+)?fn\s+\w+", line) and not stripped.startswith("//"):
                in_function = True
                fn_start_line = i
                brace_depth = 0

            if in_function:
                brace_depth += line.count("{") - line.count("}")
                if brace_depth <= 0 and i > fn_start_line:
                    in_function = False

                # Check for use statements inside function bodies
                if in_function and i > fn_start_line and re.match(r"\s+use\s+", line):
                    # Allow use in test modules (cfg(test)) - these often have local imports for convenience
                    if "use super::" not in line and "test" not in rel_path.lower():
                        # Also check if we're inside a #[cfg(test)] module by looking at previous lines
                        lines_before = "\n".join(lines[max(0, i-50):i])
                        if "#[cfg(test)]" not in lines_before and "mod tests" not in lines_before:
                            assert False, (
                                f"Local import found inside function body at "
                                f"{rel_path}:{i}: {stripped!r}. "
                                f"AGENTS.md requires imports at the top of the file."
                            )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_cargo_test_ty_mdtests_github_annotations():
    """pass_to_pass | CI job 'cargo test' → step 'ty mdtests (GitHub annotations)'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo test -p ty_python_semantic --test mdtest'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'ty mdtests (GitHub annotations)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_cargo_test_run_tests():
    """pass_to_pass | CI job 'cargo test' → step 'Run tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo insta test --all-features --unreferenced reject --test-runner nextest'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_cargo_test_dogfood_ty_on_py_fuzzer():
    """pass_to_pass | CI job 'cargo test' → step 'Dogfood ty on py-fuzzer'"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run --project=./python/py-fuzzer cargo run -p ty check --project=./python/py-fuzzer'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Dogfood ty on py-fuzzer' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_cargo_test_dogfood_ty_on_the_scripts_directory():
    """pass_to_pass | CI job 'cargo test' → step 'Dogfood ty on the scripts directory'"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run --project=./scripts cargo run -p ty check --project=./scripts'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Dogfood ty on the scripts directory' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_cargo_test_dogfood_ty_on_ty_benchmark():
    """pass_to_pass | CI job 'cargo test' → step 'Dogfood ty on ty_benchmark'"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run --project=./scripts/ty_benchmark cargo run -p ty check --project=./scripts/ty_benchmark'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Dogfood ty on ty_benchmark' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_cargo_test_cargo():
    """pass_to_pass | CI job 'cargo test' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo doc --all --no-deps'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_cargo_test_cargo_2():
    """pass_to_pass | CI job 'cargo test' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo doc --no-deps -p ty_python_semantic -p ty -p ty_test -p ruff_db -p ruff_python_formatter --document-private-items'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_cargo_build_build_tests():
    """pass_to_pass | CI job 'cargo build' → step 'Build tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo "+${MSRV}" test --no-run --all-features'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_cargo_fuzz_build_cargo():
    """pass_to_pass | CI job 'cargo fuzz build' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo fuzz build -s none'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_benchmarks_instrumented_ty_build_benchmarks():
    """pass_to_pass | CI job 'benchmarks instrumented ty' → step 'Build benchmarks'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo codspeed build -m simulation -m memory --features "codspeed,ty_instrumented" --profile profiling --no-default-features -p ruff_benchmark --bench ty'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build benchmarks' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_scripts_python():
    """pass_to_pass | CI job 'test scripts' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'python crates/ruff_python_ast/generate.py'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_scripts_python_2():
    """pass_to_pass | CI job 'test scripts' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'python crates/ruff_python_formatter/generate.py'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

# === Execution-mined f2p tests (taskforge.exec_f2p_miner) ===
# Source: dual-pass exec at base vs gold inside the task's docker image
# Test command: cargo test -p ty_python_semantic --test mdtest || true
# 0 fail→pass + 50 pass→pass test name(s) discovered.

def test_exec_p2p_mdtest_abstract_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::abstract.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_annotated_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/annotated.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_any_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/any.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_callable_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/callable.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_deferred_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/deferred.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_generic_alias_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/generic_alias.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_int_float_complex_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/int_float_complex.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_invalid_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/invalid.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_literal_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/literal.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_literal_string_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/literal_string.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_never_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/never.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_new_types_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/new_types.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_optional_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/optional.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_self_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/self.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_starred_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/starred.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_stdlib_typing_aliases_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/stdlib_typing_aliases.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_string_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/string.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_union_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/union.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_unsupported_special_forms_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/unsupported_special_forms.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_unsupported_special_types_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/unsupported_special_types.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_unsupported_type_qualifiers_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/unsupported_type_qualifiers.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_assignment_annotations_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::assignment/annotations.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_assignment_augmented_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::assignment/augmented.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_assignment_multi_target_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::assignment/multi_target.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_assignment_unbound_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::assignment/unbound.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_assignment_walrus_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::assignment/walrus.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_async_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::async.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_attributes_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::attributes.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_bidirectional_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::bidirectional.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_binary_booleans_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::binary/booleans.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_binary_classes_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::binary/classes.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_binary_custom_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::binary/custom.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_binary_instances_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::binary/instances.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_binary_integers_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::binary/integers.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_binary_tuples_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::binary/tuples.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_binary_unions_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::binary/unions.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_boolean_short_circuit_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::boolean/short_circuit.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_boundness_declaredness_public_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::boundness_declaredness/public.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_call_abstract_method_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::call/abstract_method.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_call_annotation_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::call/annotation.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_call_builtins_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::call/builtins.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_call_callable_instance_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::call/callable_instance.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_call_callables_as_descriptors_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::call/callables_as_descriptors.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_call_constructor_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::call/constructor.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_call_dunder_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::call/dunder.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_call_dunder_import_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::call/dunder_import.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_call_function_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::call/function.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_call_getattr_static_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::call/getattr_static.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_call_invalid_syntax_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::call/invalid_syntax.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_call_methods_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::call/methods.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

