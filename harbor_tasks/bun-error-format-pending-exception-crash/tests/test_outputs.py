"""
Task: bun-error-format-pending-exception-crash
Repo: oven-sh/bun @ f6528b58ed67c8fb8c80046114829d9ad79a292f
PR:   28488

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

TARGET = Path("/repo/src/bun.js/bindings/JSGlobalObject.zig")

# Structural-only because: Zig source requires Zig compiler + full Bun build system
# (CMake, hours of compile time, platform deps). Cannot compile or call functions
# in the test container.


def _strip_comments_and_strings(code: str) -> str:
    """Remove Zig // comments and string literals to prevent gaming via injection."""
    code = re.sub(r"//[^\n]*", "", code)
    code = re.sub(r'"(?:[^"\\]|\\.)*"', '""', code)
    return code


def _find_fn_region(code: str, fn_name: str, size: int = 3000) -> str | None:
    """Extract the region for a pub fn, bounded by the next pub fn or size chars."""
    marker = f"pub fn {fn_name}"
    idx = code.find(marker)
    if idx < 0:
        return None
    next_fn = code.find("pub fn ", idx + len(marker))
    end = idx + size
    if next_fn > 0:
        end = min(end, next_fn)
    return code[idx:end]


def _extract_catch_bodies(region: str) -> list[str]:
    """Extract catch block bodies using brace counting."""
    bodies = []
    for m in re.finditer(r"catch\s*(?:\|[^|]*\|)?\s*\{", region):
        start = m.end()
        depth = 1
        i = start
        while i < len(region) and depth > 0:
            if region[i] == "{":
                depth += 1
            elif region[i] == "}":
                depth -= 1
            i += 1
        if depth == 0:
            bodies.append(region[start : i - 1])
    return bodies


def _catch_clears_before_return(region: str | None) -> bool:
    """Check if any catch block calls .clearExceptionExceptTermination() before return."""
    if region is None:
        return False
    for body in _extract_catch_bodies(region):
        clear = re.search(r"\.\s*clearExceptionExceptTermination\s*\(\s*\)", body)
        ret = re.search(r"\breturn\b", body)
        if clear and ret and clear.start() < ret.start():
            return True
    return False


def _catch_returns_typed(region: str | None, method: str) -> bool:
    """Check if a catch block with clear also returns the specific error type method."""
    if region is None:
        return False
    for body in _extract_catch_bodies(region):
        clear = re.search(r"\.\s*clearExceptionExceptTermination\s*\(\s*\)", body)
        ret = re.search(r"\breturn\b", body)
        if clear and ret and clear.start() < ret.start():
            after_return = body[ret.start() :]
            if re.search(r"\." + method + r"\s*\(", after_return):
                return True
    return False


def _catch_has_generic_error(region: str | None) -> bool:
    """Check if a catch block returns generic toErrorInstance (the original bug)."""
    if region is None:
        return False
    for body in _extract_catch_bodies(region):
        ret = re.search(r"\breturn\b", body)
        if ret and ".toErrorInstance(" in body[ret.start() :]:
            return True
    return False


def _read_clean_source() -> str:
    raw = TARGET.read_text()
    return _strip_comments_and_strings(raw)


def _read_raw_source() -> str:
    return TARGET.read_text()


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_create_error_instance_clears_exception():
    """createErrorInstance catch must call clearExceptionExceptTermination before return."""
    # Structural-only because: Zig source, no compiler in container
    clean = _read_clean_source()
    region = _find_fn_region(clean, "createErrorInstance")
    assert region is not None, "createErrorInstance function not found"
    assert _catch_clears_before_return(region), (
        "createErrorInstance catch block does not call "
        ".clearExceptionExceptTermination() before return"
    )


# [pr_diff] fail_to_pass
def test_create_type_error_clears_and_returns_typed():
    """createTypeErrorInstance catch must clear exception and return TypeError (not generic Error)."""
    # Structural-only because: Zig source, no compiler in container
    clean = _read_clean_source()
    region = _find_fn_region(clean, "createTypeErrorInstance")
    assert region is not None, "createTypeErrorInstance function not found"
    assert _catch_clears_before_return(region), (
        "createTypeErrorInstance catch does not clear exception before return"
    )
    assert _catch_returns_typed(region, "toTypeErrorInstance"), (
        "createTypeErrorInstance catch does not return toTypeErrorInstance"
    )
    assert not _catch_has_generic_error(region), (
        "createTypeErrorInstance catch still returns generic toErrorInstance"
    )


# [pr_diff] fail_to_pass
def test_create_syntax_error_clears_and_returns_typed():
    """createSyntaxErrorInstance catch must clear exception and return SyntaxError."""
    # Structural-only because: Zig source, no compiler in container
    clean = _read_clean_source()
    region = _find_fn_region(clean, "createSyntaxErrorInstance")
    assert region is not None, "createSyntaxErrorInstance function not found"
    assert _catch_clears_before_return(region), (
        "createSyntaxErrorInstance catch does not clear exception before return"
    )
    assert _catch_returns_typed(region, "toSyntaxErrorInstance"), (
        "createSyntaxErrorInstance catch does not return toSyntaxErrorInstance"
    )
    assert not _catch_has_generic_error(region), (
        "createSyntaxErrorInstance catch still returns generic toErrorInstance"
    )


