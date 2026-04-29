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
        has_return = 'return' in section
        has_error_return = has_return
        assert has_error_return, (
            "hostname section missing early-return for empty string. "
            "Expected: some emptiness check followed by return ...;"
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

    # Check that unix section has a return statement (error return pattern).
    unix_section_pattern = re.compile(
        r'generated\.unix[_\s]*\.get\s*\(\s*\)\s*\|[^|]+\|\s*\{([^}]*)\}',
        re.DOTALL
    )
    unix_match = unix_section_pattern.search(code)
    if unix_match:
        section_content = unix_match.group(1)
        assert 'return' in section_content, (
            "unix section missing early-return for empty string. "
            "Expected: some emptiness check followed by return ...;"
        )
    else:
        assert not ('assertf' in code and 'length() > 0' in code), \
            "assertf with length() > 0 still present"


# [pr_diff] fail_to_pass
def test_throw_tests_added():
    """Agent added tests verifying throw on truthy-but-empty hostname/unix."""
    p = Path(TEST_FILE)
    assert p.exists(), f"{TEST_FILE} does not exist"
    lines = p.read_text().splitlines()
    assert len(lines) > 500, (
        f"socket.test.ts has only {len(lines)} lines -- likely truncated"
    )

    text = p.read_text()

    # The new test must contain the "Expected a non-empty" error message substring
    # that the fix produces (named in the task instruction)
    assert "Expected a non-empty" in text, (
        "No test for 'Expected a non-empty' error message found in socket.test.ts. "
        "Add tests verifying the descriptive error message."
    )

    # Must reference Bun.listen and Bun.connect
    lower = text.lower()
    assert "bun.listen" in lower, "No Bun.listen usage found in test file"
    assert "bun.connect" in lower, "No Bun.connect usage found in test file"

    # Must use toThrow assertion patterns
    assert "tothrow" in lower, (
        "No toThrow assertion found in test file"
    )

    # Behavioral verification: Bun.listen with [] hostname must throw (not crash)
    r = _run_bun(r"""
    const socket = { data() {}, open() {}, close() {} };
    try {
        Bun.listen({ hostname: [], port: 0, socket });
        console.log('NO_THROW');
    } catch (e) {
        const msg = e.message.toLowerCase();
        if (msg.includes('non-empty') || (msg.includes('empty') && msg.includes('hostname'))) {
            console.log('THREW_CORRECT');
        } else {
            console.log('THREW_OTHER: ' + e.message);
        }
    }
    """)
    output = (r.stdout + r.stderr).strip()
    assert "THREW_CORRECT" in output, (
        f"Fix does not produce correct error. Output: {output}. "
        "Expected: descriptive error about non-empty hostname"
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


# [agent_config] pass_to_pass - AGENTS.md:102 / CLAUDE.md:97
def test_no_hardcoded_ports():
    """New test code does not use hardcoded port numbers — uses port: 0 instead."""
    p = Path(TEST_FILE)
    assert p.exists(), f"{TEST_FILE} does not exist"
    # Check the tail of the file (where new tests are added) for hardcoded ports
    lines = p.read_text().splitlines()
    tail = "\n".join(lines[-40:])
    # Any port: <non-zero-number> in the tail is a hardcoded port violation
    hardcoded = re.findall(r'port:\s*[1-9]\d*', tail)
    assert not hardcoded, (
        f"Hardcoded port(s) found in new test code (use port: 0): {hardcoded}"
    )


# [agent_config] pass_to_pass - AGENTS.md:102
def test_no_settimeout_in_new_tests():
    """New test code does not use setTimeout — awaits conditions instead."""
    p = Path(TEST_FILE)
    assert p.exists(), f"{TEST_FILE} does not exist"
    lines = p.read_text().splitlines()
    tail = "\n".join(lines[-40:]).lower()
    assert "settimeout" not in tail, (
        "setTimeout found in new test code. Use await + conditions instead."
    )

# === PR-added f2p tests (taskforge.test_patch_miner) ===
def test_pr_added_should_throw_on_empty_hostname_from_truthy_non_s():
    """fail_to_pass | PR added test 'should throw on empty hostname from truthy non-string value' in 'test/js/bun/net/socket.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "test/js/bun/net/socket.test.ts" -t "should throw on empty hostname from truthy non-string value" 2>&1 || npx vitest run "test/js/bun/net/socket.test.ts" -t "should throw on empty hostname from truthy non-string value" 2>&1 || pnpm jest "test/js/bun/net/socket.test.ts" -t "should throw on empty hostname from truthy non-string value" 2>&1 || npx jest "test/js/bun/net/socket.test.ts" -t "should throw on empty hostname from truthy non-string value" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'should throw on empty hostname from truthy non-string value' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_should_throw_on_empty_unix_path_from_truthy_non_():
    """fail_to_pass | PR added test 'should throw on empty unix path from truthy non-string value' in 'test/js/bun/net/socket.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "test/js/bun/net/socket.test.ts" -t "should throw on empty unix path from truthy non-string value" 2>&1 || npx vitest run "test/js/bun/net/socket.test.ts" -t "should throw on empty unix path from truthy non-string value" 2>&1 || pnpm jest "test/js/bun/net/socket.test.ts" -t "should throw on empty unix path from truthy non-string value" 2>&1 || npx jest "test/js/bun/net/socket.test.ts" -t "should throw on empty unix path from truthy non-string value" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'should throw on empty unix path from truthy non-string value' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_should_not_leak_memory_when_connect_fails_again():
    """fail_to_pass | PR added test 'should not leak memory when connect() fails again' in 'test/js/bun/net/socket.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "test/js/bun/net/socket.test.ts" -t "should not leak memory when connect() fails again" 2>&1 || npx vitest run "test/js/bun/net/socket.test.ts" -t "should not leak memory when connect() fails again" 2>&1 || pnpm jest "test/js/bun/net/socket.test.ts" -t "should not leak memory when connect() fails again" 2>&1 || npx jest "test/js/bun/net/socket.test.ts" -t "should not leak memory when connect() fails again" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'should not leak memory when connect() fails again' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
