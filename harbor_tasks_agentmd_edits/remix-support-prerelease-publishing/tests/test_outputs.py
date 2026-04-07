"""
Task: remix-support-prerelease-publishing
Repo: remix @ ecb2847dea0dcebb0972c8de23cdfa661483745e
PR:   remix-run/remix#10953

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/remix"


def _run_ts(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Write a temp .ts file in the repo and run it with node --experimental-strip-types."""
    script_path = Path(REPO) / "_eval_tmp.ts"
    script_path.write_text(script)
    try:
        return subprocess.run(
            ["node", "--experimental-strip-types", "--no-warnings", str(script_path)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_changes_ts_exists():
    """scripts/utils/changes.ts must exist and be non-empty."""
    changes_ts = Path(REPO) / "scripts" / "utils" / "changes.ts"
    assert changes_ts.exists(), "scripts/utils/changes.ts missing"
    content = changes_ts.read_text()
    assert len(content) > 100, "changes.ts is suspiciously small"
    assert "export" in content, "changes.ts must have exports"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_parse_all_change_files_api():
    """parseAllChangeFiles must be exported and return {valid, releases} shape."""
    result = _run_ts("""
import { parseAllChangeFiles } from './scripts/utils/changes.ts'
let result = parseAllChangeFiles()
// Result must have 'valid' boolean field
if (typeof result.valid !== 'boolean') {
    console.error("result.valid is not boolean:", typeof result.valid)
    process.exit(1)
}
// If valid, must have releases array
if (result.valid) {
    if (!Array.isArray(result.releases)) {
        console.error("result.releases is not an array")
        process.exit(1)
    }
}
console.log(JSON.stringify({ valid: result.valid, hasReleases: result.valid && Array.isArray(result.releases) }))
""")
    assert result.returncode == 0, (
        f"parseAllChangeFiles not available or wrong shape:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )
    data = json.loads(result.stdout.strip())
    assert "valid" in data, "Missing 'valid' in result"
    assert "hasReleases" in data, "Missing 'hasReleases' in result"


# [pr_diff] fail_to_pass
def test_read_remix_prerelease_config():
    """readRemixPrereleaseConfig must be exported and read prerelease.json."""
    result = _run_ts("""
import { readRemixPrereleaseConfig } from './scripts/utils/changes.ts'
let config = readRemixPrereleaseConfig()
console.log(JSON.stringify(config))
""")
    assert result.returncode == 0, (
        f"readRemixPrereleaseConfig not available:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )
    data = json.loads(result.stdout.strip())
    assert data.get("exists") is True, f"prerelease config should exist, got: {data}"
    assert data.get("valid") is True, f"prerelease config should be valid, got: {data}"
    assert data["config"]["tag"] == "alpha", f"Expected tag='alpha', got: {data}"


# [pr_diff] fail_to_pass
def test_publish_dry_run():
    """publish.ts must support --dry-run flag and show dry run output."""
    result = subprocess.run(
        ["node", "--experimental-strip-types", "--no-warnings",
         "scripts/publish.ts", "--dry-run"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    combined = result.stdout + result.stderr
    assert "DRY RUN" in combined.upper() or "dry run" in combined.lower(), (
        f"--dry-run flag not supported or no dry run output:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )


# [pr_diff] fail_to_pass
def test_prerelease_json_exists():
    """packages/remix/.changes/prerelease.json must exist with tag=alpha."""
    prerelease_path = Path(REPO) / "packages" / "remix" / ".changes" / "prerelease.json"
    assert prerelease_path.exists(), "packages/remix/.changes/prerelease.json missing"
    data = json.loads(prerelease_path.read_text())
    assert "tag" in data, f"prerelease.json missing 'tag' field: {data}"
    assert data["tag"] == "alpha", f"Expected tag='alpha', got '{data['tag']}'"


# [pr_diff] fail_to_pass
def test_semver_module_removed():
    """scripts/utils/semver.ts should be removed (logic moved into changes.ts)."""
    semver_path = Path(REPO) / "scripts" / "utils" / "semver.ts"
    assert not semver_path.exists(), (
        "scripts/utils/semver.ts still exists — getNextVersion should be in changes.ts"
    )


# [pr_diff] fail_to_pass
def test_two_phase_publish_logic():
    """publish.ts must import readRemixPrereleaseConfig for two-phase publishing."""
    publish_src = (Path(REPO) / "scripts" / "publish.ts").read_text()
    assert "readRemixPrereleaseConfig" in publish_src, (
        "publish.ts must import readRemixPrereleaseConfig from changes.ts"
    )
    # Must handle the two-phase publish: filter out remix, then publish remix separately
    assert "--filter" in publish_src, (
        "publish.ts must use pnpm --filter for two-phase publishing"
    )
    assert "remixPrereleaseTag" in publish_src or "prereleaseTag" in publish_src.lower() or "prerelease" in publish_src.lower(), (
        "publish.ts must handle prerelease tag for remix package"
    )


# ---------------------------------------------------------------------------
# Config/documentation update tests (agentmd-edit)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_agents_md_prerelease_docs():
    """AGENTS.md must document prerelease mode for the remix package."""
    agents_md = (Path(REPO) / "AGENTS.md").read_text()
    # Must mention prerelease mode
    assert "prerelease" in agents_md.lower(), (
        "AGENTS.md should document prerelease mode"
    )
    # Must mention prerelease.json
    assert "prerelease.json" in agents_md, (
        "AGENTS.md should reference the prerelease.json config file"
    )
    # Must mention graduating from prerelease
    assert "graduating" in agents_md.lower() or "graduate" in agents_md.lower() or "stable" in agents_md.lower(), (
        "AGENTS.md should document how to graduate from prerelease to stable"
    )


# [pr_diff] fail_to_pass
def test_contributing_md_prerelease_section():
    """CONTRIBUTING.md must have a prerelease mode section."""
    contributing = (Path(REPO) / "CONTRIBUTING.md").read_text()
    # Must have a prerelease section
    assert "prerelease" in contributing.lower(), (
        "CONTRIBUTING.md should document prerelease mode"
    )
    # Must explain how to bump prerelease versions
    assert "prerelease.json" in contributing, (
        "CONTRIBUTING.md should reference prerelease.json"
    )
    # Must explain tag transitions (alpha -> beta)
    assert "alpha" in contributing.lower() and "beta" in contributing.lower(), (
        "CONTRIBUTING.md should explain tag transitions (e.g., alpha to beta)"
    )


# ---------------------------------------------------------------------------
# Agent config compliance (pass_to_pass)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:56 @ ecb2847
def test_preview_scripts_documented():
    """AGENTS.md must document the dry-run preview command for publish script."""
    agents_md = (Path(REPO) / "AGENTS.md").read_text()
    # The existing rule at line 56 says to test change/release code with preview scripts.
    # After this PR, it should also mention --dry-run for publish.ts
    assert "changes:preview" in agents_md, (
        "AGENTS.md should still document pnpm changes:preview"
    )
    assert "publish" in agents_md.lower(), (
        "AGENTS.md should reference publish script testing"
    )
