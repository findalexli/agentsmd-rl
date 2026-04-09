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
import re
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
    # Check that key shell files exist at the base commit
    shell_files = [
        "src/shell/shell.zig",
        "src/shell/Builtin.zig",
        "src/shell/states/Cmd.zig",
        "src/shell/interpreter.zig",
    ]
    for file_path in shell_files:
        full_path = Path(f"{REPO}/{file_path}")
        assert full_path.exists(), f"{file_path} must exist"

    # Check shell.zig has expected re-exports
    shell_zig = Path(f"{REPO}/src/shell/shell.zig").read_text()
    assert "@import(\"./interpreter.zig\")" in shell_zig, "Must import interpreter"
    assert "@import(\"bun\")" in shell_zig or "const bun" in shell_zig, "Must reference bun"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests (source code verification)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_sentinel_bun_prefix_roundtrip():
    """
    Strings with sentinel + __bun_ prefix must round-trip through shell interpolation.

    At base commit: The lexer.new() function lacks jsobjs_len parameter needed for
    proper bounds checking of sentinel strings.
    After fix: Lexer.new() has jsobjs_len parameter for proper validation.
    """
    shell_zig = Path(f"{REPO}/src/shell/shell.zig").read_text()

    # The fix adds jsobjs_len as 4th parameter to Lexer.new
    # Base commit: pub fn new(alloc: Allocator, src: []const u8, strings_to_escape: []bun.String)
    # After fix:   pub fn new(alloc: Allocator, src: []const u8, strings_to_escape: []bun.String, jsobjs_len: u32)

    # Check that the fix is applied - jsobjs_len parameter must be present
    new_sig_pattern = r'pub\s+fn\s+new\s*\([^)]*jsobjs_len\s*:\s*u32[^)]*\)'
    has_jsobjs_len = re.search(new_sig_pattern, shell_zig) is not None

    # Also check for jsobjs_len field in Lexer struct
    struct_field_pattern = r'jsobjs_len\s*:\s*u32'
    has_struct_field = re.search(struct_field_pattern, shell_zig) is not None

    assert has_jsobjs_len and has_struct_field, \
        "Lexer must have jsobjs_len parameter and field for proper bounds checking"


# [pr_diff] fail_to_pass
def test_sentinel_bunstr_prefix_roundtrip():
    """
    Strings with sentinel + __bunstr_ prefix must round-trip through shell interpolation.

    At base commit: Interpreter passes only 3 args to Lexer.new (missing jsobjs_len).
    After fix: Interpreter passes jsobjs_len as 4th argument to Lexer.new.
    """
    interpreter_zig = Path(f"{REPO}/src/shell/interpreter.zig").read_text()

    # The fix updates lexer calls to pass jsobjs_len as 4th argument
    # Base commit: LexerAscii.new(arena_allocator, script, jsstrings_to_escape)
    # After fix:   LexerAscii.new(arena_allocator, script, jsstrings_to_escape, jsobjs_len)

    # Check for jsobjs_len calculation in interpreter
    has_jsobjs_calc = 'jsobjs_len: u32 = @intCast(jsobjs.len)' in interpreter_zig or \
                      'const jsobjs_len: u32 = @intCast(jsobjs.len)' in interpreter_zig

    # Check for updated lexer calls with 4 arguments
    lexer_call_pattern = r'Lexer(?:Ascii|Unicode)\.new\([^,]+,\s*[^,]+,\s*[^,]+,\s*jsobjs_len\s*\)'
    has_updated_calls = re.search(lexer_call_pattern, interpreter_zig) is not None

    assert has_jsobjs_calc and has_updated_calls, \
        "Interpreter must calculate and pass jsobjs_len to lexer for proper bounds checking"


