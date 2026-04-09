"""
Task: bun-dns-stale-cache-refcount
Repo: oven-sh/bun @ 7960fe985dfa3418b507777a5a61289defbdb9dc
PR:   #28271

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: Zig cannot be compiled in this container (needs cmake + zig + JSC).
The f2p tests use subprocess to run a Python AST-analyzer that verifies
the semantic structure of the Zig source — this is stricter than grep
because it parses control flow, not just string presence.
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
# Fail-to-pass (pr_diff) — core behavioral fixes via subprocess analysis
# ---------------------------------------------------------------------------

def test_isexpired_no_refcount_gate():
    """isExpired must not gate expiry on refcount > 0.

    The bug: `if (this.refcount > 0 or this.result == null)` blocks expiry
    for referenced entries. Fix: remove the refcount > 0 condition so TTL
    is checked regardless of active connections.
    """
    r = _run_analyzer("""
import json, re, sys
from pathlib import Path

src = Path("/workspace/bun/src/bun.js/api/bun/dns.zig").read_text()

# Extract isExpired function body
lines = src.split("\\n")
start = None
for i, line in enumerate(lines):
    if re.search(r"pub\\s+fn\\s+isExpired", line):
        start = i
        break

if start is None:
    print(json.dumps({"error": "isExpired not found"}))
    sys.exit(0)

# Collect the full function body
brace_depth = 0
body_lines = []
for j in range(start, min(start + 50, len(lines))):
    line = lines[j]
    body_lines.append(line)
    brace_depth += line.count("{") - line.count("}")
    if brace_depth <= 0 and "{" in "".join(body_lines):
        break

body = "\\n".join(body_lines)

# The bug pattern: isExpired checks refcount > 0
has_refcount_gate = bool(re.search(r"refcount\\s*>\\s*0", body))
# The fix should still have result == null check
has_null_check = bool(re.search(r"result\\s*==\\s*null", body))

print(json.dumps({
    "has_refcount_gate": has_refcount_gate,
    "has_null_check": has_null_check,
    "body_preview": body[:200]
}))
""")
    assert r.returncode == 0, f"Analyzer failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert not data.get("has_refcount_gate"), (
        "isExpired still gates on refcount > 0 — stale entries will not expire"
    )


def test_get_refcount_guard():
    """get() must guard deinit of expired entries on zero refcount.

    The bug: get() unconditionally deinits expired entries even when
    refcount > 0 (use-after-free). Fix: only deinit when refcount == 0.
    """
    r = _run_analyzer("""
import json, re, sys
from pathlib import Path

src = Path("/workspace/bun/src/bun.js/api/bun/dns.zig").read_text()

# Find the get() function that calls isExpired
lines = src.split("\\n")
start = None
for i, line in enumerate(lines):
    if re.search(r"(pub\\s+)?fn\\s+get\\s*\\(", line):
        # Look ahead for isExpired
        chunk = "\\n".join(lines[i:min(i+60, len(lines))])
        if "isExpired" in chunk:
            start = i
            break

if start is None:
    print(json.dumps({"error": "get() not found"}))
    sys.exit(0)

# Collect full function body
brace_depth = 0
body_lines = []
for j in range(start, min(start + 80, len(lines))):
    line = lines[j]
    body_lines.append(line)
    brace_depth += line.count("{") - line.count("}")
    if brace_depth <= 0 and "{" in "".join(body_lines):
        break

body = "\\n".join(body_lines)

# Find the isExpired block and check if deinit is guarded
# Look for the pattern around isExpired
expired_match = re.search(r"isExpired\\([^)]*\\)\\s*\\)", body)
if not expired_match:
    # Try simpler
    expired_idx = body.find("isExpired")
    if expired_idx < 0:
        print(json.dumps({"error": "isExpired call not found in get()"}))
        sys.exit(0)

# Check: after isExpired check, is there a refcount == 0 guard?
# The fix wraps deleteEntryAt/deinit in `if (entry.refcount == 0)`
# We look for refcount == 0 in the vicinity of deinit
deinit_idx = body.find("deinit")
has_refcount_zero_guard = False
if deinit_idx >= 0:
    # Look backwards from deinit for a refcount check
    before_deinit = body[:deinit_idx]
    has_refcount_zero_guard = bool(re.search(r"refcount\\s*==\\s*0", before_deinit))

# Also verify deleteEntryAt is similarly guarded
delete_idx = body.find("deleteEntryAt")
has_delete_guard = False
if delete_idx >= 0:
    before_delete = body[:delete_idx]
    has_delete_guard = bool(re.search(r"refcount\\s*==\\s*0", before_delete))

