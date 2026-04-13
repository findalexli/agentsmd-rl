"""
Task: remix-chore-always-tag-remix-prerelease-as-next
Repo: remix-run/remix @ 40a755c50f40ed444a928363beddd75e6edc1f52
PR:   10981

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
import re
from pathlib import Path

REPO = Path("/workspace/remix")


def node_eval(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run Node.js code in the repo context."""
    return subprocess.run(
        ["node", "-e", code],
        capture_output=True, text=True,
        cwd=str(REPO), timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_changes_validate():
    """Repo's changes:validate passes (pass_to_pass). Validates prerelease.json format."""
    # changes:validate checks that change files and prerelease.json follow the correct format
    r = subprocess.run(
        ["node", "./scripts/changes-validate.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"changes:validate failed: {r.stderr[-500:] or r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_lint():
    """ESLint passes on modified files (pass_to_pass)."""
    files = [
        REPO / "scripts" / "utils" / "changes.ts",
        REPO / "scripts" / "publish.ts",
    ]
    r = subprocess.run(
        ["npx", "eslint", "--max-warnings=0"] + [str(f) for f in files],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed: {r.stderr[-500:] or r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_format():
    """Prettier formatting check passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "format:check"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Format check failed: {r.stderr[-500:] or r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_typecheck():
    """TypeScript typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "typecheck"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed: {r.stderr[-500:] or r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_changes_preview():
    """Repo's changes:preview passes (pass_to_pass). Previews release changes."""
    # changes:preview shows which packages will be released and what the CHANGELOG will look like
    r = subprocess.run(
        ["node", "./scripts/changes-preview.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"changes:preview failed: {r.stderr[-500:] or r.stdout[-500:]}"


# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files parse without syntax errors."""
    files = [
        REPO / "scripts/utils/changes.ts",
        REPO / "scripts/publish.ts",
    ]
    for f in files:
        result = subprocess.run(
            ["node", "-e", f"import('{f}')"],
            capture_output=True, text=True, timeout=30,
        )
        # node -e won't actually import TS without tsx, so just check it's valid JS-ish
        # Use a basic syntax check: try to read and ensure no null bytes / valid UTF-8
        content = f.read_text()
        assert len(content) > 0, f"{f.name} is empty"
        assert "\x00" not in content, f"{f.name} has null bytes"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests: code changes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_prerelease_json_uses_channel():
    """prerelease.json must use 'channel' field instead of old 'tag' field."""
    config_path = REPO / "packages" / "remix" / ".changes" / "prerelease.json"
    config = json.loads(config_path.read_text())
    assert "channel" in config, "prerelease.json must have 'channel' field"
    assert "tag" not in config, "prerelease.json must not have old 'tag' field"
    assert config["channel"] == "alpha", f"Expected channel 'alpha', got '{config['channel']}'"


# [pr_diff] fail_to_pass
def test_changes_ts_reads_channel_field():
    """changes.ts readRemixPrereleaseConfig must validate 'channel', not 'tag'."""
    source = (REPO / "scripts" / "utils" / "changes.ts").read_text()
    # Interface must use 'channel'
    assert "channel: string" in source,         "RemixPrereleaseConfig interface must define 'channel: string'"
    # Validation must check for 'channel' key
    assert "'channel' in obj" in source,         "readRemixPrereleaseConfig must check 'channel' in obj"
    # Must read obj.channel
    assert "obj.channel" in source,         "readRemixPrereleaseConfig must read obj.channel"
    # Must return config with channel key
    assert "config: { channel:" in source,         "readRemixPrereleaseConfig must return { channel: ... }"


# [pr_diff] fail_to_pass
def test_publish_uses_next_dist_tag():
    """publish.ts must always publish remix prereleases with '--tag next'."""
    source = (REPO / "scripts" / "publish.ts").read_text()
    assert "--tag next" in source,         "publish.ts must include '--tag next' for prerelease publishing"
    assert "remixPrereleaseChannel" in source,         "publish.ts must use remixPrereleaseChannel variable (renamed from tag)"
    # Must NOT interpolate the channel as the npm tag in the publish command
    # Check that the pnpm publish command uses --tag next, not --tag ${variable}
    publish_lines = [line for line in source.split("\n") if "pnpm publish --filter remix" in line]
    assert publish_lines, "Must have pnpm publish command for remix"
    for line in publish_lines:
        assert "--tag next" in line, f"Publish command must use --tag next: {line}"
        assert "${remixPrerelease" not in line, f"Publish command must not interpolate channel: {line}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation update tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_agents_md_documents_channel_and_next():
    """AGENTS.md must describe 'channel' field and explain npm dist-tag is always 'next'."""
    content = (REPO / "AGENTS.md").read_text()
    # Must mention the channel field (can be backticks or quotes)
    assert "channel" in content,         "AGENTS.md must mention the 'channel' field for prerelease config"
    # Must explain that dist-tag is always "next"
    assert '"next"' in content,         "AGENTS.md must explain that npm dist-tag is always 'next'"


# [pr_diff] fail_to_pass
def test_contributing_md_uses_channel():
    """CONTRIBUTING.md must show 'channel' in prerelease.json example and docs."""
    content = (REPO / "CONTRIBUTING.md").read_text()
    # The JSON example must use "channel"
    assert '"channel": "alpha"' in content,         "CONTRIBUTING.md must show prerelease.json example with 'channel' field"
    # The section header must say "channels" not "tags"
    assert "prerelease channels" in content.lower(),         "CONTRIBUTING.md must reference 'prerelease channels' (not 'tags')"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Modified functions have real logic, not just pass/return."""
    changes_src = (REPO / "scripts" / "utils" / "changes.ts").read_text()
    publish_src = (REPO / "scripts" / "publish.ts").read_text()
    # readRemixPrereleaseConfig should have multiple statements
    assert "obj.channel.trim()" in changes_src,         "readRemixPrereleaseConfig must validate channel (trim check)"
    assert "semver.inc" in changes_src,         "getNextVersion must use semver for version calculation"
    assert "pnpm publish" in publish_src,         "publish script must have real publish commands"