# [pr_diff] fail_to_pass
def test_raw_sentinel_no_crash():
    """
    Raw sentinel injection with out-of-bounds index must not crash - should error gracefully.

    At base commit: validateJSObjRefIdx checks against maxInt(u32) instead of jsobjs_len.
    After fix: validateJSObjRefIdx checks idx >= self.jsobjs_len.

    Also, Builtin.zig and Cmd.zig must have bounds checking for JS object references.
    """
    shell_zig = Path(f"{REPO}/src/shell/shell.zig").read_text()
    builtin_zig = Path(f"{REPO}/src/shell/Builtin.zig").read_text()
    cmd_zig = Path(f"{REPO}/src/shell/states/Cmd.zig").read_text()

    # Check shell.zig: validateJSObjRefIdx should use jsobjs_len not maxInt(u32)
    # Base commit: if (idx >= std.math.maxInt(u32))
    # After fix:   if (idx >= self.jsobjs_len)
    validate_func = re.search(
        r'fn\s+validateJSObjRefIdx\s*\([^)]*\)\s*bool\s*\{[^}]*if\s*\(\s*idx\s*>=\s*([^)]+)\)',
        shell_zig,
        re.DOTALL
    )
    if validate_func:
        bound_check = validate_func.group(1).strip()
        uses_jsobjs_len = 'jsobjs_len' in bound_check and 'maxInt' not in bound_check
    else:
        # Try simpler pattern
        uses_jsobjs_len = 'idx >= self.jsobjs_len' in shell_zig

    # Check Builtin.zig has bounds check
    builtin_check = 'idx >= interpreter.jsobjs.len' in builtin_zig or \
                    'file.jsbuf.idx >= interpreter.jsobjs.len' in builtin_zig or \
                    'jsbuf.idx >= interpreter.jsobjs.len' in builtin_zig

    # Check Cmd.zig has bounds check
    cmd_check = 'val.idx >= this.base.interpreter.jsobjs.len' in cmd_zig or \
                'idx >= this.base.interpreter.jsobjs.len' in cmd_zig

    assert uses_jsobjs_len, \
        "validateJSObjRefIdx must check against jsobjs_len, not maxInt(u32)"
    assert builtin_check, \
        "Builtin.zig must have bounds check for JS object references"
    assert cmd_check, \
        "Cmd.zig must have bounds check for JS object references"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_shell_escape_api_works():
    """$.escape() API should continue to work correctly as a regression test."""
    script = '''
import { $ } from "bun";

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
    """Check that modified functions have proper structure for bounds checking."""
    # At the base commit, we verify the files have the expected structure
    # After the fix, these will have the jsobjs_len parameter

    # Check Builtin.zig has initRedirections function
    builtin_zig = Path(f"{REPO}/src/shell/Builtin.zig").read_text()
    assert "initRedirections" in builtin_zig, "Builtin.zig must have initRedirections function"
    assert ".jsbuf" in builtin_zig or "jsbuf" in builtin_zig, "Builtin.zig must handle jsbuf"

    # Check Cmd.zig has initRedirections function
    cmd_zig = Path(f"{REPO}/src/shell/states/Cmd.zig").read_text()
    assert "initRedirections" in cmd_zig, "Cmd.zig must have initRedirections function"
    assert ".jsbuf" in cmd_zig or "jsbuf" in cmd_zig, "Cmd.zig must handle jsbuf"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks that should pass on base commit
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_banned_words():
    """Repo banned words check passes (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c",
         "apt-get update -qq && apt-get install -y -qq unzip >/dev/null 2>&1 && "
         "curl -fsSL https://bun.sh/install | bash >/dev/null 2>&1 && "
         "export PATH=\"/root/.bun/bin:$PATH\" && "
         "bun install >/dev/null 2>&1 && "
         "bun test test/internal/ban-words.test.ts"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Banned words test failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_modified_shell_files_exist():
    """Modified shell Zig files exist and are readable (pass_to_pass)."""
    files_to_check = [
        "src/shell/shell.zig",
        "src/shell/Builtin.zig",
        "src/shell/states/Cmd.zig",
        "src/shell/interpreter.zig",
    ]
    for file_path in files_to_check:
        full_path = Path(f"{REPO}/{file_path}")
        assert full_path.exists(), f"{file_path} must exist"
        content = full_path.read_text()
        assert len(content) > 0, f"{file_path} must not be empty"


# [repo_tests] pass_to_pass
def test_repo_shell_zig_has_structure():
    """Basic check that shell Zig files have valid structure (pass_to_pass)."""
    # Check interpreter.zig has expected structure
    interpreter_zig = Path(f"{REPO}/src/shell/interpreter.zig").read_text()
    assert "pub const Interpreter" in interpreter_zig or "Interpreter" in interpreter_zig, "Interpreter must be defined"
    assert "@import(\"std\")" in interpreter_zig, "Must import std"


# [repo_tests] pass_to_pass
def test_repo_shell_file_tests():
    """Repo's Bun shell file tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "test", "test/js/bun/shell/bunshell-file.test.ts", "--timeout", "30"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
        env={**os.environ, "PATH": f"/root/.bun/bin:{os.environ.get('PATH', '')}"}
    )
    assert r.returncode == 0, f"Shell file tests failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_shell_instance_tests():
    """Repo's Bun shell instance tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "test", "test/js/bun/shell/bunshell-instance.test.ts", "--timeout", "30"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
        env={**os.environ, "PATH": f"/root/.bun/bin:{os.environ.get('PATH', '')}"}
    )
    assert r.returncode == 0, f"Shell instance tests failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_run_shell_tests():
    """Repo's CLI run-shell tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "test", "test/cli/run/run-shell.test.ts", "--timeout", "30"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
        env={**os.environ, "PATH": f"/root/.bun/bin:{os.environ.get('PATH', '')}"}
    )
    assert r.returncode == 0, f"CLI run-shell tests failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["bunx", "tsc", "--noEmit", "--project", "tsconfig.json"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
        env={**os.environ, "PATH": f"/root/.bun/bin:{os.environ.get('PATH', '')}"}
    )
    assert r.returncode == 0, f"TypeScript typecheck failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"
