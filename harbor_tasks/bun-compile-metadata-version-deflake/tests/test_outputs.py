"""
Task: bun-compile-metadata-version-deflake
Repo: oven-sh/bun @ a04817ce2b7f1a1e8b7cbf8af8f2c027ab072f1d
PR:   #28205

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Note: bun is not available in the test environment, so all checks
analyse the TypeScript source directly.
"""

import re
from pathlib import Path

REPO = Path("/workspace/bun")
TEST_FILE = REPO / "test/bundler/compile-windows-metadata.test.ts"

INVALID_VERSIONS = ["not.a.version", "1.2.3.4.5", "1.-2.3.4", "65536.0.0.0"]


def _read_test_file() -> str:
    assert TEST_FILE.exists(), f"{TEST_FILE} does not exist"
    text = TEST_FILE.read_text()
    assert len(text.splitlines()) >= 280, (
        f"File too short ({len(text.splitlines())} lines); likely truncated or gutted"
    )
    return text


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_file_parses():
    """Test file exists, is substantive, and has balanced braces."""
    text = _read_test_file()
    depth = 0
    for ch in text:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        assert depth >= 0, "Unbalanced braces (closed before opened)"
    assert depth == 0, f"Unbalanced braces (depth={depth} at EOF)"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioural tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_loop_removed():
    """The sequential for-loop over invalidVersions with Bun.spawn must be removed."""
    text = _read_test_file()
    # Check for any kind of loop iterating over versions and calling Bun.spawn
    has_for_loop = bool(
        re.search(r"for\s*\([^)]*\)\s*\{[\s\S]*?Bun\.spawn", text, re.DOTALL)
    )
    has_version_array = bool(
        re.search(r"(?:const|let|var)\s+invalidVersions\s*=\s*\[", text)
    )
    has_while_loop = bool(
        re.search(r"while\s*\([^)]*\)\s*\{[\s\S]*?Bun\.spawn", text, re.DOTALL)
    )
    assert not has_for_loop, "for-loop over versions with Bun.spawn still present"
    assert not has_version_array, "invalidVersions array variable still present"
    assert not has_while_loop, "while-loop over versions with Bun.spawn still present"


# [pr_diff] fail_to_pass
def test_versions_parameterized():
    """Each invalid version gets its own test case (test.each, describe.each, etc.)."""
    text = _read_test_file()

    best = 0

    # Method 1: test.each / it.each / describe.each with array
    m = re.search(r"(?:test|it|describe)\.each\s*\((\[[\s\S]*?\])\)", text)
    if m:
        matched = sum(1 for v in INVALID_VERSIONS if v in m.group(1))
        best = max(best, matched)

    # Method 2: template literal .each
    m = re.search(r"(?:test|it|describe)\.each`([\s\S]*?)`", text)
    if m:
        matched = sum(1 for v in INVALID_VERSIONS if v in m.group(1))
        best = max(best, matched)

    # Method 3: forEach/map generating test registrations
    if re.search(r"\.(?:forEach|map)\s*\([\s\S]*?(?:test|it|describe)\s*\(", text):
        matched = sum(1 for v in INVALID_VERSIONS if v in text)
        best = max(best, matched)

    # Method 4: individual test()/it() calls each referencing a version
    individual = 0
    for v in INVALID_VERSIONS:
        escaped = re.escape(v)
        if re.search(r"(?:test|it|describe)\s*\([^)]*" + escaped, text, re.DOTALL):
            individual += 1
    best = max(best, individual)

    assert best >= 3, (
        f"Only {best}/4 versions found in separate test registrations; "
        "expected at least 3 parameterised individually"
    )


