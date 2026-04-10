"""
Task: ruff-ty-typeddict-optional-key-unpack
Repo: ruff @ f4c3807e9974d00eba3827b4494dde5bc2cf5707
PR:   24446

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/ruff"

TYPED_DICT_RS = Path(REPO) / "crates/ty_python_semantic/src/types/typed_dict.rs"
CLASS_RS = Path(REPO) / "crates/ty_python_semantic/src/types/class.rs"

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


def _extract_function_body(filepath: Path, func_name: str) -> str:
    """Extract the body of a Rust function from source."""
    source = filepath.read_text()
    marker = f"fn {func_name}"
    start = source.find(marker)
    assert start != -1, f"Function {func_name} not found in {filepath.name}"
    next_fn = source.find("\nfn ", start + 1)
    next_pub_fn = source.find("\npub", start + 1)
    candidates = [c for c in [next_fn, next_pub_fn] if c != -1]
    end = min(candidates) if candidates else len(source)
    return source[start:end]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check():
    """Modified crate compiles successfully."""
    assert Path(_ty_bin()).exists(), "ty binary not found after build"


# [repo_tests] pass_to_pass — CI cargo check
def test_cargo_check_ty_semantic():
    """Repo's cargo check passes for ty_python_semantic crate (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty_python_semantic"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass — CI cargo clippy
def test_cargo_clippy_ty_semantic():
    """Repo's cargo clippy passes for ty_python_semantic crate (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "ty_python_semantic"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo clippy failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass — CI cargo fmt
def test_cargo_fmt_check():
    """Repo's code formatting passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--", "--check"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo fmt check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass — CI cargo check for ty binary
def test_cargo_check_ty():
    """Repo's cargo check passes for ty binary (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo check -p ty failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass — CI cargo check for ty_project crate
def test_cargo_check_ty_project():
    """Repo's cargo check passes for ty_project crate (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty_project"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo check -p ty_project failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass — Library unit tests for ty_python_semantic
