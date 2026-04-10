"""
Task: next.js-add-inline-value-support-for
Repo: vercel/next.js @ fc13ca90ab14987da0b9bc556fc4c7e9e1b531af
PR:   89271

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/next.js"
CRATE = Path(REPO) / "turbopack" / "crates" / "turbo-persistence"
SRC = CRATE / "src"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check():
    """turbo-persistence crate compiles without errors."""
    r = subprocess.run(
        ["cargo", "check", "-p", "turbo-persistence"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"cargo check failed:\n{r.stderr.decode()[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo's CI/CD tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_cargo_clippy():
    """Repo's clippy lints pass for turbo-persistence (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "turbo-persistence"],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"cargo clippy failed:\n{r.stderr.decode()[-1000:]}"
    )


# [repo_tests] pass_to_pass
def test_cargo_fmt():
    """Repo's rustfmt formatting check passes for turbo-persistence (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "-p", "turbo-persistence", "--", "--check"],
        cwd=REPO,
        capture_output=True,
        timeout=60,
    )
    assert r.returncode == 0, (
        f"cargo fmt check failed:\n{r.stdout.decode()[-500:]}{r.stderr.decode()[-500:]}"
    )


# [repo_tests] pass_to_pass
def test_cargo_test_lib():
    """Repo's unit tests pass for turbo-persistence (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "turbo-persistence", "--lib"],
        cwd=REPO,
        capture_output=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"cargo test failed:\n{r.stderr.decode()[-1000:]}"
    )


# [repo_tests] pass_to_pass
def test_cargo_check_tests():
    """Test code compiles for turbo-persistence (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "--tests", "-p", "turbo-persistence"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"cargo check --tests failed:\n{r.stderr.decode()[-1000:]}"
    )


# [repo_tests] pass_to_pass
def test_cargo_check_benches():
    """Benchmark code compiles for turbo-persistence (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "--benches", "-p", "turbo-persistence"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"cargo check --benches failed:\n{r.stderr.decode()[-1000:]}"
    )


# [repo_tests] pass_to_pass
def test_cargo_doc():
    """Documentation builds for turbo-persistence (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "doc", "-p", "turbo-persistence", "--no-deps"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"cargo doc failed:\n{r.stderr.decode()[-1000:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_inline_value_size_constant():
    """A constant defining the maximum inline value size must exist."""
    content = (SRC / "constants.rs").read_text()
    # Must define a constant for the inline value threshold
    match = re.search(
        r"pub\s+const\s+MAX_INLINE_VALUE_SIZE\s*:\s*usize\s*=\s*(\d+)",
        content,
    )
    assert match, "constants.rs must define MAX_INLINE_VALUE_SIZE"
    value = int(match.group(1))
    assert value == 8, f"MAX_INLINE_VALUE_SIZE should be 8, got {value}"


# [pr_diff] fail_to_pass
def test_entry_value_has_inline_variant():
    """EntryValue enum must have an Inline variant for storing values in key blocks."""
    content = (SRC / "static_sorted_file_builder.rs").read_text()
    # Check that EntryValue enum contains an Inline variant
    enum_match = re.search(
        r"pub\s+enum\s+EntryValue.*?\{(.*?)\n\}",
        content,
        re.DOTALL,
    )
    assert enum_match, "Could not find EntryValue enum"
    enum_body = enum_match.group(1)
    assert "Inline" in enum_body, "EntryValue must have an Inline variant"


# [pr_diff] fail_to_pass
def test_inline_entry_type_constant():
    """A constant for the minimum inline entry type tag (8) must exist."""
    content = (SRC / "static_sorted_file.rs").read_text()
    match = re.search(
        r"pub\s+const\s+KEY_BLOCK_ENTRY_TYPE_INLINE_MIN\s*:\s*u8\s*=\s*(\d+)",
        content,
    )
    assert match, "static_sorted_file.rs must define KEY_BLOCK_ENTRY_TYPE_INLINE_MIN"
    value = int(match.group(1))
    assert value == 8, f"INLINE_MIN should be 8, got {value}"


# [pr_diff] fail_to_pass
def test_handle_key_match_returns_slice_for_inline():
    """handle_key_match must return a value (not bail) for inline entry types."""
    content = (SRC / "static_sorted_file.rs").read_text()
    # Find the handle_key_match function
    fn_match = re.search(
        r"fn\s+handle_key_match\b.*?\n\s+\}(?:\n\s+\))?",
        content,
        re.DOTALL,
    )
    assert fn_match, "Could not find handle_key_match function"
    fn_body = fn_match.group(0)
    # The old code had bail!("Invalid key block entry type") in the catch-all arm.
    # After the fix, the catch-all arm should produce a Slice value, not bail.
    assert "slice_from_subslice" in fn_body or "Slice" in fn_body, (
        "handle_key_match must handle inline entries by producing a Slice value, "
        "not bailing with an error"
    )
    # The catch-all should NOT be a bail-only
    # Check there's a catch-all arm that does something other than just bail
    assert "LookupValue::Slice" in fn_body or "slice_from_subslice" in fn_body, (
        "handle_key_match catch-all arm must return LookupValue::Slice for inline values"
    )


# [pr_diff] fail_to_pass
def test_entry_val_size_function():
    """An entry_val_size function must exist that handles inline types via type >= 8."""
    content = (SRC / "static_sorted_file.rs").read_text()
    # The function should compute value sizes for all entry types including inline
    fn_match = re.search(
        r"fn\s+entry_val_size\b.*?\n\}",
        content,
        re.DOTALL,
    )
    assert fn_match, "static_sorted_file.rs must define entry_val_size function"
    fn_body = fn_match.group(0)
    # Must handle inline types (those >= INLINE_MIN)
    assert "INLINE_MIN" in fn_body or ">= 8" in fn_body or "ty -" in fn_body, (
        "entry_val_size must handle inline entry types"
    )


# [pr_diff] fail_to_pass
def test_put_inline_method():
    """KeyBlockBuilder must have a put_inline method for writing inline values."""
    content = (SRC / "static_sorted_file_builder.rs").read_text()
    # Check for put_inline method
    fn_match = re.search(
        r"pub\s+fn\s+put_inline\b.*?\n\s+\}",
        content,
        re.DOTALL,
    )
    assert fn_match, "KeyBlockBuilder must have a put_inline method"
    fn_body = fn_match.group(0)
    # Method must write data to the buffer (not be a stub)
    assert "extend_from_slice" in fn_body or "copy_from_slice" in fn_body, (
        "put_inline must write value data to the buffer"
    )
    assert "INLINE_MIN" in fn_body or "entry_type" in fn_body, (
        "put_inline must compute the entry type from the inline min offset"
    )


# [pr_diff] fail_to_pass
def test_slice_from_subslice_method():
    """ArcSlice must have a slice_from_subslice method for zero-copy inline value access."""
    content = (SRC / "arc_slice.rs").read_text()
    fn_match = re.search(
        r"fn\s+slice_from_subslice\b.*?\n\s+\}",
        content,
        re.DOTALL,
    )
    assert fn_match, "ArcSlice must define slice_from_subslice method"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — README update
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
