"""
Task: bun-throw-pending-exception-crash
Repo: oven-sh/bun @ 698eb8104be9a42c9a2b5e5b03a8843f81911055
PR:   28535

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Structural analysis throughout because: Zig code — no Zig compiler available
in the test container (python:3.12-slim). The bun build system requires
custom toolchain setup not feasible in the verifier.
"""

import re
from pathlib import Path

REPO = "/workspace/bun"
FILE = "src/bun.js/bindings/JSGlobalObject.zig"


def _read_file():
    return Path(f"{REPO}/{FILE}").read_text()


def _strip_comments(code: str) -> str:
    """Remove single-line // comments from Zig code."""
    lines = code.split("\n")
    result = []
    for line in lines:
        in_string = False
        i = 0
        clean = line
        while i < len(line) - 1:
            if line[i] == '"' and (i == 0 or line[i - 1] != "\\"):
                in_string = not in_string
            elif not in_string and line[i : i + 2] == "//":
                clean = line[:i]
                break
            i += 1
        result.append(clean)
    return "\n".join(result)


def _extract_function(code: str, fn_name: str, signature_pattern: str = None) -> str | None:
    """Extract a function body by name, using brace-counting for boundaries.
    Returns the comment-stripped function body, or None if not found."""
    code = _strip_comments(code)
    lines = code.split("\n")

    fn_start = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        if signature_pattern:
            if re.search(signature_pattern, stripped):
                fn_start = i
                break
        else:
            if re.match(rf"pub fn {re.escape(fn_name)}\b", stripped) or re.match(
                rf"fn {re.escape(fn_name)}\b", stripped
            ):
                fn_start = i
                break

    if fn_start == -1:
        return None

    depth = 0
    started = False
    for i in range(fn_start, len(lines)):
        for ch in lines[i]:
            if ch == "{":
                if not started:
                    started = True
                depth += 1
            elif ch == "}":
                depth -= 1
                if started and depth == 0:
                    return "\n".join(lines[fn_start : i + 1])
    return None


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — file exists and has real content
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_file_exists_and_nontrivial():
    """JSGlobalObject.zig must exist with substantial content (not gutted)."""
    path = Path(f"{REPO}/{FILE}")
    assert path.exists(), f"{FILE} does not exist"
    line_count = len(path.read_text().splitlines())
    assert line_count > 400, f"File suspiciously small ({line_count} lines)"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — crash-causing patterns must be removed
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_crash_assert_removed():
    """bun.assert(instance != .zero) in throw()/throwPretty() must be removed.
    This assert is the direct crash trigger on stack overflow."""
    code = _read_file()
    clean = _strip_comments(code)
    assert "bun.assert(instance != .zero)" not in clean, (
        "bun.assert(instance != .zero) still present — will crash on stack overflow"
    )


# [pr_diff] fail_to_pass
def test_throwvalue_guarded():
    """throwValue() must not unconditionally call vm().throwError() — needs a
    guard for when a termination exception is already pending."""
    code = _read_file()
    body = _extract_function(code, "throwValue", r"pub fn throwValue\(")
    assert body is not None, "throwValue() function not found"

    has_vm_throw = "vm().throwError(" in body or "vm().throw(" in body
    if has_vm_throw:
        has_guard = (
            "hasException" in body
            or "hasPendingException" in body
        )
        assert has_guard, "throwValue() unconditionally calls vm().throwError() — crashes when exception pending"


# [pr_diff] fail_to_pass
def test_throw_and_throwpretty_handle_zero():
    """throw() and throwPretty() must handle createErrorInstance returning .zero
    (which happens when a termination exception like stack overflow is pending).
    An assert that .zero doesn't happen is NOT handling — must use if/orelse/catch."""
    code = _read_file()
    for fn_name, sig in [
        ("throw", r"pub fn throw\(this.*comptime fmt"),
        ("throwPretty", r"pub fn throwPretty\("),
    ]:
        body = _extract_function(code, fn_name, sig)
        assert body is not None, f"{fn_name}() function not found"

        has_create = "createErrorInstance" in body
        # Must check for actual zero-HANDLING (if/orelse/catch), not just
        # the presence of ".zero" which could be in an assert.
        has_zero_handling = (
            re.search(r"if\s*\(.*==\s*\.zero\)", body) is not None
            or "orelse" in body
            or "catch" in body
            or "error.JSError" in body
        )
        if has_create:
            assert has_zero_handling, (
                f"{fn_name}() calls createErrorInstance but doesn't handle .zero return"
            )
        else:
            assert "error.JSError" in body or "JSError" in body, (
                f"{fn_name}() refactored away from createErrorInstance but doesn't handle errors"
            )


