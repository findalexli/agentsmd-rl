"""
Task: uv-direct-url-streaming-fallback
Repo: astral-sh/uv @ 5ad8577ff847d0bf115d45dd05a1efecf6fd797f
PR:   18688

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Note: Source inspection is used because the code under test is an async method
on DistributionDatabase requiring HTTP clients, cache infra, and async runtime —
it cannot be called in isolation.
# AST-only because: Rust async method with complex runtime deps (HTTP client, cache, build context)
"""

import re
import subprocess
from pathlib import Path

REPO = "/repo"
FILE = "crates/uv-distribution/src/distribution_database.rs"


def _strip_comments(source: str) -> str:
    """Strip Rust block and line comments."""
    stripped = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    return re.sub(r"//[^\n]*", "", stripped)


def _get_source() -> str:
    """Read the full source file."""
    return Path(f"{REPO}/{FILE}").read_text()


def _get_block(start_marker: str, end_marker: str) -> str:
    """Extract a code block between two BuiltDist variant markers (comment-stripped)."""
    stripped = _strip_comments(_get_source())
    lines = stripped.split("\n")
    in_block = False
    block = []
    for line in lines:
        if not in_block and start_marker in line:
            in_block = True
        if in_block:
            block.append(line)
        if in_block and end_marker in line and len(block) > 1:
            break
    return "\n".join(block)


def _direct_url_block() -> str:
    return _get_block("BuiltDist::DirectUrl", "BuiltDist::Path")


def _registry_block() -> str:
    return _get_block("BuiltDist::Registry", "BuiltDist::DirectUrl")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check():
    """Modified crate must compile without errors."""
    r = subprocess.run(
        ["cargo", "check", "-p", "uv-distribution"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=540,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr[-2000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_direct_url_err_matches_extract_not_client():
    """DirectUrl Err arm must match Error::Extract (not Error::Client)."""
    du = _direct_url_block()
    # The fix changes Err(Error::Client(err)) to Err(Error::Extract(name, err))
    assert re.search(r"Err\s*\(\s*Error::Extract", du), (
        "DirectUrl block must match Err(Error::Extract(...))"
    )
    # Ensure the old incorrect pattern is gone
    assert not re.search(r"Err\s*\(\s*Error::Client", du), (
        "DirectUrl block must NOT match Err(Error::Client(...))"
    )


# [pr_diff] fail_to_pass
def test_streaming_failed_handled():
    """DirectUrl block must handle is_http_streaming_failed() for mid-stream failures."""
    du = _direct_url_block()
    assert re.search(r"is_http_streaming_failed", du), (
        "DirectUrl block must call is_http_streaming_failed()"
    )


# [pr_diff] fail_to_pass
def test_both_streaming_errors_fallback_to_download():
    """Both streaming error types must be present alongside download_wheel fallback."""
    du = _direct_url_block()
    assert re.search(r"is_http_streaming_unsupported", du), (
        "DirectUrl block must handle is_http_streaming_unsupported()"
    )
    assert re.search(r"is_http_streaming_failed", du), (
        "DirectUrl block must handle is_http_streaming_failed()"
    )
    assert re.search(r"download_wheel", du), (
        "DirectUrl block must call download_wheel() as fallback"
    )


# [pr_diff] fail_to_pass
def test_non_streaming_errors_reraise():
    """Non-streaming Extract errors must be re-raised (not swallowed)."""
    du = _direct_url_block()
    assert re.search(r"return\s+Err\s*\(\s*Error::Extract", du), (
        "DirectUrl block must re-raise non-streaming Error::Extract errors"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_registry_arm_intact():
    """Registry arm must still handle streaming errors and have download_wheel fallback."""
    reg = _registry_block()
    assert re.search(r"is_http_streaming_unsupported", reg), (
        "Registry block must still call is_http_streaming_unsupported()"
    )
    assert re.search(r"download_wheel", reg), (
        "Registry block must still call download_wheel()"
    )


# [pr_diff] pass_to_pass
def test_stream_wheel_called_first():
    """DirectUrl arm must still call stream_wheel before the error handling."""
    du = _direct_url_block()
    assert re.search(r"stream_wheel", du), (
        "DirectUrl block must still call stream_wheel()"
    )


# [static] pass_to_pass
def test_not_stub():
    """DirectUrl block must have substantial code (not hollowed out)."""
    du = _direct_url_block()
    meaningful = [line for line in du.split("\n") if line.strip()]
    assert len(meaningful) > 20, (
        f"DirectUrl block has only {len(meaningful)} non-empty lines — "
        f"expected >20 (block may have been hollowed out)"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — CLAUDE.md rules
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:7 @ 5ad8577ff847d0bf115d45dd05a1efecf6fd797f
def test_no_panic_unwrap_in_direct_url():
    """No unwrap()/panic!/unreachable! in the DirectUrl error handler."""
    du = _direct_url_block()
    assert not re.search(r"\.unwrap\(\)|panic!\(|unreachable!\(", du), (
        "DirectUrl block must not use .unwrap(), panic!(), or unreachable!()"
    )


# [agent_config] pass_to_pass — CLAUDE.md:7 @ 5ad8577ff847d0bf115d45dd05a1efecf6fd797f
def test_no_unsafe_in_direct_url():
    """No unsafe blocks in the DirectUrl error handler."""
    du = _direct_url_block()
    assert not re.search(r"\bunsafe\s*\{", du), (
        "DirectUrl block must not use unsafe blocks"
    )


# [agent_config] pass_to_pass — CLAUDE.md:7 @ 5ad8577ff847d0bf115d45dd05a1efecf6fd797f
def test_no_clippy_ignores_in_direct_url():
    """No #[allow(clippy::...)] in the DirectUrl error handler."""
    # Read un-stripped source to check attributes
    src = _get_source()
    lines = src.split("\n")
    in_block = False
    block = []
    for line in lines:
        if not in_block and "BuiltDist::DirectUrl" in line:
            in_block = True
        if in_block:
            block.append(line)
        if in_block and "BuiltDist::Path" in line and len(block) > 1:
            break
    du_raw = "\n".join(block)
    assert not re.search(r"#\[allow\(clippy::", du_raw), (
        "DirectUrl block must not use #[allow(clippy::...)] — use #[expect()] instead"
    )


# [agent_config] pass_to_pass — CLAUDE.md:10 @ 5ad8577ff847d0bf115d45dd05a1efecf6fd797f
def test_prefer_expect_over_allow():
    """If clippy must be disabled, use #[expect()] not #[allow()]."""
    src = _get_source()
    lines = src.split("\n")
    in_block = False
    block = []
    for line in lines:
        if not in_block and "BuiltDist::DirectUrl" in line:
            in_block = True
        if in_block:
            block.append(line)
        if in_block and "BuiltDist::Path" in line and len(block) > 1:
            break
    du_raw = "\n".join(block)
    assert not re.search(r"#\[allow\(", du_raw), (
        "DirectUrl block must use #[expect()] instead of #[allow()] per CLAUDE.md"
    )
