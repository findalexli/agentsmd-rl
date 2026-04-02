"""
Task: bun-ffi-linksymbols-nonobject-crash
Repo: oven-sh/bun @ 0de7a806d108a56a2c9f87d5974c52384059c397
PR:   28359

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/bun"
TARGET = f"{REPO}/src/bun.js/api/ffi.zig"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_target():
    return Path(TARGET).read_text()


def _added_lines_from_diff() -> list[str]:
    """Get added lines from git diff (agent's changes vs base commit)."""
    for cmd in [
        ["git", "diff", "HEAD"],
        ["git", "diff", "--cached"],
        ["git", "diff", "HEAD~1"],
    ]:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO)
        if result.stdout.strip():
            return [
                line[1:]
                for line in result.stdout.split("\n")
                if line.startswith("+") and not line.startswith("+++")
            ]
    return []


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static) — structural integrity
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_zig_file_has_required_functions():
    """ffi.zig must exist and contain required function signatures."""
    content = _read_target()
    for name in [
        "pub const FFI = struct",
        "fn generateSymbols(",
        "fn generateSymbolForFunction(",
        "fn linkSymbols(",
        "fn print(",
        "fn open(",
    ]:
        assert name in content, f"Missing required definition: {name}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_nonobject_value_rejected_in_generate_symbols():
    """generateSymbols must check isObject() to reject primitive values
    before they reach generateSymbolForFunction.

    The base code only checks isEmptyOrUndefinedOrNull(). The fix must add
    an isObject() check (or equivalent) so numbers, strings, and booleans
    don't reach the assertion that panics in generateSymbolForFunction."""
    content = _read_target()
    # Gold fix adds `or !value.isObject()` to the existing null check.
    # Accept any isObject-style check in the file.
    patterns = [
        r"!value\.isObject\(\)",
        r"value\.isObject\(\)",
        r"isObject\s*\(",
    ]
    found = any(re.search(p, content) for p in patterns)
    assert found, (
        "No isObject() check found in ffi.zig — primitive values will reach "
        "generateSymbolForFunction and cause a process panic"
    )


# [pr_diff] fail_to_pass
def test_nonobject_rejection_returns_type_error():
    """The isObject check must be paired with a TypeError return, not a
    silent skip.

    The gold fix extends `isEmptyOrUndefinedOrNull()` to `or !value.isObject()`
    on the same branch that calls toTypeError. Accept any approach that ties
    an object-type check to an explicit error return."""
    content = _read_target()
    lines = content.split("\n")

    # Strategy 1: combined condition on one line (gold fix)
    for line in lines:
        if "isEmptyOrUndefinedOrNull" in line and "isObject" in line:
            return  # Found combined check

    # Strategy 2: an isObject check on some line, with a TypeError in nearby context
    for i, line in enumerate(lines):
        if re.search(r"isObject\s*\(", line):
            context = "\n".join(lines[max(0, i - 3) : i + 6])
            if any(
                kw in context
                for kw in ["toTypeError", "TypeError", "toInvalidArguments", "throwValue"]
            ):
                return  # Found isObject check near error return

    assert False, (
        "No object-type validation found that produces a TypeError — "
        "non-object values won't be rejected with a proper error"
    )


# [pr_diff] fail_to_pass
def test_arg_types_freed_on_error_paths():
    """Error paths in print, open, and linkSymbols must deinit arg_types
    before clearing symbols, to prevent a memory leak.

    The base code frees symbol keys on error but not arg_types inside each
    function entry. The fix adds arg_types.deinit() in the error cleanup
    of all three entry points (gold fix adds 3 occurrences)."""
    content = _read_target()
    count = len(re.findall(r"arg_types\s*\.\s*deinit", content))
    assert count >= 2, (
        f"Only {count} arg_types.deinit() call(s) found in ffi.zig; "
        f"expected >=2 (in error paths of print/open/linkSymbols)"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression / anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_core_ffi_functions_intact():
    """Core FFI functions and existing null-check validation must still be present."""
    content = _read_target()
    required = [
        "pub const FFI = struct",
        "fn generateSymbols(",
        "fn generateSymbolForFunction(",
        "fn linkSymbols(",
        "fn print(",
        "fn open(",
        "isEmptyOrUndefinedOrNull()",
    ]
    for r in required:
        assert r in content, f"Missing required element: {r}"


# [repo_tests] pass_to_pass
def test_generate_symbol_for_function_not_stub():
    """generateSymbolForFunction must still contain core processing logic.
    A stub replacement would silently break all FFI functionality."""
    content = _read_target()
    match = re.search(r"fn generateSymbolForFunction\s*\(", content)
    assert match is not None, "generateSymbolForFunction not found in ffi.zig"
    # The function body (next ~3000 chars after the declaration) must still
    # contain args and returns handling
    after = content[match.start() : match.start() + 3000]
    assert "args" in after, "generateSymbolForFunction missing 'args' handling — looks stubbed"
    assert "returns" in after, "generateSymbolForFunction missing 'returns' handling — looks stubbed"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from src/CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — src/CLAUDE.md:11 @ 0de7a806d108a56a2c9f87d5974c52384059c397
def test_no_inline_imports_in_new_code():
    """New code must not add @import() inline inside function bodies.
    Imports belong at the bottom of the file or containing struct (src/CLAUDE.md:11)."""
    added = _added_lines_from_diff()
    for line in added:
        if "@import(" in line:
            # Lines with heavy indentation (>12 spaces) are inside function bodies
            leading_spaces = len(line) - len(line.lstrip())
            if leading_spaces > 12:
                assert False, (
                    f"@import() used inline inside a function body: {line.strip()}"
                )


# [agent_config] pass_to_pass — src/CLAUDE.md:16 @ 0de7a806d108a56a2c9f87d5974c52384059c397
def test_no_prohibited_std_apis():
    """New code must not use std.fs, std.posix, std.os, or std.process
    where bun.* equivalents exist (src/CLAUDE.md:16)."""
    added = _added_lines_from_diff()
    forbidden = ["std.fs", "std.posix", "std.os", "std.process"]
    for line in added:
        for f in forbidden:
            assert f not in line, (
                f"Prohibited API '{f}' found in new code: {line.strip()}"
            )
