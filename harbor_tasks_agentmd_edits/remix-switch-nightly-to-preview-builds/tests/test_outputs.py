"""
Task: remix-switch-nightly-to-preview-builds
Repo: remix-run/remix @ 721dac4c6704d5b3e8428887af21accdcb3b23ea
PR:   remix-run/remix#11003

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/remix"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / structural checks
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified TypeScript and YAML files must parse without errors."""
    script_path = Path(f"{REPO}/scripts/setup-installable-branch.ts")
    assert script_path.exists(), "setup-installable-branch.ts must exist"
    content = script_path.read_text()
    assert content.count("{") == content.count("}"), "Unbalanced braces in script"
    assert "parseArgs" in content, "Script must contain parseArgs call"

    preview_wf = Path(f"{REPO}/.github/workflows/preview.yml")
    assert preview_wf.exists(), "preview.yml must exist"
    yaml_content = preview_wf.read_text()
    assert "name:" in yaml_content, "YAML must have a name field"
    assert "jobs:" in yaml_content, "YAML must have jobs section"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral + structural tests
# ---------------------------------------------------------------------------

def test_setup_script_requires_positional_arg():
    """setup-installable-branch.ts must require a branch name as positional argument."""
    # Run the TS script with no arguments to test argument-parsing behavior.
    # Fixed version: immediately throws "You must provide an installable branch name"
    # Base version: defaults to 'nightly', proceeds past arg parsing (different error)
    r = subprocess.run(
        ["node", "--experimental-strip-types", "--no-warnings",
         "scripts/setup-installable-branch.ts"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    combined = r.stdout + r.stderr

    # If TS module loading fails entirely (import resolution), fall back to source check
    if any(marker in combined for marker in [
        "ERR_MODULE_NOT_FOUND", "Cannot find module",
        "Cannot use import statement", "ERR_UNKNOWN_FILE_EXTENSION",
    ]):
        script = Path(f"{REPO}/scripts/setup-installable-branch.ts").read_text()
        assert "You must provide" in script or "must provide" in script.lower(), \
            "Script must throw when no branch name is provided"
        assert "|| 'nightly'" not in script and '|| "nightly"' not in script, \
            "Script must not default to 'nightly'"
        return

    # Primary behavioral check
    assert r.returncode != 0, "Script must exit non-zero with no branch arg"
    assert "must provide" in combined.lower(), \
        f"Script must error about missing branch name. Got: {combined[:500]}"


def test_nightly_workflow_removed():
    """The nightly.yml workflow file must be deleted."""
    nightly_yml = Path(f"{REPO}/.github/workflows/nightly.yml")
    assert not nightly_yml.exists(), \
        "nightly.yml should be deleted — builds now happen in preview.yml"


def test_preview_workflow_continuous_build():
    """preview.yml must trigger on push to main (continuous builds, not nightly)."""
    preview_yml = Path(f"{REPO}/.github/workflows/preview.yml").read_text()
    assert "push:" in preview_yml, "preview.yml must have push trigger"
    assert "main" in preview_yml, "preview.yml must reference main branch"
    assert "workflow_dispatch" in preview_yml, \
        "preview.yml must support workflow_dispatch for experimental builds"
    assert "PR Preview" not in preview_yml, \
        "Workflow name should be updated from 'PR Preview'"


def test_readme_documents_preview_install():
    """README.md must document the preview branch install command, not nightly."""
    readme = Path(f"{REPO}/README.md").read_text()
    assert "remix-run/remix#preview" in readme, \
        "README must show install command using #preview branch"
    assert "remix-run/remix#nightly" not in readme, \
        "README should no longer reference #nightly branch"


def test_contributing_documents_preview_builds():
    """CONTRIBUTING.md must have Preview builds section with preview branch info."""
    contributing = Path(f"{REPO}/CONTRIBUTING.md").read_text()
    assert "remix-run/remix#preview" in contributing, \
        "CONTRIBUTING.md must show preview install command"
    assert "remix-run/remix#nightly" not in contributing, \
        "CONTRIBUTING.md should no longer reference #nightly install"
    assert "## Nightly Builds" not in contributing, \
        "CONTRIBUTING.md should not have 'Nightly Builds' section header"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — anti-regression
# ---------------------------------------------------------------------------

def test_setup_script_no_overwrite_protection():
    """Script should not have branch overwrite protection (preview is force-pushed)."""
    script = Path(f"{REPO}/scripts/setup-installable-branch.ts").read_text()
    assert "allowedOverwrites" not in script, \
        "Script should not have allowedOverwrites branch protection"
    assert "remoteBranches" not in script, \
        "Script should not check remote branches for overwrite protection"
