"""
Task: bun-cookiemap-tojson-numeric-crash
Repo: oven-sh/bun @ 581d45c267edeeeba53595f1663d73a8d90dec4e
PR:   28314

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Note: This is a C++ codebase (Bun runtime) that requires the Zig compiler
and a complex build system to compile. Tests verify the source-level fix
by executing Python analysis scripts via subprocess.
"""

import subprocess
import re
import pytest
from pathlib import Path

REPO = "/workspace/bun"
FILE = Path(REPO) / "src/bun.js/bindings/CookieMap.cpp"


# Banned words patterns from test/internal/ban-words.test.ts
# These are patterns that should not appear in new/modified code
BANNED_PATTERNS_CPP = {
    # C++ / JSC binding anti-patterns
    "global.hasException": "Incompatible with strict exception checks. Use a CatchScope instead.",
    "globalObject.hasException": "Incompatible with strict exception checks. Use a CatchScope instead.",
    "globalThis.hasException": "Incompatible with strict exception checks. Use a CatchScope instead.",
    "EXCEPTION_ASSERT(!scope.exception())": "Use scope.assertNoException() instead",
}


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a Python analysis script via subprocess."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — subprocess-executed code analysis
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_no_bare_putdirect_in_tojson():
    """toJSON must not use bare putDirect — crashes on numeric cookie names.
    Must use an index-safe variant like putDirectMayBeIndex, putDirectIndex,
    putByIndex, put, or defineOwnProperty."""
    r = _run_py(
        'import re, sys\n'
        'from pathlib import Path\n'
        'text = Path("' + str(FILE) + '").read_text()\n'
        'm = re.search(r"CookieMap::toJSON\\b[^{]*\\{", text)\n'
        'if not m:\n'
        '    print("FAIL:toJSON_not_found")\n'
        '    sys.exit(0)\n'
        'start = m.end()\n'
        'depth = 1\n'
        'i = start\n'
        'while i < len(text) and depth > 0:\n'
        '    if text[i] == "{": depth += 1\n'
        '    elif text[i] == "}": depth -= 1\n'
        '    i += 1\n'
        'body = text[start:i-1]\n'
        'bare = re.findall(r"->putDirect\\s*\\(", body)\n'
        'if bare:\n'
        '    print(f"FAIL:bare_putdirect:{len(bare)}")\n'
        '    sys.exit(0)\n'
        'safe = re.findall(r"->(?:putDirectMayBeIndex|putDirectIndex|putByIndex|put|defineOwnProperty)\\s*\\(", body)\n'
        'if not safe:\n'
        '    print("FAIL:no_safe_variant")\n'
        '    sys.exit(0)\n'
        'print("PASS")\n'
    )
    assert r.returncode == 0, f"Script error: {r.stderr}"
    assert "PASS" in r.stdout, f"Unsafe putDirect in toJSON: {r.stdout.strip()}"


