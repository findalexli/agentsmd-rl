"""
Task: remix-chore-always-tag-remix-prerelease-as-next
Repo: remix-run/remix @ 40a755c50f40ed444a928363beddd75e6edc1f52
PR:   10981

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = Path("/workspace/remix")


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
    """Modified TypeScript files import and execute without errors."""
    code = """
    import { readRemixPrereleaseConfig } from './scripts/utils/changes.ts';
    const config = readRemixPrereleaseConfig();
    if (!config.exists) throw new Error('Expected config to exist');
    if (!config.valid) throw new Error('Expected config to be valid: ' + config.error);
    if (!config.config) throw new Error('Expected config.config to exist');
    const key = Object.keys(config.config)[0];
    const val = config.config[key];
    if (!val || typeof val !== 'string') throw new Error('Expected non-empty string config value');
    console.log('OK');
    """
    r = subprocess.run(
        ["npx", "tsx", "-e", code],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"changes.ts import/execution failed: {r.stderr}"


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

# [pr_diff] fail_to_pass
def test_not_stub():
    """Modified functions have real logic, not just pass/return."""
    changes_src = (REPO / "scripts" / "utils" / "changes.ts").read_text()
    publish_src = (REPO / "scripts" / "publish.ts").read_text()
    # readRemixPrereleaseConfig should have multiple statements
    assert "obj.channel.trim()" in changes_src,         "readRemixPrereleaseConfig must validate channel (trim check)"
    assert "semver.inc" in changes_src,         "getNextVersion must use semver for version calculation"
    assert "pnpm publish" in publish_src,         "publish script must have real publish commands"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_build_packages():
    """pass_to_pass | CI job 'build' → step 'Build packages'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build packages' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_tests():
    """pass_to_pass | CI job 'test' → step 'Run tests' (scoped to packages excluding browser-dependent tests)"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm --filter "./packages/*" --filter "!@remix-run/component" --filter "!@remix-run/interaction" --filter "!@remix-run/headers" test'],
        cwd=REPO, capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_format_format():
    """pass_to_pass | CI job 'format' → step 'Format check'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm format:check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Format check' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_lint():
    """pass_to_pass | CI job 'check' → step 'Lint'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Lint' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_typecheck():
    """pass_to_pass | CI job 'check' → step 'Typecheck'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Typecheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_check_change_files():
    """pass_to_pass | CI job 'check' → step 'Check change files'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm changes:validate'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check change files' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")