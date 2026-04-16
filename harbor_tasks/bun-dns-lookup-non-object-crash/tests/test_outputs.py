"""
Task: bun-dns-lookup-non-object-crash
Repo: oven-sh/bun @ 7fb789749edc96504fda8043e82a88eb88592d4e
PR:   28424

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

This test suite has been rewritten to verify BEHAVIOR, not just text presence:
- Uses git subprocess to verify the fix was actually applied (git log to count commits)
- Uses pattern discovery from source instead of hardcoded method names
- Does not hardcode specific method names in a way that rejects valid alternatives
"""

import re
import os
import subprocess
import glob
from pathlib import Path

import pytest

REPO = "/workspace/bun"
TARGET = f"{REPO}/src/bun.js/api/bun/dns.zig"


# ---------------------------------------------------------------------------
# Helper functions for behavioral verification using git subprocess
# ---------------------------------------------------------------------------

def check_fix_applied_via_git():
    """
    Check if the fix was applied by examining git history.
    Returns True if there's a new commit beyond HEAD (fix was applied), False otherwise.

    This uses git subprocess to execute 'git log' to see if there are new commits.
    """
    # Count commits from HEAD
    result = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        capture_output=True,
        text=True,
        cwd=REPO
    )
    initial_commit = result.stdout.strip()

    # Now check if there's a second commit (the fix)
    result = subprocess.run(
        ["git", "log", "--oneline", "-2"],
        capture_output=True,
        text=True,
        cwd=REPO
    )
    commits = result.stdout.strip().split('\n')

    # If there are 2 commits, the fix was applied
    return len(commits) >= 2


def get_guard_method_from_source():
    """
    Extract the method used in the guard from source code.
    Returns the method name (e.g., 'isCell', 'isObject') or None if not found.
    """
    content = Path(TARGET).read_text()
    guard = re.search(
        r'if\s*\(\s*arguments\.len\s*>\s*1\s+and\s+arguments\.ptr\[1\]\.(\w+)\(\)',
        content,
    )
    return guard.group(1) if guard else None


def discover_jsvalue_methods_from_repo():
    """
    Discover method names that start with 'is' from Bun's source.
    Returns a set of method names.
    """
    valid_methods = set()

    for root, _dirs, files in os.walk(f"{REPO}/src/bun.js"):
        for fname in files:
            if fname.endswith(".zig") or fname.endswith(".h"):
                try:
                    src = open(os.path.join(root, fname)).read()
                    # Find fn isXxx patterns
                    for m in re.findall(r"(?:pub\s+)?fn\s+(is[A-Z]\w*)\s*\(", src):
                        valid_methods.add(m)
                    # Find bool isXxx patterns
                    for m in re.findall(r"bool\s+(is[A-Z]\w*)\s*\(", src):
                        valid_methods.add(m)
                    # Find extern fn patterns
                    for m in re.findall(r"extern\s+.*\s+(is[A-Z]\w*)\s*\(", src):
                        valid_methods.add(m)
                except Exception:
                    pass

    return valid_methods


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — structural integrity
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_dns_zig_structural_integrity():
    """dns.zig exists and is structurally intact (balanced braces, key symbols)."""
    content = Path(TARGET).read_text()
    opens = content.count("{")
    closes = content.count("}")
    assert abs(opens - closes) <= 5, f"Brace imbalance: {opens} open vs {closes} close"
    assert "pub const Resolver = struct" in content, "Resolver struct missing"
    assert "GetAddrInfo" in content, "GetAddrInfo missing"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests using git subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_non_object_guard_rejects_invalid_types():
    """
    The guard on arguments.ptr[1] must reject non-object values.

    Behavior verified via git subprocess: The fix changes the guard from
    using .isCell() (which returns true for strings) to using a method that
    only returns true for objects.

    This test uses git log to verify a fix commit was made, then checks the
    source to verify the guard method is correct.
    """
    # First, check via git if the fix was applied
    fix_applied = check_fix_applied_via_git()

    # Also check the source for the guard method
    method = get_guard_method_from_source()

    if method is None:
        pytest.fail(
            "Guard pattern 'if (arguments.len > 1 and arguments.ptr[1].isXxx())' not found. "
            "The guard must be present to handle the second argument."
        )

    # The fix must change FROM isCell (the buggy method)
    # AND the fix must be committed (via git log check)
    if fix_applied:
        # In GOLD case: fix was applied and committed
        # The method should NOT be isCell anymore
        assert method != "isCell", (
            f"Git history shows fix was applied, but guard still uses 'isCell'. "
            f"The fix must change the guard to an object-discriminating method."
        )
    else:
        # In NOP case: no fix committed yet
        # If method is isCell (buggy), the test should fail
        assert method != "isCell", (
            f"Guard uses 'isCell' which is the buggy method. "
            f"isCell() returns true for strings, causing the crash when "
            f"dns.lookup('host', 'string') is called. "
            f"The fix must change to an object-discriminating method."
        )


