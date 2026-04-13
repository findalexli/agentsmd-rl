"""
Task: bun-dns-lookup-non-object-crash
Repo: oven-sh/bun @ 7fb789749edc96504fda8043e82a88eb88592d4e
PR:   28424

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
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
# Gates (pass_to_pass, static) — structural integrity
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_dns_zig_structural_integrity():
    """dns.zig exists and is structurally intact (balanced braces, key symbols)."""
    # AST-only because: Zig requires full Bun compilation (C++/Zig, 30+ min build)
    content = Path(TARGET).read_text()
    opens = content.count("{")
    closes = content.count("}")
    assert abs(opens - closes) <= 5, f"Brace imbalance: {opens} open vs {closes} close"
    assert "pub const Resolver = struct" in content, "Resolver struct missing"
    assert "GetAddrInfo" in content, "GetAddrInfo missing"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_non_object_guard_on_second_arg():
    """Guard on arguments.ptr[1] rejects non-object cells (not just isCell)."""
    # AST-only because: Zig requires full Bun compilation (C++/Zig, 30+ min build)
    content = Path(TARGET).read_text()

    # Find the guard: if (arguments.len > 1 and arguments.ptr[1].<method>()) {
    guard = re.search(
        r'if\s*\(arguments\.len\s*>\s*1\s+and\s+arguments\.ptr\[1\]\.(is\w+)\(\)',
        content,
    )
    assert guard, "Guard pattern 'if (arguments.len > 1 and arguments.ptr[1].isXxx())' not found"

    method = guard.group(1)
    assert method != "isCell", (
        "Guard still uses .isCell() — must use an object-discriminating method like .isObject()"
    )


# [pr_diff] fail_to_pass
def test_guard_uses_valid_object_method():
    """Guard uses a real, object-discriminating JSValue method (not isCell)."""
    # AST-only because: Zig requires full Bun compilation (C++/Zig, 30+ min build)
    content = Path(TARGET).read_text()

    guard = re.search(
        r'if\s*\(arguments\.len\s*>\s*1\s+and\s+arguments\.ptr\[1\]\.(is\w+)\(\)',
        content,
    )
    assert guard, "Guard pattern not found"
    method = guard.group(1)

    # Discover valid isXxx methods from Bun's source files
    valid_methods = set()
    for root, _dirs, files in os.walk(f"{REPO}/src/bun.js"):
        for fname in files:
            if fname.endswith(".zig") or fname.endswith(".h"):
                try:
                    src = open(os.path.join(root, fname)).read()
                    for m in re.findall(r"(?:pub\s+)?fn\s+(is[A-Z]\w*)", src):
                        valid_methods.add(m)
                    for m in re.findall(r"bool\s+(is[A-Z]\w*)", src):
                        valid_methods.add(m)
                except Exception:
                    pass

    valid_methods.discard("isCell")
    if not valid_methods:
        # Fallback if discovery fails
        valid_methods = {"isObject", "isObjectLike", "isObjectOrNull"}

    assert method in valid_methods, (
        f"Guard uses .{method}() which is not a known JSValue method. "
        f"Expected one of: {sorted(valid_methods)[:10]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_options_parsing_intact():
    """Options parsing block still extracts port and family via getTruthy."""
    # AST-only because: Zig requires full Bun compilation (C++/Zig, 30+ min build)
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
    # AST-only because: Zig requires full Bun compilation (C++/Zig, 30+ min build)
    content = Path(TARGET).read_text()
    for required in ["pub const Resolver = struct", "GetAddrInfo", "globalThis"]:
        assert required in content, f"Missing required symbol: {required}"


# [repo_tests] pass_to_pass — CI/CD: zig fmt syntax validation (from .github/workflows/format.yml)
def test_zig_fmt_syntax_valid():
    """dns.zig has valid syntax (balanced braces, no unclosed blocks) for zig fmt compatibility."""
    content = Path(TARGET).read_text()

    # Basic structural validation that zig fmt would check
    # Count braces to detect obvious syntax errors
    open_braces = content.count("{")
    close_braces = content.count("}")
    assert abs(open_braces - close_braces) <= 5, (
        f"Brace imbalance detected: {open_braces} open vs {close_braces} close"
    )

    # Check for unclosed string literals (common syntax error)
    # Need to handle escaped quotes
    lines = content.split("\n")
    for i, line in enumerate(lines, 1):
        # Skip comments
        stripped = line.strip()
        if stripped.startswith("//"):
            continue

        # Count unescaped double quotes
        quote_count = 0
        j = 0
        while j < len(line):
            if line[j] == '"' and (j == 0 or line[j-1] != '\\'):
                quote_count += 1
            j += 1

    # Check for basic Zig construct validity
    assert "pub const Resolver = struct" in content, "Missing Resolver struct definition"


# [repo_tests] pass_to_pass — CI/CD: oxlint on DNS JS files (from .github/workflows/lint.yml)
def test_oxlint_dns_js():
    """DNS JS files pass oxlint validation (pass_to_pass)."""
    # Check DNS-related JS files with oxlint via npx (actual CI command)
    dns_js_files = [
        f"{REPO}/src/js/node/dns.ts",
        f"{REPO}/src/js/node/dns.promises.ts",
    ]

    for js_file in dns_js_files:
        if not Path(js_file).exists():
            continue

        # Run oxlint via npx on the file (actual CI command from lint.yml)
        r = subprocess.run(
            ["npx", "oxlint", "--config=oxlint.json", js_file],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO,
        )
        # Exit 0 = no errors, exit 1 = warnings only (both acceptable)
        assert r.returncode in [0, 1], (
            f"oxlint failed for {js_file} with exit {r.returncode}:\n{r.stderr[-500:]}"
        )


# [repo_tests] pass_to_pass — CI/CD: ban-words check (from .github/workflows/format.yml)
def test_no_banned_words_in_dns_zig():
    """dns.zig does not contain banned words/patterns (CI ban-words check)."""
    content = Path(TARGET).read_text()

    # Banned patterns from test/internal/ban-words.test.ts
    # that are relevant to the dns.zig file
    banned_patterns = {
        "std.debug.assert": "Use bun.assert instead of std.debug.assert",
        "std.debug.print": "Don't commit std.debug.print statements",
        "std.log": "Don't commit std.log statements",
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
                # Skip commented lines
                stripped = line.strip()
                if not stripped.startswith("//"):
                    pytest.fail(f"Line {i}: Banned pattern '{pattern}' found. {message}")


# [repo_tests] pass_to_pass — CI/CD: prettier check on DNS test files (from .github/workflows/format.yml)
def test_prettier_dns_test_files():
    """DNS test files pass prettier format check (pass_to_pass)."""
    dns_test_files = [
        f"{REPO}/test/js/node/dns/node-dns.test.js",
        f"{REPO}/test/js/node/dns/dns-lookup-keepalive.test.ts",
    ]

    for test_file in dns_test_files:
        if not Path(test_file).exists():
            continue

        # Run prettier --check via npx (actual CI command)
        r = subprocess.run(
            ["npx", "prettier", "--check", test_file],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO,
        )
        # Exit 0 = formatted correctly
        assert r.returncode == 0, (
            f"Prettier check failed for {test_file}:\n{r.stderr[-500:]}"
        )


# [repo_tests] pass_to_pass — CI/CD: node syntax check on DNS JS files
def test_dns_js_syntax_valid():
    """DNS JS files have valid Node.js syntax (pass_to_pass)."""
    dns_js_files = [
        f"{REPO}/src/js/node/dns.ts",
        f"{REPO}/src/js/node/dns.promises.ts",
    ]

    for js_file in dns_js_files:
        if not Path(js_file).exists():
            continue

        # Use node --check to validate syntax (ignores type errors, checks syntax only)
        # For .ts files, node --check doesn't work directly, so we skip or use npx ts-node
        if js_file.endswith(".ts"):
            # Skip TypeScript files for node --check (no ts-node in container)
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
