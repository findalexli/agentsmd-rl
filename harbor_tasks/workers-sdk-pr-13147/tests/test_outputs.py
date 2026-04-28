"""
Structural checks for the bonk agent instruction file.

This is a markdown_authoring task. The primary evaluation signal is Track 2
(Gemini semantic-diff of config_edits). These tests provide a sanity gate
(Track 1) ensuring distinctive signal markers from the gold markdown diff
are present in the authored file.
"""
import os
import subprocess

REPO = "/workspace/workers-sdk"
BONK_MD = os.path.join(REPO, ".opencode", "agents", "bonk.md")


def test_file_exists():
    """The agent instruction file exists at the expected path."""
    assert os.path.isfile(BONK_MD), f"{BONK_MD} not found"


def test_triggering_comment_rule():
    """The new 'Triggering comment is the task' rule is present."""
    r = subprocess.run(
        ["grep", "-qF", "**Triggering comment is the task:**", BONK_MD],
        capture_output=True,
    )
    assert r.returncode == 0, "Missing 'Triggering comment is the task' rule"


def test_no_re_reviewing_rule():
    """The new 'No re-reviewing on fixup requests' rule is present."""
    r = subprocess.run(
        ["grep", "-qF", "**No re-reviewing on fixup requests:**", BONK_MD],
        capture_output=True,
    )
    assert r.returncode == 0, "Missing 'No re-reviewing on fixup requests' rule"


def test_start_from_triggering_comment_step():
    """The implementation workflow starts from the triggering comment."""
    r = subprocess.run(
        ["grep", "-qF", "**Start from the triggering comment.**", BONK_MD],
        capture_output=True,
    )
    assert r.returncode == 0, "Missing 'Start from the triggering comment' step"


def test_negative_examples_plural():
    """The examples section uses plural 'Negative examples' heading."""
    r = subprocess.run(
        ["grep", "-qF", "Negative examples:", BONK_MD],
        capture_output=True,
    )
    assert r.returncode == 0, "Missing plural 'Negative examples:' heading"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_build():
    """pass_to_pass | CI job 'build' → step 'Build'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build --filter="./packages/*"'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_upload_packages():
    """pass_to_pass | CI job 'build' → step 'Upload packages'"""
    r = subprocess.run(
        ["bash", "-lc", 'node -r esbuild-register .github/prereleases/upload.mjs'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Upload packages' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_cleanup_test_projects_cleanup_e2e_test_projects():
    """pass_to_pass | CI job 'Cleanup Test Projects' → step 'Cleanup E2E test projects'"""
    r = subprocess.run(
        ["bash", "-lc", 'node -r esbuild-register tools/e2e/e2eCleanup.ts'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Cleanup E2E test projects' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")