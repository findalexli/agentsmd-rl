"""
Task: ruff-ty-typeddict-positional-unpack
Repo: ruff @ d2d31ee02a17f6e09631598b3ebc6a7b6c6aab96
PR:   24491

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/ruff"

TYPED_DICT_RS = Path(REPO) / "crates/ty_python_semantic/src/types/typed_dict.rs"
BUILDER_RS = Path(REPO) / "crates/ty_python_semantic/src/types/infer/builder/typed_dict.rs"

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
    # Find the function declaration
    marker = f"fn {func_name}"
    start = source.find(marker)
    assert start != -1, f"Function {func_name} not found in {filepath.name}"
    # Find the next function declaration at the same indentation level
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


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_bad_type_per_key_error():
    """ty reports per-key invalid-argument-type when positional TypedDict has wrong type."""
    output = _ty_check(
        """\
from typing import TypedDict

class Target(TypedDict):
    a: int
    b: int

class BadSource(TypedDict):
    a: str

def check(bad: BadSource) -> None:
    Target(bad, b=2)
"""
    )
    # After fix: error should mention key "a" specifically (per-key validation)
    # Before fix: generic "not assignable to" without mentioning individual keys
    assert 'key "a"' in output, (
        f"Expected per-key error mentioning key \"a\", got:\n{output}"
    )


# [pr_diff] fail_to_pass
def test_optional_source_missing_key():
    """ty reports missing-typed-dict-key when optional TypedDict source misses required key."""
    output = _ty_check(
        """\
from typing import TypedDict

class Result(TypedDict):
    x: int
    y: str

class PartialSource(TypedDict, total=False):
    x: int

def check(partial: PartialSource) -> None:
    Result(partial, y="hello")
"""
    )
    # After fix: missing-typed-dict-key diagnostic for required key 'x'
    # Before fix: generic invalid-argument-type (whole-object assignability)
    assert "Missing required key" in output or "missing" in output.lower(), (
        f"Expected missing-typed-dict-key diagnostic, got:\n{output}"
    )
    assert "'x'" in output or '"x"' in output, (
        f"Expected error to mention key 'x', got:\n{output}"
    )


# [pr_diff] fail_to_pass
def test_wider_bad_source_per_key_error():
    """ty reports per-key error for wider TypedDict with wrong type for an overlapping key."""
    output = _ty_check(
        """\
from typing import TypedDict

class Target(TypedDict):
    name: int
    value: int

class WiderBadSource(TypedDict):
    name: str
    extra: float

def check(wide_bad: WiderBadSource) -> None:
    Target(wide_bad, value=42)
"""
    )
    # After fix: per-key error for 'name' (str vs int), should NOT mention 'extra'
    # Before fix: generic "not assignable to" error
    assert 'key "name"' in output, (
        f"Expected per-key error for key \"name\", got:\n{output}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / repo_tests) — regression + valid cases
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_valid_mixed_constructors():
    """Valid TypedDict mixed positional+keyword constructors produce no type errors."""
    output = _ty_check(
        """\
from typing import TypedDict

class Target(TypedDict):
    a: int
    b: int

class Source(TypedDict):
    a: int

class WiderSource(TypedDict):
    a: int
    extra: str

def check_source(source: Source) -> None:
    Target(source, b=2)

def check_wider(wide: WiderSource) -> None:
    Target(wide, b=2)
"""
    )
    # No TypedDict-related errors expected for valid mixed constructors
    error_lines = [
        l for l in output.splitlines()
        if "invalid-argument-type" in l or "missing-typed-dict-key" in l
    ]
    assert len(error_lines) == 0, (
        f"Expected no TypedDict errors for valid sources, got:\n"
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
            "cargo", "nextest", "run",
            "-p", "ty_python_semantic",
            "--", "mdtest::typed_dict",
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

# [agent_config] pass_to_pass — AGENTS.md:79 @ d2d31ee02a17f6e09631598b3ebc6a7b6c6aab96
def test_no_panic_unwrap():
    """No panic!/unreachable!/unwrap in modified validation functions (AGENTS.md:79)."""
    for filepath in [TYPED_DICT_RS, BUILDER_RS]:
        source = filepath.read_text()
        # Check functions in the typed_dict validation area
        for func_name in [
            "validate_typed_dict_constructor",
            "validate_from_keywords",
        ]:
            if func_name not in source:
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


# [agent_config] pass_to_pass — AGENTS.md:76 @ d2d31ee02a17f6e09631598b3ebc6a7b6c6aab96
def test_no_local_imports():
    """No local use/import statements inside functions (AGENTS.md:76)."""
    for filepath in [TYPED_DICT_RS, BUILDER_RS]:
        source = filepath.read_text()
        for func_name in [
            "validate_typed_dict_constructor",
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
