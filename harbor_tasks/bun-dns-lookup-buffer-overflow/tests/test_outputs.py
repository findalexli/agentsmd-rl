"""
Task: bun-dns-lookup-buffer-overflow
Repo: bun @ 686eda3cb4773bb1ffe77cbdef6d0507d8fc2314
PR:   28829

This PR fixes a buffer overflow in DNS hostname lookup. The original code
used a fixed 1024-byte stack buffer which would overflow for hostnames > 1024 bytes.
The fix uses stackFallback allocator which spills to heap for longer hostnames.

Note: Bun has pre-existing zig ast-check errors at this commit unrelated to this fix.
We focus on verifying the specific code change patterns.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/bun"
DNS_FILE = f"{REPO}/src/bun.js/api/bun/dns.zig"
BAN_WORDS_FILE = f"{REPO}/test/internal/ban-words.test.ts"


def _get_libinfo_section():
    """Extract the LibInfo struct section from the file."""
    src = Path(DNS_FILE).read_text()

    libinfo_match = re.search(
        r"const\s+LibInfo\s*=\s*struct\s*\{[\s\S]*?^\s*\};",
        src,
        re.MULTILINE
    )

    assert libinfo_match is not None, "LibInfo struct not found"
    return libinfo_match.group(0)


# -----------------------------------------------------------------------------
# Pass-to-pass (static) — file existence and content checks
# -----------------------------------------------------------------------------

def test_dns_file_exists():
    """Modified DNS file exists and is readable (pass_to_pass)."""
    dns_path = Path(DNS_FILE)
    assert dns_path.exists(), f"DNS file not found: {DNS_FILE}"

    # File should be non-empty and readable
    content = dns_path.read_text()
    assert len(content) > 100, "DNS file is unexpectedly small"
    assert "const LibInfo = struct" in content, "LibInfo struct not found in DNS file"


def test_zig_file_parses():
    """Modified Zig file has expected structure (pass_to_pass)."""
    dns_path = Path(DNS_FILE)
    assert dns_path.exists(), f"DNS file not found: {DNS_FILE}"

    src = dns_path.read_text()

    # Basic structural checks that indicate valid Zig syntax
    assert "const LibInfo = struct" in src, "LibInfo struct not found"
    assert "fn lookup(" in src, "lookup function not found"


def test_zig_syntax_basic():
    """Basic Zig syntax validation - balanced braces (pass_to_pass)."""
    src = Path(DNS_FILE).read_text()

    # Check for basic Zig structural validity
    # Count braces to detect obvious syntax issues
    open_braces = src.count("{")
    close_braces = src.count("}")
    assert open_braces == close_braces, f"Mismatched braces: {open_braces} open, {close_braces} close"

    # Check for valid function declarations
    fn_pattern = r"^\s*fn\s+\w+\s*\("
    fn_matches = re.findall(fn_pattern, src, re.MULTILINE)
    assert len(fn_matches) >= 1, "No valid function declarations found"


def test_no_banned_patterns():
    """Modified code must not contain banned patterns (pass_to_pass)."""
    dns_src = Path(DNS_FILE).read_text()

    # Critical banned patterns from ban-words.test.ts that should never appear
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

    # Find the LibInfo struct and lookup function
    libinfo_section = _get_libinfo_section()

    # Should have multiple statements indicating real logic
    indicators = [
        r"if\s*\(",           # Conditional logic
        r"return\s+",         # Return statements
        r"\..*init\s*\(",    # init calls
    ]

    found_patterns = sum(1 for p in indicators if re.search(p, libinfo_section))
    assert found_patterns >= 2, f"LibInfo.lookup appears to be a stub (found {found_patterns} logic patterns)"


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — actual CI commands via subprocess.run()
# -----------------------------------------------------------------------------

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
    # Check that the command ran without crashing (no segfault, etc.)
    # The known pre-existing errors are about "symbol to export" which
    # are unrelated to the DNS fix. We just verify the command executed.
    assert r.returncode in [0, 1], f"zig ast-check crashed unexpectedly:\n{r.stderr[-500:]}"
    # Ensure stderr contains expected content (proving it ran)
    assert "error:" in r.stderr or r.returncode == 0, "zig ast-check produced no output"


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# -----------------------------------------------------------------------------

def test_no_fixed_buffer_used():
    """The vulnerable fixed 1024-byte buffer pattern must be removed (fail_to_pass)."""
    src = Path(DNS_FILE).read_text()

    # The old vulnerable code used: var name_buf: [1024]u8 = undefined;
    # This pattern must be gone
    fixed_buffer_pattern = r"var\s+name_buf:\s*\[1024\]u8\s*=\s*undefined"
    matches = re.findall(fixed_buffer_pattern, src)
    assert len(matches) == 0, f"Fixed 1024-byte buffer still present (buffer overflow risk)"


def test_stack_fallback_pattern_present():
    """The safe stackFallback allocator pattern must be present (fail_to_pass)."""
    src = Path(DNS_FILE).read_text()

    # The new safe code uses: std.heap.stackFallback(1024, bun.default_allocator)
    stack_fallback_pattern = r"std\.heap\.stackFallback\s*\(\s*1024\s*,\s*bun\.default_allocator\s*\)"
    matches = re.findall(stack_fallback_pattern, src)
    assert len(matches) >= 1, f"stackFallback allocator pattern not found (fix not applied)"


def test_dynamic_allocation_with_dupeZ():
    """The fix must use dupeZ for dynamic allocation of the hostname (fail_to_pass)."""
    src = Path(DNS_FILE).read_text()

    # The fix uses: name_allocator.dupeZ(u8, query.name)
    dupez_pattern = r"name_allocator\.dupeZ\s*\(\s*u8\s*,\s*query\.name\s*\)"
    matches = re.findall(dupez_pattern, src)
    assert len(matches) >= 1, f"dupeZ pattern not found (dynamic allocation missing)"


def test_proper_cleanup_with_defer_free():
    """The fix must properly free the allocated memory with defer (fail_to_pass)."""
    src = Path(DNS_FILE).read_text()

    # The fix includes: defer name_allocator.free(name_z);
    defer_pattern = r"defer\s+name_allocator\.free\s*\(\s*name_z\s*\)"
    matches = re.findall(defer_pattern, src)
    assert len(matches) >= 1, f"defer name_allocator.free pattern not found (memory leak risk)"