def test_lib_tests_ty_semantic():
    """Repo's library unit tests pass for ty_python_semantic (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_python_semantic", "--lib", "--", "--test-threads=2"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Library tests failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass — class-related mdtests
def test_class_mdtest():
    """Repo's class mdtest suite passes (pass_to_pass)."""
    env = os.environ.copy()
    env["CARGO_PROFILE_DEV_OPT_LEVEL"] = "1"
    env["INSTA_FORCE_PASS"] = "1"
    env["INSTA_UPDATE"] = "always"
    r = subprocess.run(
        [
            "cargo", "test", "-p", "ty_python_semantic",
            "--test", "mdtest", "--", "class",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env=env,
    )
    assert r.returncode == 0, (
        f"class mdtest failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_optional_unpack_missing_required():
    """ty reports missing-typed-dict-key when all-optional TypedDict is unpacked into required target."""
    output = _ty_check(
        """\
from typing import TypedDict

class MaybeName(TypedDict, total=False):
    name: str

class NeedsName(TypedDict):
    name: str

def f(maybe: MaybeName) -> NeedsName:
    return NeedsName(**maybe)
"""
    )
    assert "missing" in output.lower(), (
        f"Expected missing-typed-dict-key diagnostic, got:\n{output}"
    )
    assert "'name'" in output or '"name"' in output, (
        f"Expected error to mention key 'name', got:\n{output}"
    )


# [pr_diff] fail_to_pass
def test_mixed_required_optional_unpack():
    """ty reports missing key when optional source key does not satisfy required target key."""
    output = _ty_check(
        """\
from typing import TypedDict, NotRequired

class Source(TypedDict):
    x: int
    y: NotRequired[str]

class Target(TypedDict):
    x: int
    y: str

def f(src: Source) -> Target:
    return Target(**src)
"""
    )
    # Key 'x' is required in Source so it satisfies Target's 'x'.
    # Key 'y' is NotRequired in Source, so it should NOT satisfy Target's required 'y'.
    assert "missing" in output.lower(), (
        f"Expected missing-typed-dict-key diagnostic for key 'y', got:\n{output}"
    )
    assert "'y'" in output or '"y"' in output, (
        f"Expected error to mention key 'y', got:\n{output}"
    )


# [pr_diff] fail_to_pass
def test_multiple_optional_keys_unpack():
    """ty reports missing keys when multiple optional source keys are unpacked into required target."""
    output = _ty_check(
        """\
from typing import TypedDict

class OptionalAll(TypedDict, total=False):
    a: int
    b: str

class RequiredAll(TypedDict):
    a: int
    b: str

def f(opt: OptionalAll) -> RequiredAll:
    return RequiredAll(**opt)
"""
    )
    assert "missing" in output.lower(), (
        f"Expected missing-typed-dict-key diagnostic, got:\n{output}"
    )
    # Both 'a' and 'b' should be reported as missing
    assert ("'a'" in output or '"a"' in output), (
        f"Expected error to mention key 'a', got:\n{output}"
    )
    assert ("'b'" in output or '"b"' in output), (
        f"Expected error to mention key 'b', got:\n{output}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / repo_tests) — regression + valid cases
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_required_unpack_no_error():
    """Unpacking a TypedDict with all-required keys into a matching target produces no error."""
    output = _ty_check(
        """\
from typing import TypedDict

class Source(TypedDict):
    name: str
    age: int

class Target(TypedDict):
    name: str
    age: int

def f(src: Source) -> Target:
    return Target(**src)
"""
    )
    error_lines = [
        l for l in output.splitlines()
        if "missing-typed-dict-key" in l or "invalid-argument-type" in l
    ]
    assert len(error_lines) == 0, (
        f"Expected no TypedDict errors for all-required source, got:\n"
        + "\n".join(error_lines)
    )


# [repo_tests] pass_to_pass
def test_typed_dict_mdtest():
    """Upstream typed_dict mdtest suite passes."""
    env = os.environ.copy()
    env["CARGO_PROFILE_DEV_OPT_LEVEL"] = "1"
    env["INSTA_FORCE_PASS"] = "1"
    env["INSTA_UPDATE"] = "always"
    r = subprocess.run(
        [
            "cargo", "test", "-p", "ty_python_semantic",
            "--test", "mdtest", "--", "typed_dict",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env=env,
    )
    assert r.returncode == 0, (
        f"typed_dict mdtest failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:79 @ f4c3807e9974d00eba3827b4494dde5bc2cf5707
def test_no_panic_unwrap():
    """No panic!/unreachable!/unwrap in modified validation functions (AGENTS.md:79)."""
    for filepath in [TYPED_DICT_RS]:
        source = filepath.read_text()
        for func_name in [
            "extract_unpacked_typed_dict_keys",
            "validate_from_keywords",
        ]:
            if func_name not in source:
                # The function must exist — this is part of the fix
                if func_name == "validate_from_keywords":
                    assert False, f"Function {func_name} not found in {filepath.name}"
                continue
            func_body = _extract_function_body(filepath, func_name)
            for i, line in enumerate(func_body.splitlines(), 1):
                stripped = line.strip()
                if stripped.startswith("//"):
                    continue
                assert "panic!(" not in stripped, (
                    f"panic! in {func_name} at {filepath.name}:{i}: {stripped}"
                )
                assert ".unwrap()" not in stripped, (
                    f".unwrap() in {func_name} at {filepath.name}:{i}: {stripped}"
                )
                assert "unreachable!(" not in stripped, (
                    f"unreachable! in {func_name} at {filepath.name}:{i}: {stripped}"
                )


# [agent_config] pass_to_pass — AGENTS.md:76 @ f4c3807e9974d00eba3827b4494dde5bc2cf5707
def test_no_local_imports():
    """No local use/import statements inside functions (AGENTS.md:76)."""
    for filepath in [TYPED_DICT_RS]:
        source = filepath.read_text()
        for func_name in [
            "extract_unpacked_typed_dict_keys",
            "validate_from_keywords",
        ]:
            if func_name not in source:
                continue
            func_body = _extract_function_body(filepath, func_name)
            for i, line in enumerate(func_body.splitlines(), 1):
                stripped = line.strip()
                if stripped.startswith("//"):
                    continue
                assert not stripped.startswith("use "), (
                    f"Local import in {func_name} at {filepath.name}:{i}: {stripped}"
                )
