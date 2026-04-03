"""
Task: bun-featscripts-enhance-buildkitefailurests-to-fetch
Repo: oven-sh/bun @ 6f6f76f0c07d592ad14b1d64a2e7037deb587c21
PR:   26177

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/bun"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via --help flag
# ---------------------------------------------------------------------------

def _run_help():
    """Helper: run the script with --help and return (stdout, stderr, returncode)."""
    r = subprocess.run(
        ["bun", "run", "scripts/buildkite-failures.ts", "--help"],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    return r.stdout.decode(), r.stderr.decode(), r.returncode


# [pr_diff] fail_to_pass
def test_help_flag_exits_zero():
    """Script must support --help flag that prints usage and exits 0."""
    stdout, stderr, rc = _run_help()
    assert rc == 0, f"--help should exit 0, got {rc}.\nstderr: {stderr}"
    assert len(stdout) > 50, f"--help should print substantial usage text, got: {stdout!r}"


# [pr_diff] fail_to_pass
def test_help_documents_wait_option():
    """--help output must document the --wait polling option."""
    stdout, _, rc = _run_help()
    assert rc == 0, "--help must exit 0 first"
    text = stdout.lower()
    assert "--wait" in text, "--help should document the --wait flag"
    assert "poll" in text or "complete" in text or "wait" in text, \
        "--help should explain what --wait does (polling/waiting)"


# [pr_diff] fail_to_pass
def test_help_documents_log_saving():
    """--help output must mention log file saving to /tmp."""
    stdout, _, rc = _run_help()
    assert rc == 0, "--help must exit 0 first"
    assert "/tmp/bun-build" in stdout, \
        "--help should document the log file path format /tmp/bun-build-*"


# [pr_diff] fail_to_pass
def test_help_documents_input_types():
    """--help output must document supported input types (build number, PR, branch)."""
    stdout, _, rc = _run_help()
    assert rc == 0, "--help must exit 0 first"
    text = stdout.lower()
    # Must document at least build number and PR URL inputs
    assert "build" in text, "--help should mention build number input"
    has_pr = "pr" in text or "pull" in text or "#number" in stdout.lower()
    assert has_pr, "--help should mention PR URL or #number input"
    has_branch = "branch" in text
    assert has_branch, "--help should mention branch input"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — CLAUDE.md documentation update
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — existing functionality preserved
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_flags_preserved():
    """Script must still support existing --flaky and --warnings flags."""
    script = Path(REPO) / "scripts" / "buildkite-failures.ts"
    assert script.exists(), "Script file must exist"
    content = script.read_text()
    assert "--warnings" in content, "Script must still support --warnings flag"
    assert "--flaky" in content, "Script must still support --flaky flag"
    assert "buildkite.com" in content, "Script must still reference BuildKite API"
