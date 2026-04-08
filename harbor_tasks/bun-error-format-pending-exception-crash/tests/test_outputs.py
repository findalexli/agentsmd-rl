"""
Task: bun-error-format-pending-exception-crash
Repo: oven-sh/bun @ f6528b58ed67c8fb8c80046114829d9ad79a292f
PR:   28488

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Note: Bun is a Zig/C++ runtime requiring full build toolchain (CMake, Zig compiler,
hours of compile). The Docker container has no Zig compiler or pre-built bun binary,
so f2p tests use subprocess to run a Python analyzer that parses Zig catch blocks with
brace-counting and verifies the fix structure.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = Path("/repo")
TARGET = REPO / "src/bun.js/bindings/JSGlobalObject.zig"

# ---------------------------------------------------------------------------
# Shared Zig analysis script — invoked via subprocess with fn name + optional
# typed-error method as positional args.  Outputs JSON to stdout.
# ---------------------------------------------------------------------------
_ANALYSIS_SCRIPT = r"""
import json, re, sys
from pathlib import Path

target = Path(sys.argv[1])
fn_name = sys.argv[2]
check_typed = sys.argv[3] if len(sys.argv) > 3 else None


def strip(code):
    # Remove // comments and string literals to prevent gaming.
    code = re.sub(r"//[^\n]*", "", code)
    code = re.sub(r'"(?:[^"\\]|\\.)*"', '""', code)
    return code


def find_fn(code, name, size=3000):
    # Extract a pub fn region bounded by the next pub fn or size chars.
    marker = f"pub fn {name}"
    idx = code.find(marker)
    if idx < 0:
        return None
    next_fn = code.find("pub fn ", idx + len(marker))
    end = min(idx + size, next_fn) if next_fn > 0 else idx + size
    return code[idx:end]


def catch_bodies(region):
    # Extract catch-block bodies using brace counting.
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


raw = target.read_text()
clean = strip(raw)
region = find_fn(clean, fn_name)

if region is None:
    print(json.dumps({"found": False}))
    sys.exit(0)

result = {"found": True, "catches": []}
for body in catch_bodies(region):
    clear = re.search(r"\.\s*clearExceptionExceptTermination\s*\(\s*\)", body)
    ret = re.search(r"\breturn\b", body)
    entry = {
        "has_clear": clear is not None,
        "clear_before_return": (clear.start() < ret.start()) if (clear and ret) else False,
    }
    if check_typed and ret:
        after = body[ret.start() :]
        entry["typed_return"] = bool(re.search(r"\." + check_typed + r"\s*\(", after))
        entry["generic_return"] = ".toErrorInstance(" in after
    result["catches"].append(entry)

