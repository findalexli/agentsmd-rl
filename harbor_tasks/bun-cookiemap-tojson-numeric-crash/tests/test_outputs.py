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
from pathlib import Path

REPO = "/workspace/bun"
FILE = Path(REPO) / "src/bun.js/bindings/CookieMap.cpp"


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
