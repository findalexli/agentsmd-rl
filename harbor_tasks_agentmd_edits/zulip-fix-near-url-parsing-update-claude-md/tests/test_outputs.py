"""
Task: zulip-fix-near-url-parsing-update-claude-md
Repo: zulip/zulip @ 305c52c35a7dad3e6c9bde470e8f717186abaae5
PR:   37872

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/zulip"
FETCH_SCRIPT = (
    Path(REPO) / ".claude" / "skills" / "fetch-zulip-messages" / "fetch-zulip-web-public-messages"
)


def _load_fetch_module():
    """Import the fetch-zulip-web-public-messages script as a module."""
    spec = importlib.util.spec_from_file_location("fetch_zulip", str(FETCH_SCRIPT))
    mod = importlib.util.module_from_spec(spec)
    # Prevent the module from calling sys.exit on import
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """fetch-zulip-web-public-messages parses without syntax errors."""
    import py_compile
    py_compile.compile(str(FETCH_SCRIPT), doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_parse_near_url():
    """parse_zulip_url must handle near/ID anchor format."""
    mod = _load_fetch_module()
    url = "https://chat.zulip.org/#narrow/channel/101-design/topic/cool.20feature/near/54321"
    server, channel_id, topic, anchor = mod.parse_zulip_url(url)
    assert server == "https://chat.zulip.org", f"Wrong server: {server}"
    assert channel_id == 101, f"Wrong channel_id: {channel_id}"
    assert topic == "cool feature", f"Wrong topic: {topic}"
    assert anchor == "54321", f"Wrong anchor: {anchor}"


# [pr_diff] fail_to_pass
def test_parse_near_url_stream_variant():
    """parse_zulip_url must handle near/ID with stream prefix."""
    mod = _load_fetch_module()
    url = "https://zulip.example.com/#narrow/stream/42-general/topic/hello/near/99999"
    server, channel_id, topic, anchor = mod.parse_zulip_url(url)
    assert server == "https://zulip.example.com", f"Wrong server: {server}"
    assert channel_id == 42, f"Wrong channel_id: {channel_id}"
    assert topic == "hello", f"Wrong topic: {topic}"
    assert anchor == "99999", f"Wrong anchor: {anchor}"


# [pr_diff] fail_to_pass
def test_error_message_mentions_near():
    """Error message should document the near/ID URL format."""
    r = subprocess.run(
        [sys.executable, str(FETCH_SCRIPT), "https://invalid.example.com/#bad-url"],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode != 0, "Should fail on bad URL"
    assert "near" in r.stderr, (
        f"Error message should mention 'near' format. Got:\n{r.stderr}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_parse_with_url_still_works():
    """parse_zulip_url must still handle the original with/ID format."""
    mod = _load_fetch_module()
    url = "https://chat.zulip.org/#narrow/channel/137-feedback/topic/hello.20world/with/12345"
    server, channel_id, topic, anchor = mod.parse_zulip_url(url)
    assert server == "https://chat.zulip.org", f"Wrong server: {server}"
    assert channel_id == 137, f"Wrong channel_id: {channel_id}"
    assert topic == "hello world", f"Wrong topic: {topic}"
    assert anchor == "12345", f"Wrong anchor: {anchor}"


# [static] pass_to_pass
def test_parse_url_no_anchor():
    """parse_zulip_url must handle URLs without any anchor."""
    mod = _load_fetch_module()
    url = "https://chat.zulip.org/#narrow/channel/9-errors/topic/bug.20report"
    server, channel_id, topic, anchor = mod.parse_zulip_url(url)
    assert server == "https://chat.zulip.org", f"Wrong server: {server}"
    assert channel_id == 9, f"Wrong channel_id: {channel_id}"
    assert topic == "bug report", f"Wrong topic: {topic}"
    assert anchor is None, f"Expected None anchor, got: {anchor}"


# ---------------------------------------------------------------------------
# Config-derived (pr_diff) — CLAUDE.md update
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_claude_md_zulip_chat_links():
    """CLAUDE.md must have a section about handling Zulip chat links."""
    claude_md = Path(REPO) / ".claude" / "CLAUDE.md"
    content = claude_md.read_text()
    assert "zulip" in content.lower() and "chat" in content.lower() and "link" in content.lower(), (
        "CLAUDE.md should have a section about Zulip chat links"
    )
    assert "fetch-zulip-messages" in content, (
        "CLAUDE.md should reference the fetch-zulip-messages skill"
    )
    assert "WebFetch" in content or "webfetch" in content.lower(), (
        "CLAUDE.md should warn against using WebFetch for Zulip URLs"
    )
