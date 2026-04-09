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


def _get_libinfo_lookup_section():
    """Extract the LibInfo.lookup function section from the file."""
    src = Path(DNS_FILE).read_text()

    # Find LibInfo struct
    libinfo_match = re.search(
        r"const\s+LibInfo\s*=\s*struct\s*\{[\s\S]*?^\s*\};",
        src,
        re.MULTILINE
    )
    if libinfo_match:
        return libinfo_match.group(0)
    return src  # Fall back to full file if pattern doesn't match


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

def test_zig_file_parses():
    """Modified Zig file must at least be readable and have expected structure."""
    dns_path = Path(DNS_FILE)
    assert dns_path.exists(), f"DNS file not found: {DNS_FILE}"

    src = dns_path.read_text()

    # Basic structural checks that indicate valid Zig syntax
    assert "const LibInfo = struct" in src, "LibInfo struct not found"
    assert "fn lookup(" in src, "lookup function not found"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_no_fixed_buffer_used():
    """The vulnerable fixed 1024-byte buffer pattern must be removed."""
    src = Path(DNS_FILE).read_text()

    # The old vulnerable code used: var name_buf: [1024]u8 = undefined;
    # This pattern must be gone
    fixed_buffer_pattern = r"var\s+name_buf:\s*\[1024\]u8\s*=\s*undefined"
    matches = re.findall(fixed_buffer_pattern, src)
    assert len(matches) == 0, f"Fixed 1024-byte buffer still present (buffer overflow risk)"


def test_stack_fallback_pattern_present():
    """The safe stackFallback allocator pattern must be present."""
    src = Path(DNS_FILE).read_text()

    # The new safe code uses: std.heap.stackFallback(1024, bun.default_allocator)
    stack_fallback_pattern = r"std\.heap\.stackFallback\s*\(\s*1024\s*,\s*bun\.default_allocator\s*\)"
    matches = re.findall(stack_fallback_pattern, src)
    assert len(matches) >= 1, f"stackFallback allocator pattern not found (fix not applied)"


def test_dynamic_allocation_with_dupeZ():
    """The fix must use dupeZ for dynamic allocation of the hostname."""
    src = Path(DNS_FILE).read_text()

    # The fix uses: name_allocator.dupeZ(u8, query.name)
    dupez_pattern = r"name_allocator\.dupeZ\s*\(\s*u8\s*,\s*query\.name\s*\)"
    matches = re.findall(dupez_pattern, src)
    assert len(matches) >= 1, f"dupeZ pattern not found (dynamic allocation missing)"


def test_proper_cleanup_with_defer_free():
    """The fix must properly free the allocated memory with defer."""
    src = Path(DNS_FILE).read_text()

    # The fix includes: defer name_allocator.free(name_z);
    defer_pattern = r"defer\s+name_allocator\.free\s*\(\s*name_z\s*\)"
    matches = re.findall(defer_pattern, src)
    assert len(matches) >= 1, f"defer name_allocator.free pattern not found (memory leak risk)"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

def test_lookup_function_has_real_logic():
    """LibInfo.lookup function must have substantial implementation."""
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
