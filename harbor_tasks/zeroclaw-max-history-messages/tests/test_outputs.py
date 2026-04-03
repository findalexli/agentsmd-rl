"""
Task: zeroclaw-max-history-messages
Repo: zeroclaw-labs/zeroclaw @ 5b6d0585dd635a719f47c97f761dbaae817f6daa
PR:   4835

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/zeroclaw"
TARGET = Path(REPO) / "src" / "channels" / "mod.rs"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_compiles():
    """Code must compile with cargo check."""
    r = subprocess.run(
        ["cargo", "check"],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"cargo check failed:\n{r.stderr.decode()[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_hardcoded_max_channel_history():
    """The hardcoded MAX_CHANNEL_HISTORY constant must be removed."""
    src = TARGET.read_text()

    # Must not have a const definition
    assert not re.search(
        r"const\s+MAX_CHANNEL_HISTORY\s*:\s*usize\s*=\s*\d+", src
    ), "const MAX_CHANNEL_HISTORY is still defined"

    # Must not be redefined as a let binding
    assert not re.search(
        r"let\s+(mut\s+)?MAX_CHANNEL_HISTORY\s*=", src
    ), "MAX_CHANNEL_HISTORY redefined as let binding"


# [pr_diff] fail_to_pass
def test_uses_config_max_history():
    """History trimming must use the config value (max_history_messages)."""
    src = TARGET.read_text()

    # Look for max_history_messages in actual code lines (not comments)
    found = False
    for line in src.splitlines():
        code = line.split("//")[0]
        if "max_history_messages" not in code:
            continue
        # Reject if it's inside a string literal
        pos = code.find("max_history_messages")
        quotes_before = code[:pos].count('"')
        if quotes_before % 2 == 1:
            continue
        # Must be accessed through a config/context path
        if any(kw in code for kw in ["ctx.", "config.", "prompt_config.", "agent."]):
            found = True
            break

    assert found, (
        "No config path access found for max_history_messages in code lines"
    )


# [pr_diff] fail_to_pass
def test_no_old_constant_references():
    """MAX_CHANNEL_HISTORY must not appear in any code expression."""
    src = TARGET.read_text()

    for i, line in enumerate(src.splitlines(), 1):
        code = line.split("//")[0]
        if "MAX_CHANNEL_HISTORY" not in code:
            continue

        pos = code.find("MAX_CHANNEL_HISTORY")

        # Skip if part of a longer identifier
        if pos > 0 and code[pos - 1].isalnum():
            continue

        # Skip if inside a string literal
        if code[:pos].count('"') % 2 == 1:
            continue

        raise AssertionError(
            f"Line {i} still references MAX_CHANNEL_HISTORY: {line.strip()}"
        )


# [pr_diff] pass_to_pass
def test_no_hardcoded_fallback():
    """History limit must not fall back to a hardcoded numeric literal."""
    src = TARGET.read_text()

    # Find max_history assignment within append_sender_turn
    fn_start = src.find("fn append_sender_turn")
    if fn_start == -1:
        return  # test_append_sender_turn_exists will catch this

    mh_pos = src.find("let max_history", fn_start)
    if mh_pos == -1:
        # No max_history variable — config used directly, which is fine
        return

    region = src[mh_pos:mh_pos + 300]

    # If there's an else branch, it must not contain a bare numeric literal
    assert not re.search(r"else\s*\{\s*\d+\s*\}", region), (
        "max_history falls back to a hardcoded numeric literal instead of config"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_append_sender_turn_exists():
    """append_sender_turn function must exist with real logic."""
    src = TARGET.read_text()

    assert "fn append_sender_turn" in src, (
        "append_sender_turn function not found"
    )

    # Function must have a non-trivial body (at least contains history trimming logic)
    # Find the function and check it references history/messages
    fn_start = src.index("fn append_sender_turn")
    fn_region = src[fn_start:fn_start + 500]
    assert any(kw in fn_region for kw in ["history", "messages", "truncate", "split_at", "len()"]), (
        "append_sender_turn appears to be a stub — no history trimming logic found"
    )