# [pr_diff] fail_to_pass
def test_throwtodo_handles_zero():
    """throwTODO() must handle createErrorInstance returning .zero."""
    code = _read_file()
    body = _extract_function(code, "throwTODO", r"pub fn throwTODO\(")
    assert body is not None, "throwTODO() function not found"

    has_create = "createErrorInstance" in body
    has_zero_handling = (
        re.search(r"if\s*\(.*==\s*\.zero\)", body) is not None
        or "orelse" in body
        or "catch" in body
        or "error.JSError" in body
    )
    if has_create:
        assert has_zero_handling, "throwTODO() calls createErrorInstance but doesn't handle .zero return"
    else:
        assert "error.JSError" in body or "JSError" in body, (
            "throwTODO() refactored but doesn't handle errors"
        )


# [pr_diff] fail_to_pass
def test_throwerror_safe_path():
    """throwError(anyerror) must route through throwValue or have its own
    exception guard, not directly call vm().throwError()."""
    code = _read_file()
    body = _extract_function(code, "throwError", r"pub fn throwError\(this.*err:\s*anyerror")
    assert body is not None, "throwError(anyerror) function not found"

    has_safe = "throwValue" in body or "hasException" in body or "hasPendingException" in body
    if not has_safe:
        # Check if it still directly calls vm().throwError unguarded
        if ".vm()" in body:
            after_vm = body.split(".vm()")[1][:30]
            assert "throwError" not in after_vm, (
                "throwError(anyerror) directly calls vm().throwError() without guard"
            )


# [pr_diff] fail_to_pass
def test_createrangeerror_handles_zero():
    """createRangeError() must handle createErrorInstance returning .zero."""
    code = _read_file()
    body = _extract_function(code, "createRangeError", r"pub fn createRangeError\(")
    assert body is not None, "createRangeError() function not found"

    has_create = "createErrorInstance" in body
    has_zero_handling = (
        re.search(r"if\s*\(.*==\s*\.zero\)", body) is not None
        or "orelse" in body
        or "catch" in body
    )
    if has_create:
        assert has_zero_handling, "createRangeError() calls createErrorInstance but doesn't handle .zero return"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — existing functions must be preserved
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_throwTypeError_preserved():
    """throwTypeError must still exist with a non-trivial body."""
    code = _read_file()
    body = _extract_function(code, "throwTypeError", r"pub fn throwTypeError\(")
    assert body is not None, "throwTypeError() function not found"
    non_empty = [l for l in body.strip().split("\n") if l.strip()]
    assert len(non_empty) > 3, "throwTypeError() has been stubbed out"


# [pr_diff] pass_to_pass
def test_throwDOMException_preserved():
    """throwDOMException must still exist with a non-trivial body."""
    code = _read_file()
    body = _extract_function(code, "throwDOMException", r"pub fn throwDOMException\(")
    assert body is not None, "throwDOMException() function not found"
    non_empty = [l for l in body.strip().split("\n") if l.strip()]
    assert len(non_empty) > 3, "throwDOMException() has been stubbed out"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from src/CLAUDE.md
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — src/CLAUDE.md:11 @ 698eb8104be9a42c9a2b5e5b03a8843f81911055
def test_no_inline_import_in_functions():
    """No @import() inline inside function bodies (src/CLAUDE.md:11)."""
    code = _read_file()
    clean = _strip_comments(code)

    in_fn = False
    depth = 0
    for line in clean.split("\n"):
        stripped = line.strip()
        if re.match(r"(pub )?fn ", stripped) and "{" in stripped:
            in_fn = True
            depth = stripped.count("{") - stripped.count("}")
            continue
        if in_fn:
            depth += stripped.count("{") - stripped.count("}")
            assert "@import" not in stripped, f"Found inline @import in function body: {stripped.strip()}"
            if depth <= 0:
                in_fn = False


# [agent_config] pass_to_pass — src/CLAUDE.md:16 @ 698eb8104be9a42c9a2b5e5b03a8843f81911055
def test_uses_bun_assert_not_std():
    """Must use bun.assert, not std.debug.assert (src/CLAUDE.md:16)."""
    code = _read_file()
    clean = _strip_comments(code)
    count = clean.count("std.debug.assert")
    assert count == 0, f"Found {count} occurrences of std.debug.assert — use bun.assert"


# [agent_config] pass_to_pass — src/CLAUDE.md:16 @ 698eb8104be9a42c9a2b5e5b03a8843f81911055
def test_no_std_fs_posix_os():
    """Must not use std.fs/std.posix/std.os — use bun.* equivalents (src/CLAUDE.md:16)."""
    code = _read_file()
    clean = _strip_comments(code)
    matches = re.findall(r"std\.(fs|posix|os)\.", clean)
    assert len(matches) == 0, f"Found {len(matches)} uses of std.fs/posix/os — use bun.* equivalents"
