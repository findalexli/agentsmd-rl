"""
Task: bun-listen-empty-hostname-crash
Repo: oven-sh/bun @ 73361607d70bd77041d0fc20e45a6dbe2373a677
PR:   28426

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Note: Bun requires the full Zig + JavaScriptCore toolchain to build from source,
so the Zig fix checks are structural (comment-stripping + window analysis).
The TypeScript test validation uses subprocess (node) to execute actual code
that parses and validates the test file structure.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/bun"
ZIG_FILE = f"{REPO}/src/bun.js/api/bun/socket/Handlers.zig"
TEST_FILE = f"{REPO}/test/js/bun/net/socket.test.ts"


def _run_node(code: str, timeout: int = 15) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node.js in the repo directory."""
    return subprocess.run(
        ["node", "-e", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


def _read_zig_stripped() -> str:
    """Read Handlers.zig with // comments stripped."""
    raw = Path(ZIG_FILE).read_text()
    lines = []
    for line in raw.split("\n"):
        in_string = False
        result = []
        for i, ch in enumerate(line):
            if ch == '"' and (i == 0 or line[i - 1] != "\\"):
                in_string = not in_string
            if not in_string and line[i : i + 2] == "//":
                break
            result.append(ch)
        lines.append("".join(result))
    return "\n".join(lines)


def _find_window(code: str, markers: list[str], size: int = 600) -> str | None:
    """Find a code window starting from the first matching marker."""
    for m in markers:
        idx = code.find(m)
        if idx >= 0:
            return code[idx : idx + size]
    return None


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — Zig fix checks (structural, can't compile Zig)
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_hostname_crash_fixed():
    """Hostname assertf removed and replaced with proper error return."""
    # Zig cannot be compiled without the full bun build system — structural check
    code = _read_zig_stripped()
    window = _find_window(code, ["generated.hostname.get()", "hostname.get()"])

    if window is None:
        # Branch restructured — accept if hostname handling exists without assertf
        assert "hostname" in code, "hostname handling not found in Handlers.zig"
        assert "assertf" not in code, "assertf still present somewhere in file"
        return

    # Must NOT have the crash assertion
    has_crash = ("assertf" in window and "truthy" in window) or (
        "assertf" in window and "hostname" in window and "length" in window
    )
    assert not has_crash, "hostname assertf crash assertion still present"

    # Must have error handling (throw or return error on length == 0)
    near = window[:400].lower()
    has_error = any(
        p in near
        for p in ["throwinvalidarguments", "throwtypeerror", "throwpossiblyinvalidarguments"]
    ) or ("length" in near and "== 0" in near and "return" in near)
    assert has_error, "hostname branch has no error handling for empty string"


# [pr_diff] fail_to_pass
def test_unix_crash_fixed():
    """Unix path assertf removed and replaced with proper error return."""
    # Zig cannot be compiled without the full bun build system — structural check
    code = _read_zig_stripped()
    window = _find_window(code, ["generated.unix_.get()", "generated.unix.get()", "unix.get()"])

    if window is None:
        assert "unix" in code, "unix handling not found in Handlers.zig"
        assert "assertf" not in code, "assertf still present somewhere in file"
        return

    has_crash = ("assertf" in window and "truthy" in window) or (
        "assertf" in window and "unix" in window and "length" in window
    )
    assert not has_crash, "unix assertf crash assertion still present"

    near = window[:400].lower()
    has_error = any(
        p in near
        for p in ["throwinvalidarguments", "throwtypeerror", "throwpossiblyinvalidarguments"]
    ) or ("length" in near and "== 0" in near and "return" in near)
    assert has_error, "unix branch has no error handling for empty string"


# [pr_diff] fail_to_pass
def test_throw_tests_added():
    """Agent added tests verifying throw on truthy-but-empty hostname/unix."""
    r = _run_node(r"""
const fs = require('fs');
const path = 'test/js/bun/net/socket.test.ts';
if (!fs.existsSync(path)) {
  throw new Error(path + ' does not exist');
}
const text = fs.readFileSync(path, 'utf8');
const lower = text.toLowerCase();

// Must have test blocks (it/test/describe)
const hasTestBlock = /it\s*\(\s*["'`]/.test(text) || /test\s*\(\s*["'`]/.test(text);
if (!hasTestBlock) throw new Error('No it()/test() block found');

// Must reference the bug trigger: [], String(""), or empty + hostname
const hasTrigger =
  (text.includes('[]') && lower.includes('hostname')) ||
  lower.includes('string("")') ||
  (lower.includes('empty') && lower.includes('hostname'));
if (!hasTrigger) throw new Error('No test references the bug trigger');

// Must assert throwing behavior
const hasThrow = ['tothrow', 'throw', 'reject'].some(k => lower.includes(k));
if (!hasThrow) throw new Error('No throw/reject assertion found');

// Must test Bun.listen and/or Bun.connect
const hasListenOrConnect = lower.includes('bun.listen') || lower.includes('bun.connect');
if (!hasListenOrConnect) throw new Error('No Bun.listen/Bun.connect test');

console.log('PASS');
""")
    assert r.returncode == 0, f"Test validation failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static / pr_diff) — anti-stub and regression
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_handlers_not_stubbed():
    """Handlers.zig is substantial, not gutted or replaced with stub."""
    p = Path(ZIG_FILE)
    assert p.exists(), f"{ZIG_FILE} does not exist"
    lines = p.read_text().splitlines()
    assert len(lines) >= 200, f"Handlers.zig has only {len(lines)} lines — likely stubbed"


# [pr_diff] pass_to_pass
def test_hostname_unix_branches_preserved():
    """Both hostname and unix handling branches still exist."""
    text = Path(ZIG_FILE).read_text()
    has_hostname = "hostname" in text and (
        "generated.hostname" in text or "hostname.get" in text or "hostname_or_unix" in text
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
    assert len(lines) > 500, f"socket.test.ts has only {len(lines)} lines — likely truncated"


# ---------------------------------------------------------------------------
# Repo CI/CD (pass_to_pass) — repo's own tests, lints, typechecks
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass — from .github/workflows/lint.yml
def test_repo_lint():
    """Repo's JS linting passes (oxlint on src/js)."""
    r = subprocess.run(
        ["bunx", "oxlint", "--format=github", "src/js"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Exit code 0 = success, warnings are OK (non-zero only on errors)
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass — from .github/workflows/format.yml
def test_repo_prettier_socket_test():
    """Repo's prettier formatting passes on socket.test.ts (pass_to_pass)."""
    r = subprocess.run(
        ["bunx", "prettier", "--check", "test/js/bun/net/socket.test.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass — from .github/workflows/format.yml
def test_repo_ban_words():
    """Repo's banned words check passes (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "./test/internal/ban-words.test.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ban words check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md / CLAUDE.md
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — CLAUDE.md:97 @ 73361607d70bd77041d0fc20e45a6dbe2373a677
def test_no_hardcoded_ports():
    """New test code uses port: 0, not hardcoded port numbers."""
    p = Path(TEST_FILE)
    if not p.exists():
        return
    text = p.read_text()
    tail = "\n".join(text.splitlines()[-100:])
    hardcoded = re.findall(r"port:\s*(?!0\b)(\d+)", tail)
    assert not hardcoded, f"Hardcoded port(s) in new tests: {hardcoded} — use port: 0"


# [agent_config] pass_to_pass — AGENTS.md:102 @ 73361607d70bd77041d0fc20e45a6dbe2373a677
def test_no_settimeout_in_new_tests():
    """New test code does not use setTimeout — await conditions instead."""
    p = Path(TEST_FILE)
    if not p.exists():
        return
    text = p.read_text()
    tail = "\n".join(text.splitlines()[-100:])
    assert "setTimeout" not in tail, (
        "setTimeout found in new tests — AGENTS.md says await conditions instead"
    )


# [agent_config] pass_to_pass — AGENTS.md:99 @ 73361607d70bd77041d0fc20e45a6dbe2373a677
def test_no_panic_absence_tests():
    """New tests don't check for absence of 'panic' or 'uncaught exception'."""
    p = Path(TEST_FILE)
    if not p.exists():
        return
    text = p.read_text()
    tail = "\n".join(text.splitlines()[-100:]).lower()
    # Forbidden: .not.toThrow("panic"), expect no "uncaught exception", etc.
    has_panic_check = (
        "not" in tail
        and ("panic" in tail or "uncaught exception" in tail)
        and ("tothrow" in tail or "tocontain" in tail or "tomatch" in tail)
    )
    assert not has_panic_check, (
        "Tests check for absence of 'panic'/'uncaught exception' — "
        "AGENTS.md says these tests will never fail in CI"
    )
