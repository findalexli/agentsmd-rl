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
    prerelease = Path(REPO) / "packages" / "remix" / ".changes" / "prerelease.json"
    data = json.loads(prerelease.read_text())
    assert isinstance(data, dict), "prerelease.json must be a JSON object"

    for ts_file in ["scripts/publish.ts", "scripts/utils/changes.ts"]:
        content = (Path(REPO) / ts_file).read_text()
        assert len(content) > 100, f"{ts_file} appears truncated or empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_prerelease_config_validates_channel():
    """Node runtime reads prerelease.json and validates 'channel' field exists."""
    r = subprocess.run(
        ["node", "-e", """
const fs = require('fs');
const raw = fs.readFileSync('packages/remix/.changes/prerelease.json', 'utf-8');
const data = JSON.parse(raw);
if (typeof data !== 'object' || data === null) {
  console.error('not an object');
  process.exit(1);
}
if (!('channel' in data)) {
  console.error('missing channel field, found keys: ' + Object.keys(data).join(', '));
  process.exit(1);
}
if (typeof data.channel !== 'string' || data.channel.trim().length === 0) {
  console.error('channel must be a non-empty string');
  process.exit(1);
}
console.log(JSON.stringify({ valid: true, channel: data.channel.trim() }));
"""],
        cwd=REPO, capture_output=True, text=True, timeout=15,
    )
    assert r.returncode == 0, f"Config validation failed: {r.stderr}"
    out = json.loads(r.stdout.strip())
    assert out["valid"] is True
    assert out["channel"] == "alpha", f"Expected channel 'alpha', got '{out['channel']}'"


# [pr_diff] fail_to_pass
def test_changes_ts_uses_channel():
    """RemixPrereleaseConfig interface and validation must use 'channel' not 'tag'."""
    changes_ts = (Path(REPO) / "scripts" / "utils" / "changes.ts").read_text()

    # Interface must have channel field
    interface_match = re.search(
        r"export\s+interface\s+RemixPrereleaseConfig\s*\{([^}]+)\}",
        changes_ts,
    )
    assert interface_match, "RemixPrereleaseConfig interface not found"
    interface_body = interface_match.group(1)
    assert "channel" in interface_body, \
        "RemixPrereleaseConfig must have 'channel' field"

    # Validation logic must check for 'channel' in parsed object
    assert "'channel' in obj" in changes_ts or '"channel" in obj' in changes_ts, \
        "readRemixPrereleaseConfig must check for 'channel' key"

    # Return value must access obj.channel
    assert "obj.channel" in changes_ts, \
        "Config reader must access obj.channel"


# [pr_diff] fail_to_pass
def test_publish_uses_next_tag():
    """publish.ts must use '--tag next' for remix prerelease, not dynamic tag."""
    publish_ts = (Path(REPO) / "scripts" / "publish.ts").read_text()

    assert "--tag next" in publish_ts, \
        "publish.ts must use '--tag next' for remix prerelease publishing"

    # Must NOT use old pattern of interpolating tag into publish command
    assert "${remixPrereleaseTag}" not in publish_ts, \
        "publish.ts must not interpolate old remixPrereleaseTag into publish command"

    # Variable should be renamed from remixPrereleaseTag to remixPrereleaseChannel
    assert "remixPrereleaseTag" not in publish_ts, \
        "publish.ts must not use old 'remixPrereleaseTag' variable name"
    assert "remixPrereleaseChannel" in publish_ts, \
        "publish.ts should use 'remixPrereleaseChannel' variable name"


# ---------------------------------------------------------------------------
# Config-edit (pr_diff) — documentation/config file update tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_agents_md_documents_channel():
    """AGENTS.md must use 'channel' terminology and document 'next' npm tag."""
    agents_md = (Path(REPO) / "AGENTS.md").read_text()

    # Find the prerelease section (lines around 49-54)
    prerelease_section = ""
    for line in agents_md.split("\n"):
        if "prerelease" in line.lower() or "remix" in line.lower():
            prerelease_section += line + "\n"

    # Must mention "channel" in the prerelease documentation
    assert "channel" in prerelease_section.lower(), \
        "AGENTS.md prerelease section must use 'channel' terminology"

    # Must document that npm dist-tag is always "next"
    assert '"next"' in agents_md, \
        'AGENTS.md must document that npm dist-tag is always "next"'

    # Should reference "channels" not "tags" for transitioning
    assert "prerelease channels" in agents_md.lower() or \
        "between prerelease channels" in agents_md.lower() or \
        "Transitioning between prerelease channels" in agents_md, \
        "AGENTS.md should use 'channels' for transition terminology"


# [pr_diff] fail_to_pass
def test_contributing_md_documents_channel():
    """CONTRIBUTING.md must use 'channel' in prerelease JSON example and docs."""
    contributing_md = (Path(REPO) / "CONTRIBUTING.md").read_text()

    # The JSON example should show "channel", not "tag"
    prerelease_idx = contributing_md.find("prerelease.json")
    assert prerelease_idx >= 0, "CONTRIBUTING.md must mention prerelease.json"
    prerelease_section = contributing_md[prerelease_idx:]

    # Find the JSON block in the prerelease section
    json_start = prerelease_section.find("{")
    json_end = prerelease_section.find("}", json_start) + 1
    assert json_start >= 0 and json_end > json_start, \
        "CONTRIBUTING.md must have a JSON example in prerelease section"
    json_block = prerelease_section[json_start:json_end]
    assert '"channel"' in json_block, \
        "CONTRIBUTING.md prerelease JSON block must use 'channel'"
    assert '"tag"' not in json_block, \
        "CONTRIBUTING.md prerelease JSON block must not use old 'tag' key"

    # Section headers should reference "channels" not "tags"
    assert "channels" in contributing_md.lower(), \
        "CONTRIBUTING.md should use 'channels' terminology"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub / regression
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_changes_ts_still_validates():
    """changes.ts must still validate that the config field is a non-empty string."""
    changes_ts = (Path(REPO) / "scripts" / "utils" / "changes.ts").read_text()

    # Must still have validation logic (not gutted)
    assert "trim()" in changes_ts, \
        "Config validation must still trim whitespace"
    assert ".length === 0" in changes_ts, \
        "Config validation must still check for empty string"

    # Must still return the parsed config value
    assert "valid: true" in changes_ts, \
        "Must still return valid config"