# [pr_diff] fail_to_pass
def test_create_range_error_clears_and_returns_typed():
    """createRangeErrorInstance catch must clear exception and return RangeError."""
    # Structural-only because: Zig source, no compiler in container
    clean = _read_clean_source()
    region = _find_fn_region(clean, "createRangeErrorInstance")
    assert region is not None, "createRangeErrorInstance function not found"
    assert _catch_clears_before_return(region), (
        "createRangeErrorInstance catch does not clear exception before return"
    )
    assert _catch_returns_typed(region, "toRangeErrorInstance"), (
        "createRangeErrorInstance catch does not return toRangeErrorInstance"
    )
    assert not _catch_has_generic_error(region), (
        "createRangeErrorInstance catch still returns generic toErrorInstance"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass — regression + anti-stub
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_dom_exception_not_modified():
    """createDOMExceptionInstance uses try propagation — must NOT gain clearExceptionExceptTermination."""
    # Structural-only because: Zig source, no compiler in container
    clean = _read_clean_source()
    region = _find_fn_region(clean, "createDOMExceptionInstance")
    if region is None:
        return  # Function doesn't exist, nothing to check
    assert not re.search(
        r"\.\s*clearExceptionExceptTermination\s*\(\s*\)", region
    ), "createDOMExceptionInstance should not have clearExceptionExceptTermination"


# [static] pass_to_pass
def test_file_not_stubbed():
    """Target file must retain substantial content (not gutted)."""
    raw = _read_raw_source()
    line_count = len(raw.splitlines())
    assert line_count > 200, f"File appears stubbed ({line_count} lines)"


# [static] pass_to_pass
def test_all_four_functions_exist():
    """All four create*ErrorInstance functions must still exist."""
    clean = _read_clean_source()
    for fn in [
        "createErrorInstance",
        "createTypeErrorInstance",
        "createSyntaxErrorInstance",
        "createRangeErrorInstance",
    ]:
        assert _find_fn_region(clean, fn) is not None, f"{fn} not found in target file"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from src/CLAUDE.md
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — src/CLAUDE.md:11 @ f6528b58ed67c8fb8c80046114829d9ad79a292f
def test_no_inline_imports_in_error_functions():
    """No @import() calls inside the four create*ErrorInstance function bodies."""
    # Structural-only because: Zig source, no compiler in container
    # Rule: "Never use @import() inline inside of functions."
    raw = _read_raw_source()
    fns = [
        "createErrorInstance",
        "createTypeErrorInstance",
        "createSyntaxErrorInstance",
        "createRangeErrorInstance",
    ]
    for fn_name in fns:
        region = _find_fn_region(raw, fn_name)
        if region is None:
            continue
        # Skip the function signature line, check body only
        body_start = region.find("{")
        if body_start < 0:
            continue
        body = region[body_start:]
        inline_imports = re.findall(r"@import\s*\(", body)
        assert not inline_imports, (
            f"{fn_name} has inline @import() — must be at bottom of file or containing struct"
        )


# [agent_config] pass_to_pass — src/CLAUDE.md:16-28 @ f6528b58ed67c8fb8c80046114829d9ad79a292f
def test_no_forbidden_std_apis_in_error_functions():
    """No std.fs, std.posix, std.os, std.process usage in the four create*ErrorInstance functions."""
    # Structural-only because: Zig source, no compiler in container
    # Rule: "Always use bun.* APIs instead of std.*. Using std.fs, std.posix, or std.os directly is wrong."
    clean = _read_clean_source()
    forbidden = ["std.fs", "std.posix", "std.os", "std.process"]
    fns = [
        "createErrorInstance",
        "createTypeErrorInstance",
        "createSyntaxErrorInstance",
        "createRangeErrorInstance",
    ]
    for fn_name in fns:
        region = _find_fn_region(clean, fn_name)
        if region is None:
            continue
        for api in forbidden:
            assert api not in region, (
                f"{fn_name} uses {api} — must use bun.* equivalent instead"
            )


# [agent_config] pass_to_pass — src/CLAUDE.md:234-238 @ f6528b58ed67c8fb8c80046114829d9ad79a292f
def test_no_catch_out_of_memory_pattern():
    """No 'catch bun.outOfMemory()' in the four error functions — use bun.handleOom() instead."""
    # Structural-only because: Zig source, no compiler in container
    # Rule: "bun.handleOom(expr) converts error.OutOfMemory into a crash without swallowing other errors"
    clean = _read_clean_source()
    fns = [
        "createErrorInstance",
        "createTypeErrorInstance",
        "createSyntaxErrorInstance",
        "createRangeErrorInstance",
    ]
    for fn_name in fns:
        region = _find_fn_region(clean, fn_name)
        if region is None:
            continue
        assert "catch bun.outOfMemory()" not in region and "catch bun.oom()" not in region, (
            f"{fn_name} uses catch bun.outOfMemory() — should use bun.handleOom() instead"
        )