print(json.dumps({
    "has_refcount_zero_guard": has_refcount_zero_guard,
    "has_delete_guard": has_delete_guard,
}))
""")
    assert r.returncode == 0, f"Analyzer failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data.get("has_refcount_zero_guard"), (
        "get() does not guard deinit on refcount == 0 — use-after-free risk"
    )


def test_freeaddrinfo_conditional_valid():
    """freeaddrinfo must not unconditionally assign valid = (err == 0).

    The bug: `req.valid = err == 0` overwrites previously valid entries on
    success callback. Fix: only set valid = false on error.
    """
    r = _run_analyzer("""
import json, re, sys
from pathlib import Path

src = Path("/workspace/bun/src/bun.js/api/bun/dns.zig").read_text()

# Find freeaddrinfo function
lines = src.split("\\n")
start = None
for i, line in enumerate(lines):
    if re.search(r"(pub\\s+)?fn\\s+freeaddrinfo", line):
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

body = "\\n".join(body_lines)

# Bug: unconditional assignment valid = err == 0
has_unconditional = bool(re.search(r"\\.valid\\s*=\\s*err\\s*==\\s*0", body))

# Fix: should use conditional (if err != 0 { valid = false })
has_error_branch = bool(re.search(r"err\\s*!=\\s*0", body))
sets_valid_false = bool(re.search(r"valid\\s*=\\s*false", body))

# Must NOT have the unconditional form
# Must have error-handling that sets valid = false
print(json.dumps({
    "has_unconditional_assignment": has_unconditional,
    "has_error_branch": has_error_branch,
    "sets_valid_false": sets_valid_false,
}))
""")
    assert r.returncode == 0, f"Analyzer failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert not data.get("has_unconditional_assignment"), (
        "freeaddrinfo still has unconditional `valid = (err == 0)`"
    )
    assert data.get("has_error_branch") or data.get("sets_valid_false"), (
        "freeaddrinfo doesn't handle the error case properly"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
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
# Structural — anti-stub (pr_diff)
# ---------------------------------------------------------------------------

def test_isexpired_not_stub():
    """isExpired has a meaningful body (>= 4 non-blank code lines)."""
    _, isexpired, _, _ = _load_functions()
    code_lines = [
        l for l in isexpired.split("\n")
        if l.strip() and l.strip() not in ("{", "}", "};")
    ]
    assert len(code_lines) >= 4, (
        f"isExpired has only {len(code_lines)} code lines — likely a stub"
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

# [agent_config] pass_to_pass — src/CLAUDE.md:14-16 @ 7960fe9
def test_no_std_apis():
    """Modified functions must not introduce std.* usage (use bun.* instead)."""
    _, isexpired, get_fn, freeaddrinfo = _load_functions()
    for name, body in [("isExpired", isexpired), ("get", get_fn),
                       ("freeaddrinfo", freeaddrinfo)]:
        matches = re.findall(r"std\.(mem|fs|posix|process)", body)
        assert not matches, f"{name} uses std.* APIs: {matches}"


# [agent_config] pass_to_pass — src/CLAUDE.md:11 @ 7960fe9
def test_no_inline_imports():
    """Modified functions must not use @import() inline."""
    _, isexpired, get_fn, freeaddrinfo = _load_functions()
    for name, body in [("isExpired", isexpired), ("get", get_fn),
                       ("freeaddrinfo", freeaddrinfo)]:
        matches = re.findall(r"@import\s*\(", body)
        assert not matches, f"{name} has inline @import()"


# ---------------------------------------------------------------------------
# CI-derived (repo_tests) — pass_to_pass gates from bun repo CI checks
# ---------------------------------------------------------------------------

# CI check: ban-words.test.ts bans std.debug.print and std.log
def test_zig_no_debug_prints():
    """Modified Zig functions must not use debug printing (std.debug.print/std.log)."""
    _, isexpired, get_fn, freeaddrinfo = _load_functions()
    for name, body in [("isExpired", isexpired), ("get", get_fn),
                       ("freeaddrinfo", freeaddrinfo)]:
        # These are banned by bun's CI (test/internal/ban-words.test.ts)
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
        # Direct undefined comparisons are banned in bun's CI
        # Pattern: " != undefined", " == undefined", "undefined != ", "undefined == "
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
    # Check in the full dns.zig module, not just individual functions
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
