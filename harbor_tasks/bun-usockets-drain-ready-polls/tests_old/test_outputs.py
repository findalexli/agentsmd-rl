"""
Task: bun-usockets-drain-ready-polls
Repo: bun @ 3f41407f47eb009c654e45def5f3f67d6ce6c8ee
PR:   28823

This PR adds a drain loop to the usockets event loop (epoll/kqueue) so that
when the kernel fills the entire ready_polls buffer (1024 slots), the loop
re-polls with zero timeout and dispatches again before running callbacks.
This matches libuv's behavior and ensures a single tick services the full
backlog instead of one 1024-event slice per roundtrip.

Tests verify the C source contains the required structural changes since
the usockets code is deeply embedded in Bun's build system and cannot be
compiled independently.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/bun"
C_FILE = f"{REPO}/packages/bun-usockets/src/eventing/epoll_kqueue.c"


def _read_source():
    """Read the C source file."""
    p = Path(C_FILE)
    assert p.exists(), f"Source file not found: {C_FILE}"
    return p.read_text()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / structure checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_c_file_readable():
    """Modified C file exists and is readable with expected structure."""
    src = _read_source()
    assert "us_loop_run" in src, "us_loop_run function not found"
    assert "us_internal_dispatch_ready_polls" in src, "dispatch function not found"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core structural/behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_hardcoded_1024_removed():
    """Hardcoded 1024 in epoll/kevent calls must be replaced with LIBUS_MAX_READY_POLLS."""
    src = _read_source()

    # Find the us_loop_run function body
    loop_run_match = re.search(
        r"void\s+us_loop_run\s*\([^)]*\)\s*\{",
        src
    )
    assert loop_run_match is not None, "us_loop_run function not found"

    # Extract function body (to closing brace at same indent level)
    start = loop_run_match.end()
    depth = 1
    i = start
    while i < len(src) and depth > 0:
        if src[i] == '{':
            depth += 1
        elif src[i] == '}':
            depth -= 1
        i += 1
    loop_run_body = src[start:i]

    # Check that the hardcoded 1024 is NOT in epoll/kevent calls
    # Pattern: bare 1024 as argument to bun_epoll_pwait2 or kevent64
    hardcoded_1024_in_call = re.search(
        r"(?:bun_epoll_pwait2|kevent64)\s*\([^)]*\b1024\b",
        loop_run_body
    )
    assert hardcoded_1024_in_call is None, (
        "Hardcoded 1024 still present in epoll/kevent call in us_loop_run — "
        "should use LIBUS_MAX_READY_POLLS"
    )


# [pr_diff] fail_to_pass
def test_drain_logic_exists():
    """Logic must exist to re-poll when the ready_polls buffer is saturated."""
    src = _read_source()

    # Behavioral check: there must be a while loop that re-polls after detecting
    # the buffer was fully filled. Look for the saturation check AND re-poll together.
    # Pattern: while loop condition checks num_ready_polls against max, and inside
    # the loop there's an epoll/kevent call.
    drain_patterns = [
        # Named drain function approach
        r"us_internal_drain",
        # Any while loop checking saturation + re-polling
        r"while\s*\([^)]*num_ready_polls[^)]*\)[^{]*\{[^}]*epoll_pwait|kevent64",
    ]
    # Also accept: a while loop anywhere that checks saturation
    has_saturation_check = bool(re.search(
        r"num_ready_polls\s*==\s*(?:LIBUS_MAX_READY_POLLS|1024)", src
    ))
    has_repoll_in_while = bool(re.search(
        r"while\s*\(", src
    ) and re.search(r"(?:bun_epoll_pwait2|kevent64).*&(?:zero|NULL|{0)", src))

    found = any(re.search(p, src, re.IGNORECASE | re.DOTALL) for p in drain_patterns)
    assert found or (has_saturation_check and has_repoll_in_while), (
        "No logic found for re-polling when ready_polls buffer is saturated"
    )


# [pr_diff] fail_to_pass
def test_drain_uses_zero_timeout():
    """The drain logic must re-poll with zero/non-blocking timeout."""
    src = _read_source()

    # Extract the drain function area — look for the saturation check
    # The drain should use a zero timespec or KEVENT_FLAG_IMMEDIATE
    zero_timeout_patterns = [
        r"struct\s+timespec\s+zero\s*=\s*\{0\s*,\s*0\}",
        r"KEVENT_FLAG_IMMEDIATE",
    ]
    found = any(re.search(p, src) for p in zero_timeout_patterns)
    assert found, "Drain logic does not use zero/non-blocking timeout for re-poll"


# [pr_diff] fail_to_pass
def test_drain_has_iteration_cap():
    """The drain loop must be capped to prevent unbounded spinning."""
    src = _read_source()

    # Look for a counter/cap pattern in the drain logic
    cap_patterns = [
        r"drain_count\s*[=:]\s*\d+",
        r"max_drain",
        r"drain.*cap",
        r"drain.*limit",
    ]
    found = any(re.search(p, src, re.IGNORECASE) for p in cap_patterns)
    assert found, "Drain loop has no iteration cap — could spin indefinitely"


# [pr_diff] fail_to_pass
def test_both_loop_functions_dispatch_extra():
    """Both us_loop_run and us_loop_run_bun_tick must have extra dispatch after initial poll."""
    src = _read_source()

    # Find us_loop_run function body
    loop_run_match = re.search(
        r"void\s+us_loop_run\s*\([^)]*\)\s*\{[\s\S]*?^\}",
        src, re.MULTILINE
    )
    assert loop_run_match is not None, "us_loop_run function not found"
    loop_run_body = loop_run_match.group(0)

    # Find us_loop_run_bun_tick function body
    bun_tick_match = re.search(
        r"void\s+us_loop_run_bun_tick\s*\([^)]*\)\s*\{[\s\S]*?^\}",
        src, re.MULTILINE
    )
    assert bun_tick_match is not None, "us_loop_run_bun_tick function not found"
    bun_tick_body = bun_tick_match.group(0)

    # After us_internal_dispatch_ready_polls, there must be additional logic
    # (could be a function call, inline while loop, etc.) — not just dispatch alone
    for name, body in [("us_loop_run", loop_run_body), ("us_loop_run_bun_tick", bun_tick_body)]:
        dispatch_pos = body.find("us_internal_dispatch_ready_polls")
        assert dispatch_pos != -1, f"{name} does not call us_internal_dispatch_ready_polls"

        # Check that there's more code after the dispatch call in this function
        after_dispatch = body[dispatch_pos + len("us_internal_dispatch_ready_polls"):]
        # Should have additional non-whitespace code (not just the closing brace)
        non_trivial = after_dispatch.strip()
        # Remove trailing } and whitespace
        non_trivial = non_trivial.rstrip("} \t\n")
        assert len(non_trivial) > 5, (
            f"{name} has no logic after us_internal_dispatch_ready_polls — "
            "missing extra dispatch for saturated buffer"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_drain_has_real_logic():
    """The drain/re-poll logic must have substantial implementation, not be a stub."""
    src = _read_source()

    # Find the saturation-checking while loop or drain function
    # Look for a while loop that checks num_ready_polls
    while_match = re.search(
        r"while\s*\([^)]*num_ready_polls[^)]*\)\s*\{",
        src
    )
    if while_match is None:
        # Fall back to finding a function with "drain" in the name
        while_match = re.search(
            r"(?:static\s+)?void\s+\w*[Dd]rain\w*\s*\([^)]*\)\s*\{",
            src
        )

    assert while_match is not None, "Drain/re-poll logic not found"

    # Extract body
    start = while_match.end()
    depth = 1
    i = start
    while i < len(src) and depth > 0:
        if src[i] == '{':
            depth += 1
        elif src[i] == '}':
            depth -= 1
        i += 1
    body = src[start:i]

    # Count meaningful statements (not just whitespace/comments)
    statements = re.findall(r"(?:if|while|for|loop->|=|return|break)", body)
    assert len(statements) >= 4, (
        f"Drain logic appears to be a stub (only {len(statements)} statements found)"
    )


# [static] pass_to_pass
def test_saturation_guard_present():
    """The drain must check for buffer saturation before re-polling."""
    src = _read_source()

    # The drain should check if num_ready_polls equals the max
    saturation_patterns = [
        r"num_ready_polls\s*==\s*LIBUS_MAX_READY_POLLS",
        r"num_ready_polls\s*==\s*1024",
        r"ready_polls.*full",
        r"saturat",
    ]
    found = any(re.search(p, src, re.IGNORECASE) for p in saturation_patterns)
    assert found, "No saturation guard found — drain would re-poll unconditionally"
