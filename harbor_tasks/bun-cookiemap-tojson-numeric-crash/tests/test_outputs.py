"""
Task: bun-cookiemap-tojson-numeric-crash
Repo: oven-sh/bun @ 581d45c267edeeeba53595f1663d73a8d90dec4e
PR:   28314

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Note: This is a C++ codebase (Bun runtime) that requires the Zig compiler
and a complex build system to compile. We cannot build or call the code in
this test environment, so tests verify source-level fix patterns in
CookieMap.cpp. This is the standard approach for C++ runtime bug-fix tasks.
"""

import re
from pathlib import Path

REPO = "/workspace/bun"
FILE = Path(REPO) / "src/bun.js/bindings/CookieMap.cpp"


def _read_tojson_body() -> str:
    """Extract the body of CookieMap::toJSON method."""
    text = FILE.read_text()
    m = re.search(
        r"CookieMap::toJSON\b.*?\{(.*?)^\}",
        text,
        re.DOTALL | re.MULTILINE,
    )
    assert m, "CookieMap::toJSON method not found in CookieMap.cpp"
    return m.group(1)


def _read_full_file() -> str:
    return FILE.read_text()


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_no_bare_putdirect_in_tojson():
    """toJSON must not use bare putDirect (crashes on numeric cookie names).
    Must use an index-safe variant like putDirectMayBeIndex, putDirectIndex,
    putByIndex, put, or defineOwnProperty."""
    body = _read_tojson_body()

    # Match only bare ->putDirect( — NOT ->putDirectMayBeIndex( etc.
    bare_puts = re.findall(r"->putDirect\s*\(", body)
    assert len(bare_puts) == 0, (
        f"Found {len(bare_puts)} bare putDirect call(s) — crashes on numeric cookie names"
    )

    # Verify at least one index-safe variant exists
    safe_puts = re.findall(
        r"->(?:putDirectMayBeIndex|putDirectIndex|putByIndex|put|defineOwnProperty)\s*\(",
        body,
    )
    assert len(safe_puts) >= 1, "No index-safe property insertion found in toJSON"


# [pr_diff] fail_to_pass
def test_all_insertion_paths_safe():
    """Both modified-cookie and original-cookie loops must use index-safe
    property insertion. Accepts: two safe calls, or one call in a merged loop."""
    body = _read_tojson_body()

    all_puts = re.findall(
        r"->(putDirect\w*|putByIndex|put|defineOwnProperty)\s*\(", body
    )
    unsafe = [p for p in all_puts if p == "putDirect"]
    safe = [
        p
        for p in all_puts
        if p
        in ("putDirectMayBeIndex", "putDirectIndex", "putByIndex", "put", "defineOwnProperty")
    ]

    assert len(unsafe) == 0, f"Unsafe putDirect calls remain: {unsafe}"

    if len(safe) >= 2:
        return  # Both paths covered directly

    # Single safe call is OK if it's inside a loop (merged iteration)
    assert len(safe) == 1, "No property insertion calls found"
    assert re.search(r"\bfor\s*\(|\bwhile\s*\(", body), (
        "Single safe put found but not inside a loop — both cookie paths must be covered"
    )


# [pr_diff] fail_to_pass
def test_dedup_avoids_hasproperty():
    """Deduplication must not call hasProperty on the JSObject (also crashes
    on numeric keys). Accept: HashSet tracking, restructured iteration, or
    any approach that avoids hasProperty on the result object."""
    body = _read_tojson_body()

    has_property_calls = re.findall(r"->hasProperty\s*\(", body)
    if len(has_property_calls) == 0:
        return  # No hasProperty at all — safe

    # hasProperty present — only OK if there's native C++ tracking too
    assert re.search(
        r"HashSet|std::set|std::unordered_set|WTF::HashSet|std::unordered_map",
        body,
    ), "hasProperty called on JSObject without native tracking — crashes on numeric keys"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_tojson_preserves_functionality():
    """toJSON must still construct a JS object, handle exceptions, and iterate
    over cookies — core functionality must not be removed."""
    body = _read_tojson_body()

    has_obj = bool(
        re.search(
            r"constructEmptyObject|constructObject|JSObject::create|JSFinalObject::create",
            body,
        )
    )
    has_exc = bool(
        re.search(
            r"RETURN_IF_EXCEPTION|RELEASE_AND_RETURN|throwException|DECLARE_THROW_SCOPE|scope",
            body,
        )
    )
    has_iter = bool(re.search(r"\bfor\s*\(|\bwhile\s*\(|forEach", body))

    missing = []
    if not has_obj:
        missing.append("object construction")
    if not has_exc:
        missing.append("exception handling")
    if not has_iter:
        missing.append("iteration")
    assert len(missing) <= 1, f"toJSON missing core functionality: {', '.join(missing)}"


# [static] pass_to_pass
def test_not_stub():
    """toJSON must have a real implementation, not a stub."""
    body = _read_tojson_body()
    non_blank = [
        line
        for line in body.splitlines()
        if line.strip() and not line.strip().startswith("//")
    ]
    assert len(non_blank) >= 8, (
        f"toJSON body has only {len(non_blank)} non-blank lines — likely a stub"
    )


# [static] pass_to_pass
def test_other_methods_preserved():
    """CookieMap must retain its other methods — the fix should not replace
    the entire file with a minimal stub."""
    text = _read_full_file()
    other_methods = set(re.findall(r"CookieMap::(\w+)", text))
    other_methods.discard("toJSON")
    assert len(other_methods) >= 3, (
        f"Only {len(other_methods)} other CookieMap methods found — file may have been replaced"
    )


# [pr_diff] pass_to_pass
def test_put_inside_loop():
    """Property insertion must occur inside a loop (iterating cookies), not
    as standalone statements — ensures coherent implementation."""
    body = _read_tojson_body()
    lines = body.splitlines()

    loop_lines = [
        i for i, line in enumerate(lines) if re.search(r"\bfor\s*\(|\bwhile\s*\(", line)
    ]
    put_lines = [
        i
        for i, line in enumerate(lines)
        if re.search(
            r"->(?:putDirect\w*|putByIndex|put|defineOwnProperty)\s*\(", line
        )
    ]

    assert loop_lines, "No loops found in toJSON"
    assert put_lines, "No property insertion calls found in toJSON"

    found = any(
        0 < (put - loop) <= 15 for loop in loop_lines for put in put_lines
    )
    assert found, "Property insertion not inside a loop — implementation not coherent"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md / AGENTS.md / SKILL.md
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — .claude/skills/implementing-jsc-classes-cpp/SKILL.md:184 @ 581d45c2
def test_root_h_included():
    """C++ files in the bindings layer must include root.h.
    # AST-only because: C++ file, requires Zig/CMake build system to compile"""
    text = _read_full_file()
    assert re.search(r'#include\s+"root\.h"', text), (
        "CookieMap.cpp must include root.h — required for all C++ files in bindings"
    )


# [agent_config] pass_to_pass — .claude/skills/implementing-jsc-classes-cpp/SKILL.md:94-101 @ 581d45c2
def test_exception_scope_in_tojson():
    """toJSON must use JSC exception scope pattern (DECLARE_THROW_SCOPE or
    RELEASE_AND_RETURN) — required for all JSC binding functions.
    # AST-only because: C++ file, requires Zig/CMake build system to compile"""
    body = _read_tojson_body()
    assert re.search(r"DECLARE_THROW_SCOPE|RELEASE_AND_RETURN", body), (
        "toJSON must declare a JSC throw scope — required pattern for bindings code"
    )
