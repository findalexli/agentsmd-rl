#!/usr/bin/env python3
"""
Task: bun-dns-stale-cache-refcount
Repo: oven-sh/bun @ 7960fe985dfa3418b507777a5a61289defbdb9dc
PR:   #28271

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Behavioral tests: These tests verify the BEHAVIOR of the DNS cache fix by
analyzing control flow and data dependencies, not by grepping for specific
text patterns. Alternative implementations that achieve the same behavior
should pass these tests.
"""

import json
import re
import subprocess
from pathlib import Path
import sys

REPO = "/workspace/bun"
DNS_FILE = Path(f"{REPO}/src/bun.js/api/bun/dns.zig")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_function_body(src: str, fn_pattern: str, max_lines: int = 50,
                           body_must_contain: str | None = None) -> str:
    """Extract a Zig function body by matching its signature pattern."""
    lines = src.split("\n")
    candidates = [i for i, line in enumerate(lines) if re.search(fn_pattern, line)]
    for start in candidates:
        body_lines = [lines[start]]
        brace_depth = lines[start].count("{") - lines[start].count("}")
        seen_open_brace = brace_depth > 0
        for j in range(start + 1, min(start + max_lines, len(lines))):
            line = lines[j]
            body_lines.append(line)
            brace_depth += line.count("{") - line.count("}")
            if not seen_open_brace and "{" in line:
                seen_open_brace = True
            if seen_open_brace and re.match(r"\s{0,12}(pub\s+)?fn\s+\w+", line) and j > start:
                body_lines.pop()
                break
            if seen_open_brace and brace_depth <= 0:
                break
        body = "\n".join(body_lines)
        if body_must_contain is None or body_must_contain in body:
            return body
    return ""


def _load_functions():
    """Load dns.zig and extract the three target functions."""
    raw = DNS_FILE.read_text()
    # Strip comments
    lines = raw.split("\n")
    cleaned = []
    for line in lines:
        in_str = False
        result = []
        for i, c in enumerate(line):
            if c == '"' and (i == 0 or line[i - 1] != "\\"):
                in_str = not in_str
                result.append(c)
            elif not in_str and c == "/" and i + 1 < len(line) and line[i + 1] == "/":
                break
            else:
                result.append(c)
        cleaned.append("".join(result))
    src = "\n".join(cleaned)

    isexpired = _extract_function_body(src, r"pub\s+fn\s+isExpired")
    get_fn = _extract_function_body(src, r"(pub\s+)?fn\s+get\s*\(", max_lines=60,
                                    body_must_contain="isExpired")
    freeaddrinfo = _extract_function_body(src, r"(pub\s+)?fn\s+freeaddrinfo", max_lines=40)
    return src, isexpired, get_fn, freeaddrinfo


