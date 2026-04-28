"""
Task: ruff-ty-nested-type-checking-inherit
Repo: ruff @ 02e5d6d90e269ca2c49b231f23b7d3c4fd579d92
PR:   24470

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/ruff"

BUILDER_RS = Path(REPO) / "crates/ty_python_semantic/src/semantic_index/builder.rs"
OVERLOADS_MD = Path(REPO) / "crates/ty_python_semantic/resources/mdtest/overloads.md"

_ty_bin_cache = None


def _ty_bin():
    """Find the pre-built ty binary (built in Dockerfile or by solve.sh)."""
    global _ty_bin_cache
    if _ty_bin_cache is not None:
        return _ty_bin_cache

    for profile in ["debug", "release"]:
        p = Path(REPO) / "target" / profile / "ty"
        if p.exists():
            _ty_bin_cache = str(p)
            return _ty_bin_cache

    raise RuntimeError(
        "ty binary not found — it should be pre-built in the Docker image. "
        "Run 'cargo build --bin ty' in /workspace/ruff."
    )


def _ty_check(code: str) -> str:
    """Run ty check on a code snippet, return combined stdout+stderr."""
    with tempfile.NamedTemporaryFile(
        suffix=".py", mode="w", dir="/tmp", delete=False
    ) as f:
        f.write(code)
        tmp = f.name
    try:
        r = subprocess.run(
            [_ty_bin(), "check", tmp],
            capture_output=True,
            text=True,
            timeout=60,
        )
        return r.stdout + r.stderr
    finally:
        os.unlink(tmp)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check():
    """ty binary exists after build."""
    assert Path(_ty_bin()).exists(), "ty binary not found after build"

# [repo_tests] pass_to_pass
def test_cargo_check_ty_package():
    """ty crate and its dependencies compile without errors (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"cargo check -p ty failed:\n{r.stderr[-1000:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_nested_if_else_type_checking():
    """Overloads inside if/else nested within TYPE_CHECKING should not trigger invalid-overload."""
    output = _ty_check(
        """\
import typing
import sys

if typing.TYPE_CHECKING:
    if sys.platform == "win32":
        pass
    else:
        @typing.overload
        def foo(x: int) -> int: ...
        @typing.overload
        def foo(x: str) -> str: ...
"""
    )
    # Before fix: invalid-overload emitted because nested block doesn't inherit TYPE_CHECKING
    # After fix: no invalid-overload (treated like a stub context)
    overload_errors = [
        l for l in output.splitlines() if "invalid-overload" in l
    ]
    assert len(overload_errors) == 0, (
        f"Expected no invalid-overload for nested TYPE_CHECKING, got:\n"
        + "\n".join(overload_errors)
    )


# [pr_diff] fail_to_pass
def test_nested_elif_type_checking():
    """Overloads inside elif branch nested within TYPE_CHECKING should not trigger invalid-overload."""
    output = _ty_check(
        """\
import typing
import sys

if typing.TYPE_CHECKING:
    if sys.version_info >= (3, 12):
        pass
    elif sys.platform == "linux":
        @typing.overload
        def bar(x: int) -> int: ...
        @typing.overload
        def bar(x: str) -> str: ...
    else:
        pass
"""
    )
    overload_errors = [
        l for l in output.splitlines() if "invalid-overload" in l
    ]
    assert len(overload_errors) == 0, (
        f"Expected no invalid-overload for elif in TYPE_CHECKING, got:\n"
        + "\n".join(overload_errors)
    )


# [pr_diff] fail_to_pass
def test_deeply_nested_type_checking():
    """Overloads inside double-nested conditionals within TYPE_CHECKING should not trigger invalid-overload."""
    output = _ty_check(
        """\
import typing
import sys

if typing.TYPE_CHECKING:
    if sys.platform == "win32":
        if sys.version_info >= (3, 11):
            @typing.overload
            def baz(x: int) -> int: ...
            @typing.overload
            def baz(x: str) -> str: ...
        else:
            pass
    else:
        pass
"""
    )
    overload_errors = [
        l for l in output.splitlines() if "invalid-overload" in l
    ]
    assert len(overload_errors) == 0, (
        f"Expected no invalid-overload for deeply nested TYPE_CHECKING, got:\n"
        + "\n".join(overload_errors)
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / repo_tests) — regression + valid cases
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_direct_type_checking_no_regression():
    """Overloads directly inside TYPE_CHECKING (no nesting) still produce no false positive."""
    output = _ty_check(
        """\
import typing

if typing.TYPE_CHECKING:
    @typing.overload
    def qux(x: int) -> int: ...
    @typing.overload
    def qux(x: str) -> str: ...
"""
    )
    overload_errors = [
        l for l in output.splitlines() if "invalid-overload" in l
    ]
    assert len(overload_errors) == 0, (
        f"Expected no invalid-overload for direct TYPE_CHECKING, got:\n"
        + "\n".join(overload_errors)
    )


# [repo_tests] pass_to_pass
def test_overloads_mdtest():
    """Upstream overloads mdtest suite passes."""
    env = os.environ.copy()
    env["CARGO_PROFILE_DEV_OPT_LEVEL"] = "1"
    env["INSTA_FORCE_PASS"] = "1"
    env["INSTA_UPDATE"] = "always"
    r = subprocess.run(
        [
            "cargo", "nextest", "run",
            "-p", "ty_python_semantic",
            "--", "mdtest::overloads",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env=env,
    )
    assert r.returncode == 0, (
        f"overloads mdtest failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:79 @ 02e5d6d90e269ca2c49b231f23b7d3c4fd579d92
def test_no_panic_unwrap():
    """No panic!/unreachable!/unwrap in the visit_stmt_if Visitor section (AGENTS.md:79)."""
    source = BUILDER_RS.read_text()
    # Find the visit_stmt_if / in_type_checking_block section where the fix lives
    marker = "self.in_type_checking_block"
    occurrences = [i for i, line in enumerate(source.splitlines(), 1)
                   if marker in line]
    assert len(occurrences) > 0, "Could not find in_type_checking_block assignments in builder.rs"

    # Check a window around each occurrence for panic/unwrap patterns
    lines = source.splitlines()
    for occ in occurrences:
        window_start = max(0, occ - 5)
        window_end = min(len(lines), occ + 5)
        for i in range(window_start, window_end):
            stripped = lines[i].strip()
            if stripped.startswith("//"):
                continue
            assert "panic!(" not in stripped, (
                f"panic! near in_type_checking_block at builder.rs:{i + 1}: {stripped}"
            )
            assert ".unwrap()" not in stripped, (
                f".unwrap() near in_type_checking_block at builder.rs:{i + 1}: {stripped}"
            )
            assert "unreachable!(" not in stripped, (
                f"unreachable! near in_type_checking_block at builder.rs:{i + 1}: {stripped}"
            )


# [agent_config] pass_to_pass — AGENTS.md:76 @ 02e5d6d90e269ca2c49b231f23b7d3c4fd579d92
def test_no_local_imports():
    """No local use/import statements inside the Visitor impl (AGENTS.md:76)."""
    source = BUILDER_RS.read_text()
    # Find the Visitor impl block where the fix lives
    visitor_start = source.find("impl<'ast> Visitor<'ast> for SemanticIndexBuilder")
    assert visitor_start != -1, "Could not find Visitor impl in builder.rs"

    visitor_section = source[visitor_start:]
    for i, line in enumerate(visitor_section.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        # use statements at indentation > 0 inside impl are local imports
        if stripped.startswith("use ") and line.startswith("    "):
            # Allow use in match arms and closures (common Rust pattern) but not in fn bodies
            # A local `use` that's deeply indented inside a function is the problem
            if line.startswith("            use ") or line.startswith("                use "):
                assert False, (
                    f"Local import in Visitor impl at builder.rs: {stripped}"
                )


# [repo_tests] pass_to_pass
def test_cargo_fmt_check():
    """Code passes rustfmt formatting checks (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--", "--check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, (
        f"cargo fmt --check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"
    )


# [repo_tests] pass_to_pass
def test_overloads_md_exists():
    """Upstream overloads mdtest file exists and is readable (pass_to_pass)."""
    assert OVERLOADS_MD.exists(), f"overloads.md not found at {OVERLOADS_MD}"
    content = OVERLOADS_MD.read_text()
    assert "TYPE_CHECKING" in content, "overloads.md should contain TYPE_CHECKING tests"
    assert "@overload" in content, "overloads.md should contain @overload tests"


# [repo_tests] pass_to_pass
def test_cargo_metadata():
    """Cargo metadata command works for the workspace (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "metadata", "--format-version", "1", "-q"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, (
        f"cargo metadata failed:\n{r.stderr[-500:]}"
    )
    # Verify the output contains ty_python_semantic
    assert "ty_python_semantic" in r.stdout, "Expected ty_python_semantic in metadata"


# [repo_tests] pass_to_pass
def test_ty_binary_runs():
    """ty binary executes without errors and shows version (pass_to_pass)."""
    r = subprocess.run(
        ["./target/debug/ty", "--version"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"ty --version failed:\n{r.stderr}"
    )
    assert "ty" in r.stdout, f"Expected 'ty' in version output, got: {r.stdout}"


# [repo_tests] pass_to_pass
def test_ty_check_valid_overloads():
    """ty correctly handles valid overloads in TYPE_CHECKING block (pass_to_pass)."""
    code = '''import typing

if typing.TYPE_CHECKING:
    @typing.overload
    def test_func(x: int) -> int: ...
    @typing.overload
    def test_func(x: str) -> str: ...
'''
    with tempfile.NamedTemporaryFile(
        suffix=".py", mode="w", dir="/tmp", delete=False
    ) as f:
        f.write(code)
        tmp = f.name
    try:
        r = subprocess.run(
            ["./target/debug/ty", "check", tmp],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60,
        )
        output = r.stdout + r.stderr
        overload_errors = [l for l in output.splitlines() if "invalid-overload" in l]
        assert len(overload_errors) == 0, (
            f"Expected no invalid-overload for valid TYPE_CHECKING overloads, got:\n"
            + "\n".join(overload_errors)
        )
    finally:
        os.unlink(tmp)


# [repo_tests] pass_to_pass
def test_cargo_doc_ty_python_semantic():
    """Documentation for ty_python_semantic crate builds without errors (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "doc", "-p", "ty_python_semantic", "--no-deps"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"cargo doc for ty_python_semantic failed:\n{r.stderr[-1000:]}"
    )


# [static] pass_to_pass
def test_mdtest_file_exists():
    """Overloads mdtest file exists and contains expected TYPE_CHECKING content (pass_to_pass)."""
    assert OVERLOADS_MD.exists(), f"overloads.md not found at {OVERLOADS_MD}"
    content = OVERLOADS_MD.read_text()
    # These are existing tests in the file (pass_to_pass - should exist before and after fix)
    assert "TYPE_CHECKING" in content, "overloads.md should contain TYPE_CHECKING tests"
    assert "@overload" in content, "overloads.md should contain @overload tests"
    assert "invalid-overload" in content, "overloads.md should test invalid-overload cases"


# [static] pass_to_pass
def test_no_tabs_in_builder_rs():
    """Source code uses spaces not tabs for indentation (pass_to_pass)."""
    source = BUILDER_RS.read_text()
    assert "\t" not in source, "Source file should not contain tab characters"


# [static] pass_to_pass
def test_builder_rs_has_type_checking_logic():
    """Builder.rs contains TYPE_CHECKING state tracking where fix is applied (pass_to_pass)."""
    source = BUILDER_RS.read_text()
    # The state variable that is modified in the fix exists
    assert "in_type_checking_block" in source, "builder.rs should track in_type_checking_block state"
    # The Visitor trait impl exists
    assert "impl<'ast> Visitor<'ast> for SemanticIndexBuilder" in source, (
        "builder.rs should implement Visitor trait"
    )
    # The if statement handling exists
    assert "is_if_type_checking" in source, "builder.rs should have is_if_type_checking helper"
    assert "is_if_not_type_checking" in source, "builder.rs should have is_if_not_type_checking helper"

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

def test_ci_test_scripts_scripts_add_rule_py():
    """pass_to_pass | CI job 'test scripts' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", './scripts/add_rule.py --name DoTheThing --prefix F --code 999 --linter pyflakes'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_scripts_cargo():
    """pass_to_pass | CI job 'test scripts' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")