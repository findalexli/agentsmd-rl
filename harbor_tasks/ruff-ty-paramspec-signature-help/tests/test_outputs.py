"""
Task: ruff-ty-paramspec-signature-help
Repo: ruff @ ad30af4cd00b549037456ebafc803a60e4c53b37
PR:   24399

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/ruff"

COMPLETION_RS = Path(REPO) / "crates/ty_ide/src/completion.rs"
SIGNATURE_HELP_RS = Path(REPO) / "crates/ty_ide/src/signature_help.rs"
DISPLAY_RS = Path(REPO) / "crates/ty_python_semantic/src/types/display.rs"
IDE_SUPPORT_RS = Path(REPO) / "crates/ty_python_semantic/src/types/ide_support.rs"

MODIFIED_FILES = [COMPLETION_RS, SIGNATURE_HELP_RS, DISPLAY_RS, IDE_SUPPORT_RS]


def _cargo_test(crate: str, test_name: str, timeout: int = 300) -> subprocess.CompletedProcess:
    """Run a specific Rust test in a crate by exact name."""
    return subprocess.run(
        ["cargo", "test", "-p", crate, "--", test_name, "--exact"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _test_passed(result: subprocess.CompletedProcess, test_name: str) -> bool:
    """Check if a specific test passed in cargo test output."""
    return result.returncode == 0 and f"test {test_name} ... ok" in result.stdout


# ---------------------------------------------------------------------------
# P2P: static — compilation check
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_cargo_check():
    """ty_ide crate compiles without errors."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty_ide"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_cargo_fmt():
    """Rust code formatting follows style guidelines (repo pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--all", "--check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"cargo fmt check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_cargo_clippy_ty_ide():
    """ty_ide crate passes clippy lints (repo pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "ty_ide", "--all-targets", "--all-features", "--", "-D", "warnings"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"cargo clippy failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_cargo_doc_ty_ide():
    """ty_ide crate documentation builds without errors (repo pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "doc", "-p", "ty_ide", "--no-deps"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"cargo doc failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_signature_help_basic_function():
    """Signature help basic function call test passes (repo pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_ide", "signature_help::tests::signature_help_basic_function_call", "--", "--exact"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Test failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_signature_help_class_constructor():
    """Signature help class constructor test passes (repo pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_ide", "signature_help::tests::signature_help_class_constructor", "--", "--exact"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Test failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_signature_help_callable_object():
    """Signature help callable object test passes (repo pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_ide", "signature_help::tests::signature_help_callable_object", "--", "--exact"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Test failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_completion_call_keyword_only():
    """Completion call keyword-only argument test passes (repo pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_ide", "completion::tests::call_keyword_only_argument", "--", "--exact"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Test failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_completion_call_positional_only():
    """Completion call positional-only argument test passes (repo pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_ide", "completion::tests::call_positional_only_argument", "--", "--exact"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Test failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_signature_help_generic_function():
    """Signature help generic function resolves typevars test passes (repo pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_ide", "signature_help::tests::signature_help_generic_function_resolves_typevars", "--", "--exact"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Test failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_signature_help_overloaded_function():
    """Signature help overloaded function test passes (repo pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_ide", "signature_help::tests::signature_help_overloaded_function", "--", "--exact"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Test failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_signature_help_method_call():
    """Signature help method call test passes (repo pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_ide", "signature_help::tests::signature_help_method_call", "--", "--exact"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Test failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_completion_call_blank():
    """Completion call blank test passes (repo pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_ide", "completion::tests::call_blank1", "--", "--exact"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Test failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# F2P: pr_diff — core behavioral tests (upstream Rust tests added by the PR)
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_signature_help_paramspec_class_constructor():
    """Signature help for ParamSpec-generic class constructors inside subscripts renders correctly."""
    result = _cargo_test(
        "ty_ide",
        "signature_help_paramspec_generic_class_constructor_inside_subscript",
    )
    assert _test_passed(
        result, "signature_help_paramspec_generic_class_constructor_inside_subscript"
    ), (
        f"Test failed or not found.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )


# [pr_diff] fail_to_pass
def test_bare_paramspec_active_parameter():
    """Bare ParamSpec signature keeps active parameter for later arguments."""
    result = _cargo_test(
        "ty_ide",
        "signature_help_bare_paramspec_keeps_active_parameter_for_later_arguments",
    )
    assert _test_passed(
        result,
        "signature_help_bare_paramspec_keeps_active_parameter_for_later_arguments",
    ), (
        f"Test failed or not found.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )


# [pr_diff] fail_to_pass
def test_no_keyword_completions_bare_paramspec():
    """Bare ParamSpec signatures produce no keyword argument completions."""
    result = _cargo_test(
        "ty_ide",
        "call_bare_paramspec_has_no_keyword_argument_completions",
    )
    assert _test_passed(
        result, "call_bare_paramspec_has_no_keyword_argument_completions"
    ), (
        f"Test failed or not found.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )


# ---------------------------------------------------------------------------
# P2P: agent_config — rules from AGENTS.md
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — AGENTS.md:79 @ ad30af4cd00b549037456ebafc803a60e4c53b37
def test_no_panic_unwrap():
    """No panic!/unreachable!/unwrap in modified files (AGENTS.md:79)."""
    for filepath in MODIFIED_FILES:
        source = filepath.read_text()
        for i, line in enumerate(source.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("//"):
                continue
            assert "panic!(" not in stripped, (
                f"panic! at {filepath.name}:{i}: {stripped}"
            )
            assert ".unwrap()" not in stripped, (
                f".unwrap() at {filepath.name}:{i}: {stripped}"
            )
            assert "unreachable!(" not in stripped, (
                f"unreachable! at {filepath.name}:{i}: {stripped}"
            )


# [agent_config] pass_to_pass — AGENTS.md:76 @ ad30af4cd00b549037456ebafc803a60e4c53b37
def test_no_local_imports():
    """No local use/import statements inside functions (AGENTS.md:76)."""
    for filepath in MODIFIED_FILES:
        source = filepath.read_text()
        in_fn = False
        brace_depth = 0
        for i, line in enumerate(source.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("//"):
                continue
            if "fn " in stripped and "{" in stripped:
                in_fn = True
                brace_depth += stripped.count("{") - stripped.count("}")
                continue
            if in_fn:
                brace_depth += stripped.count("{") - stripped.count("}")
                if brace_depth <= 0:
                    in_fn = False
                    continue
                assert not stripped.startswith("use "), (
                    f"Local import at {filepath.name}:{i}: {stripped}"
                )
