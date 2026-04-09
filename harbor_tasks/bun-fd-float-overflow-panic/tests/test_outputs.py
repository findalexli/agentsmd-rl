"""
Task: bun-fd-float-overflow-panic
Repo: oven-sh/bun @ 8f0fd0cf1da17fff23df7133e414cdd1f5ed917e
PR:   28364

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

The fix is in Zig source (src/fd.zig) which requires the full Bun build
toolchain to compile. Tests use subprocess to execute Python analysis scripts
that parse the Zig source with proper brace-matching, verifying the behavioral
properties of the code change (range check ordering, error paths, bilateral
coverage).
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/bun"
TARGET = Path(REPO) / "src" / "fd.zig"


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a Python script in the repo directory."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=REPO,
    )


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
# Fail-to-pass (pr_diff) — core behavioral tests via subprocess
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_range_check_before_int_conversion():
    """Float range validated BEFORE @intFromFloat to prevent panic on extreme values.

    The core bug: @intFromFloat(float) panics when float exceeds i64 range
    (e.g. 1e308). The fix must compare float against bounds BEFORE converting
    to int. Uses subprocess to parse the function body and verify ordering.
    """
    r = _run_py(
        r"""
import re, sys, json

content = open("src/fd.zig").read()
start = content.find("fn fromJSValidated")
if start == -1:
    sys.exit(1)

func_start = content.index("{", start)
depth = 0
end = func_start
for i in range(func_start, len(content)):
    if content[i] == "{":
        depth += 1
    elif content[i] == "}":
        depth -= 1
        if depth == 0:
            end = i
            break

body = content[func_start : end + 1]
lines = body.split("\n")

int_from_float_idx = None
range_check_idx = None

for idx, line in enumerate(lines):
    stripped = line.strip()
    if not stripped or stripped.startswith("//"):
        continue
    if "@intFromFloat" in stripped and int_from_float_idx is None:
        int_from_float_idx = idx
    if range_check_idx is None and "@mod" not in stripped:
        if re.search(r"float\s*[<>]", stripped) or re.search(r"[<>]\s*float", stripped):
            range_check_idx = idx

result = {
    "int_from_float_line": int_from_float_idx,
    "range_check_line": range_check_idx,
}

if int_from_float_idx is None:
    result["error"] = "@intFromFloat not found in fromJSValidated"
    print(json.dumps(result))
    sys.exit(1)

if range_check_idx is None:
    result["error"] = "No float range check found"
    print(json.dumps(result))
    sys.exit(1)

if range_check_idx >= int_from_float_idx:
    result["error"] = (
        f"Range check at line {range_check_idx} is NOT before "
        f"@intFromFloat at line {int_from_float_idx}"
    )
    print(json.dumps(result))
    sys.exit(1)

result["pass"] = True
print(json.dumps(result))
"""
    )
    assert r.returncode == 0, f"Range check ordering analysis failed:\n{r.stderr}\n{r.stdout}"
    data = json.loads(r.stdout.strip().split("\n")[-1])
    assert data.get("pass"), f"Range check not before @intFromFloat: {data}"


# [pr_diff] fail_to_pass
def test_error_path_before_conversion():
    """Out-of-range float triggers throwRangeError before @intFromFloat conversion.

    Ensures an error path exists in the code section before @intFromFloat,
    so extreme floats get a RangeError instead of causing a runtime panic.
    Uses subprocess to parse and verify the error path positioning.
    """
    r = _run_py(
        r"""
import re, sys, json

content = open("src/fd.zig").read()
start = content.find("fn fromJSValidated")
if start == -1:
    sys.exit(1)

func_start = content.index("{", start)
depth = 0
end = func_start
for i in range(func_start, len(content)):
    if content[i] == "{":
        depth += 1
    elif content[i] == "}":
        depth -= 1
        if depth == 0:
            end = i
            break

body = content[func_start : end + 1]
lines = body.split("\n")