# [pr_diff] fail_to_pass
def test_all_insertion_paths_safe():
    """Both modified-cookie and original-cookie loops must use index-safe
    property insertion. Accepts: two safe calls, or one call in a merged loop."""
    r = _run_py(
        'import re, sys\n'
        'from pathlib import Path\n'
        'text = Path("' + str(FILE) + '").read_text()\n'
        'm = re.search(r"CookieMap::toJSON\\b[^{]*\\{", text)\n'
        'if not m:\n'
        '    print("FAIL:toJSON_not_found")\n'
        '    sys.exit(0)\n'
        'start = m.end()\n'
        'depth = 1\n'
        'i = start\n'
        'while i < len(text) and depth > 0:\n'
        '    if text[i] == "{": depth += 1\n'
        '    elif text[i] == "}": depth -= 1\n'
        '    i += 1\n'
        'body = text[start:i-1]\n'
        'all_puts = re.findall(r"->(putDirect\\w*|putByIndex|put|defineOwnProperty)\\s*\\(", body)\n'
        'unsafe = [p for p in all_puts if p == "putDirect"]\n'
        'safe = [p for p in all_puts if p in ("putDirectMayBeIndex", "putDirectIndex", "putByIndex", "put", "defineOwnProperty")]\n'
        'if unsafe:\n'
        '    print(f"FAIL:unsafe_calls:{unsafe}")\n'
        '    sys.exit(0)\n'
        'if len(safe) >= 2:\n'
        '    print("PASS")\n'
        '    sys.exit(0)\n'
        'if len(safe) == 1:\n'
        '    if re.search(r"\\bfor\\s*\\(|\\bwhile\\s*\\(", body):\n'
        '        print("PASS")\n'
        '        sys.exit(0)\n'
        '    print("FAIL:single_safe_no_loop")\n'
        '    sys.exit(0)\n'
        'print("FAIL:no_insertion_calls")\n'
    )
    assert r.returncode == 0, f"Script error: {r.stderr}"
    assert "PASS" in r.stdout, f"Not all insertion paths safe: {r.stdout.strip()}"


# [pr_diff] fail_to_pass
def test_dedup_avoids_hasproperty():
    """Deduplication must not call hasProperty on the JSObject (also crashes
    on numeric keys). Accept: HashSet tracking, restructured iteration, or
    any approach that avoids hasProperty on the result object."""
    r = _run_py(
        'import re, sys\n'
        'from pathlib import Path\n'
        'text = Path("' + str(FILE) + '").read_text()\n'
        'm = re.search(r"CookieMap::toJSON\\b[^{]*\\{", text)\n'
        'if not m:\n'
        '    print("FAIL:toJSON_not_found")\n'
        '    sys.exit(0)\n'
        'start = m.end()\n'
        'depth = 1\n'
        'i = start\n'
        'while i < len(text) and depth > 0:\n'
        '    if text[i] == "{": depth += 1\n'
        '    elif text[i] == "}": depth -= 1\n'
        '    i += 1\n'
        'body = text[start:i-1]\n'
        'has_prop = re.findall(r"->hasProperty\\s*\\(", body)\n'
        'if not has_prop:\n'
        '    print("PASS")\n'
        '    sys.exit(0)\n'
        'if re.search(r"HashSet|std::set|std::unordered_set|WTF::HashSet|std::unordered_map", body):\n'
        '    print("PASS")\n'
        '    sys.exit(0)\n'
        'print("FAIL:hasproperty_without_tracking")\n'
    )
    assert r.returncode == 0, f"Script error: {r.stderr}"
    assert "PASS" in r.stdout, (
        f"hasProperty without native tracking: {r.stdout.strip()}"
    )


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
    text = FILE.read_text()
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


# [agent_config] pass_to_pass — .claude/skills/implementing-jsc-classes-cpp/SKILL.md:94-101 @ 581d45c2
def test_exception_scope_in_tojson():
    """toJSON must use JSC exception scope pattern (DECLARE_THROW_SCOPE or
    RELEASE_AND_RETURN) — required for all JSC binding functions."""
    body = _read_tojson_body()
    assert re.search(r"DECLARE_THROW_SCOPE|RELEASE_AND_RETURN", body), (
        "toJSON must declare a JSC throw scope — required pattern for bindings code"
    )


# ---------------------------------------------------------------------------
# Helpers for p2p tests
# ---------------------------------------------------------------------------


