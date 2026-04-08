"""
Task: remix-add-script-to-setup-a
Repo: remix-run/remix @ 598a92e3dc3488b02da7e4edafd1ff2498cc4c34
PR:   10964

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/remix"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_process_ts_exists():
    """scripts/utils/process.ts exists and exports logAndExec."""
    p = Path(f"{REPO}/scripts/utils/process.ts")
    assert p.exists(), "scripts/utils/process.ts not found"
    content = p.read_text()
    assert "logAndExec" in content, "logAndExec not found in process.ts"
    assert "export" in content, "Missing exports in process.ts"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via subprocess
# ---------------------------------------------------------------------------

def test_logandexec_capture_returns_output():
    """logAndExec(cmd, true) returns the command's stdout as a string."""
    script = Path(REPO) / "_eval_capture.mjs"
    script.write_text(
        "let mod = await import('./scripts/utils/process.ts');\n"
        "let result = mod.logAndExec('echo CAPTURE_WORKS', true);\n"
        "if (typeof result !== 'string' || !result.includes('CAPTURE_WORKS')) {\n"
        "  process.stderr.write("
        "'logAndExec(cmd, true) returned ' + typeof result + ': ' + String(result));\n"
        "  process.exit(1);\n"
        "}\n"
        "process.stdout.write('PASS');\n"
    )
    try:
        r = subprocess.run(
            ["node", "--experimental-strip-types", str(script)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"Capture test failed (rc={r.returncode}): {r.stderr}"
        assert "PASS" in r.stdout, f"Expected PASS in output, got: {r.stdout}"
    finally:
        script.unlink(missing_ok=True)


def test_logandexec_default_returns_string():
    """logAndExec(cmd) without capture returns empty string, not void."""
    script = Path(REPO) / "_eval_nocapture.mjs"
    script.write_text(
        "let mod = await import('./scripts/utils/process.ts');\n"
        "let result = mod.logAndExec('echo nocapture_test');\n"
        "if (typeof result !== 'string') {\n"
        "  process.stderr.write("
        "'logAndExec() returned ' + typeof result + ' instead of string');\n"
        "  process.exit(1);\n"
        "}\n"
        "process.stdout.write('PASS');\n"
    )
    try:
        r = subprocess.run(
            ["node", "--experimental-strip-types", str(script)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"No-capture test failed (rc={r.returncode}): {r.stderr}"
        assert "PASS" in r.stdout, f"Expected PASS in output, got: {r.stdout}"
    finally:
        script.unlink(missing_ok=True)


def test_setup_script_exists():
    """scripts/setup-installable-branch.ts exists with key functionality."""
    p = Path(f"{REPO}/scripts/setup-installable-branch.ts")
    assert p.exists(), "scripts/setup-installable-branch.ts not found"
    content = p.read_text()
    assert "logAndExec" in content, "Script must use logAndExec"
    assert "gitignore" in content.lower(), "Script must handle .gitignore"
    assert "dependencies" in content, "Script must update package dependencies"
    assert "parseArgs" in content or "argv" in content, \
        "Script must accept branch name argument"


def test_package_json_has_setup_script():
    """package.json registers the setup-installable-branch npm script."""
    pkg = json.loads(Path(f"{REPO}/package.json").read_text())
    scripts = pkg.get("scripts", {})
    assert "setup-installable-branch" in scripts, \
        "package.json must have setup-installable-branch script"


def test_nightly_workflow_exists():
    """GitHub Actions nightly workflow exists with correct triggers."""
    p = Path(f"{REPO}/.github/workflows/nightly.yml")
    assert p.exists(), ".github/workflows/nightly.yml not found"
    content = p.read_text()
    assert "schedule" in content, "Workflow must have schedule trigger"
    assert "setup-installable-branch" in content, \
        "Workflow must run setup-installable-branch script"


def test_readme_installation_section():
    """README.md has Installation section with nightly build instructions."""
    content = Path(f"{REPO}/README.md").read_text()
    assert "## Installation" in content, \
        "README.md must have '## Installation' section"
    assert "nightly" in content, "README.md must mention the nightly branch"
    assert "remix-run/remix#" in content and "path:" in content, \
        "README.md must show the github#branch&path: install syntax"


def test_contributing_nightly_section():
    """CONTRIBUTING.md documents the nightly build process."""
    content = Path(f"{REPO}/CONTRIBUTING.md").read_text()
    assert "Nightly" in content, "CONTRIBUTING.md must mention nightly builds"
    assert "setup-installable-branch" in content, \
        "CONTRIBUTING.md must reference the setup-installable-branch script"
