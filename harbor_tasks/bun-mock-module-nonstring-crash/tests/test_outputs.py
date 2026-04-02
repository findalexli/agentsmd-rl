"""
Task: bun-mock-module-nonstring-crash
Repo: oven-sh/bun @ e94c3035c6f9d7868fb814cfeaf27b219d00e565
PR:   28518

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/bun"
TARGET = f"{REPO}/src/bun.js/bindings/BunPlugin.cpp"


def _get_function_body():
    """Extract JSMock__jsModuleMock body (first 3000 chars), C++ comments stripped."""
    code = Path(TARGET).read_text()
    stripped = re.sub(r"//[^\n]*", "", code)
    stripped = re.sub(r"/\*.*?\*/", "", stripped, flags=re.DOTALL)
    match = re.search(r"JSMock__jsModuleMock", stripped)
    assert match, "JSMock__jsModuleMock not found in BunPlugin.cpp"
    return stripped[match.start() : match.start() + 3000]


def _run_bun_test(test_code: str, filename: str):
    """Write a bun test file to a temp dir and run it."""
    tmp_dir = Path(tempfile.mkdtemp(prefix="bun-mock-"))
    test_file = tmp_dir / filename
    test_file.write_text(test_code)
    r = subprocess.run(
        ["bun", "test", str(test_file)],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(tmp_dir),
    )
    assert r.returncode == 0, f"Bun test failed:\n{r.stdout}\n{r.stderr}"


def _find_agent_test_files():
    """Find test files the agent created for mock.module non-string validation."""
    test_dir = Path(REPO) / "test"
    if not test_dir.exists():
        return []
    results = []
    for path in test_dir.rglob("*.test.ts"):
        try:
            content = path.read_text()
        except Exception:
            continue
        if "mock.module" not in content:
            continue
        if any(kw in content for kw in ["TypeError", "SharedArrayBuffer", "non-string", "isString"]):
            results.append(path)
    for path in test_dir.rglob("*.test.tsx"):
        try:
            content = path.read_text()
        except Exception:
            continue
        if "mock.module" not in content:
            continue
        if any(kw in content for kw in ["TypeError", "SharedArrayBuffer", "non-string", "isString"]):
            results.append(path)
    return results


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- structural source code checks
# (Bun is compiled C++; container cannot build agent changes, so F2P tests
#  verify the source-level fix via code analysis.)
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


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) -- behavioral tests against installed bun binary
# (Installed bun already has the fix; these verify the spec as regression.)
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_nonstring_throws_typeerror():
    """mock.module() throws TypeError for non-string args (number, object, symbol, bool, null)."""
    _run_bun_test(
        """\
import { test, expect, mock } from "bun:test";

test("number arg throws TypeError", () => {
  expect(() => mock.module(123 as any, () => ({}))).toThrow(TypeError);
});

test("object arg throws TypeError", () => {
  expect(() => mock.module({} as any, () => ({}))).toThrow(TypeError);
});

test("symbol arg throws TypeError", () => {
  expect(() => mock.module(Symbol("x") as any, () => ({}))).toThrow(TypeError);
});

test("boolean arg throws TypeError", () => {
  expect(() => mock.module(true as any, () => ({}))).toThrow(TypeError);
});

test("null arg throws TypeError", () => {
  expect(() => mock.module(null as any, () => ({}))).toThrow(TypeError);
});
""",
        "nonstring_throws.test.ts",
    )


# [pr_diff] pass_to_pass
def test_string_arg_accepted():
    """mock.module() works correctly with a valid string argument."""
    _run_bun_test(
        """\
import { test, expect, mock } from "bun:test";

test("mock.module works with string first arg", () => {
  expect(() => mock.module("some-test-module", () => ({ default: 42 }))).not.toThrow();
});

test("mock.module returns undefined", () => {
  const result = mock.module("another-test-module", () => ({ default: "hello" }));
  expect(result).toBeUndefined();
});
""",
        "string_ok.test.ts",
    )


# [pr_diff] pass_to_pass
def test_existing_guards_preserved():
    """Original argumentCount() and isEmpty() validation guards still present."""
    fn_body = _get_function_body()
    assert "argumentCount()" in fn_body, "argumentCount() check was removed"
    assert "isEmpty()" in fn_body, "isEmpty() check was removed"


# ---------------------------------------------------------------------------
# Static -- anti-stub
# ---------------------------------------------------------------------------

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
# Config-derived (agent_config) -- rules from CLAUDE.md / AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass -- CLAUDE.md:226,229 @ e94c3035
def test_agent_test_file_created():
    """Agent created a test file for mock.module non-string validation in test/."""
    found = _find_agent_test_files()
    assert len(found) > 0, "No test file for mock.module non-string validation found in test/"


# [agent_config] fail_to_pass -- CLAUDE.md:229 @ e94c3035
def test_agent_test_file_naming():
    """Agent test file ends in .test.ts or .test.tsx per CLAUDE.md:229."""
    found = _find_agent_test_files()
    assert len(found) > 0, "No agent test file found"
    for f in found:
        assert f.name.endswith(".test.ts") or f.name.endswith(".test.tsx"), (
            f"Test file {f.name} does not end in .test.ts or .test.tsx"
        )


# [agent_config] fail_to_pass -- CLAUDE.md:32-33 @ e94c3035
def test_agent_test_file_location():
    """Agent test file is in test/js/bun/ (Bun-specific API test location per CLAUDE.md:32-33)."""
    found = _find_agent_test_files()
    assert len(found) > 0, "No agent test file found"
    for f in found:
        rel = f.relative_to(Path(REPO))
        assert str(rel).startswith("test/js/bun/"), (
            f"Test file {rel} is not in test/js/bun/ (expected location for Bun API tests)"
        )


# [agent_config] fail_to_pass -- CLAUDE.md:102 @ e94c3035
def test_agent_test_no_settimeout():
    """Agent test file does not use setTimeout (flaky test pattern per CLAUDE.md:102)."""
    found = _find_agent_test_files()
    assert len(found) > 0, "No agent test file found"
    for f in found:
        content = f.read_text()
        assert "setTimeout" not in content, (
            f"Test file {f.name} uses setTimeout, which produces flaky tests"
        )


# [agent_config] fail_to_pass -- CLAUDE.md:99 @ e94c3035
def test_agent_test_asserts_positive_behavior():
    """Agent test asserts TypeError is thrown, not just absence of crash (CLAUDE.md:99)."""
    found = _find_agent_test_files()
    assert len(found) > 0, "No agent test file found"
    for f in found:
        content = f.read_text()
        # Must assert TypeError is thrown, not just "no panic" or "no crash"
        positive_patterns = ["toThrow", "TypeError", "rejects", "throws"]
        assert any(p in content for p in positive_patterns), (
            f"Test file {f.name} does not assert positive behavior (TypeError thrown)"
        )
