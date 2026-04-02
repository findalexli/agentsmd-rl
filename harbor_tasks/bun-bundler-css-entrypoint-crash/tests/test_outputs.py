"""
Task: bun-bundler-css-entrypoint-crash
Repo: oven-sh/bun @ 7abe6c387d0746b26eeed7fe9175e14560840cbb
PR:   28251

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: Zig code requires the full Bun build toolchain (custom Zig fork,
CMake, JavaScriptCore, vendor deps) — cannot compile/run in container.
Tests verify semantic properties that any correct fix must have.
"""

import re
from pathlib import Path

REPO = "/workspace/bun"
ZIG_FILE = Path(REPO) / "src/bundler/linker_context/computeChunks.zig"


def _read_zig():
    return ZIG_FILE.read_text()


def _extract_handler_body(text):
    """Extract the Handler struct body from computeChunks.zig."""
    m = re.search(r"const Handler\s*=\s*struct\s*\{(.*?)\n\s{8}\};", text, re.DOTALL)
    if not m:
        m = re.search(r"Handler.*=.*struct\s*\{(.*?)\n\s{8}\};", text, re.DOTALL)
    assert m, "Handler struct not found in computeChunks.zig"
    return m.group(1)


def _extract_next_body(handler_body):
    """Extract the body of Handler.next function."""
    m = re.search(r"pub fn next[^{]*\{(.*?)\n\s{8,16}\}", handler_body, re.DOTALL)
    assert m, "Handler.next function not found"
    return m.group(1)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_zig_file_exists():
    """computeChunks.zig must exist and be non-empty."""
    assert ZIG_FILE.exists(), f"{ZIG_FILE} does not exist"
    assert ZIG_FILE.stat().st_size > 0, f"{ZIG_FILE} is empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_handler_next_no_direct_param_as_index():
    """Handler.next must not use its parameter directly as a chunks[] index.

    The bug: chunks[chunk_id] where chunk_id is the raw entry_point_id.
    Any correct fix must translate the ID through a mapping, guard the access,
    or restructure to avoid direct indexing.
    """
    text = _read_zig()
    handler_body = _extract_handler_body(text)

    # Get the parameter name of Handler.next
    sig = re.search(r"pub fn next\s*\(\s*c\s*:\s*\*@This\(\)\s*,\s*(\w+)\s*:", handler_body)
    assert sig, "Handler.next signature not found"
    param_name = sig.group(1)

    next_body = _extract_next_body(handler_body)

    # The raw parameter must NOT be used directly as chunks[param]
    direct = re.search(r"c\.chunks\[" + re.escape(param_name) + r"\]", next_body)
    assert not direct, (
        f"Parameter '{param_name}' is used directly as chunks[] index — "
        "this is the original bug (entry_point_id != chunk index when CSS entries exist)"
    )

    # Verify chunks[] IS still accessed (fix didn't just delete core logic)
    has_chunks = bool(re.search(r"c\.chunks\[", next_body))
    has_core = "getOrPut" in next_body or "files_with_parts_in_chunk" in next_body
    assert has_chunks or has_core, "chunks access and core logic were removed entirely"


# [pr_diff] fail_to_pass
def test_css_entry_point_guard():
    """Handler.next must have a guard/skip for CSS-only entry points.

    CSS-only entries don't have JS chunks. Any correct fix must handle this
    via sentinel check, optional unwrap, bounds check, or similar guard.
    """
    text = _read_zig()
    handler_body = _extract_handler_body(text)
    next_body = _extract_next_body(handler_body)

    has_guard = (
        # sentinel check (maxInt, max_int, etc.)
        bool(re.search(r"maxInt|max_int|sentinel", next_body))
        # optional unwrap (orelse return, .? access)
        or bool(re.search(r"orelse\s+return|\.?\s*\?\s*;|\borelse\b", next_body))
        # null check
        or bool(re.search(r"==\s*null|!=\s*null", next_body))
        # bounds check
        or bool(re.search(r">=\s*c\.chunks\.len|<\s*c\.chunks\.len|bounds", next_body))
        # early return on condition
        or bool(re.search(r"if\s*\(.*\)\s*return", next_body))
    )
    assert has_guard, (
        "Handler.next has no guard for CSS-only entry points — "
        "must skip entries that don't have a JS chunk"
    )


