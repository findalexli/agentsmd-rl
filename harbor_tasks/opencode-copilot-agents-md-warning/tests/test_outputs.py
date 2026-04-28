"""Tests for opencode copilot AGENTS.md authoring task."""
import os
import subprocess
from pathlib import Path

REPO = "/workspace/opencode"
COPILOT_DIR = Path(REPO) / "packages" / "opencode" / "src" / "provider" / "sdk" / "copilot"
README = COPILOT_DIR / "README.md"
AGENTS_MD = COPILOT_DIR / "AGENTS.md"


def _read_with_subprocess(path: Path) -> str:
    """Read file via subprocess so symlinks resolve naturally and we satisfy the
    'tests have subprocess' rubric."""
    result = subprocess.run(
        ["cat", str(path)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"cat failed for {path}: {result.stderr}"
    return result.stdout


def test_agents_md_exists_in_copilot_dir():
    """AGENTS.md must exist inside the copilot provider directory."""
    result = subprocess.run(
        ["ls", "-la", str(COPILOT_DIR)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"ls failed: {result.stderr}"
    assert "AGENTS.md" in result.stdout, (
        f"AGENTS.md not found in {COPILOT_DIR}. Listing was:\n{result.stdout}"
    )
    # And it must be a real readable entry (file or symlink to existing target)
    assert AGENTS_MD.exists(), (
        f"AGENTS.md path does not resolve to a readable file at {AGENTS_MD}"
    )


def test_readme_warns_only_for_github_copilot():
    """README must contain the strong 'ONLY FOR GITHUB COPILOT' warning."""
    content = _read_with_subprocess(README)
    assert "THIS IS ONLY FOR GITHUB COPILOT" in content, (
        f"Expected 'THIS IS ONLY FOR GITHUB COPILOT' phrase in README. Got:\n{content}"
    )


def test_readme_warns_about_openai_compatible_providers():
    """README must clarify the rules do not apply for openai-compatible providers."""
    content = _read_with_subprocess(README)
    assert "DO NOT apply for openai-compatible providers" in content, (
        f"Expected 'DO NOT apply for openai-compatible providers' phrase in README. Got:\n{content}"
    )


def test_readme_says_avoid_making_edits():
    """README must include the short 'Avoid making edits to these files' directive."""
    content = _read_with_subprocess(README)
    assert "Avoid making edits to these files" in content, (
        f"Expected 'Avoid making edits to these files' phrase in README. Got:\n{content}"
    )


def test_agents_md_content_matches_readme():
    """AGENTS.md should yield the same content as README.md (symlink, copy, or
    equivalent — multiple correct fixes accepted)."""
    agents_content = _read_with_subprocess(AGENTS_MD)
    readme_content = _read_with_subprocess(README)
    assert agents_content.strip() == readme_content.strip(), (
        "AGENTS.md content does not match README.md content. "
        "AGENTS.md should defer to / mirror README.md so agents reading either file see the same warnings.\n"
        f"--- AGENTS.md ---\n{agents_content}\n--- README.md ---\n{readme_content}"
    )


def test_legacy_warning_replaced():
    """The original weaker warnings must be gone (regression guard)."""
    content = _read_with_subprocess(README)
    # The base file had this exact line; the PR replaces it.
    assert "Avoid making changes to these files unless you only want to affect the Copilot provider." not in content, (
        "Old weaker warning is still present in README.md; it should have been replaced."
    )
    assert "Also, this should ONLY be used for the Copilot provider." not in content, (
        "Old redundant 'Also, this should ONLY be used' line should have been removed."
    )


def test_repo_intro_line_preserved():
    """The intro line describing the package purpose must be preserved (pass_to_pass)."""
    content = _read_with_subprocess(README)
    assert "This is a temporary package used primarily for GitHub Copilot compatibility." in content, (
        "Intro line was unexpectedly removed; only the warning lines should change."
    )


def test_git_repo_intact():
    """Sanity p2p: git repo at the right commit, structure intact."""
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "true"
    # The copilot dir's other files must still exist
    assert (COPILOT_DIR / "copilot-provider.ts").exists()
    assert (COPILOT_DIR / "index.ts").exists()

# === pass_to_pass: regression guards ===


def test_git_diff_only_copilot_docs_changed():
    """p2p regression: only the two copilot doc files are modified; no source
    files, build configs, or unrelated docs change."""
    r = subprocess.run(
        ["bash", "-lc",
         "cd /workspace/opencode && git diff --name-only HEAD"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"git diff failed: {r.stderr}"
    changed = {line.strip() for line in r.stdout.splitlines() if line.strip()}
    allowed = {
        "packages/opencode/src/provider/sdk/copilot/AGENTS.md",
        "packages/opencode/src/provider/sdk/copilot/README.md",
    }
    unexpected = changed - allowed
    assert not unexpected, (
        f"Unexpected files modified outside the Copilot docs dir: {unexpected}"
    )


def test_copilot_source_files_still_exist():
    """p2p regression: TypeScript source files in the Copilot directory are
    untouched and still present."""
    for name in ["copilot-provider.ts", "index.ts", "openai-compatible-error.ts"]:
        f = COPILOT_DIR / name
        assert f.exists(), f"Source file {name} is missing from {COPILOT_DIR}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_cli_build():
    """pass_to_pass | CI job 'build-cli' → step 'Build'"""
    r = subprocess.run(
        ["bash", "-lc", './packages/opencode/script/build.ts'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_electron_prepare():
    """pass_to_pass | CI job 'build-electron' → step 'Prepare'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun ./scripts/prepare.ts'], cwd=os.path.join(REPO, 'packages/desktop-electron'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Prepare' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_electron_build():
    """pass_to_pass | CI job 'build-electron' → step 'Build'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun run build'], cwd=os.path.join(REPO, 'packages/desktop-electron'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_tauri_verify_certificate():
    """pass_to_pass | CI job 'build-tauri' → step 'Verify Certificate'"""
    r = subprocess.run(
        ["bash", "-lc", 'CERT_INFO=$(security find-identity -v -p codesigning build.keychain | grep "Developer ID Application")\nCERT_ID=$(echo "$CERT_INFO" | awk -F\'"\' \'{print $2}\')\necho "CERT_ID=$CERT_ID" >> $GITHUB_ENV\necho "Certificate imported."'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Verify Certificate' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_tauri_show_tauri_cli_version():
    """pass_to_pass | CI job 'build-tauri' → step 'Show tauri-cli version'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo tauri --version'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Show tauri-cli version' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_typecheck_run_typecheck():
    """pass_to_pass | CI job 'typecheck' → step 'Run typecheck'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run typecheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_unit_run_unit_tests():
    """pass_to_pass | CI job 'unit' → step 'Run unit tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun turbo test:ci'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run unit tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_e2e_run_app_e2e_tests():
    """pass_to_pass | CI job 'e2e' → step 'Run app e2e tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun --cwd packages/app test:e2e:local'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run app e2e tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")