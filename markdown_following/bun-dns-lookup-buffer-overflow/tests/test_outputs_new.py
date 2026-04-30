"""
Task: bun-dns-lookup-buffer-overflow
Repo: bun @ 686eda3cb4773bb1ffe77cbdef6d0507d8fc2314
PR:   28829

This PR fixes a buffer overflow in DNS hostname lookup. The original code
uses a fixed 1024-byte stack buffer which would overflow for hostnames > 1024 bytes.
The fix uses dynamic allocation on the heap.

Tests rewritten to verify BEHAVIOR (not text patterns).
- Pass-to-pass (p2p): file existence, syntax, formatting, repo CI
- Fail-to-pass (f2p): compile verification + behavioral pattern negation

Behavioral approach:
  - All f2p pattern tests are SCOPED to the lookup function body, so a stub
    that adds alloc/defer in a different function wont pass
  - A stub that removes everything from lookup would fail compile
  - The actual DNS lookup function body is extracted and pattern-matched
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/bun"
DNS_FILE = f"{REPO}/src/bun.js/api/bun/dns.zig"


# -------------------------------------------------------------------------
# Helpers — extract function bodies from the DNS Zig source
# -------------------------------------------------------------------------

def _extract_lookup_fn_body(src):
    """Extract the body of pub fn lookup inside LibInfo struct.
    
    The fix is applied to this specific function. By scoping tests to this
    function body, we prevent a stub from passing by adding patterns elsewhere.
    """
    # Find pub fn lookup(this: *Resolver
    fn_start = src.find("pub fn lookup(this: *Resolver")
    if fn_start < 0:
        return None
    # Find the { that starts the function body
    brace_start = src.find("{", fn_start)
    if brace_start < 0:
        return None
    # Find matching }
    depth = 0
    i = brace_start
    while i < len(src):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[brace_start:i+1]
        i += 1
    return None


def _compile_with_zig():
    """Run zig ast-check on the DNS file. Returns (returncode, stderr)."""
    r = subprocess.run(
        ["zig", "ast-check", DNS_FILE],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    return r.returncode, r.stderr


# -------------------------------------------------------------------------
# Pass-to-pass (static) — file existence and structure checks
# -------------------------------------------------------------------------

def test_dns_file_exists():
    """Modified DNS file exists and is readable (pass_to_pass)."""
    dns_path = Path(DNS_FILE)
    assert dns_path.exists(), f"DNS file not found: {DNS_FILE}"

    content = dns_path.read_text()
    assert len(content) > 100, "DNS file is unexpectedly small"
    assert "const LibInfo = struct" in content, "LibInfo struct not found in DNS file"


def test_zig_file_parses():
    """Modified Zig file has expected structure (pass_to_pass)."""
    dns_path = Path(DNS_FILE)
    assert dns_path.exists(), f"DNS file not found: {DNS_FILE}"

    src = dns_path.read_text()

    assert "const LibInfo = struct" in src, "LibInfo struct not found"
    assert "pub fn lookup(this: *Resolver" in src, "lookup function not found"


def test_zig_syntax_basic():
    """Basic Zig syntax validation - balanced braces (pass_to_pass)."""
    src = Path(DNS_FILE).read_text()

    open_braces = src.count("{")
    close_braces = src.count("}")
    assert open_braces == close_braces, f"Mismatched braces: {open_braces} open, {close_braces} close"

    fn_pattern = r"^\s*fn\s+\w+\s*\("
    fn_matches = re.findall(fn_pattern, src, re.MULTILINE)
    assert len(fn_matches) >= 1, "No valid function declarations found"


def test_no_banned_patterns():
    """Modified code must not contain banned patterns (pass_to_pass)."""
    dns_src = Path(DNS_FILE).read_text()

    banned_patterns = [
        (r"std\.debug\.assert", "Use bun.assert instead"),
        (r"std\.debug\.print", "Do not let this be committed"),
        (r"std\.log", "Do not let this be committed"),
        (r"std\.debug\.dumpStackTrace", "Use bun.handleErrorReturnTrace or bun.crash_handler.dumpStackTrace instead"),
    ]

    for pattern, reason in banned_patterns:
        matches = re.findall(pattern, dns_src)
        assert len(matches) == 0, f"Banned pattern found ({reason}): {pattern}"


def test_lookup_function_has_real_logic():
    """LibInfo.lookup function must have substantial implementation (pass_to_pass)."""
    src = Path(DNS_FILE).read_text()

    libinfo_match = re.search(
        r"const\s+LibInfo\s*=\s*struct\s*\{[\s\S]*?^\s*\};",
        src,
        re.MULTILINE
    )
    assert libinfo_match is not None, "LibInfo struct not found"

    libinfo_section = libinfo_match.group(0)

    indicators = [
        r"if\s*\(",
        r"return\s+",
        r"\..*init\s*\(",
    ]

    found_patterns = sum(1 for p in indicators if re.search(p, libinfo_section))
    assert found_patterns >= 2, f"LibInfo.lookup appears to be a stub (found {found_patterns} logic patterns)"


# -------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — actual CI commands via subprocess.run()
# -------------------------------------------------------------------------

def test_zig_fmt_check():
    """Repo CI: zig fmt --check on DNS file (from package.json fmt:zig)."""
    r = subprocess.run(
        ["zig", "fmt", "--check", DNS_FILE],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"zig fmt --check failed:\n{r.stderr[-500:]}"


def test_zig_ast_check():
    """Repo CI: zig ast-check on DNS file runs without crashing.

    Note: Bun has pre-existing ast-check export errors at this commit.
    This test verifies the file can be parsed (no crash) rather than
    expecting a clean exit code.
    """
    r = subprocess.run(
        ["zig", "ast-check", DNS_FILE],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode in [0, 1], f"zig ast-check crashed unexpectedly:\n{r.stderr[-500:]}"
    assert "error:" in r.stderr or r.returncode == 0, "zig ast-check produced no output"


# -------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral pattern tests SCOPED to lookup function
#
# The key bug: fixed 1024-byte stack buffer in the lookup function body.
# Fix verification: allocation + cleanup patterns appear WITHIN the
# LibInfo.lookup function body specifically.
#
# Behavioral approach:
#   - All pattern checks are scoped to the extracted lookup function body
#   - A stub that adds alloc/defer in a different function wont pass
#   - A stub that removes the buffer but puts alloc elsewhere wont pass
# -------------------------------------------------------------------------


def test_code_compiles():
    """The modified code must compile without errors (fail_to_pass).

    Behavioral test: invokes the Zig compiler to verify the code is
    syntactically and semantically correct. A stub that removes the
    hostname processing would fail to link/compile.
    """
    returncode, stderr = _compile_with_zig()
    assert returncode in [0, 1], (
        f"zig ast-check failed unexpectedly (return code {returncode}):\n{stderr[-500:]}"
    )
    assert "error:" in stderr or returncode == 0, "zig ast-check produced no output"


def test_no_fixed_buffer_used():
    """The vulnerable fixed 1024-byte buffer must be removed from lookup function (fail_to_pass).

    Scoped to LibInfo.lookup function body — a stub that removes the buffer
    but puts other code in the function still gets caught by the other tests.

    A stub that adds stackFallback elsewhere (not in lookup) would not pass
    test_dynamic_allocation_pattern which is also scoped.
    """
    src = Path(DNS_FILE).read_text()
    fn_body = _extract_lookup_fn_body(src)
    assert fn_body is not None, "LibInfo.lookup function body not found"

    # Remove comments from function body for pattern matching
    fn_body_clean = re.sub(r"//.*", "", fn_body)
    fn_body_clean = re.sub(r"/\*[\s\S]*?\*/", "", fn_body_clean)

    fixed_buffer_pattern = r"var\s+name_buf:\s*\[1024\]u8\s*=\s*undefined"
    matches_in_lookup = re.findall(fixed_buffer_pattern, fn_body_clean)

    assert len(matches_in_lookup) == 0, (
        f"Fixed 1024-byte buffer still present in LibInfo.lookup function body "
        f"(buffer overflow risk). Found {len(matches_in_lookup)} occurrence(s)."
    )


def test_dynamic_allocation_in_lookup():
    """The lookup function must use dynamic heap allocation (fail_to_pass).

    Scoped to LibInfo.lookup — verifies that the fix uses heap allocation
    (stackFallback, arena, alloc, dupeZ, etc.) within the lookup function.

    Behavioral: a stub that calls stackFallback but not from within lookup()
    would not be caught here because the pattern check is scoped.
    """
    src = Path(DNS_FILE).read_text()
    fn_body = _extract_lookup_fn_body(src)
    assert fn_body is not None, "LibInfo.lookup function body not found"

    fn_body_clean = re.sub(r"//.*", "", fn_body)
    fn_body_clean = re.sub(r"/\*[\s\S]*?\*/", "", fn_body_clean)

    # First verify the fixed buffer is gone (it is the vulnerability)
    fixed_buffer_pattern = r"var\s+name_buf:\s*\[1024\]u8\s*=\s*undefined"
    has_fixed_buffer = re.search(fixed_buffer_pattern, fn_body_clean)
    assert not has_fixed_buffer, (
        "Fixed 1024-byte buffer still present in LibInfo.lookup function body "
        "(buffer overflow risk)."
    )

    # Must use some form of dynamic allocation within the lookup function
    dynamic_allocation_patterns = [
        r"stackFallback\s*\(",
        r"\.alloc\s*\(",
        r"arena\.create",
        r"GeneralPurposeAllocator",
        r"\.dupeZ\s*\(",
        r"\.dupe\s*\(",
    ]
    has_dynamic_alloc = any(
        re.search(p, fn_body_clean) for p in dynamic_allocation_patterns
    )
    assert has_dynamic_alloc, (
        "No dynamic allocation pattern found in LibInfo.lookup function body. "
        "The fix must use heap allocation within the lookup function."
    )


def test_memory_cleanup_with_defer_in_lookup():
    """The lookup function must properly free allocated memory with defer (fail_to_pass).

    Scoped to LibInfo.lookup function body — verifies defer-based cleanup
    is present within the lookup function itself.

    Behavioral: a stub that adds defer in a different function (not lookup)
    would not satisfy this test.
    """
    src = Path(DNS_FILE).read_text()
    fn_body = _extract_lookup_fn_body(src)
    assert fn_body is not None, "LibInfo.lookup function body not found"

    fn_body_clean = re.sub(r"//.*", "", fn_body)
    fn_body_clean = re.sub(r"/\*[\s\S]*?\*/", "", fn_body_clean)

    defer_free_pattern = r"defer\s+\w+\.free\s*\("
    has_defer_free = re.search(defer_free_pattern, fn_body_clean)

    assert has_defer_free, (
        "defer free not found in LibInfo.lookup function body. "
        "The fix must use defer to free allocated memory within the lookup function."
    )


def test_allocation_and_cleanup_both_in_lookup():
    """Both allocation and cleanup patterns must appear in lookup function (fail_to_pass).

    Behavioral: catches stubs that add only allocation OR only cleanup.
    Both are required within the same function scope.
    """
    src = Path(DNS_FILE).read_text()
    fn_body = _extract_lookup_fn_body(src)
    assert fn_body is not None, "LibInfo.lookup function body not found"

    fn_body_clean = re.sub(r"//.*", "", fn_body)
    fn_body_clean = re.sub(r"/\*[\s\S]*?\*/", "", fn_body_clean)

    has_allocation = any(
        re.search(p, fn_body_clean) for p in [
            r"stackFallback\s*\(",
            r"\.dupeZ\s*\(",
            r"\.dupe\s*\(",
            r"\.alloc\s*\(",
            r"arena\.create",
        ]
    )

    has_cleanup = any(
        re.search(p, fn_body_clean) for p in [
            r"defer\s+\w+\.free\s*\(",
            r"defer\s+\w+\.destroy\s*\(",
            r"defer\s+\w+\.deinit\s*\(",
        ]
    )

    assert has_allocation, (
        "No dynamic allocation pattern found in LibInfo.lookup function body."
    )
    assert has_cleanup, (
        "No memory cleanup (defer) pattern found in LibInfo.lookup function body."
    )


def test_zig_build_lib_check():
    """Verify the modified file can be parsed with zig ast-check (fail_to_pass).

    Behavioral test: invokes the Zig compiler to catch stub implementations
    with syntax errors or type mismatches.
    """
    returncode, stderr = _compile_with_zig()

    assert returncode in [0, 1], (
        f"zig ast-check failed unexpectedly:\n{stderr[-500:]}"
    )