# [pr_diff] pass_to_pass
def test_substantive_bodies():
    """Invalid-version test bodies contain Bun.spawn + await exited + expect (not stubs)."""
    text = _read_test_file()

    # Grab the region around invalid version strings (±1000 chars)
    invalid_region = ""
    for v in INVALID_VERSIONS:
        idx = text.find(v)
        if idx != -1:
            start = max(0, idx - 1000)
            end = min(len(text), idx + 1000)
            invalid_region += text[start:end]

    assert invalid_region, "No invalid version strings found in file"
    assert "Bun.spawn" in invalid_region, (
        "No Bun.spawn found near invalid version tests — bodies may be stubs"
    )
    assert ".exited" in invalid_region, (
        "No .exited await found near invalid version tests"
    )
    assert re.search(r"expect\s*\(", invalid_region), (
        "No expect assertion found near invalid version test bodies"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_all_invalid_versions_present():
    """All 5 invalid version strings must still be tested."""
    text = _read_test_file()
    for v in INVALID_VERSIONS:
        assert v in text, f"Invalid version string {v!r} missing from test file"
    # Empty string: must appear as "" in some version context
    assert '""' in text or "version: ''" in text, "Empty string version case missing"


# [pr_diff] pass_to_pass
def test_exit_code_assertion():
    """Non-zero exit code assertion must be preserved."""
    text = _read_test_file()
    patterns = [
        r"expect\s*\(\s*\w*[Ee]xit[Cc]ode\w*\s*\)\s*\.not\s*\.toBe\s*\(\s*0\s*\)",
        r"expect\s*\(\s*\w*[Ee]xit[Cc]ode\w*\s*\)\s*\.toBeGreaterThan\s*\(\s*0\s*\)",
        r"expect\s*\(\s*\w*[Ee]xit[Cc]ode\w*\s*\)\s*\.toBeTruthy",
        r"[Ee]xit[Cc]ode\s*!==?\s*0",
    ]
    assert any(re.search(p, text) for p in patterns), (
        "No non-zero exit code assertion found"
    )


# [pr_diff] pass_to_pass
def test_valid_version_tests_intact():
    """Valid version parsing tests (1.0.0.0, 2.0.0.0, 3.0.0.0) must remain."""
    text = _read_test_file()
    assert "1.0.0.0" in text, "Valid version test for 1.0.0.0 missing"
    assert "2.0.0.0" in text, "Valid version test for 2.0.0.0 missing"
    assert "3.0.0.0" in text, "Valid version test for 3.0.0.0 missing"


# [pr_diff] pass_to_pass
def test_describe_structure_preserved():
    """Main describe blocks (Windows/compile/metadata + CLI flags) must remain."""
    text = _read_test_file()
    assert re.search(r"describe\s*[.(].*(?:Windows|compile|metadata)", text, re.I), (
        "Main Windows/compile/metadata describe block missing"
    )
    assert re.search(r"describe\s*[.(].*(?:CLI|flags)", text, re.I), (
        "CLI flags describe block missing"
    )


# [pr_diff] pass_to_pass
def test_other_tests_preserved():
    """Other test blocks (all metadata flags, partial metadata flags) must remain."""
    text = _read_test_file()
    assert re.search(r"(?:all|every)\s+metadata\s+flags", text, re.I), (
        "'all metadata flags' test block missing"
    )
    assert re.search(r"partial\s+metadata\s+flags", text, re.I), (
        "'partial metadata flags' test block missing"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — test/AGENTS.md:4265 @ a04817ce2b7f
def test_no_flaky_patterns():
    """No setTimeout or sleep calls should be added (anti-flake)."""
    text = _read_test_file()
    assert not re.search(r"(?:setTimeout|sleep)\s*\(", text), (
        "Flaky setTimeout/sleep pattern detected"
    )


# [agent_config] pass_to_pass — test/AGENTS.md:4266 @ a04817ce2b7f
def test_concurrent_pattern_preserved():
    """describe.concurrent (or skipIf().concurrent) must remain."""
    text = _read_test_file()
    assert re.search(r"\.concurrent\s*\(", text), (
        "describe.concurrent pattern missing"
    )


# [agent_config] pass_to_pass — test/AGENTS.md:4364 @ a04817ce2b7f
def test_no_test_timeout():
    """No explicit test timeout set — Bun already has timeouts."""
    text = _read_test_file()
    assert not re.search(r"\.timeout\s*\(\s*\d", text), (
        "Explicit .timeout() call detected — Bun already has timeouts"
    )
    assert not re.search(r"jest\.setTimeout\s*\(", text), (
        "jest.setTimeout() detected — Bun already has timeouts"
    )


# [agent_config] pass_to_pass — test/AGENTS.md:4272 @ a04817ce2b7f
def test_uses_harness_helpers():
    """Test file must use bunExe() and bunEnv from harness for spawning bun."""
    text = _read_test_file()
    assert "bunExe" in text, "bunExe() not used — must use harness helper for bun path"
    assert "bunEnv" in text, "bunEnv not used — must use harness helper for env"
    assert "tempDir" in text, "tempDir not used — must use harness helper for temp dirs"
