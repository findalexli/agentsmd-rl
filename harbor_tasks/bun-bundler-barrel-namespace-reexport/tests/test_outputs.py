"""
Task: bun-bundler-barrel-namespace-reexport
Repo: oven-sh/bun @ 1628bfeceb07085263b5da5adb1ec3b094e4b188
PR:   28173

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/bun"
ZIG_FILE = f"{REPO}/src/bundler/barrel_imports.zig"


def _read_zig():
    return Path(ZIG_FILE).read_text()


def _bfs_body(text):
    """Extract scheduleBarrelDeferredImports function body."""
    m = re.search(r"pub fn scheduleBarrelDeferredImports\b(.*)", text, re.DOTALL)
    return m.group(1) if m else ""


def _resolve_body(text):
    """Extract resolveBarrelExport function body up to its closing brace."""
    m = re.search(r"fn resolveBarrelExport\b(.*?)\n\}", text, re.DOTALL)
    return m.group(1) if m else ""


def _struct_body(text):
    """Extract BarrelExportResolution struct body."""
    m = re.search(
        r"const BarrelExportResolution\s*=\s*struct\s*\{(.*?)\};", text, re.DOTALL
    )
    return m.group(1) if m else ""


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core structural tests
# AST-only because: Zig source cannot be compiled in the test container
# (bun is a ~200k LOC Zig project requiring full build toolchain)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_is_star_not_hardcoded_false():
    """After resolveBarrelExport, the BFS queue append must use a dynamic
    is_star value (not the hardcoded 'false' from the buggy code).

    Base code: `.is_star = false` (hardcoded)
    Fixed code: `.is_star = resolution.alias_is_star` (dynamic)
    """
    text = _read_zig()
    bfs = _bfs_body(text)

    # Find the section after resolveBarrelExport call
    res_pos = bfs.find("resolveBarrelExport")
    assert res_pos >= 0, "resolveBarrelExport call not found in BFS function"

    # Look in a window after the call for queue.append with .is_star
    after_resolve = bfs[res_pos : res_pos + 5000]

    # Find all .is_star = <value> assignments in the queue append area
    is_star_assigns = re.findall(r"\.is_star\s*=\s*([^,}\s]+)", after_resolve)
    assert is_star_assigns, "No .is_star assignment found after resolveBarrelExport"

    # At least one assignment must use a dynamic value (not literal false)
    dynamic_values = [
        v.strip().rstrip(",") for v in is_star_assigns if v.strip().rstrip(",") != "false"
    ]
    assert dynamic_values, (
        "All .is_star assignments are hardcoded 'false' — "
        "the star-import flag is not propagated from resolution"
    )

    # The dynamic value must be a meaningful reference, not just 'true'
    meaningful = [v for v in dynamic_values if v != "true" and re.match(r"\w+(\.\w+)*", v)]
    assert meaningful, (
        f"is_star values {dynamic_values} are not meaningful references — "
        "expected a field access like resolution.alias_is_star"
    )


# [pr_diff] fail_to_pass
def test_star_flag_sourced_from_import_data():
    """The star-import flag must originate from import record data.

    The fix reads `import_entry.alias_is_star` inside resolveBarrelExport
    and returns it. An alternative fix could read it inline at the BFS site.
    Either way, the star flag must come from the import data, not be invented.
    """
    text = _read_zig()
    resolve = _resolve_body(text)
    bfs = _bfs_body(text)

    # Patterns that indicate reading star-import info from import data.
    # The gold fix uses `alias_is_star`, but alternatives might check
    # name length (star imports have empty name) or use different field names.
    star_patterns_resolve = [
        r"alias_is_star",            # gold fix: direct field access
        r"is_star",                  # variant field name
        r"is_namespace",             # variant field name
        r"name\.len\s*[=!]=\s*0",   # star imports have empty name
        r'\.name\s*==\s*""',        # empty name check
    ]

    # Check resolveBarrelExport for star-related return data
    resolve_has_star = any(re.search(p, resolve) for p in star_patterns_resolve)

    # Check BFS body for inline star-flag reads from import data
    bfs_has_inline_star = False
    res_pos = bfs.find("resolveBarrelExport")
    if res_pos >= 0:
        after = bfs[res_pos : res_pos + 5000]
        bfs_has_inline_star = bool(
            re.search(r"import.+\.(alias_is_star|is_star|is_namespace)", after, re.IGNORECASE)
            or re.search(r"named_import.+\.(alias_is_star|is_star)", after, re.IGNORECASE)
            or re.search(r"import.+\.name.*len", after)
        )

    assert resolve_has_star or bfs_has_inline_star, (
        "No star-import flag read from import record data — "
        "resolveBarrelExport must return star info or BFS must read it inline"
    )


# [pr_diff] fail_to_pass
def test_resolution_carries_star_info():
    """Star-import info must be carried from resolveBarrelExport to the BFS
    queue append. The gold fix adds an alias_is_star field to
    BarrelExportResolution; alternatives include out-params, inline lookups,
    or return type changes."""
    text = _read_zig()

    # Approach A: New field in BarrelExportResolution struct
    struct = _struct_body(text)
    has_new_field = False
    if struct:
        fields = re.findall(r"(\w+)\s*:", struct)
        original = {"import_record_index", "original_alias"}
        has_new_field = bool([f for f in fields if f not in original])

    # Approach B: out-parameter on resolveBarrelExport
    has_out_param = bool(re.search(r"fn resolveBarrelExport\([^)]*\*\s*bool", text))

    # Approach C: different return type (tuple/struct)
    has_tuple_return = bool(
        re.search(r"fn resolveBarrelExport\([^)]*\)\s*[^{]*(?:struct|tuple)", text)
    )

    # Approach D: inline lookup at BFS site (read star from import data directly)
    has_inline_lookup = False
    bfs = _bfs_body(text)
    res_pos = bfs.find("resolveBarrelExport")
    if res_pos >= 0:
        after = bfs[res_pos : res_pos + 5000]
        if (
            re.search(r"import.+\.(alias_is_star|is_star|is_namespace)", after, re.IGNORECASE)
            or re.search(r"import.+\.name.*len", after)
        ):
            has_inline_lookup = True

    assert has_new_field or has_out_param or has_tuple_return or has_inline_lookup, (
        "No mechanism found to carry star-import info from resolveBarrelExport "
        "to the BFS queue append site"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_core_functions_preserved():
    """Core functions resolveBarrelExport and scheduleBarrelDeferredImports
    must still exist with their key BFS logic (queue + while loop)."""
    text = _read_zig()
    assert "fn resolveBarrelExport" in text, "resolveBarrelExport function missing"
    assert "fn scheduleBarrelDeferredImports" in text, (
        "scheduleBarrelDeferredImports function missing"
    )
    bfs = _bfs_body(text)
    assert "queue" in bfs, "BFS queue reference missing from scheduleBarrelDeferredImports"
    assert "append" in bfs, "queue.append call missing from scheduleBarrelDeferredImports"
    assert re.search(r"while\s*\(", bfs), "BFS while loop missing"


# [pr_diff] pass_to_pass
def test_original_fields_preserved():
    """BarrelExportResolution must retain original fields:
    import_record_index and original_alias."""
    text = _read_zig()
    struct = _struct_body(text)
    if struct:
        assert "import_record_index" in struct, (
            "import_record_index field missing from BarrelExportResolution"
        )
        assert "original_alias" in struct, (
            "original_alias field missing from BarrelExportResolution"
        )
    else:
        # Struct may have been refactored — check fields exist somewhere
        assert "import_record_index" in text, "import_record_index not found anywhere"
        assert "original_alias" in text, "original_alias not found anywhere"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from src/CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — src/CLAUDE.md:16-36 @ 1628bfeceb07085263b5da5adb1ec3b094e4b188
def test_no_std_api_in_new_code():
    """New code must not use prohibited std.* APIs directly — use bun.*
    wrappers instead. Covers: std.fs, std.posix, std.os, std.process,
    std.base64, std.crypto.sha, std.mem.eql/indexOf/startsWith.
    Only checks agent's diff."""
    result = subprocess.run(
        ["git", "diff", "HEAD", "--", "src/bundler/barrel_imports.zig"],
        capture_output=True, text=True, cwd=REPO,
    )
    added_lines = [
        line[1:] for line in result.stdout.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ]
    bad = []
    for line in added_lines:
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        # std.fs, std.posix, std.os, std.process (use bun.sys.*, bun.FD.*, etc.)
        bad.extend(re.findall(r"std\.(fs|posix|os|process)\.", line))
        # std.base64 (use bun.base64)
        bad.extend(re.findall(r"std\.base64\b", line))
        # std.crypto.sha (use bun.sha.Hashers)
        bad.extend(re.findall(r"std\.crypto\.sha\b", line))
        # std.mem string ops (use bun.strings.*)
        bad.extend(re.findall(r"std\.mem\.(eql|indexOf|startsWith)\b", line))
    assert not bad, f"Prohibited std.* API usage in new code: {bad}"


# [agent_config] pass_to_pass — src/CLAUDE.md:11 @ 1628bfeceb07085263b5da5adb1ec3b094e4b188
def test_no_inline_import_in_new_code():
    """New code must not use @import() inline inside functions
    (put imports at bottom of file or containing struct)."""
    result = subprocess.run(
        ["git", "diff", "HEAD", "--", "src/bundler/barrel_imports.zig"],
        capture_output=True, text=True, cwd=REPO,
    )
    added_lines = [
        line[1:] for line in result.stdout.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ]
    assert not any("@import(" in line for line in added_lines), (
        "Found @import() in agent's new code — imports must be at file/struct bottom"
    )
