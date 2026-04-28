"""Structural tests for the version-release skill markdown_authoring task.

The PR adds a new SKILL.md at .agents/skills/version-release/SKILL.md.
These tests act as a sanity gate (Track 1). The actual evaluation signal
comes from Track 2 (Gemini semantic-diff against config_edits).
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/ant-design")
SKILL_DIR = REPO / ".agents" / "skills" / "version-release"
SKILL_FILE = SKILL_DIR / "SKILL.md"


def _read_skill() -> str:
    assert SKILL_FILE.exists(), f"Expected file at {SKILL_FILE} (relative to repo root)"
    return SKILL_FILE.read_text(encoding="utf-8")


def test_skill_file_exists():
    """A new SKILL.md must exist at the expected directory."""
    assert SKILL_DIR.is_dir(), f"Expected directory {SKILL_DIR}"
    assert SKILL_FILE.is_file(), f"Expected file {SKILL_FILE}"
    content = SKILL_FILE.read_text(encoding="utf-8")
    assert len(content.strip()) > 200, (
        f"SKILL.md too short ({len(content)} chars); expected substantive content"
    )


def test_skill_has_frontmatter():
    """SKILL.md must start with YAML frontmatter containing name and description."""
    text = _read_skill()
    assert text.startswith("---\n") or text.startswith("---\r\n"), (
        "SKILL.md must begin with YAML frontmatter delimited by '---' lines"
    )
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    assert m is not None, "SKILL.md must have a closed YAML frontmatter block"
    fm = m.group(1)
    assert re.search(r"(?m)^name:\s*\S", fm), "frontmatter must have a 'name:' field"
    assert re.search(r"(?m)^description:\s*\S", fm), (
        "frontmatter must have a 'description:' field"
    )


def test_skill_recommends_npm_publish():
    """Skill must recommend the canonical release command `npm publish`."""
    text = _read_skill()
    assert "npm publish" in text, (
        "SKILL.md must mention the `npm publish` command (the actual release entrypoint)"
    )


def test_skill_warns_against_npm_run_pub():
    """Skill must warn against using `npm run pub` (the repo's own scripts.pub
    just echoes a redirect to `npm publish`)."""
    text = _read_skill()
    assert "npm run pub" in text, (
        "SKILL.md must mention `npm run pub` (typically as something to avoid, "
        "since the repo's package.json explicitly redirects it)"
    )


def test_skill_references_changelog_lint():
    """Skill must reference the repo's changelog lint script."""
    text = _read_skill()
    assert "lint:changelog" in text, (
        "SKILL.md must reference the `lint:changelog` script used to validate changelogs"
    )


def test_repo_lint_changelog_script_exists():
    """pass_to_pass: The repo's package.json defines a lint:changelog script
    that the skill is documenting."""
    pkg = REPO / "package.json"
    assert pkg.exists()
    import json
    data = json.loads(pkg.read_text(encoding="utf-8"))
    scripts = data.get("scripts", {})
    assert "lint:changelog" in scripts, (
        "Repository's package.json should define a `lint:changelog` script"
    )
    assert "pub" in scripts, "Repository's package.json should define a `pub` script"


def test_git_repo_at_base_commit():
    """pass_to_pass: confirm the test is running in the cloned repo."""
    r = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"git rev-parse failed: {r.stderr}"
    sha = r.stdout.strip()
    assert sha == "75feea4c5543ef2dc68f7832c2774d592fe4a032", (
        f"Expected base commit, got {sha}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_image_generate_image_snapshots():
    """pass_to_pass | CI job 'test image' → step 'generate image snapshots'"""
    r = subprocess.run(
        ["bash", "-lc", 'node node_modules/puppeteer/install.mjs'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'generate image snapshots' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_build():
    """pass_to_pass | CI job 'build' → step 'Build'"""
    r = subprocess.run(
        ["bash", "-lc", 'ut build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_lib_es_module_compile():
    """pass_to_pass | CI job 'test lib/es module' → step 'compile'"""
    r = subprocess.run(
        ["bash", "-lc", 'ut compile'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'compile' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_if_workflow_run_is_trust_check_trust():
    """pass_to_pass | CI job 'Check if workflow run is trusted' → step 'Check trust'"""
    r = subprocess.run(
        ["bash", "-lc", 'if [[ "$REPO" == "ant-design/ant-design" && "$EVENT" == "pull_request" ]]; then\n  echo "trusted=true" >> $GITHUB_OUTPUT\nelse\n  echo "trusted=false" >> $GITHUB_OUTPUT\nfi'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check trust' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_project_run_script():
    """pass_to_pass | CI job 'Build Project' → step 'Run Script'"""
    r = subprocess.run(
        ["bash", "-lc", 'bash ./scripts/ci-mock-project-build.sh'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run Script' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")