"""
Task: bun-compile-metadata-version-deflake
Repo: oven-sh/bun @ a04817ce2b7f1a1e8b7cbf8af8f2c027ab072f1d
PR:   #28205

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Node.js is used to parse and evaluate the TypeScript test file structure.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/bun")
TEST_FILE = REPO / "test/bundler/compile-windows-metadata.test.ts"

EXPECTED_INVALID_VERSIONS = ["not.a.version", "1.2.3.4.5", "1.-2.3.4", "65536.0.0.0", ""]


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via a temp file with Node.js."""
    script = REPO / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=str(REPO),
        )
    finally:
        script.unlink(missing_ok=True)


def _read_test_file() -> str:
    assert TEST_FILE.exists(), f"{TEST_FILE} does not exist"
    text = TEST_FILE.read_text()
    assert len(text.splitlines()) >= 280, (
        f"File too short ({len(text.splitlines())} lines); likely truncated or gutted"
    )
    return text


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests using subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_loop_removed():
    """The sequential for-loop over invalidVersions with Bun.spawn must be removed."""
    r = _run_node("""\
import { readFileSync } from 'fs';

const text = readFileSync('test/bundler/compile-windows-metadata.test.ts', 'utf8');

// Check 1: No for...of loop iterating over invalidVersions
if (/for\\s*\\(\\s*(?:const|let|var)\\s+\\w+\\s+of\\s+invalidVersions/.test(text)) {
  console.error('FAIL: for...of loop over invalidVersions still present');
  process.exit(1);
}

// Check 2: No invalidVersions array declaration
if (/(?:const|let|var)\\s+invalidVersions\\s*=\\s*\\[/.test(text)) {
  console.error('FAIL: invalidVersions array variable still present');
  process.exit(1);
}

// Check 3: No for-loop body that calls Bun.spawn (the core flaky pattern)
if (/for\\s*\\([^)]*\\)\\s*\\{[\\s\\S]*?Bun\\.spawn/.test(text)) {
  console.error('FAIL: for-loop containing Bun.spawn calls still present');
  process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Loop check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_versions_parameterized():
    """Each invalid version gets its own test case via test.each with correct versions."""
    r = _run_node("""\
import { readFileSync } from 'fs';

const text = readFileSync('test/bundler/compile-windows-metadata.test.ts', 'utf8');

// Find test.each([...]) or it.each([...])
const match = text.match(/(?:test|it)\\.each\\s*\\(\\s*(\\[[\\s\\S]*?\\])\\s*\\)/);
if (!match) {
  console.error('FAIL: No test.each() or it.each() found');
  process.exit(1);
}

// Strip comments and evaluate the array as real JavaScript
let arrayStr = match[1]
  .replace(/\\/\\/.*$/gm, '')
  .trim();

let arr;
try {
  arr = eval(arrayStr);
} catch (e) {
  console.error('FAIL: test.each array is not valid JS: ' + e.message);
  process.exit(1);
}

if (!Array.isArray(arr) || arr.length === 0) {
  console.error('FAIL: test.each argument is not a non-empty array');
  process.exit(1);
}

// Verify every entry has a 'version' string property
const versions = arr.map(item => {
  if (!item || typeof item.version !== 'string') {
    console.error('FAIL: entry missing string "version" property: ' + JSON.stringify(item));
    process.exit(1);
  }
  return item.version;
});

const expected = ['not.a.version', '1.2.3.4.5', '1.-2.3.4', '65536.0.0.0', ''];

for (const v of expected) {
  if (!versions.includes(v)) {
    console.error('FAIL: Missing version: ' + JSON.stringify(v) + '. Got: ' + JSON.stringify(versions));
    process.exit(1);
  }
}

if (versions.length !== expected.length) {
  console.error('FAIL: Expected ' + expected.length + ' versions, got ' + versions.length);
  process.exit(1);
}

// Verify test name references $version for proper reporting
const afterEach = text.slice(text.indexOf(match[0]) + match[0].length);
if (!afterEach.includes('$version')) {
  console.error('FAIL: test.each test name does not reference $version');
  process.exit(1);
}

console.log(JSON.stringify({ count: arr.length, versions }));
""")
    assert r.returncode == 0, f"Parameterization check failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["count"] == 5, f"Expected 5 versions, got {data['count']}"


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


# [pr_diff] pass_to_pass
def test_substantive_bodies():
    """Invalid-version test bodies contain Bun.spawn + await exited + expect (not stubs)."""
    text = _read_test_file()

    invalid_region = ""
    for v in EXPECTED_INVALID_VERSIONS:
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
    for v in EXPECTED_INVALID_VERSIONS:
        assert v in text, f"Invalid version string {v!r} missing from test file"
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


# [agent_config] pass_to_pass — test/AGENTS.md:100 @ a04817ce2b7f
def test_uses_await_using_for_proc():
    """Bun.spawn calls must use 'await using' for automatic resource cleanup."""
    text = _read_test_file()
    spawn_calls = list(re.finditer(r"Bun\.spawn\s*\(", text))
    assert spawn_calls, "No Bun.spawn calls found in test file"
    for m in spawn_calls:
        start = max(0, m.start() - 100)
        prefix = text[start : m.end()]
        assert re.search(r"await\s+using\s+\w+\s*=\s*Bun\.spawn", prefix), (
            "Bun.spawn not assigned with 'await using' — "
            "use 'await using proc = Bun.spawn(...)' for resource cleanup"
        )
