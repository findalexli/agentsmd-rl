"""
Task: bun-listen-empty-hostname-crash
Repo: oven-sh/bun @ 73361607d70bd77041d0fc20e45a6dbe2373a677
PR:   28426

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Behavioral tests: where possible, execute the code and verify output/behavior.
For Zig code that requires full build toolchain, structural checks are used but
made solution-unique by checking for error-pattern categories, not gold-specific names.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/bun"
ZIG_FILE = f"{REPO}/src/bun.js/api/bun/socket/Handlers.zig"
TEST_FILE = f"{REPO}/test/js/bun/net/socket.test.ts"


def _run_bun(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Bun in the repo directory."""
    return subprocess.run(
        ["bun", "-e", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


def _zig_syntax_valid(path: str) -> bool:
    """Check if Zig file has valid syntax (no parse errors)."""
    r = subprocess.run(
        ["zig", "fmt", "--check", path],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    if r.returncode != 0:
        stderr_lower = r.stderr.lower()
        if "parse error" in stderr_lower or "error:" in stderr_lower:
            return False
    return True


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- behavioral + structural checks
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_hostname_crash_fixed():
    """Hostname assertf removed and replaced with proper error return."""
    code = Path(ZIG_FILE).read_text()

    lines = [l for l in code.splitlines()
             if l.strip() and not l.strip().startswith("//")]
    assert len(lines) >= 100, (
        f"Handlers.zig appears stubbed ({len(lines)} non-comment lines)"
    )

    try:
        syntax_ok = _zig_syntax_valid(ZIG_FILE)
    except Exception:
        syntax_ok = True

    # Detect the crash pattern: assertf with length() > 0 on a truthy string
    crash_pattern = re.compile(
        r'assertf\s*\([^)]*\blength\s*\(\s*\)\s*>\s*0[^)]*"truthy',
        re.IGNORECASE
    )
    has_crash = bool(crash_pattern.search(code))
    assert not has_crash, "hostname assertf crash pattern still present in code"

    hostname_match = re.search(
        r'generated\.hostname\.get\s*\(\s*\)\s*\|hostname\|\s*\{[^}]*\}',
        code, re.DOTALL
    )
    if hostname_match:
        section = hostname_match.group(0)
        has_empty_check = bool(re.search(r'length\s*\(\s*\)\s*==\s*0', section))
        has_return = 'return' in section
        has_error_return = has_empty_check and has_return
        assert has_error_return, (
            "hostname section missing early-return for empty string. "
            "Expected: if (hostname.length() == 0) return ...;"
        )
    else:
        assert not ('assertf' in code and 'length() > 0' in code), \
            "assertf with length() > 0 still present"


# [pr_diff] fail_to_pass
def test_unix_crash_fixed():
    """Unix path assertf removed and replaced with proper error return."""
    code = Path(ZIG_FILE).read_text()

    lines = [l for l in code.splitlines()
             if l.strip() and not l.strip().startswith("//")]
    assert len(lines) >= 100, (
        f"Handlers.zig appears stubbed ({len(lines)} non-comment lines)"
    )

    try:
        syntax_ok = _zig_syntax_valid(ZIG_FILE)
    except Exception:
        syntax_ok = True

    crash_pattern = re.compile(
        r'assertf\s*\([^)]*\blength\s*\(\s*\)\s*>\s*0[^)]*"truthy',
        re.IGNORECASE
    )
    has_crash = bool(crash_pattern.search(code))
    assert not has_crash, "unix assertf crash pattern still present in code"

    unix_match = re.search(
        r'generated\.unix[_\s]*\.get\s*\(\s*\)\s*\|unix[_\s]*\|\s*\{[^}]*\}',
        code, re.DOTALL
    )
    if unix_match:
        section = unix_match.group(0)
        has_empty_check = bool(re.search(r'length\s*\(\s*\)\s*==\s*0', section))
        has_return = 'return' in section
        has_error_return = has_empty_check and has_return
        assert has_error_return, (
            "unix section missing early-return for empty string. "
            "Expected: if (unix.length() == 0) return ...;"
        )
    else:
        assert not ('assertf' in code and 'length() > 0' in code), \
            "assertf with length() > 0 still present"


# [pr_diff] fail_to_pass
def test_throw_tests_added():
    """Agent added tests verifying throw on truthy-but-empty hostname/unix.

    Behavioral approach: verify the test code exists and actually throws correctly.
    """
    p = Path(TEST_FILE)
    assert p.exists(), f"{TEST_FILE} does not exist"
    lines = p.read_text().splitlines()
    assert len(lines) > 500, (
        f"socket.test.ts has only {len(lines)} lines -- likely truncated"
    )

    # Check file contains test code for the new behavior
    text = p.read_text()

    # Must have test for hostname throwing
    assert "should throw on empty hostname from truthy non-string value" in text, (
        "hostname throw test not found in socket.test.ts"
    )

    # Must have test for unix throwing
    assert "should throw on empty unix path from truthy non-string value" in text, (
        "unix throw test not found in socket.test.ts"
    )

    # Must reference Bun.listen and/or Bun.connect
    lower = text.lower()
    assert "bun.listen" in lower or "bun.connect" in lower, (
        "No Bun.listen/Bun.connect usage found"
    )

    # Must use toThrow/reject patterns
    assert "tothrow" in lower or "throw" in lower, (
        "No throw assertion found in test file"
    )

    # Behavioral verification: run inline test to verify the fix works
    # This actually EXECUTES the code (subprocess) and checks behavior
    r = _run_bun(r"""
    const socket = { data() {}, open() {}, close() {} };
    try {
        Bun.listen({ hostname: [], port: 0, socket });
        console.log('NO_THROW');
    } catch (e) {
        if (e.message.includes('Expected a non-empty')) {
            console.log('THREW_CORRECT');
        } else {
            console.log('THREW_OTHER: ' + e.message);
        }
    }
    """)
    output = (r.stdout + r.stderr).strip()
    # The fix must produce the correct error message (not crash, not wrong error)
    assert "THREW_CORRECT" in output, (
        f"Fix does not produce correct error. Output: {output}. "
        "Expected: 'Expected a non-empty' error"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static / pr_diff) -- anti-stub and regression
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_handlers_not_stubbed():
    """Handlers.zig is substantial, not gutted or replaced with stub."""
    p = Path(ZIG_FILE)
    assert p.exists(), f"{ZIG_FILE} does not exist"
    lines = p.read_text().splitlines()
    assert len(lines) >= 200, (
        f"Handlers.zig has only {len(lines)} lines -- likely stubbed"
    )


# [pr_diff] pass_to_pass
def test_hostname_unix_branches_preserved():
    """Both hostname and unix handling branches still exist."""
    text = Path(ZIG_FILE).read_text()
    has_hostname = "hostname" in text and (
        "generated.hostname" in text or "hostname.get" in text
        or "hostname_or_unix" in text
    )
    has_unix = "unix" in text and (
        "generated.unix" in text or "unix.get" in text or "unix_" in text
    )
    assert has_hostname, "hostname handling branch deleted from Handlers.zig"
    assert has_unix, "unix handling branch deleted from Handlers.zig"


# [pr_diff] pass_to_pass
def test_socket_test_file_preserved():
    """socket.test.ts not truncated or deleted."""
    p = Path(TEST_FILE)
    assert p.exists(), f"{TEST_FILE} does not exist"
    lines = p.read_text().splitlines()
    assert len(lines) > 500, (
        f"socket.test.ts has only {len(lines)} lines -- likely truncated"
    )


# ---------------------------------------------------------------------------
# Repo CI/CD (pass_to_pass) -- repo's own tests, lints, typechecks
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_repo_lint():
    """Repo's JS linting passes (oxlint on src/js)."""
    r = subprocess.run(
        ["bunx", "oxlint", "src/js"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_prettier_socket_test():
    """Repo's prettier formatting passes on socket.test.ts."""
    r = subprocess.run(
        ["bunx", "prettier", "--check", "test/js/bun/net/socket.test.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ban_words():
    """Repo's banned words check passes."""
    r = subprocess.run(
        ["bun", "./test/internal/ban-words.test.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ban words check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_typecheck():
    """Repo's TypeScript typecheck passes."""
    r = subprocess.run(
        ["bunx", "tsc", "--noEmit"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_node_works():
    """Node.js is available and functional in the repo."""
    r = subprocess.run(
        ["node", "-e", "console.log('NODE_WORKS')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Node check failed: {r.stderr}"
    assert "NODE_WORKS" in r.stdout, "Node did not execute correctly"


# [repo_tests] pass_to_pass
def test_repo_bun_works():
    """Bun is available and functional in the repo."""
    r = subprocess.run(
        ["bun", "--version"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Bun check failed: {r.stderr}"
    assert r.stdout.strip(), "Bun version not returned"


# [repo_tests] pass_to_pass
def test_repo_package_json_lint():
    """Repo's package.json lint passes (exact versions check)."""
    r = subprocess.run(
        ["bun", "test", "test/package-json-lint.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Package JSON lint failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [agent_config] pass_to_pass - AGENTS.md:99
def test_no_panic_absence_tests():
    """New tests don't check for absence of 'panic' or 'uncaught exception'."""
    p = Path(TEST_FILE)
    if not p.exists():
        return
    text = p.read_text()
    tail = "\n".join(text.splitlines()[-100:]).lower()
    has_panic_check = (
        "not" in tail
        and ("panic" in tail or "uncaught exception" in tail)
        and ("tothrow" in tail or "tocontain" in tail or "tomatch" in tail)
    )
    assert not has_panic_check, (
        "Tests check for absence of 'panic'/'uncaught exception' -- "
        "AGENTS.md says these tests will never fail in CI"
    )
