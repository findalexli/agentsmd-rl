"""
Task: ruff-f507-percent-format-nontuple
Repo: astral-sh/ruff @ b8fad8312fde560943653811ae3e16e22b99dfc7
PR:   24142

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/ruff"
STRINGS_RS = Path(REPO) / "crates/ruff_linter/src/rules/pyflakes/rules/strings.rs"


_ruff_bin_cache = None


def _ruff_bin():
    """Find the pre-built ruff binary (built in Dockerfile or by solve.sh)."""
    global _ruff_bin_cache
    if _ruff_bin_cache is not None:
        return _ruff_bin_cache

    for profile in ["debug", "release"]:
        p = Path(REPO) / "target" / profile / "ruff"
        if p.exists():
            _ruff_bin_cache = str(p)
            return _ruff_bin_cache

    raise RuntimeError(
        "ruff binary not found — it should be pre-built in the Docker image. "
        "Run 'cargo build --bin ruff' in /workspace/ruff."
    )


def _f507_diagnostics(code: str) -> list[str]:
    """Run ruff F507 on a code snippet, return diagnostic lines."""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code)
        tmp = f.name
    try:
        r = subprocess.run(
            [_ruff_bin(), "check", "--output-format=concise", "--select=F507", tmp],
            capture_output=True, text=True, timeout=30,
        )
        return [l for l in r.stdout.splitlines() if "F507" in l]
    finally:
        os.unlink(tmp)


def _extract_target_function() -> str:
    """Extract the body of percent_format_positional_count_mismatch from strings.rs."""
    source = STRINGS_RS.read_text()
    func_start = source.find("pub(crate) fn percent_format_positional_count_mismatch")
    assert func_start != -1, "Target function not found in strings.rs"
    func_end = source.find("\npub(crate) fn ", func_start + 1)
    if func_end == -1:
        func_end = source.find("\npub fn ", func_start + 1)
    if func_end == -1:
        func_end = len(source)
    return source[func_start:func_end]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_compiles():
    """Modified ruff crate compiles successfully."""
    assert Path(_ruff_bin()).exists(), "ruff binary not found after build"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — F507 must fire for literal non-tuple RHS
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_f507_literal_int():
    """F507 fires when RHS is an int literal with multiple placeholders."""
    # Two placeholders, int RHS
    diags = _f507_diagnostics("'%s %s' % 42\n")
    assert len(diags) == 1, f"Expected 1 F507 for '%s %s' % 42, got {len(diags)}: {diags}"
    # Three placeholders, different int
    diags = _f507_diagnostics("'%s %s %s' % 99\n")
    assert len(diags) == 1, f"Expected 1 F507 for '%s %s %s' % 99, got {len(diags)}: {diags}"
    # Negative int via unary
    diags = _f507_diagnostics("'%s %s' % 0\n")
    assert len(diags) == 1, f"Expected 1 F507 for '%s %s' % 0, got {len(diags)}: {diags}"


# [pr_diff] fail_to_pass
def test_f507_literal_string():
    """F507 fires when RHS is a string literal with multiple placeholders."""
    diags = _f507_diagnostics("'%s %s %s' % \"hello\"\n")
    assert len(diags) == 1, f"Expected 1 F507 for string literal, got {len(diags)}: {diags}"
    # f-string RHS
    diags = _f507_diagnostics("name = 'x'\n'%s %s' % f\"hello {name}\"\n")
    assert len(diags) == 1, f"Expected 1 F507 for f-string literal, got {len(diags)}: {diags}"
    # bytes literal
    diags = _f507_diagnostics("'%s %s' % b\"hello\"\n")
    assert len(diags) == 1, f"Expected 1 F507 for bytes literal, got {len(diags)}: {diags}"


# [pr_diff] fail_to_pass
def test_f507_literal_bool_and_none():
    """F507 fires for bool, None, float, and ellipsis literals with multiple placeholders."""
    diags_bool = _f507_diagnostics("'%s %s' % True\n")
    assert len(diags_bool) == 1, f"Expected F507 for True, got {diags_bool}"
    diags_none = _f507_diagnostics("'%s %s %s' % None\n")
    assert len(diags_none) == 1, f"Expected F507 for None, got {diags_none}"
    diags_float = _f507_diagnostics("'%s %s' % 3.14\n")
    assert len(diags_float) == 1, f"Expected F507 for 3.14, got {diags_float}"
    diags_ellipsis = _f507_diagnostics("'%s %s' % ...\n")
    assert len(diags_ellipsis) == 1, f"Expected F507 for ..., got {diags_ellipsis}"


# [pr_diff] fail_to_pass
def test_f507_compound_expression():
    """F507 fires for unary/binary ops with known non-tuple result types."""
    diags_unary = _f507_diagnostics("'%s %s' % -1\n")
    assert len(diags_unary) >= 1, f"Expected F507 for unary -1, got {diags_unary}"
    diags_binop = _f507_diagnostics("'%s %s' % (1 + 2)\n")
    assert len(diags_binop) >= 1, f"Expected F507 for (1+2), got {diags_binop}"
    diags_not = _f507_diagnostics("x = True\n'%s %s' % (not x)\n")
    assert len(diags_not) >= 1, f"Expected F507 for (not x), got {diags_not}"
    diags_str_concat = _f507_diagnostics("'%s %s' % (\"a\" + \"b\")\n")
    assert len(diags_str_concat) >= 1, f"Expected F507 for str concat, got {diags_str_concat}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — existing correct behavior preserved
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_no_f507_variable_rhs():
    """Variables/calls must NOT trigger F507 — could be tuples at runtime."""
    code = (
        "banana = (1, 2)\n"
        "'%s %s' % banana\n"
        "'%s %s' % obj.attr\n"
        "'%s %s' % get_args()\n"
        "'%s %s' % arr[0]\n"
    )
    diags = _f507_diagnostics(code)
    assert len(diags) == 0, f"Expected 0 F507 on variables/calls, got {len(diags)}: {diags}"


# [pr_diff] pass_to_pass
def test_no_f507_single_placeholder():
    """Single placeholder with literal RHS is valid — no F507."""
    code = "'%s' % 42\n'%s' % \"hello\"\n'%s' % True\n'%s' % 3.14\n"
    diags = _f507_diagnostics(code)
    assert len(diags) == 0, f"Expected 0 F507 for single placeholder, got {len(diags)}: {diags}"


# [pr_diff] pass_to_pass
def test_existing_tuple_f507():
    """Pre-existing behavior: tuple with wrong element count still triggers F507."""
    diags = _f507_diagnostics("'%s %s' % (1,)\n")
    assert len(diags) == 1, f"Expected 1 F507 for mismatched tuple, got {len(diags)}: {diags}"
    # Three placeholders, two-element tuple
    diags = _f507_diagnostics("'%s %s %s' % (1, 2)\n")
    assert len(diags) == 1, f"Expected 1 F507 for 3-vs-2 tuple, got {len(diags)}: {diags}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:79 @ b8fad8312fde560943653811ae3e16e22b99dfc7
def test_no_panic_unwrap_in_target_function():
    """No panic!/unwrap in percent_format_positional_count_mismatch (AGENTS.md:79)."""
    func_body = _extract_target_function()
    for i, line in enumerate(func_body.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        assert "panic!(" not in stripped, f"panic! in target function line {i}: {stripped}"
        assert ".unwrap()" not in stripped, f".unwrap() in target function line {i}: {stripped}"


# [agent_config] pass_to_pass — AGENTS.md:76 @ b8fad8312fde560943653811ae3e16e22b99dfc7
def test_no_local_imports_in_target_function():
    """No local use statements inside the target function (AGENTS.md:76)."""
    func_body = _extract_target_function()
    for i, line in enumerate(func_body.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        assert not stripped.startswith("use "), (
            f"Local import in target function line {i}: {stripped}"
        )


# [agent_config] pass_to_pass — AGENTS.md:79 @ b8fad8312fde560943653811ae3e16e22b99dfc7
def test_no_unreachable_in_target_function():
    """No unreachable! macro in percent_format_positional_count_mismatch (AGENTS.md:79)."""
    func_body = _extract_target_function()
    for i, line in enumerate(func_body.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        assert "unreachable!(" not in stripped, (
            f"unreachable! in target function line {i}: {stripped}"
        )


# [agent_config] pass_to_pass — AGENTS.md:81 @ b8fad8312fde560943653811ae3e16e22b99dfc7
def test_no_allow_lint_suppression():
    """Prefer #[expect()] over #[allow()] for lint suppression (AGENTS.md:81)."""
    # AST-only because: Rust source, cannot be imported/called from Python
    func_body = _extract_target_function()
    for i, line in enumerate(func_body.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        assert "#[allow(" not in stripped, (
            f"Use #[expect()] instead of #[allow()] at line {i}: {stripped}"
        )


# ---------------------------------------------------------------------------
# Repo CI/CD tests (pass_to_pass) — ensure existing functionality not broken
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_fmt():
    """Repo code formatting passes cargo fmt check (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--all", "--check"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo fmt check failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_clippy():
    """Repo lints pass cargo clippy check on ruff_linter crate (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "--package", "ruff_linter", "--all-targets", "--", "-D", "warnings"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo clippy failed:\n{r.stderr[-1000:]}{r.stdout[-1000:]}"



# [repo_tests] pass_to_pass
def test_repo_pyflakes_percent_format_tests():
    """Repo percent format (F50x) tests pass - highly relevant to F507 changes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ruff_linter", "--", "rule_percentformat", "--test-threads=4"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Percent format tests failed:\\n{r.stderr[-1000:]}{r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_cargo_check_ruff_linter():
    """Repo ruff_linter package compiles without errors (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "--package", "ruff_linter"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo check failed:\\n{r.stderr[-1000:]}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_benchmarks_instrumented_ty_build_benchmarks():
    """pass_to_pass | CI job 'benchmarks instrumented ty' → step 'Build benchmarks'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo codspeed build -m instrumentation --features "codspeed,ty_instrumented" --profile profiling --no-default-features -p ruff_benchmark --bench ty'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build benchmarks' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_cargo_fuzz_build_cargo():
    """pass_to_pass | CI job 'cargo fuzz build' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo fuzz build -s none'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

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

def test_ci_benchmarks_walltime_build_benchmarks():
    """pass_to_pass | CI job 'benchmarks walltime' → step 'Build benchmarks'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo codspeed build -m walltime --features "codspeed,ty_walltime" --profile profiling --no-default-features -p ruff_benchmark'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build benchmarks' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_ruff_lsp_build_ruff_binary():
    """pass_to_pass | CI job 'test ruff-lsp' → step 'Build Ruff binary'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo build -p ruff --bin ruff'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build Ruff binary' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_ruff_lsp_run_ruff_lsp_tests():
    """pass_to_pass | CI job 'test ruff-lsp' → step 'Run ruff-lsp tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pip uninstall --yes ruff && ruff version && just test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run ruff-lsp tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")