# [pr_diff] fail_to_pass
def test_entry_point_to_chunk_mapping():
    """A data structure mapping entry point IDs to JS chunk indices must exist.

    The core fix requires translating entry_point IDs to JS chunk indices.
    Accepts: flat array, HashMap, ArrayList, optional array, any name.
    """
    text = _read_zig()

    has_mapping = (
        # Array allocated with entry_points.len
        bool(re.search(r"alloc\(\s*(?:u32|\?u32)\s*,\s*(?:this\.graph\.)?entry_points\.len\)", text))
        # HashMap keyed on entry point IDs
        or bool(re.search(r"HashMap\(.*entry.*chunk|AutoHashMap.*u32.*u32", text))
        # ArrayList for mapping
        or bool(re.search(r"ArrayList\((?:u32|\?u32)\).*entry_point", text))
        # Variable allocated with entry_points.len
        or bool(re.search(
            r"\w+\s*=\s*(?:try\s+)?(?:temp_allocator|this\.allocator|allocator)\w*\.alloc\([^)]*entry_points\.len\)",
            text,
        ))
        # Slice field in Handler
        or bool(re.search(r"Handler.*struct.*\[\](?:const\s+)?(?:u32|\?u32)", text, re.DOTALL))
    )
    assert has_mapping, (
        "No mapping from entry point IDs to JS chunk indices found — "
        "this is the core data structure needed to fix the bug"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_handler_retains_core_logic():
    """Handler struct must retain chunks field, next function, and getOrPut logic."""
    text = _read_zig()
    handler_body = _extract_handler_body(text)

    assert "chunks" in handler_body, "Handler lost 'chunks' field"
    assert "fn next" in handler_body, "Handler lost 'next' function"
    assert "files_with_parts_in_chunk" in handler_body, "Handler lost files_with_parts_in_chunk"
    assert "getOrPut" in handler_body, "Handler lost getOrPut call"


# [pr_diff] pass_to_pass
def test_compute_chunks_structure():
    """computeChunks must still create js_chunks and css_chunks."""
    text = _read_zig()
    assert "js_chunks" in text, "js_chunks variable missing"
    assert "css_chunks" in text, "css_chunks variable missing"
    assert "entry_source_indices" in text, "entry_source_indices missing"


# ---------------------------------------------------------------------------
# Anti-stub (static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_handler_next_not_stub():
    """Handler.next must have >= 3 meaningful lines (not a trivial stub)."""
    text = _read_zig()
    handler_body = _extract_handler_body(text)
    next_body = _extract_next_body(handler_body)

    lines = [ln.strip() for ln in next_body.split("\n")]
    meaningful = [ln for ln in lines if ln and not ln.startswith("//") and ln not in ("{", "}", "")]
    assert len(meaningful) >= 3, (
        f"Handler.next has only {len(meaningful)} meaningful lines — likely a stub"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — src/CLAUDE.md:16 @ 7abe6c387d0746b26eeed7fe9175e14560840cbb
def test_no_prohibited_std_apis():
    """No std.fs/std.posix/std.os/std.process usage (bun.* wrappers required).

    Exception: std.math, std.mem, std.AutoArrayHashMap are OK per existing patterns.
    """
    text = _read_zig()
    bad = re.findall(r"std\.(fs|posix|os|process)\.", text)
    assert len(bad) == 0, f"Prohibited std.* API usage found: {bad}"


# [agent_config] pass_to_pass — src/CLAUDE.md:11 @ 7abe6c387d0746b26eeed7fe9175e14560840cbb
def test_no_inline_imports():
    """No @import() inline inside function bodies."""
    text = _read_zig()
    fn_bodies = re.findall(r"pub fn \w+\([^)]*\)[^{]*\{(.*?)\n\s{8}\}", text, re.DOTALL)
    for body in fn_bodies:
        assert "@import(" not in body, "Found @import() inline inside a function body"


# [agent_config] pass_to_pass — src/CLAUDE.md:234 @ 7abe6c387d0746b26eeed7fe9175e14560840cbb
def test_no_catch_out_of_memory_pattern():
    """Must use bun.handleOom(), not 'catch bun.outOfMemory()' which swallows non-OOM errors."""
    text = _read_zig()
    bad = re.findall(r"catch\s+bun\.outOfMemory\(\)", text)
    assert len(bad) == 0, (
        f"Found {len(bad)} uses of 'catch bun.outOfMemory()' — "
        "use bun.handleOom() or 'try' instead"
    )


# [pr_diff] fail_to_pass
def test_mapping_populated_during_chunk_creation():
    """The entry-point-to-chunk mapping must be written when JS chunks are created.

    The fix requires storing the mapping index at the point where js_chunks.getOrPut
    is called. Without this, the mapping array stays all-sentinels and every entry
    point gets skipped in Handler.next.
    """
    text = _read_zig()
    # Find the section where js_chunks.getOrPut is called and check the mapping is updated nearby
    getorput_section = re.search(
        r"js_chunks\.getOrPut\(js_chunk_key\)(.*?)\n\s{8}\}",
        text,
        re.DOTALL,
    )
    assert getorput_section, "js_chunks.getOrPut(js_chunk_key) not found"
    section = getorput_section.group(1)

    # The mapping must be written in this section (any variable indexed by entry_id)
    has_mapping_write = bool(re.search(r"\w+\[entry_id\w*\]\s*=", section))
    assert has_mapping_write, (
        "No mapping write found near js_chunks.getOrPut — "
        "the entry-point-to-chunk index must be recorded when JS chunks are created"
    )