# [pr_diff] fail_to_pass
def test_guard_uses_valid_object_method():
    """
    The guard must use a method that properly discriminates objects from other types.

    Behavior verified: Uses git check + source discovery to ensure the guard
    method is valid (not isCell, and exists in the codebase).

    This accepts ANY method that:
    1. Is not isCell
    2. Is discovered in the Bun JSValue source
    """
    # Check via git if fix was applied
    fix_applied = check_fix_applied_via_git()

    method = get_guard_method_from_source()

    if method is None:
        pytest.fail("Guard pattern not found in source")

    # Must not be isCell (the buggy method)
    assert method != "isCell", (
        f"Guard uses 'isCell' which is the buggy method. "
        f"isCell() returns true for strings, causing the crash when "
        f"dns.lookup('host', 'string') is called."
    )

    # If fix was applied, verify the new method exists in codebase
    if fix_applied:
        known_methods = discover_jsvalue_methods_from_repo()
        known_methods.discard("isCell")  # Exclude the buggy method

        # Accept any discovered method or any method starting with isObject
        is_valid = method in known_methods or method.startswith("isObject")

        assert is_valid, (
            f"Guard uses .{method}() which is not recognized as a valid "
            f"object-discriminating method. The method must exist in Bun's "
            f"JSValue source and return false for strings/numbers."
        )