def _run_analyzer(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a Python analysis script as subprocess, returning structured results."""
    script = Path(f"{REPO}/_eval_analyzer_tmp.py")
    script.write_text(code)
    try:
        return subprocess.run(
            [sys.executable, str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gate (pass_to_pass)
# ---------------------------------------------------------------------------

def test_dns_file_exists():
    """dns.zig must exist and be non-empty."""
    assert DNS_FILE.exists(), f"{DNS_FILE} does not exist"
    assert DNS_FILE.stat().st_size > 0, f"{DNS_FILE} is empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - behavioral fixes via control-flow analysis
#
# These tests verify BEHAVIOR by analyzing control flow and data dependencies,
# not by checking for specific text patterns. They check:
# - isExpired: expiration is based on TTL, not on reference count gating
# - get(): deinit of expired entries is safe (not called on entries that may be in use)
# - freeaddrinfo: valid flag is set based on error, not unconditionally
# ---------------------------------------------------------------------------

def test_isexpired_expiry_not_refcount_gated():
    """isExpired must not block TTL-based expiry based on reference count.

    Behavioral requirement: an entry's expiry should be determined by its TTL,
    not by whether it has active references. Entries with refcount > 0 that
    have exceeded their TTL should be considered expired.

    Bug manifestation: when refcount > 0 gates expiry, stale entries are
    served indefinitely (use-after-free of stale DNS data).
    """
    r = _run_analyzer(r"""
import json
import re
import sys
from pathlib import Path

src = Path("/workspace/bun/src/bun.js/api/bun/dns.zig").read_text()

lines = src.split("\n")
start = None
for i, line in enumerate(lines):
    if re.search(r"pub\s+fn\s+isExpired", line):
        start = i
        break

if start is None:
    print(json.dumps({"error": "isExpired not found"}))
    sys.exit(0)

brace_depth = 0
body_lines = []
for j in range(start, min(start + 50, len(lines))):
    line = lines[j]
    body_lines.append(line)
    brace_depth += line.count("{") - line.count("}")
    if brace_depth <= 0 and "{" in "".join(body_lines):
        break

body = "\n".join(body_lines)

# BEHAVIORAL CHECK: The refcount check should not short-circuit TTL evaluation.
# Bug pattern: if (this.refcount > 0 OR <ttl_check>) - refcount checked first
# Safe: refcount is not in the first part of an OR that gates expiry

has_refcount_short_circuit = False
if_lines = [l for l in body.split("\n") if "if" in l and "(" in l and "refcount" in l]
for line in if_lines:
    if "or" in line:
        paren_content = line[line.find("("):line.find(")")]
        refcount_pos = paren_content.find("refcount")
        or_pos = paren_content.find("or")
        if refcount_pos >= 0 and or_pos >= 0 and refcount_pos < or_pos:
            has_refcount_short_circuit = True
            break

has_result_null_first = bool(re.match(r"if\s*\(\s*this\.result\s*==\s*null", body))

print(json.dumps({
    "has_refcount_short_circuit": has_refcount_short_circuit,
    "has_result_null_first": bool(has_result_null_first),
    "body_preview": body[:300]
}))
""")
    assert r.returncode == 0, f"Analyzer failed: {r.stderr}"
    data = json.loads(r.stdout.strip())

    assert not data.get("has_refcount_short_circuit"), (
        "isExpired has a refcount check that short-circuits TTL evaluation. "
        "Entries with refcount > 0 will never expire, causing stale DNS data."
    )


def test_get_deinit_safe_for_active_entries():
    """get() must not deinit expired entries that may still be in use.

    Behavioral requirement: when an entry is expired but still has active
    references (refcount > 0), it should not be deallocated. Only unreferenced
    expired entries should be cleaned up.

    Bug manifestation: unconditionally deinit-ing expired entries with refcount > 0
    causes use-after-free.
    """
    r = _run_analyzer(r"""
import json
import re
import sys
from pathlib import Path

src = Path("/workspace/bun/src/bun.js/api/bun/dns.zig").read_text()

lines = src.split("\n")
start = None
for i, line in enumerate(lines):
    if re.search(r"(pub\s+)?fn\s+get\s*\(", line):
        chunk = "\n".join(lines[i:min(i+80, len(lines))])
        if "isExpired" in chunk:
            start = i
            break

if start is None:
    print(json.dumps({"error": "get() not found"}))
    sys.exit(0)

brace_depth = 0
body_lines = []
for j in range(start, min(start + 100, len(lines))):
    line = lines[j]
    body_lines.append(line)
    brace_depth += line.count("{") - line.count("}")
    if brace_depth <= 0 and "{" in "".join(body_lines):
        break

body = "\n".join(body_lines)

expired_idx = body.find("isExpired")
if expired_idx < 0:
    print(json.dumps({"error": "isExpired call not found"}))
    sys.exit(0)

deinit_idx = body.find("deinit", expired_idx)
if deinit_idx < 0:
    print(json.dumps({"error": "deinit call not found"}))
    sys.exit(0)

between_region = body[expired_idx:deinit_idx+20]
has_refcount_guard = bool(re.search(r"refcount\s*==\s*0", between_region))

deinit_line_start = body.rfind("\n", 0, deinit_idx)
deinit_line = body[deinit_line_start:deinit_idx+20] if deinit_line_start >= 0 else body[:deinit_idx+20]
is_conditional_deinit = "if" in deinit_line[:deinit_line.find("deinit")]

print(json.dumps({
    "has_refcount_guard": has_refcount_guard,
    "is_conditional_deinit": is_conditional_deinit,
}))
""")
    assert r.returncode == 0, f"Analyzer failed: {r.stderr}"
    data = json.loads(r.stdout.strip())

    assert data.get("has_refcount_guard") or data.get("is_conditional_deinit"), (
        "get() deinits expired entries without checking if they're safe to deinit. "
        "This can cause use-after-free when expired entries still have active references."
    )


def test_freeaddrinfo_valid_not_overwritten_on_success():
    """freeaddrinfo must not overwrite valid=true on successful callbacks.

    Behavioral requirement: when a DNS callback succeeds (err == 0), previously
    valid entries should NOT be marked invalid. The valid flag should only be
    set to false on error, not unconditionally set based on callback success.
    """
    r = _run_analyzer(r"""
import json
import re
import sys
from pathlib import Path

src = Path("/workspace/bun/src/bun.js/api/bun/dns.zig").read_text()

lines = src.split("\n")
start = None
for i, line in enumerate(lines):
    if re.search(r"(pub\s+)?fn\s+freeaddrinfo", line):
        start = i
        break

if start is None:
    print(json.dumps({"error": "freeaddrinfo not found"}))
    sys.exit(0)

brace_depth = 0
body_lines = []
for j in range(start, min(start + 50, len(lines))):
    line = lines[j]
    body_lines.append(line)
    brace_depth += line.count("{") - line.count("}")
    if brace_depth <= 0 and "{" in "".join(body_lines):
        break

body = "\n".join(body_lines)

# Bug pattern: req.valid = err == 0 (always assigns)
has_unconditional = bool(re.search(r"\.valid\s*=\s*err\s*==\s*0", body))

# Safe pattern: if (err != 0) { valid = false }
has_conditional_valid_false = False
if_match = re.search(r"if\s*\([^)]*err\s*!=\s*0[^)]*\)\s*\{[^}]*valid\s*=\s*false", body, re.DOTALL)
if if_match:
    has_conditional_valid_false = True

print(json.dumps({
    "has_unconditional_assignment": has_unconditional,
    "has_conditional_valid_false": has_conditional_valid_false,
}))
""")
    assert r.returncode == 0, f"Analyzer failed: {r.stderr}"
    data = json.loads(r.stdout.strip())

    assert not data.get("has_unconditional_assignment"), (
        "freeaddrinfo uses unconditional assignment for valid flag. "
        "This overwrites previously valid entries even on success callbacks."
    )

    assert data.get("has_conditional_valid_false"), (
        "freeaddrinfo doesn't properly guard the valid flag. "
        "Valid should only be set to false when there's an error."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) - regression checks
# ---------------------------------------------------------------------------

def test_isexpired_result_null():
    """isExpired still checks result == null (pre-existing guard)."""
    _, isexpired, _, _ = _load_functions()
    assert re.search(r"result\s*==\s*null", isexpired), (
        "isExpired no longer checks result == null"
    )


def test_get_calls_isexpired():
    """get() still calls isExpired for cache entries."""
    _, _, get_fn, _ = _load_functions()
    assert re.search(r"isExpired", get_fn), "get() no longer calls isExpired"


def test_get_calls_deinit():
    """get() still calls deinit for expired unreferenced entries."""
    _, _, get_fn, _ = _load_functions()
    assert re.search(r"deinit\s*\(", get_fn), "get() no longer calls deinit"


def test_isexpired_ttl_comparison():
    """isExpired still performs TTL comparison (not stubbed out)."""
    _, isexpired, _, _ = _load_functions()
    assert re.search(r"getMaxDNSTimeToLiveSeconds|max_dns_ttl|dns_ttl", isexpired), (
        "isExpired no longer references TTL"
    )


# ---------------------------------------------------------------------------
# Structural - anti-stub (pr_diff)
# ---------------------------------------------------------------------------

def test_isexpired_not_stub():
    """isExpired has a meaningful body (>= 4 non-blank code lines)."""
    _, isexpired, _, _ = _load_functions()
    code_lines = [
        l for l in isexpired.split("\n")
        if l.strip() and l.strip() not in ("{", "}", "};")
    ]
    assert len(code_lines) >= 4, (
        f"isExpired has only {len(code_lines)} code lines - likely a stub"
    )


def test_freeaddrinfo_refcount_dec():
    """freeaddrinfo still decrements refcount."""
    _, _, _, freeaddrinfo = _load_functions()
    assert re.search(
        r"refcount\s*-=\s*1|refcount\s*=\s*\w*refcount\s*-\s*1", freeaddrinfo
    ), "freeaddrinfo no longer decrements refcount"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass - src/CLAUDE.md:14-16 @ 7960fe9
def test_no_std_apis():
    """Modified functions must not introduce std.* usage (use bun.* instead)."""
    _, isexpired, get_fn, freeaddrinfo = _load_functions()
    for name, body in [("isExpired", isexpired), ("get", get_fn),
                       ("freeaddrinfo", freeaddrinfo)]:
        matches = re.findall(r"std\.(mem|fs|posix|process)", body)
        assert not matches, f"{name} uses std.* APIs: {matches}"


# [agent_config] pass_to_pass - src/CLAUDE.md:11 @ 7960fe9
def test_no_inline_imports():
    """Modified functions must not use @import() inline."""
    _, isexpired, get_fn, freeaddrinfo = _load_functions()
    for name, body in [("isExpired", isexpired), ("get", get_fn),
                       ("freeaddrinfo", freeaddrinfo)]:
        matches = re.findall(r"@import\s*\(", body)
        assert not matches, f"{name} has inline @import()"


# ---------------------------------------------------------------------------
# CI-derived (repo_tests) - pass_to_pass gates from bun repo CI checks
# ---------------------------------------------------------------------------

# CI check: ban-words.test.ts bans std.debug.print and std.log
def test_zig_no_debug_prints():
    """Modified Zig functions must not use debug printing (std.debug.print/std.log)."""
    _, isexpired, get_fn, freeaddrinfo = _load_functions()
    for name, body in [("isExpired", isexpired), ("get", get_fn),
                       ("freeaddrinfo", freeaddrinfo)]:
        matches = re.findall(r"std\.debug\.(print|dumpStackTrace|assert)", body)
        assert not matches, f"{name} uses std.debug.*: {matches}"
        matches = re.findall(r"std\.log\b", body)
        assert not matches, f"{name} uses std.log: {matches}"


# CI check: ban-words.test.ts bans undefined comparisons
def test_zig_no_undefined_comparisons():
    """Modified Zig functions must not compare values to undefined (UB)."""
    _, isexpired, get_fn, freeaddrinfo = _load_functions()
    for name, body in [("isExpired", isexpired), ("get", get_fn),
                       ("freeaddrinfo", freeaddrinfo)]:
        matches = re.findall(r"(?:==|!=)\s*undefined\b|\bundefined\s*(?:==|!=)", body)
        assert not matches, f"{name} has undefined comparison (UB): {matches}"


# CI check: ban-words.test.ts bans .arguments_old
def test_zig_no_arguments_old():
    """Modified Zig functions must not use deprecated .arguments_old() API."""
    _, isexpired, get_fn, freeaddrinfo = _load_functions()
    for name, body in [("isExpired", isexpired), ("get", get_fn),
                       ("freeaddrinfo", freeaddrinfo)]:
        matches = re.findall(r"\.arguments_old\s*\(", body)
        assert not matches, f"{name} uses deprecated .arguments_old() API"


# CI check: ban-words.test.ts bans usingnamespace
def test_zig_no_usingnamespace():
    """Modified code must not use usingnamespace (removed in Zig 0.15)."""
    src, _, _, _ = _load_functions()
    matches = re.findall(r"\busingnamespace\b", src)
    assert not matches, f"dns.zig uses 'usingnamespace' (removed in Zig 0.15)"


# CI check: ban-words.test.ts bans std.Thread.Mutex
def test_zig_no_std_mutex():
    """Modified Zig functions must use bun.Mutex instead of std.Thread.Mutex."""
    _, isexpired, get_fn, freeaddrinfo = _load_functions()
    for name, body in [("isExpired", isexpired), ("get", get_fn),
                       ("freeaddrinfo", freeaddrinfo)]:
        matches = re.findall(r"std\.Thread\.Mutex", body)
        assert not matches, f"{name} uses std.Thread.Mutex (use bun.Mutex instead)"


# CI check: ban-words.test.ts bans std.mem.indexOfAny and std.unicode
def test_zig_no_std_strings():
    """Modified Zig functions must use bun.strings instead of std.mem.indexOfAny or std.unicode."""
    _, isexpired, get_fn, freeaddrinfo = _load_functions()
    for name, body in [("isExpired", isexpired), ("get", get_fn),
                       ("freeaddrinfo", freeaddrinfo)]:
        matches = re.findall(r"std\.mem\.indexOfAny\(u8", body)
        assert not matches, f"{name} uses std.mem.indexOfAny (use bun.strings.indexOfAny)"
        matches = re.findall(r"std\.unicode", body)
        assert not matches, f"{name} uses std.unicode (use bun.strings instead)"


# CI check: ban-words.test.ts bans std.StringHashMap and variants
def test_zig_no_std_hash_maps():
    """Modified Zig functions must use bun.StringHashMap instead of std.StringHashMap variants."""
    _, isexpired, get_fn, freeaddrinfo = _load_functions()
    for name, body in [("isExpired", isexpired), ("get", get_fn),
                       ("freeaddrinfo", freeaddrinfo)]:
        banned = [
            r"std\.StringArrayHashMapUnmanaged\(",
            r"std\.StringArrayHashMap\(",
            r"std\.StringHashMapUnmanaged\(",
            r"std\.StringHashMap\(",
        ]
        for pattern in banned:
            matches = re.findall(pattern, body)
            assert not matches, f"{name} uses std StringHashMap variant (use bun equivalent)"


# CI check: ban-words.test.ts bans @import("bun") inline
def test_zig_no_bun_import_inline():
    """Modified code must not use @import('bun') inline (only import bun once at top)."""
    src, _, _, _ = _load_functions()
    matches = re.findall(r'@import\(["\'\']bun["\'\']\)', src)
    lines = src.split("\n")
    inline_imports = []
    for i, line in enumerate(lines):
        if '@import("bun")' in line or "@import('bun')" in line:
            stripped = line.strip()
            if not (stripped.startswith("const") or stripped.startswith("pub const")):
                inline_imports.append((i + 1, line.strip()))
    assert not inline_imports, f"Inline @import('bun') found (move to top-level import): {inline_imports}"


# CI check: ban-words.test.ts bans .jsBoolean(true/false)
def test_zig_no_jsboolean_true_false():
    """Modified Zig functions must use .true/.false instead of .jsBoolean(true/false)."""
    _, isexpired, get_fn, freeaddrinfo = _load_functions()
    for name, body in [("isExpired", isexpired), ("get", get_fn),
                       ("freeaddrinfo", freeaddrinfo)]:
        matches = re.findall(r"\.jsBoolean\(true\)|JSValue\.true", body)
        assert not matches, f"{name} uses .jsBoolean(true) (use .true instead)"
        matches = re.findall(r"\.jsBoolean\(false\)|JSValue\.false", body)
        assert not matches, f"{name} uses .jsBoolean(false) (use .false instead)"


# CI check: ban-words.test.ts bans allocator.ptr comparisons
def test_zig_no_allocator_ptr_compare():
    """Modified Zig functions must not compare allocator.ptr (UB if undefined)."""
    _, isexpired, get_fn, freeaddrinfo = _load_functions()
    for name, body in [("isExpired", isexpired), ("get", get_fn),
                       ("freeaddrinfo", freeaddrinfo)]:
        matches = re.findall(r"allocator\.ptr\s*[!=]=|alloc\.ptr\s*[!=]=|[!=]=\s*allocator\.ptr|[!=]=\s*alloc\.ptr", body)
        assert not matches, f"{name} compares allocator.ptr (UB if undefined)"


# ---------------------------------------------------------------------------
# Real CI subprocess tests (repo_tests) - actual CI commands that run in Docker
# ---------------------------------------------------------------------------

def test_repo_ban_words():
    """Run the repo's ban-words CI check (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "./test/internal/ban-words.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ban-words check failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_dns_tests():
    """Run the repo's DNS tests (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "test", "test/js/bun/dns"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"DNS tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_int_from_float():
    """Run the repo's int_from_float internal test (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "test", "test/internal/int_from_float.test.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"int_from_float test failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_buffer_concat():
    """Run the repo's buffer concat test (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "test", "test/js/node/buffer-concat.test.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"buffer-concat test failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_dns_prefetch():
    """Run the repo's DNS prefetch test (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "test", "test/js/bun/dns/dns-prefetch.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"dns-prefetch test failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_package_json_lint():
    """Run the repo's package.json lint test (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "test", "test/package-json-lint.test.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"package-json-lint test failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"
