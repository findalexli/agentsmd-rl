"""
Task: lotti-widgetbook-macos-release
Repo: matthiasn/lotti @ 70765a65c0428ad8086177d7affc53b7a7b9c420
PR:   2835

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/lotti"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Makefile is valid and build script parses without bash syntax errors."""
    # Verify Makefile is parseable by make (dry run of an existing target)
    r = subprocess.run(
        ["make", "-n", "test"],
        cwd=REPO, capture_output=True, timeout=15,
    )
    assert r.returncode == 0, f"Makefile syntax error:\n{r.stderr.decode()}"

    # Verify build script has valid bash syntax
    script = Path(REPO) / "tool" / "widgetbook" / "build_macos_bundle.sh"
    if script.exists():
        r = subprocess.run(
            ["bash", "-n", str(script)],
            capture_output=True, timeout=10,
        )
        assert r.returncode == 0, f"Build script syntax error:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_build_script_structure():
    """Build script exists with argument parsing, platform check, and strict mode."""
    script = Path(REPO) / "tool" / "widgetbook" / "build_macos_bundle.sh"
    assert script.exists(), "Build script tool/widgetbook/build_macos_bundle.sh must exist"
    content = script.read_text()

    # Strict bash mode
    assert "set -euo pipefail" in content, "Script must use strict bash mode"

    # Argument parsing for build-skip and upload capabilities
    assert "skip" in content.lower() or "no.build" in content.lower() or "build=false" in content.lower(), \
        "Script must support skipping the build step"
    assert "upload" in content.lower() or "release" in content.lower() or "publish" in content.lower(), \
        "Script must support uploading to a release"

    # Platform validation (macOS only)
    assert "uname" in content, "Script must check the OS platform"
    assert "Darwin" in content, "Script must validate it's running on macOS"

    # Flutter build command for widgetbook
    assert "widgetbook" in content.lower(), "Script must reference widgetbook"
    assert "flutter" in content.lower(), "Script must invoke flutter"

    # Output paths
    assert "Lotti_Widgetbook" in content, "Script must use Lotti_Widgetbook naming"


# [pr_diff] fail_to_pass
def test_makefile_widgetbook_targets():
    """Makefile has widgetbook build, upload, and publish targets referencing the build script."""
    makefile = Path(REPO) / "Makefile"
    content = makefile.read_text()

    # All three targets must exist
    assert "widgetbook_macos_build" in content, \
        "Makefile must have widgetbook_macos_build target"
    assert "widgetbook_macos_upload" in content, \
        "Makefile must have widgetbook_macos_upload target"
    assert "widgetbook_macos_publish" in content, \
        "Makefile must have widgetbook_macos_publish target"

    # Targets must reference a widgetbook build script or tool
    assert "build_macos_bundle" in content or "widgetbook" in content.lower(), \
        "Makefile targets must invoke a widgetbook build script"

    # Verify each target has a recipe (command line after target declaration)
    import re
    for target in ["widgetbook_macos_build", "widgetbook_macos_upload", "widgetbook_macos_publish"]:
        pattern = rf"^{target}\s*:.*\n\t.+"
        assert re.search(pattern, content, re.MULTILINE), \
            f"Target {target} must have a recipe (command)"


# [pr_diff] fail_to_pass
def test_ci_workflow_structure():
    """CI workflow for widgetbook macOS release is valid YAML with proper structure."""
    import yaml

    # Find a widgetbook-related workflow file
    workflows_dir = Path(REPO) / ".github" / "workflows"
    assert workflows_dir.exists(), ".github/workflows directory must exist"

    widgetbook_wfs = [
        f for f in workflows_dir.glob("*.yml")
        if "widgetbook" in f.name.lower()
    ]
    assert len(widgetbook_wfs) > 0, \
        "Must have a widgetbook-related workflow in .github/workflows/"

    wf_path = widgetbook_wfs[0]
    content = wf_path.read_text()
    data = yaml.safe_load(content)

    # Must have jobs and trigger config
    assert "jobs" in data, "Workflow must define jobs"
    assert "on" in data or True in data, "Workflow must have trigger config"

    # Must trigger on pushes to main
    on_config = data.get("on") or data.get(True, {})
    push_config = on_config.get("push", {}) if isinstance(on_config, dict) else {}
    branches = push_config.get("branches", [])
    assert "main" in branches, "Workflow must trigger on pushes to main branch"

    # Must reference the build script or flutter build
    assert "build_macos_bundle" in content or "flutter build macos" in content, \
        "Workflow must build the widgetbook macOS bundle"

    # Must have a release/upload step
    assert "release" in content.lower(), \
        "Workflow must include release upload steps"


# [pr_diff] fail_to_pass

    # Must support gh CLI for releases
    assert "gh release" in content or "gh " in content, \
        "Script must use gh CLI for release management"

    # Must handle release tag
    assert "widgetbook-macos-latest" in content or "release_tag" in content, \
        "Script must manage a release tag"

    # Must support creating or editing releases
    assert "release create" in content or "release edit" in content, \
        "Script must be able to create/edit GitHub releases"

    # Must upload the zip artifact
    assert "release upload" in content or ".zip" in content, \
        "Script must upload the zip artifact"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:line 148 @ 70765a65

    # AGENTS.md says: "Use fvm when running any flutter command"
    # Script should check for fvm and use it when available
    assert "fvm" in content, \
        "Build script must support fvm per AGENTS.md guidelines"


# ---------------------------------------------------------------------------
# Config edit tests — README documentation update
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # Must have a section about widgetbook export
    content_lower = content.lower()
    assert "widgetbook" in content_lower and "export" in content_lower, \
        "README must document widgetbook export"

    # Must document the make commands
    assert "widgetbook_macos_build" in content, \
        "README must document the widgetbook_macos_build make target"
    assert "widgetbook_macos_upload" in content or "widgetbook_macos_publish" in content, \
        "README must document upload/publish make targets"

    # Must mention output paths
    assert "Lotti_Widgetbook" in content, \
        "README must reference the output bundle name"

    # Must mention that the app is unsigned (important usage note)
    assert "unsigned" in content_lower or "quarantine" in content_lower, \
        "README should note the app is unsigned or mention quarantine handling"


# [config_edit] fail_to_pass

    # Must mention the output directory/paths
    assert "widgetbook_macos_export" in content or "build/" in content, \
        "README must document the output location for build artifacts"

    # Must mention the zip file
    assert ".zip" in content or "zip" in content.lower(), \
        "README must mention the zip artifact"