print(json.dumps(result))
"""


def _analyze_fn(fn_name: str, check_typed: str | None = None) -> dict:
    """Run the Zig-source analyzer in a subprocess and return parsed JSON."""
    script = REPO / "_eval_check.py"
    try:
        script.write_text(_ANALYSIS_SCRIPT)
        args = ["python3", str(script), str(TARGET), fn_name]
        if check_typed:
            args.append(check_typed)
        r = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(REPO),
        )
        assert r.returncode == 0, f"Analysis script failed: {r.stderr}"
        return json.loads(r.stdout.strip())
    finally:
        script.unlink(missing_ok=True)


def _first_clearing_catch(result: dict) -> dict | None:
    """Return the first catch entry that has clear_before_return, or None."""
    for c in result.get("catches", []):
        if c.get("clear_before_return"):
            return c
    return None


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — subprocess-based Zig analysis
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_create_error_instance_clears_exception():
    """createErrorInstance catch must call clearExceptionExceptTermination before return."""
    result = _analyze_fn("createErrorInstance")
    assert result["found"], "createErrorInstance function not found"
    assert _first_clearing_catch(result) is not None, (
        "createErrorInstance catch block does not call "
        ".clearExceptionExceptTermination() before return"
    )


# [pr_diff] fail_to_pass
def test_create_type_error_clears_and_returns_typed():
    """createTypeErrorInstance catch must clear exception and return TypeError (not generic Error)."""
    result = _analyze_fn("createTypeErrorInstance", check_typed="toTypeErrorInstance")
    assert result["found"], "createTypeErrorInstance function not found"
    c = _first_clearing_catch(result)
    assert c is not None, "createTypeErrorInstance catch does not clear exception before return"
    assert c.get("typed_return"), (
        "createTypeErrorInstance catch does not return toTypeErrorInstance"
    )
    assert not c.get("generic_return"), (
        "createTypeErrorInstance catch still returns generic toErrorInstance"
    )


# [pr_diff] fail_to_pass
def test_create_syntax_error_clears_and_returns_typed():
    """createSyntaxErrorInstance catch must clear exception and return SyntaxError."""
    result = _analyze_fn("createSyntaxErrorInstance", check_typed="toSyntaxErrorInstance")
    assert result["found"], "createSyntaxErrorInstance function not found"
    c = _first_clearing_catch(result)
    assert c is not None, "createSyntaxErrorInstance catch does not clear exception before return"
    assert c.get("typed_return"), (
        "createSyntaxErrorInstance catch does not return toSyntaxErrorInstance"
    )
    assert not c.get("generic_return"), (
        "createSyntaxErrorInstance catch still returns generic toErrorInstance"
    )


# [pr_diff] fail_to_pass
def test_create_range_error_clears_and_returns_typed():
    """createRangeErrorInstance catch must clear exception and return RangeError."""
    result = _analyze_fn("createRangeErrorInstance", check_typed="toRangeErrorInstance")
    assert result["found"], "createRangeErrorInstance function not found"
    c = _first_clearing_catch(result)
    assert c is not None, "createRangeErrorInstance catch does not clear exception before return"
    assert c.get("typed_return"), (
        "createRangeErrorInstance catch does not return toRangeErrorInstance"
    )
    assert not c.get("generic_return"), (
        "createRangeErrorInstance catch still returns generic toErrorInstance"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass — regression + anti-stub
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_dom_exception_not_modified():
    """createDOMExceptionInstance must NOT gain clearExceptionExceptTermination."""
    result = _analyze_fn("createDOMExceptionInstance")
    if not result["found"]:
        return  # Function doesn't exist, nothing to check
    has_clear = any(c.get("has_clear") for c in result.get("catches", []))
    assert not has_clear, (
        "createDOMExceptionInstance should not have clearExceptionExceptTermination"
    )


# [static] pass_to_pass
def test_file_not_stubbed():
    """Target file must retain substantial content (not gutted)."""
    assert TARGET.exists(), "Target file does not exist"
    line_count = len(TARGET.read_text().splitlines())
    assert line_count > 200, f"File appears stubbed ({line_count} lines)"


# [static] pass_to_pass
def test_all_four_functions_exist():
    """All four create*ErrorInstance functions must still exist."""
    raw = TARGET.read_text()
    for fn in [
        "createErrorInstance",
        "createTypeErrorInstance",
        "createSyntaxErrorInstance",
        "createRangeErrorInstance",
    ]:
        assert f"pub fn {fn}" in raw, f"{fn} not found in target file"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from src/CLAUDE.md
# ---------------------------------------------------------------------------


def _strip_comments_and_strings(code: str) -> str:
    """Remove Zig // comments and string literals."""
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


# [agent_config] pass_to_pass — src/CLAUDE.md:11 @ f6528b58ed67c8fb8c80046114829d9ad79a292f
def test_no_inline_imports_in_error_functions():
    """No @import() calls inside the four create*ErrorInstance function bodies."""
    # Rule: "Never use @import() inline inside of functions."
    raw = TARGET.read_text()
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
    # Rule: "Always use bun.* APIs instead of std.*. Using std.fs, std.posix, or std.os directly is wrong."
    clean = _strip_comments_and_strings(TARGET.read_text())
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
    # Rule: "bun.handleOom(expr) converts error.OutOfMemory into a crash without swallowing other errors"
    clean = _strip_comments_and_strings(TARGET.read_text())
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
