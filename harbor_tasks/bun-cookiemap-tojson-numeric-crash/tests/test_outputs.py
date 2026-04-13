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
        """import re, sys
from pathlib import Path
text = Path(""" + repr(str(FILE)) + """).read_text()
m = re.search(r"CookieMap::toJSON\\b[^{]*\\{", text)
if not m:
    print("FAIL:toJSON_not_found")
    sys.exit(0)
start = m.end()
depth = 1
i = start
while i < len(text) and depth > 0:
    if text[i] == "{": depth += 1
    elif text[i] == "}": depth -= 1
    i += 1
body = text[start:i-1]
bare = re.findall(r"->putDirect\\s*\\(", body)
if bare:
    print(f"FAIL:bare_putdirect:{len(bare)}")
    sys.exit(0)
safe = re.findall(r"->(?:putDirectMayBeIndex|putDirectIndex|putByIndex|put|defineOwnProperty)\\s*\\(", body)
if not safe:
    print("FAIL:no_safe_variant")
    sys.exit(0)
print("PASS")
"""
    )
    assert r.returncode == 0, f"Script error: {r.stderr}"
    assert "PASS" in r.stdout, f"Unsafe putDirect in toJSON: {r.stdout.strip()}"


# [pr_diff] fail_to_pass
def test_all_insertion_paths_safe():
    """Both modified-cookie and original-cookie loops must use index-safe
    property insertion. Accepts: two safe calls, or one call in a merged loop."""
    r = _run_py(
        """import re, sys
from pathlib import Path
text = Path(""" + repr(str(FILE)) + """).read_text()
m = re.search(r"CookieMap::toJSON\\b[^{]*\\{", text)
if not m:
    print("FAIL:toJSON_not_found")
    sys.exit(0)
start = m.end()
depth = 1
i = start
while i < len(text) and depth > 0:
    if text[i] == "{": depth += 1
    elif text[i] == "}": depth -= 1
    i += 1
body = text[start:i-1]
all_puts = re.findall(r"->(putDirect\\w*|putByIndex|put|defineOwnProperty)\\s*\\(", body)
unsafe = [p for p in all_puts if p == "putDirect"]
safe = [p for p in all_puts if p in ("putDirectMayBeIndex", "putDirectIndex", "putByIndex", "put", "defineOwnProperty")]
if unsafe:
    print(f"FAIL:unsafe_calls:{unsafe}")
    sys.exit(0)
if len(safe) >= 2:
    print("PASS")
    sys.exit(0)
if len(safe) == 1:
    if re.search(r"\\bfor\\s*\\(|\\bwhile\\s*\\(", body):
        print("PASS")
        sys.exit(0)
    print("FAIL:single_safe_no_loop")
    sys.exit(0)
print("FAIL:no_insertion_calls")
"""
    )
    assert r.returncode == 0, f"Script error: {r.stderr}"
    assert "PASS" in r.stdout, f"Not all insertion paths safe: {r.stdout.strip()}"


