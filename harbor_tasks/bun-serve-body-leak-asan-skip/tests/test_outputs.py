"""
Task: bun-serve-body-leak-asan-skip
Repo: oven-sh/bun @ 66f7c41412e8a41c9686b0f4524b778a5f69b40e
PR:   28301

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/bun"
TARGET = f"{REPO}/test/js/bun/http/serve-body-leak.test.ts"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_asan_true_skips_memory_leak_tests():
    """When isASAN=true, memory leak tests are skipped via todoIf/skipIf/describe.skipIf."""
    text = Path(TARGET).read_text()
    # Find lines with todoIf/skipIf/describe.skipIf that reference isASAN
    skip_lines = [
        line for line in text.splitlines()
        if re.search(r"(?:it|describe)\.(?:todoIf|skipIf)\s*\(", line)
        and "isASAN" in line
    ]
    # Also check for if-guard: if (isASAN) { ... } wrapping the test block
    guard_lines = [
        line for line in text.splitlines()
        if re.search(r"if\s*\(\s*!?\s*isASAN\s*\)", line)
    ]
    assert skip_lines or guard_lines, \
        "isASAN=true does not cause memory leak tests to be skipped"


# [pr_diff] fail_to_pass
def test_asan_imported_from_harness():
    """isASAN is imported from the harness module."""
    text = Path(TARGET).read_text()
    has_import = bool(
        re.search(r"import\s*\{[^}]*\bisASAN\b[^}]*\}\s*from\s*['\"]harness['\"]", text)
        or re.search(
            r"(?:const|let|var)\s*\{[^}]*\bisASAN\b[^}]*\}\s*=\s*require\s*\(\s*['\"]harness['\"]\s*\)",
            text,
        )
    )
    assert has_import, "isASAN not imported from harness"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_non_asan_build_tests_still_run():
    """When isASAN=false (normal build), memory leak tests are NOT skipped."""
    text = Path(TARGET).read_text()
    # The skip condition should only activate when isASAN is true.
    # Check that there's no unconditional skip of the memory leak tests.
    # The condition must include isASAN (not just `true` or always-true expr).
    for line in text.splitlines():
        if re.search(r"(?:it|describe)\.(?:todoIf|skipIf)\s*\(", line):
            # Ensure the condition isn't just `true` or always-true
            stripped = line.strip()
            assert not re.match(
                r"(?:it|describe)\.(?:todoIf|skipIf)\s*\(\s*true\s*\)", stripped
            ), "Tests unconditionally skipped"
    # Also verify the file still has test cases (not all removed)
    assert "should not leak memory" in text, "Memory leak test cases removed entirely"


# [pr_diff] pass_to_pass
def test_original_test_cases_preserved():
    """All 7 original memory leak test case names still present."""
    text = Path(TARGET).read_text()
    expected = [
        "should not leak memory when ignoring the body",
        "should not leak memory when buffering the body",
        "should not leak memory when buffering a JSON body",
        "should not leak memory when buffering the body and accessing req.body",
        "should not leak memory when streaming the body",
        "should not leak memory when streaming the body incompletely",
        "should not leak memory when streaming the body and echoing it back",
    ]
    found = sum(1 for t in expected if t in text)
    assert found == 7, f"Only {found}/7 original test case names found"


# [pr_diff] pass_to_pass
def test_existing_skip_conditions_preserved():
    """The existing isFlaky && isWindows skip condition is still present."""
    text = Path(TARGET).read_text()
    assert re.search(r"isFlaky\s*&&\s*isWindows", text), \
        "Existing isFlaky && isWindows skip condition removed"


# [static] pass_to_pass
def test_not_stub():
    """File retains substantial test logic (not gutted/stubbed)."""
    text = Path(TARGET).read_text()
    lines = len(text.splitlines())
    assert lines > 140, f"File suspiciously small ({lines} lines) — likely stubbed"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — test/AGENTS.md:219-220 @ 66f7c41412e8a41c9686b0f4524b778a5f69b40e
def test_uses_module_scope_import():
    """isASAN is imported via a module-scope import statement, not a dynamic import."""
    text = Path(TARGET).read_text()
    # Must have a top-level import (not inside a function/block)
    for line in text.splitlines():
        stripped = line.strip()
        # Module-scope import: starts at column 0 (no indentation)
        if re.match(r'^import\s*\{[^}]*\bisASAN\b', stripped):
            return  # Found module-scope import
    # Check for dynamic import/require of isASAN (should NOT exist)
    assert not re.search(r'(?:await\s+)?import\s*\([^)]*harness', text), \
        "isASAN uses dynamic import instead of module-scope import"
    assert not re.search(r'require\s*\(\s*["\']harness["\']\s*\)', text), \
        "isASAN uses require instead of module-scope import"
    assert False, "isASAN not found in any module-scope import statement"


# [agent_config] fail_to_pass — CLAUDE.md:102 @ 66f7c41412e8a41c9686b0f4524b778a5f69b40e
def test_skip_uses_deterministic_detection():
    """Skip condition uses deterministic build flag, not timing heuristics."""
    text = Path(TARGET).read_text()
    # Ensure no non-deterministic patterns near skip conditions
    for line in text.splitlines():
        if re.search(r"(?:todoIf|skipIf)\s*\(", line):
            assert not re.search(r"setTimeout|Math\.random|Date\.now|performance\.now", line), \
                f"Skip condition uses non-deterministic pattern: {line.strip()}"
    # isASAN must appear in a skip/todoIf condition or if-guard
    has_asan_skip = bool(
        re.search(r"(?:todoIf|skipIf)\s*\([^;\n]*isASAN", text)
        or re.search(r"describe\.skipIf\s*\([^;\n]*isASAN", text)
        or re.search(r"if\s*\(\s*!?\s*isASAN\s*\)", text)
    )
    assert has_asan_skip, "No skip condition references isASAN"


# [agent_config] fail_to_pass — CLAUDE.md:228 @ 66f7c41412e8a41c9686b0f4524b778a5f69b40e
def test_uses_standard_skip_pattern():
    """Uses standard bun:test skip mechanisms (todoIf/skipIf), not process.exit."""
    text = Path(TARGET).read_text()
    # Must use standard bun:test skip patterns with isASAN
    uses_standard = bool(
        re.search(r"(?:todoIf|skipIf)\s*\([^;\n]*isASAN", text)
        or re.search(r"describe\.skipIf\s*\([^;\n]*isASAN", text)
        or re.search(r"if\s*\(\s*!?\s*isASAN\s*\)", text)
    )
    assert uses_standard, "isASAN not used in a standard skip pattern"
    has_exit_skip = bool(re.search(r"process\.exit\s*\(", text)) and "isASAN" in text
    assert not has_exit_skip, "Uses process.exit to skip instead of standard pattern"