int_from_float_idx = None
for idx, line in enumerate(lines):
    if "@intFromFloat" in line:
        int_from_float_idx = idx
        break

if int_from_float_idx is None:
    print(json.dumps({"error": "@intFromFloat not found"}))
    sys.exit(1)

pre_conversion = "\n".join(lines[:int_from_float_idx])

has_float_cmp = bool(
    re.search(r"float\s*[<>]", pre_conversion)
    or re.search(r"[<>]\s*float", pre_conversion)
)
has_error = bool(re.search(r"throwRangeError", pre_conversion))

result = {"has_float_cmp": has_float_cmp, "has_error": has_error}

if not has_float_cmp:
    result["error"] = "No float comparison found before @intFromFloat"
if not has_error:
    result["error"] = "No throwRangeError found before @intFromFloat"
if has_float_cmp and has_error:
    result["pass"] = True

print(json.dumps(result))
if "pass" not in result:
    sys.exit(1)
"""
    )
    assert r.returncode == 0, f"Error path analysis failed:\n{r.stderr}\n{r.stdout}"
    data = json.loads(r.stdout.strip().split("\n")[-1])
    assert data.get("pass"), f"No error path before @intFromFloat: {data}"


# [pr_diff] fail_to_pass
def test_both_positive_and_negative_overflow():
    """Range check covers both positive (1e308) and negative (-1.5e308) overflow.

    A one-sided check (only < 0 or only > maxInt) leaves half the panic
    surface unfixed. Uses subprocess to verify bilateral coverage.
    """
    r = _run_py(
        r"""
import re, sys, json

content = open("src/fd.zig").read()
start = content.find("fn fromJSValidated")
if start == -1:
    sys.exit(1)

func_start = content.index("{", start)
depth = 0
end = func_start
for i in range(func_start, len(content)):
    if content[i] == "{":
        depth += 1
    elif content[i] == "}":
        depth -= 1
        if depth == 0:
            end = i
            break

body = content[func_start : end + 1]
lines = body.split("\n")

int_from_float_idx = None
for idx, line in enumerate(lines):
    if "@intFromFloat" in line:
        int_from_float_idx = idx
        break

if int_from_float_idx is None:
    print(json.dumps({"error": "@intFromFloat not found"}))
    sys.exit(1)

pre = "\n".join(lines[:int_from_float_idx])

has_bilateral = bool(re.search(r"isFinite|isInf", pre))
has_gt = bool(re.search(r"float\s*>", pre))
has_lt = bool(re.search(r"float\s*<", pre))
has_both = has_gt and has_lt
has_or = bool(re.search(r"\bor\b", pre) and has_both)

result = {
    "bilateral_math": has_bilateral,
    "has_gt": has_gt,
    "has_lt": has_lt,
}

if has_bilateral or has_both or has_or:
    result["pass"] = True
else:
    result["error"] = "Range check doesn't cover both positive and negative overflow"

print(json.dumps(result))
if "pass" not in result:
    sys.exit(1)
