"""
Task: zulip-url-parser-near-anchor
Repo: zulip/zulip @ 305c52c35a7dad3e6c9bde470e8f717186abaae5
PR:   #37872

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import importlib.util
import py_compile
from pathlib import Path

REPO = "/workspace/zulip"

SCRIPT_PATH = (
    Path(REPO)
    / ".claude"
    / "skills"
    / "fetch-zulip-messages"
    / "fetch-zulip-web-public-messages"
)


def _load_module():
    """Dynamically import the fetch-zulip-web-public-messages script."""
    spec = importlib.util.spec_from_file_location("fetch_zulip", SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    py_compile.compile(str(SCRIPT_PATH), doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_parse_near_channel_url():
    """parse_zulip_url must accept near/ID in channel-style URLs."""
    mod = _load_module()
    url = "https://chat.zulip.org/#narrow/channel/101-design/topic/hello.20world/near/42"
    server, channel_id, topic, anchor = mod.parse_zulip_url(url)
    assert server == "https://chat.zulip.org"
    assert channel_id == 101
    assert topic == "hello world"
    assert anchor == "42"


# [pr_diff] fail_to_pass
def test_parse_near_stream_url():
    """parse_zulip_url must accept near/ID in stream-style URLs."""
    mod = _load_module()
    url = "https://chat.zulip.org/#narrow/stream/200-general/topic/testing/near/999"
    server, channel_id, topic, anchor = mod.parse_zulip_url(url)
    assert server == "https://chat.zulip.org"
    assert channel_id == 200
    assert topic == "testing"
    assert anchor == "999"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_parse_with_url_still_works():
    """parse_zulip_url must still accept with/ID URLs (regression)."""
    mod = _load_module()
    url = "https://chat.zulip.org/#narrow/channel/5-design/topic/test.20topic/with/77"
    server, channel_id, topic, anchor = mod.parse_zulip_url(url)
    assert server == "https://chat.zulip.org"
    assert channel_id == 5
    assert topic == "test topic"
    assert anchor == "77"


# [repo_tests] pass_to_pass
def test_parse_no_anchor():
    """parse_zulip_url must still accept URLs without any anchor."""
    mod = _load_module()
    url = "https://chat.zulip.org/#narrow/channel/5-design/topic/hello"
    server, channel_id, topic, anchor = mod.parse_zulip_url(url)
    assert server == "https://chat.zulip.org"
    assert channel_id == 5
    assert topic == "hello"
    assert anchor is None


# ---------------------------------------------------------------------------
# Config edit tests (config_edit) — CLAUDE.md update
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
