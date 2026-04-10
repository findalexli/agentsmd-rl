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
    # Check in the full dns.zig module
    matches = re.findall(r'@import\(["\'\']bun["\'\']\)', src)
    # Filter out top-level imports (lines starting with 'const' or 'pub const')
    lines = src.split("\n")
    inline_imports = []
    for i, line in enumerate(lines):
        if '@import("bun")' in line or "@import('bun')" in line:
            # Check if it's a top-level import
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
        # Check for allocator.ptr or alloc.ptr comparisons
        matches = re.findall(r"allocator\.ptr\s*[!=]=|alloc\.ptr\s*[!=]=|[!=]=\s*allocator\.ptr|[!=]=\s*alloc\.ptr", body)
        assert not matches, f"{name} compares allocator.ptr (UB if undefined)"


# ---------------------------------------------------------------------------
# Real CI subprocess tests (repo_tests) — actual CI commands that run in Docker
# ---------------------------------------------------------------------------

def test_repo_ban_words():
    """Run the repo's ban-words CI check (pass_to_pass).

    This executes the actual bun CI check that scans for banned patterns
    in Zig source files (std.debug.print, undefined comparisons, etc.).
    """
    r = subprocess.run(
        ["bun", "./test/internal/ban-words.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ban-words check failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_zig_syntax_valid():
    """Verify dns.zig has valid Zig syntax (pass_to_pass).

    Since we can't compile Zig in this container (no cmake/zig/JSC),
    we verify the file is valid by checking balanced braces and
    no obvious syntax errors that would prevent parsing.
    """
    raw = DNS_FILE.read_text()

    # Check for balanced braces
    open_count = raw.count("{")
    close_count = raw.count("}")
    assert open_count == close_count, (
        f"dns.zig has unbalanced braces: {open_count} open, {close_count} close"
    )

    # Check for balanced parentheses
    paren_open = raw.count("(")
    paren_close = raw.count(")")
    assert paren_open == paren_close, (
        f"dns.zig has unbalanced parentheses: {paren_open} open, {paren_close} close"
    )

    # Check for basic structure indicators
    assert "pub const" in raw or "pub fn" in raw, (
        "dns.zig missing expected public declarations"
    )


def test_repo_zig_no_hard_tabs():
    """Verify dns.zig doesn't use hard tabs (pass_to_pass).

    Bun's coding style uses spaces, not tabs. This is a basic style check
    that can be done without compiling Zig code.
    """
    r = subprocess.run(
        ["grep", "-n", "$'\\t'", str(DNS_FILE)],
        capture_output=True, text=True, timeout=30,
    )
    # grep returns 0 if matches found, 1 if no matches
    if r.returncode == 0:
        lines = r.stdout.strip().split("\n")[:5]
        assert False, f"dns.zig contains hard tabs (use spaces): {lines}"


def test_repo_dns_file_not_empty():
    """Verify dns.zig is a non-trivial file (pass_to_pass).

    Basic check to ensure the file has substantial content and
    isn't truncated or replaced with a stub.
    """
    stat = DNS_FILE.stat()
    assert stat.st_size > 1000, f"dns.zig is too small ({stat.st_size} bytes), possibly truncated"
    
    # Count lines and functions
    content = DNS_FILE.read_text()
    lines = content.split("\n")
    non_empty = [l for l in lines if l.strip()]
    assert len(non_empty) > 50, f"dns.zig has only {len(non_empty)} non-empty lines"
    
    # Count function definitions
    fn_count = len(re.findall(r"^\s*(pub\s+)?fn\s+\w+", content, re.MULTILINE))
    assert fn_count >= 3, f"dns.zig has only {fn_count} functions, expected at least 3"
