"""
Task: bun-harden-shell-sentinel-validation
Repo: bun @ f06119ad0cd49bba93908329ef5e53a39c50fb70
PR:   27506

Shell sentinel byte hardening - prevents injection vulnerabilities and out-of-bounds access.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import tempfile
import os
from pathlib import Path

REPO = "/workspace/bun"
BUN = "bun"


def _run_bun_ts(script_content: str, timeout: int = 30) -> tuple[int, str, str]:
    """Run a TypeScript script using bun and return (exit_code, stdout, stderr)."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ts', delete=False) as f:
        f.write(script_content)
        f.flush()
        tmp_path = f.name

    try:
        result = subprocess.run(
            [BUN, "run", tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=REPO
        )
        return result.returncode, result.stdout, result.stderr
    finally:
        os.unlink(tmp_path)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified shell Zig files must exist and contain expected structural elements."""
    shell_zig = Path(f"{REPO}/src/shell/shell.zig")
    assert shell_zig.exists(), "shell.zig must exist"

    content = shell_zig.read_text()
    # Verify key structural elements exist
    assert "jsobjs_len: u32" in content, "jsobjs_len field must be present"
    assert "validateJSObjRefIdx" in content, "validateJSObjRefIdx function must exist"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_sentinel_bun_prefix_roundtrip():
    """Strings with sentinel + __bun_ prefix must round-trip through shell interpolation."""
    # \x08 is the internal sentinel byte. When followed by "__bun_" and non-digits,
    # the old code didn't escape \x08, causing lex errors.
    script = '''
import { $ } from "bun";

const str = "\\x08__bun_abc";
const result = await $`echo ${str}`.text();
if (result.trim() !== str) {
    console.error(`FAIL: expected "${str}" but got "${result.trim()}"`);
    process.exit(1);
}
console.log("OK");
'''
    exit_code, stdout, stderr = _run_bun_ts(script)
    assert exit_code == 0, f"Test failed with exit {exit_code}: {stderr}"
    assert "OK" in stdout, f"Expected OK in output, got: {stdout}"


# [pr_diff] fail_to_pass
def test_sentinel_bunstr_prefix_roundtrip():
    """Strings with sentinel + __bunstr_ prefix must round-trip through shell interpolation."""
    script = '''
import { $ } from "bun";

const str = "\\x08__bunstr_xyz";
const result = await $`echo ${str}`.text();
if (result.trim() !== str) {
    console.error(`FAIL: expected "${str}" but got "${result.trim()}"`);
    process.exit(1);
}
console.log("OK");
'''
    exit_code, stdout, stderr = _run_bun_ts(script)
    assert exit_code == 0, f"Test failed with exit {exit_code}: {stderr}"
    assert "OK" in stdout, f"Expected OK in output, got: {stdout}"


# [pr_diff] fail_to_pass
def test_raw_sentinel_no_crash():
    """Raw sentinel injection with out-of-bounds index must not crash - should error gracefully."""
    # { raw: ... } bypasses escaping, allowing injection of sentinel patterns.
    # Old code only checked idx >= maxInt(u32), so idx 9999 on empty array caused segfault.
    # Fix checks against actual jsobjs_len and throws an error.
    script = '''
import { $ } from "bun";

// Create a sentinel pattern with out-of-bounds index
const sentinel = String.fromCharCode(8) + "__bun_9999";

try {
    // This should throw an error, not crash
    await $`echo hello > ${{ raw: sentinel }}`;
    // If we get here without error, that's also acceptable (may be handled differently)
    console.log("OK");
} catch (e) {
    // Error is expected - the fix should cause an error to be thrown
    console.log("OK");
}
'''
    exit_code, stdout, stderr = _run_bun_ts(script)
    # The test should complete without crashing - either exit 0 with OK
    assert exit_code == 0, f"Process crashed or failed unexpectedly: exit={exit_code}, stderr={stderr}"
    assert "OK" in stdout, f"Expected OK in output, got: {stdout}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_shell_escape_api_works():
    """$.escape() API should continue to work correctly as a regression test."""
    script = '''
import { $ } from "bun";

// Test that $.escape properly handles special characters
const escaped = $.escape("hello world");
if (typeof escaped !== "string") {
    console.error("$.escape should return a string");
    process.exit(1);
}
console.log("OK");
'''
    exit_code, stdout, stderr = _run_bun_ts(script)
    assert exit_code == 0, f"$.escape test failed: {stderr}"
    assert "OK" in stdout, f"Expected OK in output, got: {stdout}"


# [static] pass_to_pass
def test_bounds_check_logic_present():
    """Modified functions have real bounds-checking logic with proper error messages."""
    # Check shell.zig for jsobjs_len parameter
    shell_zig = Path(f"{REPO}/src/shell/shell.zig").read_text()

    # validateJSObjRefIdx should check against jsobjs_len, not maxInt(u32)
    assert "self.jsobjs_len" in shell_zig, "validateJSObjRefIdx must check jsobjs_len"

    # SPECIAL_CHARS should include SPECIAL_JS_CHAR (sentinel)
    assert "SPECIAL_JS_CHAR" in shell_zig, "SPECIAL_CHARS must include SPECIAL_JS_CHAR"

    # Check Builtin.zig for bounds check
    builtin_zig = Path(f"{REPO}/src/shell/Builtin.zig").read_text()
    assert "Invalid JS object reference in shell" in builtin_zig, \
        "Builtin.zig must have bounds check with error message"

    # Check Cmd.zig for bounds check
    cmd_zig = Path(f"{REPO}/src/shell/states/Cmd.zig").read_text()
    assert "Invalid JS object reference in shell" in cmd_zig, \
        "Cmd.zig must have bounds check with error message"