def _read_tojson_body() -> str:
    """Extract the body of CookieMap::toJSON method."""
    text = FILE.read_text()
    m = re.search(r"CookieMap::toJSON\b[^{]*\{", text)
    assert m, "CookieMap::toJSON method not found in CookieMap.cpp"
    start = m.end()
    depth = 1
    i = start
    while i < len(text) and depth > 0:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1
    return text[start : i - 1]


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks from the repository
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
# Origin: bun repo CI checks for C++ code quality
# The repo has banned patterns (see test/internal/ban-words.test.ts) that
# should not be introduced in new code.
def test_cookiemap_no_banned_patterns():
    """CookieMap.cpp must not contain banned C++ anti-patterns.
    This is a pass-to-pass check from the repo's CI (pass_to_pass)."""
    text = FILE.read_text()

    banned_found = []
    for pattern, reason in BANNED_PATTERNS_CPP.items():
        if pattern in text:
            banned_found.append(f"{pattern}: {reason}")

    assert not banned_found, (
        f"Banned patterns found in CookieMap.cpp:\n" +
        "\n".join(banned_found)
    )


# [repo_tests] pass_to_pass
# Origin: bun repo CI checks for file structure
# Verifies the file structure is intact and follows conventions.
def test_cookiemap_file_structure():
    """CookieMap.cpp must have proper structure: includes, namespace,
    class definition with expected methods (pass_to_pass)."""
    text = FILE.read_text()

    # Check essential includes
    assert "#include" in text, "CookieMap.cpp missing #include statements"

    # Check namespace
    assert "namespace WebCore" in text, "CookieMap.cpp missing WebCore namespace"

    # Check class definition exists
    assert "class CookieMap" in text or "CookieMap::" in text, (
        "CookieMap class definition or method implementations not found"
    )

    # Check toJSON method exists (the method being fixed)
    assert "CookieMap::toJSON" in text, "CookieMap::toJSON method not found"


# [repo_tests] pass_to_pass
# Origin: bun repo format CI workflow (.github/workflows/format.yml)
# The repo has a .clang-format file and requires C++ files to follow it.
def test_cookiemap_clang_format():
    """CookieMap.cpp must follow the repo's C++ formatting style (pass_to_pass).
    Uses clang-format --dry-run if available, otherwise skips gracefully."""
    # Check if clang-format is available
    r = subprocess.run(
        ["which", "clang-format"],
        capture_output=True,
        timeout=5,
    )
    if r.returncode != 0:
        # Try versioned clang-format
        r = subprocess.run(
            ["which", "clang-format-19"],
            capture_output=True,
            timeout=5,
        )
        if r.returncode != 0:
            pytest.skip("clang-format not available in environment")
            return
        clang_format = "clang-format-19"
    else:
        clang_format = "clang-format"

    # Run clang-format check on CookieMap.cpp
    r = subprocess.run(
        [clang_format, "--dry-run", "--Werror", str(FILE)],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )

    # If it fails due to version issues, check the error message
    if r.returncode != 0:
        # Some versions don't support --Werror, try alternative
        r2 = subprocess.run(
            [clang_format, "--dry-run", str(FILE)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=REPO,
        )
        # Check if there are any formatting differences reported
        if "Formatting" in r2.stderr or "code should be" in r2.stderr.lower():
            assert False, f"CookieMap.cpp needs formatting:\n{r2.stderr[:500]}"


# [repo_tests] pass_to_pass
# Origin: bun repo source file conventions (see src/.clang-format)
# Verifies basic C++ syntax validity of the modified file.
def test_cookiemap_cpp_syntax_valid():
    """CookieMap.cpp must have valid C++ syntax (basic checks) (pass_to_pass).
    Checks for balanced braces and valid structure."""
    text = FILE.read_text()

    # Check for balanced braces
    open_count = text.count("{")
    close_count = text.count("}")
    assert open_count == close_count, (
        f"Unbalanced braces: {open_count} open, {close_count} close"
    )

    # Check for balanced parentheses
    open_paren = text.count("(")
    close_paren = text.count(")")
    assert open_paren == close_paren, (
        f"Unbalanced parentheses: {open_paren} open, {close_paren} close"
    )

    # Check for basic C++ file markers
    assert "//" in text or "/*" in text or "#include" in text, (
        "File appears to lack C++ structure (comments or includes)"
    )
