"""
Task: ruff-sim102-collapsible-if-safe-fix
Repo: astral-sh/ruff @ de6d6be794a1b649ba5d60af6fe956c194dc9b2a
PR:   24371

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
import pytest
from pathlib import Path

REPO = "/workspace/ruff"
COLLAPSIBLE_IF = f"{REPO}/crates/ruff_linter/src/rules/flake8_simplify/rules/collapsible_if.rs"
PREVIEW_RS = f"{REPO}/crates/ruff_linter/src/preview.rs"


@pytest.fixture(scope="session")
def ruff_bin():
    """Build ruff (incremental) and return binary path."""
    r = subprocess.run(
        ["cargo", "build", "--bin", "ruff"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"cargo build failed:\n{r.stderr[-3000:]}"
    binary = Path(REPO) / "target" / "debug" / "ruff"
    assert binary.exists(), f"Binary not found at {binary}"
    return str(binary)


def _check_sim102(ruff_bin, code, tmp_path, *, preview=False, suffix=""):
    """Write code to a temp file and run ruff check --select SIM102, return JSON results."""
    test_file = tmp_path / f"collapsible{suffix}.py"
    test_file.write_text(code)
    cmd = [ruff_bin, "check", "--select", "SIM102", "--output-format", "json", "--no-cache"]
    if preview:
        cmd.append("--preview")
    cmd.append(str(test_file))
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return json.loads(r.stdout)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check():
    """The crate must compile without errors."""
    r = subprocess.run(
        ["cargo", "check", "--bin", "ruff"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr[-3000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_fix_safe_in_preview(ruff_bin, tmp_path):
    """In preview mode, the SIM102 collapsible-if fix must have 'safe' applicability.

    On the base commit, the fix is always 'unsafe' even with --preview.
    After the fix, --preview makes it 'safe'.
    """
    code = "x = True\ny = True\nif x:\n    if y:\n        print('nested')\n"
    results = _check_sim102(ruff_bin, code, tmp_path, preview=True, suffix="_preview")
    assert len(results) > 0, "SIM102 should detect a collapsible if"
    fix = results[0].get("fix")
    assert fix is not None, "SIM102 should offer a fix for simple collapsible if"
    applicability = fix.get("applicability")
    assert applicability == "safe", (
        f"With --preview, SIM102 fix applicability should be 'safe', got '{applicability}'"
    )


# [pr_diff] fail_to_pass
def test_fix_safe_in_preview_varied_inputs(ruff_bin, tmp_path):
    """Preview-safe fix works across multiple different collapsible-if patterns.

    Tests multiple inputs to prevent hardcoded constants.
    """
    cases = [
        ("a = 1\nb = 2\nif a > 0:\n    if b > 0:\n        result = a + b\n", "comparison"),
        ("items = []\nflags = {}\nif items:\n    if flags:\n        pass\n", "truthiness"),
        ("val = None\nif val is not None:\n    if isinstance(val, str):\n        val.upper()\n", "isinstance"),
    ]
    for code, label in cases:
        results = _check_sim102(ruff_bin, code, tmp_path, preview=True, suffix=f"_{label}")
        assert len(results) > 0, f"SIM102 not triggered for {label}"
        fix = results[0].get("fix")
        assert fix is not None, f"SIM102 fix not offered for {label}"
        assert fix.get("applicability") == "safe", (
            f"With --preview, SIM102 fix for {label} should be 'safe', "
            f"got '{fix.get('applicability')}'"
        )


# [pr_diff] fail_to_pass
def test_preview_function_defined():
    """preview.rs must define is_collapsible_if_fix_safe_enabled.

    On the base commit, this function does not exist.
    """
    content = Path(PREVIEW_RS).read_text()
    assert "is_collapsible_if_fix_safe_enabled" in content, (
        "preview.rs must define is_collapsible_if_fix_safe_enabled"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / repo_tests / static) — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_fix_unsafe_without_preview(ruff_bin, tmp_path):
    """Without preview, the SIM102 fix must remain 'unsafe'."""
    code = "x = True\ny = True\nif x:\n    if y:\n        print('nested')\n"
    results = _check_sim102(ruff_bin, code, tmp_path, preview=False, suffix="_no_preview")
    assert len(results) > 0, "SIM102 should detect a collapsible if"
    fix = results[0].get("fix")
    assert fix is not None, "SIM102 should offer a fix"
    applicability = fix.get("applicability")
    assert applicability == "unsafe", (
        f"Without --preview, SIM102 fix should be 'unsafe', got '{applicability}'"
    )


# [repo_tests] pass_to_pass
def test_sim102_snapshot_tests():
    """Upstream SIM102 snapshot tests must pass."""
    r = subprocess.run(
        ["cargo", "test", "--package", "ruff_linter", "--", "SIM102"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"SIM102 snapshot tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


# [repo_tests] pass_to_pass — CI/CD check for the modified package
def test_cargo_check_ruff_linter():
    """The ruff_linter package (modified) must compile without errors."""
    r = subprocess.run(
        ["cargo", "check", "--package", "ruff_linter"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"cargo check --package ruff_linter failed:\n{r.stderr[-3000:]}"


# [repo_tests] pass_to_pass — CI/CD check for the modified module
def test_cargo_test_flake8_simplify():
    """flake8_simplify module tests must pass (includes SIM102)."""
    r = subprocess.run(
        ["cargo", "test", "--package", "ruff_linter", "flake8_simplify"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, (
        f"flake8_simplify tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:79 @ de6d6be794a1b649ba5d60af6fe956c194dc9b2a
def test_no_unwrap_or_panic():
    """Preview.rs must not introduce panic!(), unreachable!(), or .unwrap() in the new function."""
    # Only check preview.rs for the new function, not the entire collapsible_if.rs
    # The collapsible_if.rs has existing .unwrap() calls from the base commit
    content = Path(PREVIEW_RS).read_text()
    for pattern, label in [
        (r'\bunwrap\(\)', '.unwrap()'),
        (r'\bpanic!\s*\(', 'panic!()'),
        (r'\bunreachable!\s*\(', 'unreachable!()'),
    ]:
        matches = re.findall(pattern, content)
        assert not matches, (
            f"Found {label} in preview.rs — "
            f"AGENTS.md line 79 says to avoid these patterns in new code"
        )


# [agent_config] pass_to_pass — AGENTS.md:76 @ de6d6be794a1b649ba5d60af6fe956c194dc9b2a
def test_rust_imports_at_top():
    """Rust imports must be at the top of the file, not locally inside functions."""
    for filepath in [COLLAPSIBLE_IF, PREVIEW_RS]:
        content = Path(filepath).read_text()
        in_function = False
        brace_depth = 0
        for line in content.splitlines():
            stripped = line.strip()
            if re.match(r'(pub(\(crate\))?\s+)?fn\s+', stripped):
                in_function = True
            if in_function:
                brace_depth += line.count('{') - line.count('}')
                if stripped.startswith('use '):
                    assert False, (
                        f"Found local import inside function body: {stripped!r} — "
                        f"AGENTS.md line 76 says imports must be at the top of the file"
                    )
                if brace_depth <= 0:
                    in_function = False
                    brace_depth = 0

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

def test_ci_benchmarks_walltime_build_benchmarks():
    """pass_to_pass | CI job 'benchmarks walltime' → step 'Build benchmarks'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo codspeed build -m walltime --features "codspeed,ty_walltime" --profile profiling --no-default-features -p ruff_benchmark'], cwd=REPO,
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