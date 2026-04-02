"""
Task: bun-expect-extend-numeric-key-crash
Repo: oven-sh/bun @ 6034bd82b1a0d9b3635560405354e931b7e0e192
PR:   28504

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/bun"
FILE = Path(REPO) / "src/bun.js/test/expect.zig"

TARGETS = ["expect_proto", "expect_constructor", "expect_static_proto"]
READ_ONLY = {
    "get", "has", "contains", "count", "next", "keys", "iterator",
    "len", "ptr", "items", "reset", "deinit", "init", "format",
}


def _strip_comments_and_strings(text: str) -> str:
    """Remove single-line comments and string literals from Zig source."""
    text = re.sub(r"//[^\n]*", "", text)
    text = re.sub(r'"(?:[^"\\]|\\.)*"', '""', text)
    return text


def _extract_extend_body() -> str:
    """Extract the body of `pub fn extend` with comments/strings stripped."""
    text = FILE.read_text()
    idx = text.find("pub fn extend")
    assert idx != -1, "pub fn extend not found in expect.zig"
    brace = text.index("{", idx)
    depth, i = 1, brace + 1
    while i < len(text) and depth > 0:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1
    body = text[brace + 1 : i - 1]
    return _strip_comments_and_strings(body)


def _iterator_skips_indices(body: str) -> bool:
    """Check if the JSPropertyIterator is configured to skip index properties."""
    if re.search(r"\.initFast\s*\([^)]*\b(?:true|false)\b[^)]*\)", body):
        return True
    if re.search(
        r"(?:isIndex|parseIndex)\s*\([^)]*\)\s*[^;]*(?:continue|break|return)", body
    ):
        return True
    return False


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_no_bare_put_on_registration_targets():
    """Buggy .put() calls on expect_proto/constructor/static_proto are removed or guarded."""
    body = _extract_extend_body()

    for target in TARGETS:
        assert target in body, f"{target} not found in extend body — registration logic removed?"

    if _iterator_skips_indices(body):
        return

    for target in TARGETS:
        pattern = re.escape(target) + r"\.put\s*\("
        assert not re.search(pattern, body), (
            f"Bare .put() still used on {target} — crashes on numeric index keys"
        )


# [pr_diff] fail_to_pass
def test_index_safe_property_setting():
    """Properties are registered via a method that handles index keys safely."""
    body = _extract_extend_body()

    if _iterator_skips_indices(body):
        return

    for target in TARGETS:
        methods = re.findall(re.escape(target) + r"\.(\w+)\s*\(", body)
        setters = [m for m in methods if m.lower() not in READ_ONLY and m != "put"]
        assert setters, (
            f"{target} has no safe property-setting method (e.g. putMayBeIndex, defineProperty)"
        )


# [pr_diff] fail_to_pass
def test_all_three_targets_use_safe_setter():
    """All three registration targets are updated, not just one or two."""
    body = _extract_extend_body()

    if _iterator_skips_indices(body):
        return

    safe_count = 0
    for target in TARGETS:
        bare_puts = re.findall(re.escape(target) + r"\.put\s*\(", body)
        all_methods = re.findall(re.escape(target) + r"\.(\w+)\s*\(", body)
        safe_methods = [m for m in all_methods if m.lower() not in READ_ONLY and m != "put"]
        if safe_methods and not bare_puts:
            safe_count += 1
    assert safe_count == 3, (
        f"Only {safe_count}/3 targets use safe property setting — all three must be fixed"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_extend_preserves_core_logic():
    """Extend function still iterates properties and creates wrapper functions."""
    body = _extract_extend_body()

    assert re.search(r"while\s*\(", body) or re.search(r"[Ii]terator", body), (
        "extend() missing property iteration loop"
    )
    assert re.search(r"Bun__JSWrappingFunction__create|WrappingFunction|wrapFunction", body), (
        "extend() missing wrapper function creation"
    )
    assert "applyCustomMatcher" in body, (
        "extend() missing applyCustomMatcher callback"
    )


# [static] pass_to_pass
def test_key_functions_preserved():
    """Core expect functions still exist in expect.zig."""
    text = FILE.read_text()
    required = ["applyCustomMatcher", "pub fn extend", "pub fn toBeCloseTo", "pub fn toEqual"]
    missing = [fn for fn in required if fn not in text]
    assert not missing, f"Missing functions: {missing}"


# [static] pass_to_pass
def test_not_stub():
    """expect.zig has substantial Zig content (not stubbed out)."""
    text = FILE.read_text()
    lines = len(text.strip().split("\n"))
    pub_fns = len(re.findall(r"\bpub\s+fn\b", text))
    structs = len(re.findall(r"\bstruct\b", text))
    consts = len(re.findall(r"\bconst\b", text))
    assert lines >= 500, f"File too small: {lines} lines"
    assert pub_fns >= 5, f"Too few pub fn: {pub_fns}"
    assert structs >= 2, f"Too few structs: {structs}"
    assert consts >= 10, f"Too few consts: {consts}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from src/CLAUDE.md
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — src/CLAUDE.md:11 @ 6034bd82
def test_no_inline_import_in_functions():
    """No @import() inline inside the extend function body (src/CLAUDE.md:11).

    Scoped to the extend body only — the agent only touches this function,
    so pre-existing violations in other functions are not checked here.
    """
    # AST-only because: Zig code cannot be imported/executed in Python
    body = _extract_extend_body()
    body_nc = re.sub(r"//[^\n]*", "", body)
    for line in body_nc.split("\n"):
        stripped = line.strip()
        assert "@import" not in stripped, (
            f"Inline @import found inside extend() body: {stripped[:80]}"
        )


# [agent_config] pass_to_pass — src/CLAUDE.md:16 @ 6034bd82
def test_no_std_direct_usage():
    """No std.fs/std.posix/std.os introduced in the extend function (src/CLAUDE.md:16).

    Scoped to the extend body only — the agent only touches this function.
    """
    # AST-only because: Zig code cannot be imported/executed in Python
    body = _extract_extend_body()
    violations = re.findall(r"std\.(fs|posix|os)\.\w+", body)
    assert not violations, f"Found std.* in extend() (should use bun.* instead): {violations}"


# [agent_config] pass_to_pass — src/CLAUDE.md:232 @ 6034bd82
def test_no_wrong_allocator():
    """New allocator usage should use bun.default_allocator (src/CLAUDE.md:232)."""
    # AST-only because: Zig code cannot be imported/executed in Python
    body = _extract_extend_body()
    # Check the extend function doesn't introduce std.heap or gpa allocator
    assert "std.heap" not in body, "extend() uses std.heap — should use bun.default_allocator"
    assert "GeneralPurposeAllocator" not in body, (
        "extend() uses GeneralPurposeAllocator — should use bun.default_allocator"
    )


# [agent_config] pass_to_pass — src/CLAUDE.md:234 @ 6034bd82
def test_no_catch_outofmemory_pattern():
    """Must not use 'catch bun.outOfMemory()' — use bun.handleOom() (src/CLAUDE.md:234)."""
    # AST-only because: Zig code cannot be imported/executed in Python
    body = _extract_extend_body()
    assert not re.search(r"catch\s+bun\.outOfMemory\s*\(\s*\)", body), (
        "extend() uses 'catch bun.outOfMemory()' — use bun.handleOom() instead"
    )
