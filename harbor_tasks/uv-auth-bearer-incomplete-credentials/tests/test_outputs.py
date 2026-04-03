"""
Task: uv-auth-bearer-incomplete-credentials
Repo: astral-sh/uv @ e169f431729c6dcf2cf3e518c0c86e0f962538f1
PR:   18646

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess

MIDDLEWARE = "/repo/crates/uv-auth/src/middleware.rs"
EDIT_RS = "/repo/crates/uv/tests/it/edit.rs"


def _read_code_lines():
    """Read middleware.rs and return (raw_lines, comment-stripped lines)."""
    with open(MIDDLEWARE) as f:
        lines = f.readlines()
    stripped = []
    for line in lines:
        code = line.split("//")[0] if "//" in line else line
        stripped.append(code)
    return lines, stripped


def _guard_window(stripped, before=3, after=8):
    """Yield code windows around every AuthPolicy::Always occurrence."""
    for i, line in enumerate(stripped):
        if "AuthPolicy::Always" in line:
            yield "".join(stripped[max(0, i - before) : i + after])


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
# Structural-only because: Rust code — cannot import into Python
def test_syntax_valid_rust():
    """middleware.rs must parse as valid Rust."""
    r = subprocess.run(
        ["rustfmt", "--check", MIDDLEWARE],
        capture_output=True,
        timeout=30,
    )
    # rustfmt returns 0 (formatted) or 1 (needs formatting) for valid Rust;
    # exit > 1 means parse error.
    assert r.returncode in (0, 1), (
        f"rustfmt failed with exit code {r.returncode}: {r.stderr.decode()[:500]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
# Structural-only because: Rust code — cannot import into Python, cargo check too slow for full uv build
def test_auth_guard_uses_is_authenticated():
    """Auth policy guard must use is_authenticated() instead of password().is_none().

    The base commit checks password().is_none() which breaks Bearer auth because
    Bearer credentials have a token, not a password. The fix replaces it with
    is_authenticated() which correctly handles both Basic and Bearer.
    """
    _, stripped = _read_code_lines()
    src = "".join(stripped)

    assert "is_authenticated()" in src, (
        "is_authenticated() not found in code (excluding comments)"
    )

    # is_authenticated() must appear near AuthPolicy::Always (within 8 lines)
    found_guard = False
    for window in _guard_window(stripped):
        if "is_authenticated()" in window:
            found_guard = True
            break
    assert found_guard, "No auth policy guard using is_authenticated() found"

    # The guard must return an Err
    err_near_guard = False
    for window in _guard_window(stripped, before=1):
        if "is_authenticated()" in window and "Err(" in window:
            err_near_guard = True
            break
    assert err_near_guard, (
        "Auth guard with is_authenticated() does not return an error"
    )


# [pr_diff] fail_to_pass
# Structural-only because: Rust code — cannot import into Python, cargo check too slow for full uv build
def test_password_is_none_removed_from_guard():
    """The buggy password().is_none() pattern must be removed from the auth guard.

    The base commit checks password().is_none() near AuthPolicy::Always, which
    incorrectly rejects Bearer tokens (they have no password, only a token).
    """
    _, stripped = _read_code_lines()

    for window in _guard_window(stripped, before=2, after=6):
        assert not ("password()" in window and "is_none()" in window), (
            "Auth policy guard still uses password().is_none()"
        )


# [pr_diff] fail_to_pass
# Structural-only because: Rust code — cannot import into Python, cargo check too slow for full uv build
def test_error_message_not_missing_password():
    """Error message must not say 'Missing password' — misleading for Bearer auth.

    Any error message that doesn't reference 'Missing password' is acceptable.
    """
    _, stripped = _read_code_lines()

    for line in stripped:
        assert "Missing password" not in line, (
            "Code still contains misleading 'Missing password' error"
        )

    # Verify error handling wasn't just deleted
    src = "".join(stripped)
    assert "format_err!" in src, (
        "No format_err! found — error handling may have been deleted"
    )


# [pr_diff] fail_to_pass
# Structural-only because: Rust code — cannot import into Python, cargo check too slow for full uv build
def test_edit_rs_error_message_updated():
    """Integration test in edit.rs must not assert on 'Missing password'.

    The PR also modifies crates/uv/tests/it/edit.rs to update the expected
    error message. If the agent changes middleware.rs but forgets to update
    the test, the project's own test suite would break.
    """
    with open(EDIT_RS) as f:
        src = f.read()

    assert "Missing password" not in src, (
        "edit.rs still asserts on 'Missing password' — test needs updating"
    )


# [pr_diff] fail_to_pass
# Structural-only because: Rust code — cannot import into Python, cargo check too slow for full uv build
def test_trace_no_username_and_password():
    """Trace message in complete_request_with_request_credentials must not say
    'username and password'.

    The old trace message said 'already contains username and password' which is
    misleading since the code handles Bearer too. The PR updates both the trace!
    call and the comment above it.
    """
    with open(MIDDLEWARE) as f:
        lines = f.readlines()

    # Find complete_request_with_request_credentials and check trace! calls
    in_function = False
    found_function = False
    for line in lines:
        if "fn complete_request_with_request_credentials(" in line:
            in_function = True
            found_function = True
        elif in_function and line.strip().startswith("fn "):
            break
        elif in_function and "trace!" in line:
            assert "username and password" not in line, (
                f"Trace still says 'username and password': {line.strip()}"
            )

    assert found_function, "complete_request_with_request_credentials not found"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
# Structural-only because: Rust code — cannot import into Python, cargo check too slow for full uv build
def test_auth_guard_not_deleted():
    """AuthPolicy::Always guard must still exist — fix should modify it, not delete it."""
    _, stripped = _read_code_lines()
    src = "".join(stripped)
    assert "AuthPolicy::Always" in src, (
        "AuthPolicy::Always guard was deleted instead of fixed"
    )


# [static] pass_to_pass
# Structural-only because: Rust code — cannot import into Python, cargo check too slow for full uv build
def test_complete_request_exists():
    """complete_request and complete_request_with_request_credentials must still exist."""
    with open(MIDDLEWARE) as f:
        src = f.read()
    assert "fn complete_request(" in src, (
        "complete_request function was deleted"
    )
    assert "fn complete_request_with_request_credentials(" in src, (
        "complete_request_with_request_credentials function was deleted"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:7 @ e169f431729c6dcf2cf3e518c0c86e0f962538f1
# Structural-only because: Rust code — cannot import into Python, cargo check too slow for full uv build
def test_no_unwrap_panic_near_guard():
    """No unwrap()/panic!/unreachable! near auth policy guard (CLAUDE.md line 7).

    CLAUDE.md: "AVOID using panic!, unreachable!, .unwrap(), unsafe code, and clippy rule ignores"
    """
    with open(MIDDLEWARE) as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if "AuthPolicy::Always" in line:
            region = lines[max(0, i - 2) : i + 8]
            for rline in region:
                code = rline.split("//")[0]
                assert ".unwrap()" not in code, (
                    f"Found .unwrap() near auth guard: {rline.strip()}"
                )
                assert "panic!" not in code, (
                    f"Found panic! near auth guard: {rline.strip()}"
                )
                assert "unreachable!" not in code, (
                    f"Found unreachable! near auth guard: {rline.strip()}"
                )


# [agent_config] pass_to_pass — CLAUDE.md:7 @ e169f431729c6dcf2cf3e518c0c86e0f962538f1
# Structural-only because: Rust code — cannot import into Python, cargo check too slow for full uv build
def test_no_unsafe_near_guard():
    """No unsafe blocks near auth policy guard (CLAUDE.md line 7).

    CLAUDE.md: "AVOID using panic!, unreachable!, .unwrap(), unsafe code, and clippy rule ignores"
    """
    with open(MIDDLEWARE) as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if "AuthPolicy::Always" in line:
            region = lines[max(0, i - 5) : i + 10]
            for rline in region:
                code = rline.split("//")[0]
                assert "unsafe " not in code and "unsafe{" not in code, (
                    f"Found unsafe block near auth guard: {rline.strip()}"
                )


# [agent_config] pass_to_pass — CLAUDE.md:10 @ e169f431729c6dcf2cf3e518c0c86e0f962538f1
# Structural-only because: Rust code — cannot import into Python, cargo check too slow for full uv build
def test_no_allow_attr_near_guard():
    """No #[allow(...)] attributes near auth policy guard (CLAUDE.md line 10).

    CLAUDE.md: "PREFER #[expect()] over [allow()] if clippy must be disabled"
    Agents should use #[expect()] if suppressing a lint, never #[allow()].
    """
    with open(MIDDLEWARE) as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if "AuthPolicy::Always" in line:
            region = lines[max(0, i - 5) : i + 10]
            for rline in region:
                stripped = rline.strip()
                if stripped.startswith("#[allow("):
                    assert False, (
                        f"Found #[allow()] near auth guard (use #[expect()] instead): {stripped}"
                    )
