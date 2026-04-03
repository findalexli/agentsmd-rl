"""
Task: bun-braces-empty-input-oob
Repo: oven-sh/bun @ 5b7fe81279a40f3fccebe6e7f52278c81b39dfb6
PR:   28490

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/bun"
TARGET = Path(REPO) / "src" / "shell" / "braces.zig"


def _src():
    return TARGET.read_text()


def _get_diff():
    r = subprocess.run(["git", "diff", "HEAD"], capture_output=True, text=True, cwd=REPO)
    diff = r.stdout
    if not diff:
        r = subprocess.run(
            ["git", "diff", "--cached"], capture_output=True, text=True, cwd=REPO
        )
        diff = r.stdout
    return diff


def _added_lines(diff):
    return [
        line[1:]
        for line in diff.split("\n")
        if line.startswith("+") and not line.startswith("+++")
    ]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_braces_zig_structure_intact():
    """braces.zig exists and contains core Parser struct with key functions."""
    content = _src()
    assert "pub const Parser = struct" in content
    for fn_name in ("flattenTokens", "advance", "prev", "peek", "is_at_end"):
        assert f"fn {fn_name}(" in content, f"Missing function: {fn_name}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_flatten_tokens_empty_guard():
    """flattenTokens must guard against empty token list before first items[] access.

    Bug: flattenTokens calls items[0] unconditionally — panics when token list is empty.
    Valid fixes: 'if (len == 0) return', 'if (len < 1) return', wrap body, etc.
    """
    lines = _src().splitlines()

    # Find the flattenTokens function definition line
    fn_line = next(
        (i for i, l in enumerate(lines) if "fn flattenTokens(" in l), None
    )
    assert fn_line is not None, "flattenTokens not found in braces.zig"

    # Find first unconditional items[] access after the function start
    first_access = None
    for i in range(fn_line + 1, min(fn_line + 80, len(lines))):
        stripped = lines[i].strip()
        if stripped.startswith("//"):
            continue
        if re.search(r"items\[", stripped):
            first_access = i
            break

    assert first_access is not None, "No items[] access found near flattenTokens"

    # There must be an empty/length guard BEFORE the first items[] access
    guard_found = False
    for i in range(fn_line + 1, first_access):
        stripped = lines[i].strip()
        if stripped.startswith("//"):
            continue
        # Guard patterns: .len == 0, .len < 1, tokens.items.len check
        if re.search(r"\.len\s*(==\s*0|<\s*1)", stripped) and "return" in stripped:
            guard_found = True
            break
        # Early-return guard split across two lines
        if re.search(r"\.len\s*(==\s*0|<\s*1)", stripped):
            for j in range(i + 1, min(i + 3, first_access)):
                if "return" in lines[j].strip():
                    guard_found = True
                    break
            if guard_found:
                break
        # Wrap body in if (len > 0) { ... }
        if re.search(r"if\s*\(.*\.len\s*(>|!=|>=)", stripped):
            guard_found = True
            break

    assert guard_found, (
        f"No empty-token guard found in flattenTokens before items[] access "
        f"at line {first_access + 1}"
    )


# [pr_diff] fail_to_pass
def test_advance_prev_no_underflow():
    """advance()/prev() must not underflow when current == 0.

    Bug: advance() calls self.prev() which does current-1; u32 underflows at 0.
    Valid fixes:
      A) advance() uses conditional: 'return if (self.current > 0) self.prev() else ...'
      B) prev() guards: 'if (self.current == 0) return .eof;'
      C) Either uses saturating subtraction (-|)
    """
    lines = _src().splitlines()

    # Find the Parser struct
    parser_line = next(
        (i for i, l in enumerate(lines) if "pub const Parser = struct" in l), None
    )
    assert parser_line is not None, "pub const Parser = struct not found"

    # Find advance() and prev() inside Parser (search from parser_line)
    advance_line = next(
        (
            i
            for i, l in enumerate(lines)
            if i > parser_line and "fn advance(" in l
        ),
        None,
    )
    prev_line = next(
        (
            i
            for i, l in enumerate(lines)
            if i > parser_line and "fn prev(" in l
        ),
        None,
    )
    assert advance_line is not None, "fn advance( not found in Parser"
    assert prev_line is not None, "fn prev( not found in Parser"

    fixed = False

    # Approach A: advance() uses conditional return instead of bare prev()
    for i in range(advance_line, min(advance_line + 20, len(lines))):
        stripped = lines[i].strip()
        if stripped.startswith("//"):
            continue
        # Conditional return pattern
        if re.search(r"return\s+if\s*\(.*current", stripped) and "prev" in stripped:
            fixed = True
            break
        # Guard: if (current > 0 || != 0) before calling prev
        if re.search(r"current\s*(>|!=|>=)\s*(0|1)", stripped) and "prev" in stripped:
            fixed = True
            break
        # Saturating sub in advance
        if "-|" in stripped and "current" in stripped:
            fixed = True
            break

    # Approach B: prev() guards against current == 0
    if not fixed:
        for i in range(prev_line, min(prev_line + 15, len(lines))):
            stripped = lines[i].strip()
            if stripped.startswith("//"):
                continue
            if re.search(r"current\s*==\s*0", stripped) and "return" in stripped:
                fixed = True
                break
            # Saturating sub in prev
            if "-|" in stripped and "current" in stripped:
                fixed = True
                break
            if "@max" in stripped and "current" in stripped:
                fixed = True
                break

    assert fixed, (
        "advance()/prev() still vulnerable to u32 underflow: "
        "no guard found for current==0 in either function"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_prev_normal_case_intact():
    """prev() still accesses current-1 for the non-zero case (not replaced by stub)."""
    content = _src()
    assert any(s in content for s in ("current - 1", "current -| 1")), (
        "prev() no longer accesses current-1 — normal case may be broken"
    )


# [static] pass_to_pass
def test_flatten_tokens_not_stub():
    """flattenTokens still has real brace-expansion logic (not a stub return)."""
    content = _src()
    assert "brace_count" in content, "brace_count variable missing — flattenTokens may be stubbed"
    assert ".open" in content, ".open token reference missing"
    lines = content.splitlines()
    fn_line = next((i for i, l in enumerate(lines) if "fn flattenTokens(" in l), None)
    assert fn_line is not None
    # Count substantive lines in the ~60 lines after the function signature
    body = [
        l
        for l in lines[fn_line : fn_line + 70]
        if l.strip() and not l.strip().startswith("//")
    ]
    assert len(body) >= 15, f"flattenTokens only {len(body)} lines — likely stubbed"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from src/CLAUDE.md
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — src/CLAUDE.md:16 @ 5b7fe81
def test_no_prohibited_std_apis():
    """New code must not use std.fs, std.posix, std.os, std.process (src/CLAUDE.md:16)."""
    diff = _get_diff()
    if not diff:
        return  # no changes — vacuously passes
    prohibited = ["std.fs", "std.posix", "std.os", "std.process"]
    for line in _added_lines(diff):
        for api in prohibited:
            assert api not in line, f"Prohibited API '{api}' in added line: {line.strip()}"


# [agent_config] pass_to_pass — src/CLAUDE.md:11 @ 5b7fe81
def test_no_inline_imports():
    """@import() must not appear inline inside function bodies (src/CLAUDE.md:11)."""
    diff = _get_diff()
    if not diff:
        return  # no changes — vacuously passes
    for line in _added_lines(diff):
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        if "@import(" in stripped and not re.match(r"^\s*(pub\s+)?const\s+", stripped):
            assert False, f"Inline @import found in added code: {stripped}"


# [agent_config] pass_to_pass — src/CLAUDE.md:25 @ 5b7fe81
def test_no_std_mem_for_strings():
    """Must not use std.mem.eql/indexOf/startsWith for strings; use bun.strings.* (src/CLAUDE.md:25)."""
    diff = _get_diff()
    if not diff:
        return  # no changes — vacuously passes
    prohibited_string_fns = ["std.mem.eql", "std.mem.indexOf", "std.mem.startsWith", "std.mem.endsWith"]
    for line in _added_lines(diff):
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        for fn in prohibited_string_fns:
            assert fn not in stripped, (
                f"Use bun.strings.* instead of '{fn}' for string operations: {stripped}"
            )


# [agent_config] pass_to_pass — src/CLAUDE.md:234 @ 5b7fe81
def test_no_catch_outofmemory_pattern():
    """Must use bun.handleOom() not 'catch bun.outOfMemory()' (src/CLAUDE.md:234)."""
    diff = _get_diff()
    if not diff:
        return  # no changes — vacuously passes
    for line in _added_lines(diff):
        assert "catch bun.outOfMemory()" not in line, (
            f"Use bun.handleOom() not catch bun.outOfMemory(): {line.strip()}"
        )