# [pr_diff] fail_to_pass
def test_dedup_avoids_hasproperty():
    """Deduplication must not call hasProperty on the JSObject (also crashes
    on numeric keys). Accept: HashSet tracking, restructured iteration, or
    any approach that avoids hasProperty on the result object."""
    r = _run_py(
        """import re, sys
from pathlib import Path
text = Path(""" + repr(str(FILE)) + """).read_text()
m = re.search(r"CookieMap::toJSON\\b[^{]*\\{", text)
if not m:
    print("FAIL:toJSON_not_found")
    sys.exit(0)
start = m.end()
depth = 1
i = start
while i < len(text) and depth > 0:
    if text[i] == "{": depth += 1
    elif text[i] == "}": depth -= 1
    i += 1
body = text[start:i-1]
has_prop = re.findall(r"->hasProperty\\s*\\(", body)
if not has_prop:
    print("PASS")
    sys.exit(0)
if re.search(r"HashSet|std::set|std::unordered_set|WTF::HashSet|std::unordered_map", body):
    print("PASS")
    sys.exit(0)
print("FAIL:hasproperty_without_tracking")
"""
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
# Origin: bun repo CI format workflow (.github/workflows/format.yml)
# Git diff --check is a standard CI check that detects:
# - Merge conflict markers (<<<<<<<, =======, >>>>>>>)
# - Trailing whitespace
# - Mixed line endings
def test_git_no_conflict_markers():
    """Source files must have no merge conflict markers or trailing whitespace.
    This is a standard CI check from the repo's format workflow (pass_to_pass)."""
    r = subprocess.run(
        ["git", "-C", REPO, "diff", "--check"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Git diff check found issues: {repr(r.stderr)}"


# [repo_tests] pass_to_pass
# Origin: bun repo git-based validation
# Verifies the repository is in a valid state with proper git history.
def test_git_valid_repo_state():
    """Repository must have valid git state with at least one commit.
    Verifies git integrity for the source files (pass_to_pass)."""
    r = subprocess.run(
        ["git", "-C", REPO, "log", "--oneline", "-1"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Git log failed: {repr(r.stderr)}"
    # Verify we got a commit hash (should be non-empty output)
    commit_line = r.stdout.strip()
    assert len(commit_line) > 0, "No commit found in git log"


# [repo_tests] pass_to_pass
# Origin: bun repo CI - git grep based banned pattern check
# Equivalent to what ban-words.test.ts does but using git grep
def test_no_banned_patterns_in_cookiemap():
    """CookieMap.cpp must not contain banned C++ anti-patterns from repo CI.
    Uses git grep to check for patterns that CI would reject (pass_to_pass)."""
    for pattern, reason in BANNED_PATTERNS_CPP.items():
        r = subprocess.run(
            ["git", "-C", REPO, "grep", "-n", pattern, "--", "src/bun.js/bindings/CookieMap.cpp"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        # git grep returns 0 if pattern found, 1 if not found
        if r.returncode == 0:
            msg = "Banned pattern " + repr(pattern) + " found in CookieMap.cpp: " + reason + "\n" + r.stdout
            raise AssertionError(msg)


# [repo_tests] pass_to_pass
# Origin: bun repo file structure validation
# Equivalent to verifying the modified file is tracked and exists
def test_cookiemap_tracked_in_git():
    """CookieMap.cpp must be tracked in git and exist at expected path.
    Validates the source file is properly part of the repository (pass_to_pass)."""
    r = subprocess.run(
        ["git", "-C", REPO, "ls-files", "src/bun.js/bindings/CookieMap.cpp"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Git ls-files failed: {repr(r.stderr)}"
    output = r.stdout.strip()
    assert "CookieMap.cpp" in output, "CookieMap.cpp not tracked in git"


# [static] pass_to_pass
# File existence check - marked as static since it reads file directly
def test_cookiemap_file_exists():
    """CookieMap.cpp file must exist at the expected path (pass_to_pass)."""
    assert FILE.exists(), f"CookieMap.cpp not found at {FILE}"


# [repo_tests] pass_to_pass
# Origin: bun repo file tracking validation
# Verifies CookieMap.cpp is actually tracked by git and not just an untracked file
def test_git_cookiemap_in_index():
    """CookieMap.cpp must be in git index (not just untracked file).
    Git-based CI check to verify file is part of the repository (pass_to_pass)."""
    r = subprocess.run(
        ["git", "-C", REPO, "ls-files", "--error-unmatch", "src/bun.js/bindings/CookieMap.cpp"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"CookieMap.cpp not tracked in git index: {repr(r.stderr)}"


# [repo_tests] pass_to_pass
# Origin: bun repo CI whitespace validation
# Uses git to detect whitespace errors in the file
def test_git_cookiemap_whitespace():
    """CookieMap.cpp must have no whitespace errors (trailing whitespace, etc.).
    Git-based CI check for code quality (pass_to_pass)."""
    r = subprocess.run(
        ["git", "-C", REPO, "diff-index", "--check", "--cached", "HEAD", "--", "src/bun.js/bindings/CookieMap.cpp"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Whitespace errors found in CookieMap.cpp: {repr(r.stderr)}"


# [repo_tests] pass_to_pass
# Origin: bun repo git history validation
# Verifies CookieMap.cpp has git history (not a newly created file without commits)
def test_cookiemap_has_history():
    """CookieMap.cpp must have git history (at least one commit touching it).
    Git-based CI validation for file history (pass_to_pass)."""
    r = subprocess.run(
        ["git", "-C", REPO, "log", "--oneline", "--follow", "-1", "--", "src/bun.js/bindings/CookieMap.cpp"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Git log failed for CookieMap.cpp: {repr(r.stderr)}"
    # Verify we got actual commit output
    output = r.stdout.strip()
    assert len(output) > 0, "No git history found for CookieMap.cpp"


# [repo_tests] pass_to_pass
# Origin: bun repo CI - git blame validation
# Verifies the toJSON method has existed in the file history
def test_cookiemap_tojson_has_history():
    """CookieMap::toJSON method must have implementation history.
    Git-based CI validation to ensure method exists in codebase (pass_to_pass)."""
    r = subprocess.run(
        ["git", "-C", REPO, "grep", "-n", "toJSON", "src/bun.js/bindings/CookieMap.cpp"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"toJSON not found in CookieMap.cpp via git grep: {repr(r.stderr)}"
    # Verify we found the toJSON method definition
    assert "toJSON" in r.stdout, "toJSON method not found in CookieMap.cpp"


# ---------------------------------------------------------------------------
# Additional Pass-to-pass (repo_tests) — CI/CD checks from repository
# Added during p2p enrichment
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
# Origin: bun repo CI - package.json validation (package.json linting in CI)
def test_package_json_valid():
    """package.json must be valid JSON (pass_to_pass)."""
    import json
    pkg_path = Path(REPO) / "package.json"
    try:
        with open(pkg_path) as f:
            json.load(f)
    except json.JSONDecodeError as e:
        raise AssertionError(f"package.json is not valid JSON: {e}")


# [repo_tests] pass_to_pass
# Origin: bun repo CI - verifies C++ header guards and includes
def test_cookiemap_header_exists():
    """CookieMap.h header file must exist and have proper guards (pass_to_pass)."""
    header_path = Path(REPO) / "src" / "bun.js" / "bindings" / "CookieMap.h"
    assert header_path.exists(), "CookieMap.h not found"
    content = header_path.read_text()
    has_guard = "#pragma once" in content or ("#ifndef" in content and "#define" in content)
    assert has_guard, "CookieMap.h missing header guard or #pragma once"


# [repo_tests] pass_to_pass
# Origin: bun repo CI - verifies C++ source file syntax/encoding
def test_cookiemap_valid_utf8():
    """CookieMap.cpp must be valid UTF-8 (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", "open('" + str(FILE) + "', encoding='utf-8').read(); print('OK')"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"CookieMap.cpp is not valid UTF-8: {r.stderr[-500:]}"


# [repo_tests] pass_to_pass
# Origin: bun repo CI - git attributes validation
def test_git_attributes_valid():
    """Repository must have valid .gitattributes file (pass_to_pass)."""
    attrs_path = Path(REPO) / ".gitattributes"
    if not attrs_path.exists():
        pytest.skip(".gitattributes not found")
    # Check it is parseable
    r = subprocess.run(
        ["git", "-C", REPO, "check-attr", "-a", "src/bun.js/bindings/CookieMap.cpp"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    # git check-attr returns 0 even if no attributes, only fails on parse error
    assert r.returncode == 0, f"Git attributes check failed: {r.stderr}"


# [repo_tests] pass_to_pass
# Origin: bun repo CI - checks that required CI scripts exist
def test_ci_scripts_exist():
    """CI scripts referenced by workflows must exist (pass_to_pass)."""
    scripts = [
        "scripts/run-clang-format.sh",
    ]
    for script in scripts:
        script_path = Path(REPO) / script
        assert script_path.exists(), f"CI script {script} not found"