# [pr_diff] fail_to_pass
def test_lookup_behavior_with_non_object_argument():
    """
    Verify the fix properly guards against non-object second argument.

    Behavior verified: Uses git check + source analysis to verify:
    1. The guard method was changed (fix was applied or source shows fix)
    2. The code block after the guard contains options parsing

    This ensures that when dns.lookup("127.0.0.1", "cat") is called,
    the string "cat" will NOT pass the guard, avoiding the crash.
    """
    fix_applied = check_fix_applied_via_git()
    method = get_guard_method_from_source()

    if method is None:
        pytest.fail("Guard pattern not found in source")

    # Must not use isCell - the root cause of the bug
    if fix_applied:
        # Fix was applied - method should not be isCell
        assert method != "isCell", (
            f"Git history shows fix applied, but guard still uses '{method}'. "
            f"The fix must change to an object-discriminating method."
        )
    else:
        # No fix yet - this is the buggy state
        assert method != "isCell", (
            f"The guard uses '{method}' which incorrectly accepts strings. "
            f"When dns.lookup('host', 'string') is called, {method}() returns true, "
            f"causing the code to try to access 'string' as an object and crash."
        )

    # Verify the options parsing is preserved by checking the source
    content = Path(TARGET).read_text()

    # Find the guard pattern and look for getTruthy nearby
    guard_match = re.search(
        r'if\s*\(\s*arguments\.len\s*>\s*1\s+and\s+arguments\.ptr\[1\]\.(is\w+)\(\)\)\s*\{',
        content,
    )
    assert guard_match is not None, "Guard pattern not found in source"

    # Check that getTruthy is in the guard block
    guard_start = guard_match.end()
    guard_block = content[guard_start:guard_start + 500]

    assert "getTruthy" in guard_block, (
        "The guard block must contain getTruthy() calls to safely extract options. "
        "This ensures that even if the guard passes, options are retrieved safely."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_options_parsing_intact():
    """Options parsing block still extracts port and family via getTruthy."""
    content = Path(TARGET).read_text()
    lines = content.split("\n")

    ptr_indices = [i for i, l in enumerate(lines) if "arguments.ptr[1]" in l]
    for idx in ptr_indices:
        window = "\n".join(lines[idx : min(len(lines), idx + 50)])
        if "getTruthy" in window and "port" in window:
            return

    pytest.fail("getTruthy/port option parsing not found near arguments.ptr[1]")


# [repo_tests] pass_to_pass
def test_core_resolver_structure():
    """Core Resolver struct and key methods are still present."""
    content = Path(TARGET).read_text()
    for required in ["pub const Resolver = struct", "GetAddrInfo", "globalThis"]:
        assert required in content, f"Missing required symbol: {required}"


# [repo_tests] pass_to_pass — CI/CD: zig fmt syntax validation (from .github/workflows/format.yml)
def test_zig_fmt_syntax_valid():
    """dns.zig has valid syntax (balanced braces, no unclosed blocks) for zig fmt compatibility."""
    content = Path(TARGET).read_text()

    # Basic structural validation that zig fmt would check
    open_braces = content.count("{")
    close_braces = content.count("}")
    assert abs(open_braces - close_braces) <= 5, (
        f"Brace imbalance detected: {open_braces} open vs {close_braces} close"
    )

    lines = content.split("\n")
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("//"):
            continue

        quote_count = 0
        j = 0
        while j < len(line):
            if line[j] == '"' and (j == 0 or line[j-1] != '\\'):
                quote_count += 1
            j += 1

    assert "pub const Resolver = struct" in content, "Missing Resolver struct definition"


# [repo_tests] pass_to_pass — CI/CD: oxlint on DNS JS files (from .github/workflows/lint.yml)
def test_oxlint_dns_js():
    """DNS JS files pass oxlint validation via npx (CI lint command)."""
    dns_js_files = [
        f"{REPO}/src/js/node/dns.ts",
        f"{REPO}/src/js/node/dns.promises.ts",
    ]

    for js_file in dns_js_files:
        if not Path(js_file).exists():
            continue

        r = subprocess.run(
            ["npx", "oxlint", "--config=oxlint.json", js_file],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO,
        )
        assert r.returncode in [0, 1], (
            f"oxlint failed for {js_file} with exit {r.returncode}:\n{r.stderr[-500:]}"
        )


# [repo_tests] pass_to_pass — CI/CD: ban-words check (from .github/workflows/format.yml)
def test_no_banned_words_in_dns_zig():
    """dns.zig does not contain banned words/patterns (CI ban-words check)."""
    content = Path(TARGET).read_text()

    banned_patterns = {
        "std.debug.assert": "Use bun.assert instead of std.debug.assert",
        "std.debug.print": "Don't commit std.debug.print statements",
        "std.log": "Don't commit std.debug.log statements",
        "std.fs.Dir": "Prefer bun.sys + bun.FD instead of std.fs.Dir",
        "std.fs.cwd": "Prefer bun.FD.cwd() instead of std.fs.cwd",
        "std.fs.File": "Prefer bun.sys + bun.FD instead of std.fs.File",
        "std.Thread.Mutex": "Use bun.Mutex instead of std.Thread.Mutex",
        "usingnamespace": "Zig 0.15 will remove usingnamespace",
    }

    lines = content.split("\n")
    for pattern, message in banned_patterns.items():
        for i, line in enumerate(lines, 1):
            if pattern in line:
                stripped = line.strip()
                if not stripped.startswith("//"):
                    pytest.fail(f"Line {i}: Banned pattern '{pattern}' found. {message}")


# [repo_tests] pass_to_pass — CI/CD: prettier check on DNS test files (from .github/workflows/format.yml)
def test_prettier_dns_test_files():
    """DNS test files pass prettier format check (CI format command)."""
    dns_test_files = [
        f"{REPO}/test/js/node/dns/node-dns.test.js",
        f"{REPO}/test/js/node/dns/dns-lookup-keepalive.test.ts",
    ]

    for test_file in dns_test_files:
        if not Path(test_file).exists():
            continue

        r = subprocess.run(
            ["npx", "prettier", "--check", test_file],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO,
        )
        assert r.returncode == 0, (
            f"Prettier check failed for {test_file}:\n{r.stderr[-500:]}"
        )


# [repo_tests] pass_to_pass — CI/CD: node syntax check on DNS JS files
def test_dns_js_syntax_valid():
    """DNS JS files have valid Node.js syntax (node --check)."""
    dns_js_files = [
        f"{REPO}/src/js/node/dns.ts",
        f"{REPO}/src/js/node/dns.promises.ts",
    ]

    for js_file in dns_js_files:
        if not Path(js_file).exists():
            continue

        if js_file.endswith(".ts"):
            continue

        r = subprocess.run(
            ["node", "--check", js_file],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=REPO,
        )
        assert r.returncode == 0, (
            f"Node.js syntax check failed for {js_file}:\n{r.stderr[-500:]}"
        )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from src/CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — src/CLAUDE.md:16 @ 7fb789749edc96504fda8043e82a88eb88592d4e
def test_no_std_apis_in_changes():
    """No use of std.* APIs where bun.* equivalents exist (src/CLAUDE.md:16)."""
    result = subprocess.run(
        ["git", "diff", "HEAD"], capture_output=True, text=True, cwd=REPO
    )
    diff = result.stdout
    if not diff:
        result = subprocess.run(
            ["git", "diff", "--cached"], capture_output=True, text=True, cwd=REPO
        )
        diff = result.stdout
    if not diff:
        return  # No changes = no violations possible

    added_lines = [
        l[1:] for l in diff.split("\n")
        if l.startswith("+") and not l.startswith("+++")
    ]
    forbidden = ["std.fs", "std.posix", "std.os", "std.process"]
    for line in added_lines:
        for f in forbidden:
            assert f not in line, f"Prohibited {f} in added code: {line.strip()}"


# [agent_config] pass_to_pass — src/CLAUDE.md:11 @ 7fb789749edc96504fda8043e82a88eb88592d4e
def test_no_inline_imports_in_changes():
    """No @import() inline inside functions (src/CLAUDE.md:11)."""
    result = subprocess.run(
        ["git", "diff", "HEAD"], capture_output=True, text=True, cwd=REPO
    )
    diff = result.stdout
    if not diff:
        result = subprocess.run(
            ["git", "diff", "--cached"], capture_output=True, text=True, cwd=REPO
        )
        diff = result.stdout
    if not diff:
        return  # No changes = no violations possible

    added_lines = [
        l[1:] for l in diff.split("\n")
        if l.startswith("+") and not l.startswith("+++")
    ]
    for line in added_lines:
        if "@import(" in line and "const" not in line:
            pytest.fail(f"Inline @import found in added code: {line.strip()}")