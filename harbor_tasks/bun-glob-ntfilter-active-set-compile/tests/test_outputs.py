"""
Task: bun-glob-ntfilter-active-set-compile
Repo: oven-sh/bun @ 39094877abb3e74557d3975dd015ee677220eb35
PR:   28543

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

All tests use structural text analysis because: Zig code cannot be compiled
or executed from Python, and the bun build system requires a full native
Zig toolchain + cmake + system deps not available in the test container.
"""

import re
from pathlib import Path

REPO = "/workspace/bun"
TARGET = Path(REPO) / "src/glob/GlobWalker.zig"


def _strip_zig_comments(text: str) -> str:
    """Remove // line comments from Zig source."""
    out = []
    for line in text.splitlines():
        idx = line.find("//")
        if idx >= 0:
            out.append(line[:idx])
        else:
            out.append(line)
    return "\n".join(out)


def _read_stripped() -> str:
    return _strip_zig_comments(TARGET.read_text())


def _find_setNameFilter_callsite(code: str, before: int = 20, after: int = 10) -> str:
    """Return code lines surrounding the setNameFilter CALL site (not definition).

    The file has multiple occurrences of 'setNameFilter': the method definition
    inside DirIter (~line 141) and the call site (~line 715). We want the call
    site, which is the one near 'computeNtFilter' / 'isWindows'.
    """
    lines = code.splitlines()
    # Find the call site: `iterator.setNameFilter(...)`.
    # Must skip: the method definition body (`self.value.setNameFilter`), the
    # function signature ("fn setNameFilter"), and the @hasDecl check.
    # The call site uses `iterator` as the receiver (not `self.value`).
    best_idx = None
    for i, line in enumerate(lines):
        s = line.strip()
        if "iterator.setNameFilter" in s:
            best_idx = i
            break
    if best_idx is None:
        # Fallback: find setNameFilter near computeNtFilter (both exist at call site)
        for i, line in enumerate(lines):
            if "computeNtFilter" in line and "fn " not in line:
                # Look for setNameFilter within 15 lines
                for j in range(max(0, i - 15), min(len(lines), i + 15)):
                    if "setNameFilter" in lines[j] and "fn " not in lines[j] and "@hasDecl" not in lines[j]:
                        best_idx = j
                        break
                if best_idx is not None:
                    break
    if best_idx is None:
        # Fallback: use the LAST occurrence (call site is after definition)
        for i, line in enumerate(lines):
            if "setNameFilter" in line and line.strip():
                best_idx = i
        if best_idx is None:
            return ""
    start = max(0, best_idx - before)
    end = min(len(lines), best_idx + after)
    return "\n".join(lines[start:end])


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_source_file_exists_balanced_braces():
    """GlobWalker.zig exists and has roughly balanced braces."""
    # Structural because: Zig cannot be compiled in test container
    code = TARGET.read_text()
    assert len(code) > 1000, "File appears truncated or empty"
    opens = code.count("{")
    closes = code.count("}")
    assert abs(opens - closes) <= 5, (
        f"Unbalanced braces: {opens} open, {closes} close"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core fix verification
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_buggy_component_idx_removed():
    """The broken computeNtFilter(component_idx) call is removed."""
    # Structural because: Zig cannot be compiled in test container
    code = _read_stripped()
    assert "computeNtFilter(component_idx)" not in code, (
        "Still references undeclared 'component_idx' variable"
    )


# [pr_diff] fail_to_pass
def test_fix_uses_active_bitset():
    """Fix derives component index from the active BitSet near setNameFilter."""
    # Structural because: Zig cannot be compiled in test container
    # The fix must use active BitSet methods (like findFirstSet, count) in the
    # actual setNameFilter argument or its immediately preceding const/var.
    # Use a tight window (4 lines) to avoid matching the log() call further up
    # which already has active.count() for debug output.
    block = _find_setNameFilter_callsite(_read_stripped(), before=4, after=1)
    assert block, "setNameFilter call site not found in source"
    assert re.search(r"\bactive\.\w+\(", block), (
        "No BitSet method call on 'active' near setNameFilter — "
        "fix must derive component index from active BitSet "
        "(e.g., active.findFirstSet(), active.count())"
    )


# [pr_diff] fail_to_pass
def test_multi_active_conditional():
    """Fix checks active.count() and uses null when multiple components active."""
    # Structural because: Zig cannot be compiled in test container
    #
    # The NT filter is a single-component optimization. When multiple pattern
    # indices are active (after **), a single-component filter could hide
    # entries needed by other indices. The fix MUST:
    #   1. Check how many bits are active (via .count())
    #   2. Use null as fallback when count != 1
    block = _find_setNameFilter_callsite(_read_stripped(), before=8, after=3)
    assert block, "setNameFilter call site not found in source"

    assert re.search(r"\.count\(\)", block), (
        "No .count() check on active set — fix must check if multiple "
        "components are active to decide whether to apply the NT filter"
    )
    assert "null" in block, (
        "No null fallback — when multiple components are active, "
        "setNameFilter must receive null to skip single-component filtering"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_set_name_filter_preserved():
    """setNameFilter call still exists in the Windows block."""
    # Structural because: Zig cannot be compiled in test container
    code = _read_stripped()
    assert any(
        "setNameFilter" in line
        for line in code.splitlines()
        if line.strip()
    ), "setNameFilter call was removed entirely"


# [pr_diff] pass_to_pass
def test_compute_nt_filter_function_preserved():
    """computeNtFilter function definition still exists with u32 parameter."""
    # Structural because: Zig cannot be compiled in test container
    code = TARGET.read_text()
    assert "fn computeNtFilter" in code, "computeNtFilter function was removed"
    idx = code.index("fn computeNtFilter")
    sig = code[idx : idx + 200]
    assert "u32" in sig, "computeNtFilter signature changed — missing u32 param"


# [pr_diff] pass_to_pass
def test_compute_nt_filter_still_called():
    """computeNtFilter is called (not just defined) near setNameFilter."""
    # Structural because: Zig cannot be compiled in test container
    code = _read_stripped()
    lines = code.splitlines()
    set_filter_idx = None
    compute_call_idx = None
    for i, line in enumerate(lines):
        s = line.strip()
        if "setNameFilter" in s:
            set_filter_idx = i
        if "computeNtFilter" in s and "fn " not in s:
            compute_call_idx = i
    assert set_filter_idx is not None, "setNameFilter not found"
    assert compute_call_idx is not None, (
        "computeNtFilter is never called — fix must still use it for single-active case"
    )
    assert abs(set_filter_idx - compute_call_idx) <= 25, (
        "computeNtFilter call too far from setNameFilter — should be nearby"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — src/CLAUDE.md:16 @ 39094877abb3e74557d3975dd015ee677220eb35
def test_no_std_usage_near_fix():
    """No std.* API usage near the fix (use bun.* instead per src/CLAUDE.md)."""
    # Structural because: Zig cannot be compiled in test container
    block = _find_setNameFilter_callsite(_read_stripped(), before=15, after=10)
    assert block, "setNameFilter call site not found"
    for line in block.splitlines():
        s = line.strip()
        assert not (s and "std." in s and "@import" not in s), (
            f"std.* usage near fix: {s}"
        )


# [agent_config] pass_to_pass — src/CLAUDE.md:11 @ 39094877abb3e74557d3975dd015ee677220eb35
def test_no_inline_import_near_fix():
    """No inline @import near the fix (per src/CLAUDE.md)."""
    # Structural because: Zig cannot be compiled in test container
    block = _find_setNameFilter_callsite(_read_stripped(), before=15, after=10)
    assert block, "setNameFilter call site not found"
    for line in block.splitlines():
        s = line.strip()
        assert not (s and "@import" in s), (
            f"Inline @import near fix: {s}"
        )
