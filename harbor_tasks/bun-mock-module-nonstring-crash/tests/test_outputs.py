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
import os
from pathlib import Path

REPO = "/workspace/bun"


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
# Fail-to-pass (pr_diff) — behavioral tests via bun test
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_type_guard_before_tostring():
    """Type validation guard exists before toString() call — verified by running agent's test."""
    agent_test_files = _find_agent_test_files()
    assert len(agent_test_files) > 0, (
        "No test file found for mock.module non-string validation. "
        "Agent must create a test file in test/ that verifies TypeError is thrown "
        "for non-string arguments."
    )

    result = subprocess.run(
        ["bun", "test", "--bail", str(agent_test_files[0])],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )

    assert result.returncode == 0, (
        f"Agent test file failed — mock.module does not properly handle non-string "
        f"arguments (type guard may be missing):\n"
        f"stdout: {result.stdout[-500:]}\n"
        f"stderr: {result.stderr[-500:]}"
    )


# [pr_diff] fail_to_pass
def test_type_guard_error_path():
    """Error thrown and early return when first argument is not a string — verified by running agent's test."""
    agent_test_files = _find_agent_test_files()
    assert len(agent_test_files) > 0, (
        "No test file found for mock.module non-string validation"
    )

    result = subprocess.run(
        ["bun", "test", "--bail", str(agent_test_files[0])],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )

    assert result.returncode == 0, (
        f"Agent test file failed — error path may not be correct:\n"
        f"stdout: {result.stdout[-500:]}\n"
        f"stderr: {result.stderr[-500:]}"
    )


# [pr_diff] fail_to_pass
def test_error_message_descriptive():
    """Error message is descriptive — verified by running agent's test which asserts on message."""
    agent_test_files = _find_agent_test_files()
    assert len(agent_test_files) > 0, (
        "No test file found for mock.module non-string validation"
    )

    result = subprocess.run(
        ["bun", "test", "--bail", str(agent_test_files[0])],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )

    assert result.returncode == 0, (
        f"Agent test file failed — error message may not be descriptive:\n"
        f"stdout: {result.stdout[-500:]}\n"
        f"stderr: {result.stderr[-500:]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — behavioral regression checks
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_existing_guards_preserved():
    """
    Original validation behavior (argumentCount and isEmpty checks) still works.
    Verified by testing that mock.module throws appropriate errors for edge cases.
    """
    # Create a test file that exercises edge cases that would be affected
    # if argumentCount or isEmpty checks were broken
    test_code = '''
import { expect, mock, test } from "bun:test";

// Test that calling with no arguments throws (exercises argumentCount check)
test("mock.module with no arguments throws", () => {
  expect(() => {
    // @ts-expect-error
    mock.module();
  }).toThrow();
});

// Test that calling with empty/undefined first argument throws
// (exercises isEmpty check if it exists)
test("mock.module with undefined first argument throws", () => {
  expect(() => {
    // @ts-expect-error
    mock.module(undefined, () => ({}));
  }).toThrow();
});
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.test.ts', delete=False) as f:
        f.write(test_code)
        temp_test = f.name

    try:
        result = subprocess.run(
            ["bun", "test", "--bail", temp_test],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO,
        )

        assert result.returncode == 0, (
            f"Original validation behavior broken — argumentCount/isEmpty guards may be affected:\n"
            f"stdout: {result.stdout[-500:]}\n"
            f"stderr: {result.stderr[-500:]}"
        )
    finally:
        os.unlink(temp_test)


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


# Static — behavioral verification that a meaningful fix exists


# [static] fail_to_pass
def test_meaningful_source_changes():
    """
    A meaningful fix for the type guard bug exists in the codebase.
    Verified behaviorally by checking that:
    1. Non-string arguments throw TypeError with the expected message
    2. The error message mentions 'module name string' or similar
    """
    # Create a test file that specifically checks the expected fix behavior
    test_code = '''
import { expect, mock, test } from "bun:test";

// Verify the specific error message behavior
const expectedMessage = "mock(module, fn) requires a module name string";

test("mock.module throws TypeError with specific message for non-string", () => {
  // @ts-expect-error
  expect(() => mock.module(123, () => ({}))).toThrow(expectedMessage);
});

test("mock.module throws for multiple non-string types", () => {
  // @ts-expect-error
  expect(() => mock.module({}, () => ({}))).toThrow(/module.*string|string.*module/i);
  // @ts-expect-error
  expect(() => mock.module(Symbol("test"), () => ({}))).toThrow(/module.*string|string.*module/i);
});
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.test.ts', delete=False) as f:
        f.write(test_code)
        temp_test = f.name

    try:
        result = subprocess.run(
            ["bun", "test", "--bail", temp_test],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO,
        )

        assert result.returncode == 0, (
            f"Behavioral check for meaningful fix failed — "
            f"expected TypeError with 'module name string' message:\n"
            f"stdout: {result.stdout[-500:]}\n"
            f"stderr: {result.stderr[-500:]}"
        )
    finally:
        os.unlink(temp_test)


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
