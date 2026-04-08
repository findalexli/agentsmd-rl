"""
Task: ghost-removed-setupjs-script
Repo: TryGhost/Ghost @ c1e86e6dd150e7ab1a226cfce8f73bc4ee441787
PR:   #26507

The old .github/scripts/setup.js handled MySQL Docker setup and config
writing during `yarn setup`. Since `yarn dev` now handles this, setup.js
is removed, the package.json setup script is simplified, and docs/README.md
is updated to reflect the new workflow.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/Ghost"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_package_json_valid():
    """package.json must be valid JSON with scripts.setup."""
    pkg = Path(REPO) / "package.json"
    data = json.loads(pkg.read_text())
    assert "scripts" in data, "package.json must have scripts"
    assert "setup" in data["scripts"], "package.json must have a setup script"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavior
# ---------------------------------------------------------------------------

def test_setup_script_removed():
    """The .github/scripts/setup.js file must be deleted."""
    setup_js = Path(REPO) / ".github" / "scripts" / "setup.js"
    assert not setup_js.exists(), \
        ".github/scripts/setup.js should be removed — yarn dev now handles MySQL/config setup"


def test_setup_script_simplified():
    """package.json setup script must not invoke setup.js and must use --recursive."""
    r = subprocess.run(
        ["python3", "-c", """
import json
with open("package.json") as f:
    data = json.load(f)
setup = data["scripts"]["setup"]
assert "setup.js" not in setup, f"setup script still references setup.js: {setup}"
assert "--recursive" in setup, f"setup script missing --recursive: {setup}"
# Must NOT run arbitrary node scripts — just yarn + submodule init
parts = setup.split(" && ")
assert len(parts) == 2, f"setup should be 'yarn && git submodule update --init --recursive', got: {setup}"
print("PASS")
"""],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, f"Setup script validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_docs_setup_section():
    """docs/README.md setup section must not mention database initialization."""
    r = subprocess.run(
        ["python3", "-c", """
from pathlib import Path
content = Path("docs/README.md").read_text()
# Old text mentioned database initialization — must be gone
assert "initializes the database" not in content.lower(), \
    "docs/README.md still mentions database initialization in setup section"
assert "sets up git hooks" not in content, \
    "docs/README.md still mentions git hooks in setup section"
# New text should be present
assert "Install dependencies and initialize submodules" in content, \
    "docs/README.md missing updated setup description"
print("PASS")
"""],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, f"Docs setup section check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_docs_dev_description():
    """docs/README.md yarn dev description must mention frontend dev servers."""
    r = subprocess.run(
        ["python3", "-c", """
from pathlib import Path
content = Path("docs/README.md").read_text()
# Old description only mentioned Docker backend services
assert "frontend dev servers" in content, \
    "docs/README.md yarn dev description must mention frontend dev servers"
# Old text should be gone
assert "Start development server (uses Docker for backend services)" not in content, \
    "docs/README.md still has old yarn dev description"
print("PASS")
"""],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, f"Docs dev description check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_docs_reset_command():
    """docs/README.md must use yarn reset:data instead of knex-migrator for reset."""
    r = subprocess.run(
        ["python3", "-c", """
from pathlib import Path
content = Path("docs/README.md").read_text()
# Old commands should be gone
assert "yarn knex-migrator reset" not in content, \
    "docs/README.md still references 'yarn knex-migrator reset'"
assert "yarn knex-migrator init" not in content, \
    "docs/README.md still references 'yarn knex-migrator init'"
# New command should be present
assert "yarn reset:data" in content, \
    "docs/README.md missing 'yarn reset:data' in reset section"
print("PASS")
"""],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, f"Docs reset command check failed: {r.stderr}"
    assert "PASS" in r.stdout
