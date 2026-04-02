"""
Task: bun-ffi-viewsource-nonobject-crash
Repo: oven-sh/bun @ 0de7a806d108a56a2c9f87d5974c52384059c397
PR:   28361

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: Zig requires the full Bun build toolchain to compile+run, which is
unavailable in the test container.  All checks therefore operate on source
analysis — this is the only viable approach for this codebase.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/bun"
TARGET = Path(REPO) / "src/bun.js/api/ffi.zig"


def _stripped_source() -> str:
    """Return ffi.zig with comments and string literals removed."""
    content = TARGET.read_text()
    content = re.sub(r"//[^\n]*", "", content)
    content = re.sub(r'"[^"]*"', '""', content)
    return content


def _generate_symbols_region(stripped: str, size: int = 8000) -> str:
    """Extract the region around the generateSymbols function definition."""
    # Search for the function definition — "fn generateSymbols(" in Zig
    m = re.search(r'fn\s+generateSymbols\s*\(', stripped)
    if m:
        idx = m.start()
    else:
        # Fallback: find any generateSymbols that isn't generateSymbolForFunction
        matches = [m.start() for m in re.finditer(r'generateSymbols(?!ForFunction)', stripped)]
        assert matches, "generateSymbols not found in ffi.zig"
        idx = matches[0]
    return stripped[idx : idx + size]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_ffi_struct_integrity():
    """ffi.zig has balanced braces and all core FFI identifiers."""
    content = TARGET.read_text()
    opens = content.count("{")
    closes = content.count("}")
    assert abs(opens - closes) <= 5, f"Unbalanced braces: {opens} open vs {closes} close"

    stripped = _stripped_source()
    required = [
        "pub const FFI = struct",
        "generateSymbols",
        "generateSymbolForFunction",
        "symbols_iter",
        "isEmptyOrUndefinedOrNull",
        "clearAndFree",
    ]
    for token in required:
        assert token in stripped, f"Missing required identifier: {token}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_value_guard_rejects_non_objects():
    """generateSymbols condition must reject non-object values (numbers, strings, booleans)."""
    stripped = _stripped_source()
    region = _generate_symbols_region(stripped)

    # Find the while loop that iterates symbols (symbols_iter.next)
    loop_idx = region.find("while")
    assert loop_idx != -1, "No while loop found in generateSymbols"
    loop_region = region[loop_idx : loop_idx + 3000]
    lines = loop_region.split("\n")

    type_checks = [
        "isObject", "isStruct", "isCallable", "isFunction",
        "@intFromEnum", ".tag", "typeof", "jsType",
    ]

    found = False

    # Approach 1: type check on same expression as isEmptyOrUndefinedOrNull
    for i, line in enumerate(lines):
        if "isEmptyOrUndefinedOrNull" in line:
            block = "\n".join(lines[i : i + 3])
            if any(tc in block for tc in type_checks):
                found = True
                break

    # Approach 2: separate if-block with type check leading to toTypeError
    if not found:
        for i, line in enumerate(lines):
            sl = line.strip()
            if (sl.startswith("if") or "else" in sl) and any(tc in sl for tc in type_checks):
                following = "\n".join(lines[i : i + 10])
                if "toTypeError" in following:
                    found = True
                    break

    assert found, (
        "generateSymbols while-loop lacks a type-guard (e.g. !value.isObject()) "
        "in a conditional that leads to toTypeError"
    )


# [pr_diff] fail_to_pass
def test_arg_types_cleanup_in_error_paths():
    """arg_types must be freed in error-return paths before clearAndFree (memory leak fix)."""
    stripped = _stripped_source()
    parts = stripped.split("clearAndFree")
    assert len(parts) >= 3, f"Expected >=3 clearAndFree call sites, found {len(parts) - 1}"

    cleanup_count = 0
    for i in range(1, len(parts)):
        preceding = parts[i - 1][-600:]
        has_arg_cleanup = "arg_types" in preceding and (
            "deinit" in preceding or ".free(" in preceding
        )
        if not has_arg_cleanup:
            continue
        # Must iterate over all symbols (loop nearby)
        tail = preceding[-300:]
        has_loop = "for " in tail or "while" in tail or "symbols.values()" in preceding
        if has_loop:
            cleanup_count += 1

    assert cleanup_count >= 2, (
        f"Only {cleanup_count} error-return paths clean up arg_types before clearAndFree; "
        "expected at least 2 (print, open, linkSymbols)"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_not_stub():
    """generateSymbols retains substantive symbol-parsing logic."""
    stripped = _stripped_source()
    region = _generate_symbols_region(stripped)

    indicators = [
        "symbols_iter",
        "generateSymbolForFunction",
        "toTypeError",
        "isEmptyOrUndefinedOrNull",
        "clearAndFree",
    ]
    found = sum(1 for ind in indicators if ind in region)
    assert found >= 4, (
        f"generateSymbols only contains {found}/5 expected logic indicators — "
        "function appears to be stubbed out"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from src/CLAUDE.md
# ---------------------------------------------------------------------------


# [agent_config] fail_to_pass — src/CLAUDE.md:16 @ 0de7a80
def test_no_std_apis_in_diff():
    """Agent must not introduce std.fs/std.posix/std.os/std.process calls."""
    r = subprocess.run(
        ["git", "diff", "HEAD"],
        capture_output=True, text=True, cwd=REPO,
    )
    diff = r.stdout
    if not diff.strip():
        r = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True, text=True, cwd=REPO,
        )
        diff = r.stdout
    if not diff.strip():
        r = subprocess.run(
            ["git", "diff", "HEAD~1"],
            capture_output=True, text=True, cwd=REPO,
        )
        diff = r.stdout

    assert diff.strip(), "No diff detected — agent has not made any changes"

    added = [l[1:] for l in diff.split("\n") if l.startswith("+") and not l.startswith("+++")]
    forbidden = ["std.fs", "std.posix", "std.os", "std.process"]
    for line in added:
        for f in forbidden:
            assert f not in line, f"Prohibited API '{f}' found in added line: {line.strip()}"


# [agent_config] fail_to_pass — src/CLAUDE.md:11 @ 0de7a80
def test_no_inline_import_in_diff():
    """Agent must not add @import() inline inside functions."""
    r = subprocess.run(
        ["git", "diff", "HEAD"],
        capture_output=True, text=True, cwd=REPO,
    )
    diff = r.stdout
    if not diff.strip():
        r = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True, text=True, cwd=REPO,
        )
        diff = r.stdout
    if not diff.strip():
        r = subprocess.run(
            ["git", "diff", "HEAD~1"],
            capture_output=True, text=True, cwd=REPO,
        )
        diff = r.stdout

    assert diff.strip(), "No diff detected — agent has not made any changes"

    added = [l[1:] for l in diff.split("\n") if l.startswith("+") and not l.startswith("+++")]
    for line in added:
        # @import at file/struct level is OK; deeply indented = inside a function
        if "@import(" in line and len(line) - len(line.lstrip()) > 8:
            raise AssertionError(f"Inline @import inside function body: {line.strip()}")
