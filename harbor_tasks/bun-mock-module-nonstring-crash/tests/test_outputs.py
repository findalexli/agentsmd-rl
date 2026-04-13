"""
Task: bun-mock-module-nonstring-crash
Repo: oven-sh/bun @ e94c3035c6f9d7868fb814cfeaf27b219d00e565
PR:   28518

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/bun"
TARGET = f"{REPO}/src/bun.js/bindings/BunPlugin.cpp"


def _get_function_body():
    """Extract JSMock__jsModuleMock body (first 3000 chars), C++ comments stripped."""
    # AST-only because: C++ code requires full Bun build system (zig/cmake) to compile
    code = Path(TARGET).read_text()
    stripped = re.sub(r"//[^\n]*", "", code)
    stripped = re.sub(r"/\*.*?\*/", "", stripped, flags=re.DOTALL)
    match = re.search(r"JSMock__jsModuleMock", stripped)
    assert match, "JSMock__jsModuleMock not found in BunPlugin.cpp"
    return stripped[match.start() : match.start() + 3000]


def _find_agent_test_files():
    """Find test files the agent created for mock.module non-string validation."""
    test_dir = Path(REPO) / "test"
    if not test_dir.exists():
        return []
    results = []
    for ext in ("*.test.ts", "*.test.tsx"):
        for path in test_dir.rglob(ext):
            try:
                content = path.read_text()
            except Exception:
                continue
            if "mock.module" not in content:
                continue
            if any(
                kw in content
                for kw in [
                    "TypeError",
                    "SharedArrayBuffer",
                    "non-string",
                    "isString",
                    "not a string",
                    "requires a",
                    "module name string",
                ]
            ):
                results.append(path)
    return results


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — structural source code checks
# AST-only because: C++ code requires full Bun build system to compile
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_type_guard_before_tostring():
    """Type validation guard (isString or equivalent) exists before toString() call."""
    fn_body = _get_function_body()

    to_string_pos = fn_body.find(".toString(")
    ts_alt = fn_body.find("toWTFString(")

    # If toString is gone entirely, check for safe alternatives
    if to_string_pos == -1 and ts_alt == -1:
        safe_alts = ["toStringOrNull", "tryGetString", "getString("]
        assert any(
            alt in fn_body for alt in safe_alts
        ), "toString not found and no safe alternative used"
        return

    positions = [p for p in [to_string_pos, ts_alt] if p > 0]
    checkpoint = min(positions)
    before = fn_body[:checkpoint]

    type_guard_patterns = [
        r"isString\s*\(",
        r"isCell\s*\(",
        r"jsTypeInfo\s*\(",
        r"JSType::\w*String",
        r"\.type\s*\(\s*\)\s*[!=]=",
        r"isObject\s*\(",
        r"isSymbol\s*\(",
        r"isNumber\s*\(",
        r"isUndefinedOrNull\s*\(",
        r"toStringOrNull",
        r"tryGetString",
        r"isBoolean\s*\(",
        r"isHeapBigInt\s*\(",
    ]

    assert any(
        re.search(p, before) for p in type_guard_patterns
    ), "No type validation guard found before toString() call"


# [pr_diff] fail_to_pass
def test_type_guard_error_path():
    """Error thrown and early return when first argument is not a string."""
    fn_body = _get_function_body()

    guard_patterns = [
        r"isString\s*\(",
        r"isCell\s*\(",
        r"jsTypeInfo\s*\(",
        r"toStringOrNull",
        r"tryGetString",
        r"isObject\s*\(",
        r"isSymbol\s*\(",
        r"isNumber\s*\(",
        r"isUndefinedOrNull\s*\(",
        r"isBoolean\s*\(",
    ]

    guard_pos = -1
    for p in guard_patterns:
        m = re.search(p, fn_body)
        if m:
            guard_pos = m.start()
            break

    assert guard_pos >= 0, "No type guard found in JSMock__jsModuleMock"

    after_guard = fn_body[guard_pos : guard_pos + 500]

    error_patterns = [
        r"throwException",
        r"createTypeError",
        r"createError",
        r"throwTypeError",
        r"ThrowTypeError",
    ]
    assert any(
        re.search(p, after_guard) for p in error_patterns
    ), "No error thrown after type guard"

    return_patterns = [
        r"return\s*[\{\};]",
        r"return\s+JSValue",
        r"return\s+js",
        r"RETURN_IF_EXCEPTION",
    ]
    assert any(
        re.search(p, after_guard) for p in return_patterns
    ), "No early return after error throw"


# [pr_diff] fail_to_pass
def test_error_message_descriptive():
    """Error message mentions 'string' or 'module' so the user knows what went wrong."""
    fn_body = _get_function_body()

    # Find the error creation near the type guard
    guard_match = re.search(r"isString\s*\(", fn_body)
    if not guard_match:
        # If no isString guard, check for alternative type checks with error messages
        error_match = re.search(r"createTypeError|throwTypeError|createError", fn_body)
        assert error_match, "No type error creation found"
        region = fn_body[error_match.start() : error_match.start() + 300]
    else:
        region = fn_body[guard_match.start() : guard_match.start() + 500]

    # The error message should be descriptive — mention "string" or "module"
    assert re.search(r'(?i)(string|module|specifier)', region), (
        "Error message near type guard does not mention 'string', 'module', or 'specifier'"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — source code regression checks
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_existing_guards_preserved():
    """Original argumentCount() and isEmpty() validation guards still present."""
    fn_body = _get_function_body()
    assert "argumentCount()" in fn_body, "argumentCount() check was removed"
    assert "isEmpty()" in fn_body, "isEmpty() check was removed"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks that must pass on base and gold
# ---------------------------------------------------------------------------

REPO_DIR = "/workspace/bun"


# [repo_tests] pass_to_pass
def test_repo_ts_typecheck():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["bunx", "tsc", "--noEmit"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO_DIR,
    )
    assert r.returncode == 0, f"TypeScript typecheck failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ban_words():
    """Repo's banned words check passes (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "./test/internal/ban-words.test.ts"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO_DIR,
    )
    assert r.returncode == 0, f"Ban words check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_js_lint():
    """Repo's JS lint (oxlint on src/js/bun) passes (pass_to_pass)."""
    r = subprocess.run(
        ["bunx", "oxlint", "--format=github", "src/js/bun"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO_DIR,
    )
    # Exit code 0 means no errors (warnings are okay)
    assert r.returncode == 0, f"JS lint failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_repo_package_json_lint():
    """Repo's package.json lint passes (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "test", "test/package-json-lint.test.ts"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO_DIR,
    )
    assert r.returncode == 0, f"Package.json lint failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_mock_fn_tests():
    """Repo's mock function tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "test", "test/js/bun/test/mock-fn.test.js"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO_DIR,
    )
    assert r.returncode == 0, f"Mock function tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_mock_disposable_tests():
    """Repo's mock disposable tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "test", "test/js/bun/test/mock-disposable.test.ts"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO_DIR,
    )
    assert r.returncode == 0, f"Mock disposable tests failed:\n{r.stderr[-500:]}"

# [repo_tests] pass_to_pass
def test_repo_mock_module_tests():
    """Repo's mock module tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "test", "test/js/bun/test/mock/mock-module.test.ts"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO_DIR,
    )
    assert r.returncode == 0, f"Mock module tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_mock_module_resolve_log_tests():
    """Repo's mock module resolve log tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "test", "test/js/bun/test/mock/mock-module-resolve-log.test.ts"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO_DIR,
    )
    assert r.returncode == 0, f"Mock module resolve log tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_bun_test_framework():
    """Repo's bun:test framework core tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "test", "test/js/bun/test/bun_test.test.ts"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO_DIR,
    )
    assert r.returncode == 0, f"Bun test framework tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_jest_hooks():
    """Repo's jest hooks tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "test", "test/js/bun/test/jest-hooks.test.ts"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO_DIR,
    )
    assert r.returncode == 0, f"Jest hooks tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_jest_each():
    """Repo's jest-each tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "test", "test/js/bun/test/jest-each.test.ts"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO_DIR,
    )
    assert r.returncode == 0, f"Jest each tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_describe_tests():
    """Repo's describe block tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "test", "test/js/bun/test/describe.test.ts"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO_DIR,
    )
    assert r.returncode == 0, f"Describe tests failed:\n{r.stderr[-500:]}"


# Static — anti-stub


# [static] fail_to_pass
def test_meaningful_source_changes():
    """At least 3 meaningful (non-comment, non-blank) lines added to BunPlugin.cpp."""
    r = subprocess.run(
        ["git", "diff", "--no-color", "--", "src/bun.js/bindings/BunPlugin.cpp"],
        capture_output=True,
        text=True,
        cwd=REPO,
        timeout=10,
    )

    added = 0
    for line in r.stdout.splitlines():
        if not line.startswith("+") or line.startswith("+++"):
            continue
        content = line[1:].strip()
        if not content:
            continue
        if content.startswith("//") or content.startswith("/*") or content.startswith("*"):
            continue
        added += 1

    assert added >= 3, f"Only {added} meaningful lines added (need >=3)"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md / AGENTS.md
# ---------------------------------------------------------------------------


# [agent_config] fail_to_pass — CLAUDE.md:226,229 @ e94c3035
def test_agent_test_file_created():
    """Agent created a test file for mock.module non-string validation in test/."""
    found = _find_agent_test_files()
    assert len(found) > 0, "No test file for mock.module non-string validation found in test/"


# [agent_config] fail_to_pass — CLAUDE.md:229 @ e94c3035
def test_agent_test_file_naming():
    """Agent test file ends in .test.ts or .test.tsx per CLAUDE.md:229."""
    found = _find_agent_test_files()
    assert len(found) > 0, "No agent test file found"
    for f in found:
        assert f.name.endswith(".test.ts") or f.name.endswith(
            ".test.tsx"
        ), f"Test file {f.name} does not end in .test.ts or .test.tsx"


# [agent_config] fail_to_pass — CLAUDE.md:32-33 @ e94c3035
def test_agent_test_file_location():
    """Agent test file is in test/js/bun/ (Bun-specific API test location per CLAUDE.md:32-33)."""
    found = _find_agent_test_files()
    assert len(found) > 0, "No agent test file found"
    for f in found:
        rel = f.relative_to(Path(REPO))
        assert str(rel).startswith("test/js/bun/"), (
            f"Test file {rel} is not in test/js/bun/"
        )


# [agent_config] fail_to_pass — CLAUDE.md:102 @ e94c3035
def test_agent_test_no_settimeout():
    """Agent test file does not use setTimeout (flaky test pattern per CLAUDE.md:102)."""
    found = _find_agent_test_files()
    assert len(found) > 0, "No agent test file found"
    for f in found:
        content = f.read_text()
        assert "setTimeout" not in content, (
            f"Test file {f.name} uses setTimeout, which produces flaky tests"
        )


# [agent_config] fail_to_pass — CLAUDE.md:99 @ e94c3035
def test_agent_test_asserts_positive_behavior():
    """Agent test asserts TypeError is thrown, not just absence of crash (CLAUDE.md:99)."""
    found = _find_agent_test_files()
    assert len(found) > 0, "No agent test file found"
    for f in found:
        content = f.read_text()
        positive_patterns = ["toThrow", "TypeError", "rejects", "throws"]
        assert any(p in content for p in positive_patterns), (
            f"Test file {f.name} does not assert positive behavior (TypeError thrown)"
        )


# [agent_config] fail_to_pass — test/AGENTS.md:120 @ e94c3035
def test_agent_test_no_timeout_option():
    """Agent test does not set a custom timeout (Bun has built-in timeouts per test/AGENTS.md:120)."""
    found = _find_agent_test_files()
    assert len(found) > 0, "No agent test file found"
    for f in found:
        content = f.read_text()
        # Check for timeout option in test() calls: test("name", fn, { timeout: ... })
        assert not re.search(r'timeout\s*:', content), (
            f"Test file {f.name} sets a custom timeout — Bun already has built-in timeouts"
        )


# [agent_config] fail_to_pass — CLAUDE.md:231 @ e94c3035
def test_agent_test_no_shell_commands():
    """Agent test file does not use find/grep shell commands — use Bun's Glob and built-in tools (CLAUDE.md:231)."""
    found = _find_agent_test_files()
    assert len(found) > 0, "No agent test file found"
    for f in found:
        content = f.read_text()
        assert not re.search(r'["\']find["\']', content), (
            f"Test file {f.name} uses 'find' shell command — use Bun's Glob instead"
        )
        assert not re.search(r'["\']grep["\']', content), (
            f"Test file {f.name} uses 'grep' shell command — use Bun's built-in tools instead"
        )
