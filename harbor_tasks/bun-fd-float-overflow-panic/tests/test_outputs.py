"""
Task: bun-fd-float-overflow-panic
Repo: oven-sh/bun @ 8f0fd0cf1da17fff23df7133e414cdd1f5ed917e
PR:   28364

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: Zig source requires the full Bun build toolchain (cmake, zig compiler,
etc.) which is not available in this environment. Tests use structural analysis
of the source file since we cannot compile or run fd.zig functions directly.
"""

import re
from pathlib import Path

REPO = "/workspace/bun"
TARGET = Path(REPO) / "src" / "fd.zig"


def _extract_from_js_validated() -> str:
    """Extract fromJSValidated function body with comments stripped."""
    content = TARGET.read_text()
    match = re.search(
        r"fn fromJSValidated\b[^{]*\{(.*?)(?=\n    (?:pub )?fn |\n    \};|\Z)",
        content,
        re.DOTALL,
    )
    assert match, "fromJSValidated function not found in fd.zig"
    raw = match.group(1)
    lines = []
    for line in raw.split("\n"):
        if line.strip().startswith("//"):
            continue
        lines.append(re.sub(r"//.*$", "", line))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_fd_zig_structural_integrity():
    """fd.zig exists with FD packed struct and fromJSValidated function."""
    content = TARGET.read_text()
    assert "pub const FD = packed struct" in content
    assert "fn fromJSValidated" in content
    opens = content.count("{")
    closes = content.count("}")
    assert abs(opens - closes) <= 5, "Brace mismatch suggests broken structure"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_range_check_before_int_conversion():
    """Float range must be validated BEFORE @intFromFloat to prevent panic.

    The bug: @intFromFloat(float) panics when float exceeds i64 range (e.g.
    1e308). The fix: compare float against bounds BEFORE converting to int.
    """
    body = _extract_from_js_validated()
    lines = body.split("\n")

    range_check_line = None
    int_from_float_line = None

    for i, line in enumerate(lines):
        s = line.strip()
        if not s:
            continue
        if int_from_float_line is None and "@intFromFloat" in s:
            int_from_float_line = i
        if range_check_line is None and "@mod" not in s:
            has_float_cmp = bool(
                re.search(r"float\s*[<>=!]+\s*", s)
                or re.search(r"[<>=!]+\s*float", s)
            )
            has_math_check = bool(
                re.search(r"std\.math\.\w+\(float\)|isFinite|isNan|isInf", s)
            )
            if has_float_cmp or has_math_check:
                range_check_line = i

    assert int_from_float_line is not None, "@intFromFloat not found"
    assert range_check_line is not None, "No float range check found"
    assert range_check_line < int_from_float_line, (
        f"Range check (line {range_check_line}) must come before "
        f"@intFromFloat (line {int_from_float_line})"
    )


# [pr_diff] fail_to_pass
def test_error_path_before_conversion():
    """Out-of-range float must trigger throwRangeError before @intFromFloat."""
    body = _extract_from_js_validated()
    lines = body.split("\n")

    int_from_float_line = None
    for i, line in enumerate(lines):
        if "@intFromFloat" in line:
            int_from_float_line = i
            break

    assert int_from_float_line is not None, "@intFromFloat not found"
    pre = "\n".join(lines[:int_from_float_line])

    has_float_cmp = bool(
        re.search(r"float\s*[<>=!]+", pre)
        or re.search(r"[<>=!]+\s*float", pre)
        or re.search(r"(?:isFinite|isNan|isInf).*float", pre)
    )
    assert has_float_cmp, "No float comparison found before @intFromFloat"

    has_error = bool(
        re.search(
            r"throwRangeError|throwError|return\s+.*error|return\s+.*null|return\s+\.err",
            pre,
            re.IGNORECASE,
        )
    )
    assert has_error, "No error path (throwRangeError) found before @intFromFloat"


# [pr_diff] fail_to_pass
def test_both_positive_and_negative_overflow():
    """Range check must handle both positive AND negative out-of-range floats.

    A one-sided check (only < 0 or only > maxInt) leaves half the panic
    surface unfixed. Accepts: two comparisons, or/and combined, isFinite, etc.
    """
    body = _extract_from_js_validated()
    lines = body.split("\n")

    int_from_float_line = None
    for i, line in enumerate(lines):
        if "@intFromFloat" in line:
            int_from_float_line = i
            break

    assert int_from_float_line is not None, "@intFromFloat not found"
    pre = "\n".join(lines[:int_from_float_line])

    has_bilateral_math = bool(re.search(r"isFinite|isInf", pre))
    has_gt = bool(re.search(r"float\s*>\s*|<\s*float", pre))
    has_lt = bool(re.search(r"float\s*<\s*|>\s*float", pre))
    has_both_cmp = has_gt and has_lt
    has_or_combined = bool(
        re.search(r"float\s*[<>]=?\s*.*\bor\b.*float\s*[<>]=?", pre)
    )

    assert has_bilateral_math or has_both_cmp or has_or_combined, (
        "Range check must cover both positive and negative overflow"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_mod_check_preserved():
    """Non-integer float detection (@mod check) must still be present."""
    content = TARGET.read_text()
    assert "@mod(float, 1)" in content or "@mod(float, 1.0)" in content, (
        "@mod check for non-integer floats was removed"
    )


# [pr_diff] pass_to_pass
def test_int_from_float_still_used():
    """@intFromFloat must still be used for valid float-to-int conversion."""
    body = _extract_from_js_validated()
    assert "@intFromFloat" in body, "@intFromFloat removed from fromJSValidated"


# [static] pass_to_pass
def test_not_stub():
    """fromJSValidated must be substantive, not gutted to a stub."""
    body = _extract_from_js_validated()
    code_lines = [l for l in body.split("\n") if l.strip()]
    assert len(code_lines) >= 8, f"Function too short ({len(code_lines)} lines)"
    assert "throwRangeError" in body, "throwRangeError missing"
    assert "@intCast" in body, "@intCast missing"
    assert "@intFromFloat" in body, "@intFromFloat missing"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from src/CLAUDE.md
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — src/CLAUDE.md:11 @ 8f0fd0cf1da17fff23df7133e414cdd1f5ed917e
def test_no_inline_import():
    """No inline @import() inside fromJSValidated (src/CLAUDE.md:11)."""
    body = _extract_from_js_validated()
    assert "@import(" not in body, "Inline @import found in fromJSValidated"


# [agent_config] pass_to_pass — src/CLAUDE.md:16 @ 8f0fd0cf1da17fff23df7133e414cdd1f5ed917e
def test_no_forbidden_std_apis():
    """No forbidden std.* API usage in fromJSValidated (src/CLAUDE.md:16).

    std.math is exempted (numeric constants); std.fs, std.posix, std.os are
    forbidden per Bun convention.
    """
    body = _extract_from_js_validated()
    for forbidden in ["std.fs.", "std.posix.", "std.os."]:
        assert forbidden not in body, f"Forbidden API {forbidden} found"
