"""
Task: bun-listen-empty-hostname-crash
Repo: oven-sh/bun @ 73361607d70bd77041d0fc20e45a6dbe2373a677
PR:   28426

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Note: Bun requires the full Zig + JavaScriptCore toolchain to build from source,
so structural checks are used for the Zig fix. AST-only because: Zig code cannot
be compiled without the full bun build system (multi-hour GPU-less build).
"""

import re
from pathlib import Path

REPO = "/workspace/bun"
ZIG_FILE = f"{REPO}/src/bun.js/api/bun/socket/Handlers.zig"
TEST_FILE = f"{REPO}/test/js/bun/net/socket.test.ts"


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
# Fail-to-pass (pr_diff) — core structural checks on the Zig fix
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_hostname_crash_fixed():
    """Hostname assertf removed and replaced with proper error return."""
    # AST-only because: Zig code cannot be compiled without the full bun build system
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
    # AST-only because: Zig code cannot be compiled without the full bun build system
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
    assert Path(TEST_FILE).exists(), f"{TEST_FILE} does not exist"
    text = Path(TEST_FILE).read_text()
    lower = text.lower()

    # Must reference the bug trigger: [], String(""), or empty + hostname
    has_trigger = (
        ("[]" in text and "hostname" in lower)
        or ('string("")' in lower)
        or ("empty" in lower and "hostname" in lower)
    )
    assert has_trigger, "No test references the bug trigger ([], new String(''), empty hostname)"

    # Must assert throwing behavior
    has_throw = any(k in lower for k in ["tothrow", "throw", "reject"])
    assert has_throw, "No throw/reject assertion found in tests"

    # Must be in a test block
    has_block = any(
        f'{kw}("' in text or f"{kw}('" in text or f"{kw}(`" in text
        for kw in ("it", "test", "describe")
    )
    assert has_block, "No it()/test()/describe() block found"


# ---------------------------------------------------------------------------
# Pass-to-pass (static / pr_diff) — anti-stub and regression
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_handlers_not_stubbed():
    """Handlers.zig is substantial, not gutted or replaced with stub."""
    # AST-only because: Zig code cannot be compiled without the full bun build system
    p = Path(ZIG_FILE)
    assert p.exists(), f"{ZIG_FILE} does not exist"
    lines = p.read_text().splitlines()
    assert len(lines) >= 200, f"Handlers.zig has only {len(lines)} lines — likely stubbed"


# [pr_diff] pass_to_pass
def test_hostname_unix_branches_preserved():
    """Both hostname and unix handling branches still exist."""
    # AST-only because: Zig code cannot be compiled without the full bun build system
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
