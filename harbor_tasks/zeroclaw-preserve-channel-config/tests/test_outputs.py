"""
Task: zeroclaw-preserve-channel-config
Repo: zeroclaw-labs/zeroclaw @ ce6dd7ca3740473e6414c3eee3d8172e15d79758
PR:   4907

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/zeroclaw"
TARGET = Path(REPO) / "src/onboard/wizard.rs"


def _read_source() -> str:
    assert TARGET.exists(), f"{TARGET} does not exist"
    return TARGET.read_text()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — file integrity + compilation
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_file_exists_with_content():
    """wizard.rs exists and has substantial content (anti-stub)."""
    src = _read_source()
    lines = src.strip().splitlines()
    assert len(lines) > 200, f"File has only {len(lines)} lines — likely gutted or stubbed"
    assert "setup_channels" in src, "setup_channels function missing"
    assert "ChannelsConfig" in src, "ChannelsConfig type missing"
    assert "run_wizard" in src, "run_wizard function missing"


# [static] pass_to_pass
def test_wizard_rs_syntax():
    """wizard.rs has balanced braces and no obvious syntax corruption."""
    src = _read_source()
    # Check balanced braces (basic syntax sanity for Rust)
    depth = 0
    for ch in src:
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
        assert depth >= 0, "Unmatched closing brace in wizard.rs"
    assert depth == 0, f"Unmatched opening braces in wizard.rs (depth={depth})"
    # Ensure key functions still have bodies (not just signatures)
    assert src.count("fn setup_channels") == 1, "setup_channels should appear exactly once"
    assert src.count("fn run_wizard") >= 1, "run_wizard function missing"
    assert src.count("fn run_channels_repair_wizard") >= 1, "run_channels_repair_wizard missing"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# Regex-only because: Rust code cannot be imported/called from Python
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_setup_channels_accepts_existing_config():
    """setup_channels() must accept a parameter for existing channel config."""
    src = _read_source()
    # Match the function signature of setup_channels
    m = re.search(r"fn\s+setup_channels\s*\(([^)]*)\)", src)
    assert m, "setup_channels function definition not found"
    params = m.group(1)
    # Must accept some parameter (not zero-arg) that involves ChannelsConfig
    assert params.strip(), "setup_channels still takes no parameters"
    assert "ChannelsConfig" in params, (
        f"setup_channels param does not reference ChannelsConfig: {params}"
    )


# [pr_diff] fail_to_pass
def test_repair_wizard_passes_existing_config():
    """run_channels_repair_wizard must pass existing config to setup_channels."""
    src = _read_source()
    # Find the repair wizard function body
    repair_start = src.find("run_channels_repair_wizard")
    assert repair_start != -1, "run_channels_repair_wizard not found"
    repair_body = src[repair_start:]
    # It must pass the existing channels_config (via Some() or directly)
    assert "channels_config" in repair_body, (
        "repair wizard does not reference channels_config"
    )
    # Must wrap it in Some() for Option<ChannelsConfig>, or pass it directly
    has_some_wrap = bool(re.search(r"Some\([^)]*channels_config", repair_body))
    has_direct_pass = bool(
        re.search(r"setup_channels\([^)]*channels_config", repair_body)
    )
    assert has_some_wrap or has_direct_pass, (
        "repair wizard does not pass existing channels_config to setup_channels"
    )


# [pr_diff] fail_to_pass
def test_fresh_wizard_passes_none_or_default():
    """run_wizard (fresh setup) must not pass existing config to setup_channels."""
    src = _read_source()
    # Find run_wizard function
    wizard_match = re.search(r"(pub\s+)?(async\s+)?fn\s+run_wizard", src)
    assert wizard_match, "run_wizard function not found"
    wizard_body = src[wizard_match.start():]
    # Truncate at next top-level fn to isolate run_wizard body
    next_fn = re.search(r"\n(pub\s+)?(async\s+)?fn\s+", wizard_body[1:])
    if next_fn:
        wizard_body = wizard_body[: next_fn.start() + 1]
    # In run_wizard, setup_channels should be called with an explicit argument
    # (None or a default), not with zero args like the unfixed version
    setup_call = re.search(r"setup_channels\(([^)]*)\)", wizard_body)
    assert setup_call, "setup_channels not called in run_wizard"
    arg = setup_call.group(1).strip()
    # Must have an explicit argument — empty args means the old unfixed call
    assert arg, (
        "run_wizard calls setup_channels() with no arguments — must pass None or default"
    )
    # Must not pass the existing config (that's what repair_wizard does)
    assert "channels_config" not in arg or "default" in arg.lower(), (
        f"run_wizard should not pass existing config: setup_channels({arg})"
    )


# [pr_diff] fail_to_pass
def test_uses_existing_or_default_pattern():
    """setup_channels must use existing config or fall back to default, not always default."""
    src = _read_source()
    # Find setup_channels body
    fn_match = re.search(r"fn\s+setup_channels\s*\([^)]*\)", src)
    assert fn_match, "setup_channels not found"
    fn_body = src[fn_match.start():]
    # Should use unwrap_or_default, unwrap_or, match, or if let on the param
    body = fn_body[:2000]
    has_unwrap_or_default = "unwrap_or_default" in body
    has_unwrap_or = "unwrap_or(" in body
    has_match_some = bool(re.search(r"match\s+\w+", body)) and "Some(" in body
    has_if_let = bool(re.search(r"if\s+let\s+Some", body))
    assert has_unwrap_or_default or has_unwrap_or or has_match_some or has_if_let, (
        "setup_channels does not use existing config — no unwrap_or_default, "
        "unwrap_or, match+Some, or if-let pattern found"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_telegram_channel_handling_intact():
    """Telegram channel handling code must still be present (not deleted)."""
    src = _read_source()
    assert "telegram" in src.lower() or "tg_" in src.lower(), (
        "Telegram channel handling appears to have been removed"
    )