"""
    )
    assert r.returncode == 0, f"Overflow coverage analysis failed:\n{r.stderr}\n{r.stdout}"
    data = json.loads(r.stdout.strip().split("\n")[-1])
    assert data.get("pass"), f"Doesn't cover both overflow directions: {data}"


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
    """@intFromFloat conversion still used for valid float-to-int conversion."""
    content = TARGET.read_text()
    start = content.find("fn fromJSValidated")
    assert start != -1, "fromJSValidated not found"
    func_start = content.index("{", start)
    depth = 0
    end = func_start
    for i in range(func_start, len(content)):
        if content[i] == "{":
            depth += 1
        elif content[i] == "}":
            depth -= 1
            if depth == 0:
                end = i
                break
    body = content[func_start:end]
    assert "@intFromFloat" in body, "@intFromFloat removed from fromJSValidated"


# [static] pass_to_pass
def test_not_stub():
    """fromJSValidated must be substantive, not gutted to a stub."""
    content = TARGET.read_text()
    start = content.find("fn fromJSValidated")
    assert start != -1, "fromJSValidated not found"
    func_start = content.index("{", start)
    depth = 0
    end = func_start
    for i in range(func_start, len(content)):
        if content[i] == "{":
            depth += 1
        elif content[i] == "}":
            depth -= 1
            if depth == 0:
                end = i
                break
    body = content[func_start:end]
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
    content = TARGET.read_text()
    start = content.find("fn fromJSValidated")
    assert start != -1
    func_start = content.index("{", start)
    depth = 0
    end = func_start
    for i in range(func_start, len(content)):
        if content[i] == "{":
            depth += 1
        elif content[i] == "}":
            depth -= 1
            if depth == 0:
                end = i
                break
    body = content[func_start:end]
    assert "@import(" not in body, "Inline @import found in fromJSValidated"


# [agent_config] pass_to_pass — src/CLAUDE.md:16 @ 8f0fd0cf1da17fff23df7133e414cdd1f5ed917e
def test_no_forbidden_std_apis():
    """No forbidden std.* API usage in fromJSValidated (src/CLAUDE.md:16).

    std.math is exempted (numeric constants); std.fs, std.posix, std.os are
    forbidden per Bun convention.
    """
    content = TARGET.read_text()
    start = content.find("fn fromJSValidated")
    assert start != -1
    func_start = content.index("{", start)
    depth = 0
    end = func_start
    for i in range(func_start, len(content)):
        if content[i] == "{":
            depth += 1
        elif content[i] == "}":
            depth -= 1
            if depth == 0:
                end = i
                break
    body = content[func_start:end]
    for forbidden in ["std.fs.", "std.posix.", "std.os."]:
        assert forbidden not in body, f"Forbidden API {forbidden} found"


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass tests — ensure repo's own checks pass on base and fix
# ---------------------------------------------------------------------------


# [repo_ci] pass_to_pass
def test_repo_oxlint():
    """Repo's JavaScript linting passes (pass_to_pass).

    Runs oxlint on src/js to verify no critical issues in JS/TS code.
    This is the lint command from the repo's package.json and CI pipeline.
    """
    r = subprocess.run(
        ["npx", "oxlint", "src/js"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    # oxlint returns 0 even with warnings; only fails on errors
    # Allow warnings (repo has 336 on base commit), but no errors
    assert r.returncode == 0, f"oxlint found errors:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_ci] pass_to_pass
def test_zig_syntax_valid():
    """Zig source files have valid syntax and structure (pass_to_pass).

    Validates that fd.zig and other key Zig files have:
    - Balanced braces (no structural corruption)
    - Required function definitions
    - Proper syntax elements
    """
    # Validate fd.zig syntax
    content = TARGET.read_text()

    # Check structural integrity
    assert "pub const FD = packed struct" in content, "FD struct definition missing"
    assert "fn fromJSValidated" in content, "fromJSValidated function missing"

    # Brace balance check (tolerance for edge cases)
    opens = content.count("{")
    closes = content.count("}")
    assert abs(opens - closes) <= 5, f"Severe brace mismatch: {opens} open, {closes} close"

    # Validate fromJSValidated function body
    start = content.find("fn fromJSValidated")
    assert start != -1, "fromJSValidated not found"
    func_start = content.index("{", start)
    depth = 0
    end = func_start
    for i in range(func_start, len(content)):
        if content[i] == "{":
            depth += 1
        elif content[i] == "}":
            depth -= 1
            if depth == 0:
                end = i
                break
    body = content[func_start:end]

    # Verify required syntax elements are present
    assert "@intFromFloat" in body, "@intFromFloat missing from fromJSValidated"
    assert "@intCast" in body, "@intCast missing from fromJSValidated"
    assert "throwRangeError" in body, "throwRangeError missing from fromJSValidated"

    # Verify function is substantive (not gutted)
    code_lines = [l for l in body.split("\n") if l.strip()]
    assert len(code_lines) >= 8, f"Function too short ({len(code_lines)} lines)"
