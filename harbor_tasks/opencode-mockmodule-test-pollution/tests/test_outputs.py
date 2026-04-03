"""
Task: opencode-mockmodule-test-pollution
Repo: anomalyco/opencode @ e973bbf54a519566bfdccce3474178b26b163a6d
PR:   19445

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/opencode"
THREAD_TEST = f"{REPO}/packages/opencode/test/cli/tui/thread.test.ts"
CONFIG_TEST = f"{REPO}/packages/opencode/test/config/config.test.ts"
BASE_COMMIT = "e973bbf54a519566bfdccce3474178b26b163a6d"


def _strip_comments(src: str) -> str:
    """Remove single-line and block comments from TypeScript source."""
    lines = src.split("\n")
    out = []
    in_block = False
    for line in lines:
        t = line.strip()
        if t.startswith("/*"):
            in_block = True
        if in_block:
            if "*/" in t:
                in_block = False
            continue
        if t.startswith("//"):
            continue
        out.append(line)
    return "\n".join(out)


def _added_lines_in_diff() -> list[str]:
    """Return only the '+' lines from git diff HEAD for the two modified test files."""
    r = subprocess.run(
        ["git", "diff", BASE_COMMIT, "--",
         "packages/opencode/test/cli/tui/thread.test.ts",
         "packages/opencode/test/config/config.test.ts"],
        cwd=REPO, capture_output=True, timeout=10,
    )
    diff = r.stdout.decode()
    return [l for l in diff.split("\n")
            if l.startswith("+") and not l.startswith("+++")]


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_mock_module_in_thread_test():
    """thread.test.ts must not use mock.module() (leaks globally in Bun)."""
    code = _strip_comments(Path(THREAD_TEST).read_text())
    assert not re.search(r"mock\s*\.\s*module\s*\(", code), (
        "mock.module() found in thread.test.ts — it leaks globally in Bun. "
        "Use spyOn() instead (see oven-sh/bun#7823)."
    )


# [pr_diff] fail_to_pass
def test_uses_spyon_for_mocking():
    """thread.test.ts must use spyOn() for mocking dependencies."""
    src = Path(THREAD_TEST).read_text()
    # The fix replaces mock.module() with spyOn() calls on imported modules.
    # At minimum, the key modules that were previously mock.module'd must be spyOn'd.
    spyon_calls = re.findall(r"spyOn\s*\(", src)
    assert len(spyon_calls) >= 3, (
        f"Expected at least 3 spyOn() calls in thread.test.ts to replace "
        f"mock.module(), found {len(spyon_calls)}. The fix should use spyOn "
        f"on imported module objects instead of mock.module()."
    )
    # Verify spyOn targets key modules that were previously mock.module'd
    key_modules = ["App", "Rpc", "UI", "TuiConfig", "Instance"]
    found = [m for m in key_modules if re.search(rf"spyOn\s*\(\s*{m}\b", src)]
    assert len(found) >= 3, (
        f"spyOn must target key modules. Found targets for: {found}. "
        f"Expected at least 3 of: {key_modules}"
    )


# [pr_diff] fail_to_pass
def test_setup_per_test_pattern():
    """Mocking must happen per-test (in a function/hook), not at module level.

    The root cause is that mock.module() at the top level persists across
    test files. The fix must ensure mocking is scoped to individual tests
    via a setup function, beforeEach, or similar pattern.
    """
    src = Path(THREAD_TEST).read_text()
    code = _strip_comments(src)
    # Check that spyOn calls are NOT at the module top level.
    # They should be inside a function body (setup, beforeEach, etc.)
    # Strategy: find all spyOn calls and verify they're inside a function/describe block
    lines = code.split("\n")
    toplevel_spyon = []
    depth = 0
    for i, line in enumerate(lines):
        # Track brace depth (rough heuristic for top-level detection)
        depth += line.count("{") - line.count("}")
        if depth <= 0 and re.search(r"spyOn\s*\(", line):
            toplevel_spyon.append((i + 1, line.strip()))
    assert not toplevel_spyon, (
        f"spyOn() calls found at module top level (depth=0): "
        f"{toplevel_spyon[:3]}. Mocks must be set up inside a function "
        f"or lifecycle hook to prevent leakage."
    )
    # Verify there's a setup function or beforeEach that contains spyOn
    has_setup_fn = bool(re.search(r"function\s+setup\s*\(", code))
    has_before_hook = bool(re.search(r"before(?:Each|All)\s*\(", code))
    assert has_setup_fn or has_before_hook, (
        "thread.test.ts must have a setup() function or beforeEach/beforeAll "
        "hook to initialize mocks per test."
    )


# [pr_diff] fail_to_pass
def test_config_mock_filters_by_cwd():
    """config.test.ts BunProc.run mock must filter calls by working directory.

    The base version counts ALL BunProc.run invocations, including unrelated
    background calls. The fix must compare opts.cwd against the test directory
    so only relevant calls are counted.
    """
    src = Path(CONFIG_TEST).read_text()
    # Look for cwd comparison pattern in the mock implementation
    # The fix normalizes opts.cwd and compares it to the test directory
    has_cwd_filter = bool(re.search(
        r"(opts\??\.\s*cwd|options\??\.\s*cwd).*(?:normalize|===|==|includes|startsWith)",
        src,
    ))
    has_hit_pattern = bool(re.search(
        r"(const|let|var)\s+\w+\s*=.*(?:normalize|cwd).*(?:===|==)", src,
    ))
    assert has_cwd_filter or has_hit_pattern, (
        "config.test.ts BunProc.run mock does not filter by cwd — "
        "unrelated calls will inflate counters and cause flaky tests."
    )
    # Verify the filter is used to gate the counter increment
    # The pattern should be: check cwd match, then conditionally increment
    has_conditional_count = bool(re.search(
        r"if\s*\(\s*\w+\s*\)[\s\S]{0,100}calls\s*\+=", src,
    ))
    assert has_conditional_count, (
        "config.test.ts must conditionally increment call counters only when "
        "the cwd matches the test directory."
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:122 @ e973bbf5
def test_mock_cleanup_in_lifecycle_hook():
    """thread.test.ts must clean up mocks in afterEach/afterAll."""
    src = Path(THREAD_TEST).read_text()
    has_after_hook = bool(re.search(r"after(?:Each|All)\s*\(", src))
    has_restore = bool(re.search(r"mock\s*\.\s*restore|mockRestore", src))
    assert has_after_hook and has_restore, (
        "thread.test.ts must have afterEach/afterAll calling mock.restore() "
        "to clean up spyOn mocks between tests (AGENTS.md: avoid mocks as "
        "much as possible — when mocks are needed, clean them up)."
    )


# [agent_config] pass_to_pass — AGENTS.md:13 @ e973bbf5
def test_no_any_type_added():
    """Changes must not introduce the `any` type."""
    added = _added_lines_in_diff()
    any_lines = [l for l in added if re.search(r":\s*any\b|as\s+any\b|<any>", l)]
    assert not any_lines, (
        f"Added `any` type annotations (AGENTS.md: avoid using the any type):\n"
        + "\n".join(any_lines[:5])
    )


# [agent_config] pass_to_pass — AGENTS.md:12 @ e973bbf5
def test_no_try_catch_added():
    """Changes must not introduce try/catch blocks."""
    added = _added_lines_in_diff()
    try_catch = [l for l in added
                 if re.search(r"\btry\s*\{", l) or re.search(r"\bcatch\s*\(", l)]
    assert not try_catch, (
        f"Added try/catch (AGENTS.md: avoid try/catch):\n"
        + "\n".join(try_catch[:5])
    )


# [agent_config] pass_to_pass — AGENTS.md:84 @ e973bbf5
def test_no_else_added():
    """Changes must not introduce else statements."""
    added = _added_lines_in_diff()
    else_lines = [l for l in added
                  if re.search(r"}\s*else\b|\belse\s*\{|\belse\s+if\b", l)]
    assert not else_lines, (
        f"Added else statements (AGENTS.md: prefer early returns):\n"
        + "\n".join(else_lines[:5])
    )


# ---------------------------------------------------------------------------
# Anti-stub (static) — prevent trivial/gutted solutions
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_thread_test_not_stubbed():
    """thread.test.ts must not be stubbed out."""
    src = Path(THREAD_TEST).read_text()
    lines = len(src.strip().split("\n"))
    assert lines >= 40, f"thread.test.ts looks stubbed ({lines} lines)"
    assert "TuiThreadCommand" in src, "thread.test.ts must reference TuiThreadCommand"
    assert "describe" in src, "thread.test.ts must have describe blocks"
    assert "expect" in src, "thread.test.ts must have expect assertions"


# [static] pass_to_pass
def test_config_test_not_stubbed():
    """config.test.ts must not be stubbed and must have substantive mock logic."""
    src = Path(CONFIG_TEST).read_text()
    lines = len(src.strip().split("\n"))
    assert lines >= 200, f"config.test.ts looks stubbed ({lines} lines)"
    assert re.search(r"dedupes concurrent", src), "Missing 'dedupes concurrent' test block"
    assert re.search(r"serializes.*across dirs|serializes config", src), (
        "Missing serialization test block"
    )
    assert re.search(r"spyOn.*BunProc|BunProc.*mock", src), "Missing BunProc.run mock"
