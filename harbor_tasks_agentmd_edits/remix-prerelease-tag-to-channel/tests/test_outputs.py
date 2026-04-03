"""
Task: remix-prerelease-tag-to-channel
Repo: remix-run/remix @ 40a755c50f40ed444a928363beddd75e6edc1f52
PR:   10981

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/remix"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript and JSON files must parse without errors."""
    # Verify JSON is valid
    prerelease = Path(REPO) / "packages" / "remix" / ".changes" / "prerelease.json"
    data = json.loads(prerelease.read_text())
    assert isinstance(data, dict), "prerelease.json must be a JSON object"

    # Verify TypeScript files have no obvious syntax errors (balanced braces etc.)
    for ts_file in ["scripts/publish.ts", "scripts/utils/changes.ts"]:
        content = (Path(REPO) / ts_file).read_text()
        assert len(content) > 100, f"{ts_file} appears truncated or empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_prerelease_json_uses_channel():
    """prerelease.json must use 'channel' key instead of 'tag'."""
    prerelease = Path(REPO) / "packages" / "remix" / ".changes" / "prerelease.json"
    data = json.loads(prerelease.read_text())
    assert "channel" in data, "prerelease.json must have a 'channel' field"
    assert "tag" not in data, "prerelease.json must not have the old 'tag' field"
    assert data["channel"] == "alpha", "channel value should be 'alpha'"


# [pr_diff] fail_to_pass
def test_changes_ts_interface_uses_channel():
    """RemixPrereleaseConfig interface must use 'channel' instead of 'tag'."""
    changes_ts = (Path(REPO) / "scripts" / "utils" / "changes.ts").read_text()

    # Find the interface definition and check it uses channel
    interface_match = re.search(
        r"export\s+interface\s+RemixPrereleaseConfig\s*\{([^}]+)\}",
        changes_ts,
    )
    assert interface_match, "RemixPrereleaseConfig interface not found"
    interface_body = interface_match.group(1)
    assert "channel" in interface_body, \
        "RemixPrereleaseConfig must have 'channel' field"
    assert "tag" not in interface_body.split("//")[0], \
        "RemixPrereleaseConfig must not have old 'tag' field (outside comments)"


# [pr_diff] fail_to_pass
def test_changes_ts_reads_channel_from_config():
    """readRemixPrereleaseConfig must validate and return 'channel', not 'tag'."""
    changes_ts = (Path(REPO) / "scripts" / "utils" / "changes.ts").read_text()

    # The validation code should check for 'channel' in the parsed object
    assert "'channel' in obj" in changes_ts or '"channel" in obj' in changes_ts, \
        "readRemixPrereleaseConfig must check for 'channel' key in parsed JSON"

    # Error messages should reference 'channel'
    assert '"channel"' in changes_ts, \
        "Error messages must reference 'channel' field"

    # The return value should use .channel
    assert "obj.channel" in changes_ts, \
        "Config reader must access obj.channel"


# [pr_diff] fail_to_pass

    # The publish command for remix should use --tag next (hardcoded)
    assert "--tag next" in publish_ts, \
        "publish.ts must use '--tag next' for remix prerelease publishing"

    # Should NOT interpolate the channel/tag value into the publish command
    assert "${remixPrereleaseTag}" not in publish_ts, \
        "publish.ts must not use dynamic tag from config in publish command"
    assert "${remixPrereleaseChannel}" not in publish_ts, \
        "publish.ts must not interpolate channel into npm tag"


# [pr_diff] fail_to_pass

    # Should log "channel" in the status message
    assert "channel:" in publish_ts or "channel =" in publish_ts or \
        "remixPrereleaseChannel" in publish_ts, \
        "publish.ts should reference channel in variable names or logs"

    # Should not use old variable name
    assert "remixPrereleaseTag" not in publish_ts, \
        "publish.ts must not use old 'remixPrereleaseTag' variable name"


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — documentation/config file update tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass — AGENTS.md:49-54 @ 4c77c95a478c863bc7245c7ec11a576df2808d20

    # Should use "channel" in the prerelease documentation section
    assert "channel" in agents_md.lower(), \
        "AGENTS.md should use 'channel' terminology for prerelease config"

    # Should mention that npm dist-tag is always "next"
    # (The key behavioral change: decouple channel from npm tag)
    assert "next" in agents_md, \
        "AGENTS.md should document that npm dist-tag is 'next'"

    # Should use "channels" not "tags" for transitioning terminology
    # Check for "prerelease channels" or "between channels" or similar
    agents_lower = agents_md.lower()
    assert "channel" in agents_lower and ("transition" in agents_lower or "prerelease" in agents_lower), \
        "AGENTS.md should document prerelease channels"


# [config_edit] fail_to_pass — CONTRIBUTING.md:132-155 @ 4c77c95a478c863bc7245c7ec11a576df2808d20

    # The JSON example should show "channel", not "tag"
    assert '"channel"' in contributing_md, \
        'CONTRIBUTING.md prerelease JSON example must use "channel" key'

    # Should not have the old "tag" key in the JSON example
    # (Check specifically in the prerelease section context)
    prerelease_section = contributing_md[contributing_md.find("prerelease.json"):]
    # Find the JSON block
    json_start = prerelease_section.find("{")
    json_end = prerelease_section.find("}", json_start) + 1
    if json_start >= 0 and json_end > json_start:
        json_block = prerelease_section[json_start:json_end]
        assert '"channel"' in json_block, \
            "CONTRIBUTING.md prerelease JSON block must use 'channel'"
        assert '"tag"' not in json_block, \
            "CONTRIBUTING.md prerelease JSON block must not use old 'tag' key"

    # Section headers should reference "channels" not "tags"
    assert "channels" in contributing_md.lower(), \
        "CONTRIBUTING.md should use 'channels' terminology (not 'tags')"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub / regression
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_changes_ts_still_validates_config():
    """changes.ts must still validate that the config field is a non-empty string."""
    changes_ts = (Path(REPO) / "scripts" / "utils" / "changes.ts").read_text()

    # Must still have validation logic (not gutted)
    assert "trim()" in changes_ts, \
        "Config validation must still trim whitespace"
    assert "non-empty string" in changes_ts or "length === 0" in changes_ts or \
        ".length === 0" in changes_ts, \
        "Config validation must still check for non-empty string"

    # Must still return the parsed config value
    assert ".config" in changes_ts or "config:" in changes_ts, \
        "Must still return parsed config"
