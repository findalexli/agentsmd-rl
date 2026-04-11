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
# Gates (pass_to_pass, repo_tests - using git/Python validation)
# ---------------------------------------------------------------------------

def test_repo_git_valid():
    """Repo has valid git structure and HEAD commit (pass_to_pass)."""
    r = subprocess.run(
        ["git", "status"], capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Git status failed:\n{r.stderr}"
    assert "HEAD detached at c1e86e6" in r.stdout, "Repo not at expected base commit"


def test_repo_package_json_schema():
    """package.json has valid schema with required fields (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import json
import sys
with open('package.json') as f:
    data = json.load(f)
assert 'name' in data, 'Missing name field'
assert 'version' in data, 'Missing version field'
assert 'scripts' in data, 'Missing scripts field'
assert 'setup' in data['scripts'], 'Missing setup script'
assert 'workspaces' in data, 'Missing workspaces field'
print('SCHEMA_OK')
"""], capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"package.json schema check failed:\n{r.stderr}"
    assert "SCHEMA_OK" in r.stdout, "Schema validation did not complete"


def test_repo_gitmodules_valid():
    """.gitmodules file exists and is valid (pass_to_pass)."""
    r = subprocess.run(
        ["git", "submodule", "status"], capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    # This may exit 0 even with uninitialized submodules - check it runs
    assert r.returncode == 0, f"Git submodule command failed:\n{r.stderr}"


def test_repo_docs_valid():
    """docs/README.md exists and has required content (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
from pathlib import Path
p = Path('docs/README.md')
content = p.read_text()
assert len(content) > 1000, 'docs/README.md is too short'
assert 'Ghost' in content, 'Missing Ghost mention in docs/README.md'
assert 'Quick Start' in content, 'Missing Quick Start section in docs/README.md'
print('DOCS_OK')
"""], capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Docs README validation failed:\n{r.stderr}"
    assert "DOCS_OK" in r.stdout, "Docs validation did not complete"


def test_repo_core_package_valid():
    """ghost/core/package.json has valid schema (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import json
with open('ghost/core/package.json') as f:
    data = json.load(f)
assert 'name' in data, 'Missing name field in ghost/core/package.json'
assert 'version' in data, 'Missing version field in ghost/core/package.json'
assert data['name'] == 'ghost', f"Expected name 'ghost', got '{data['name']}'"
print('CORE_PACKAGE_OK')
"""], capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Ghost core package.json validation failed:\n{r.stderr}"
    assert "CORE_PACKAGE_OK" in r.stdout, "Core package validation did not complete"


def test_repo_github_workflows_exist():
    """CI workflow files exist and are valid (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
from pathlib import Path

# Check CI workflow exists
ci_yml = Path('.github/workflows/ci.yml')
assert ci_yml.exists(), 'CI workflow file does not exist'

# Check it has content
content = ci_yml.read_text()
assert len(content) > 5000, 'CI workflow file seems too short'
assert 'jobs:' in content, 'Missing jobs section in CI workflow'
assert 'job_setup:' in content, 'Missing job_setup in CI workflow'
assert 'job_lint:' in content, 'Missing job_lint in CI workflow'
assert 'job_unit-tests:' in content, 'Missing job_unit-tests in CI workflow'

print('WORKFLOWS_OK')
"""], capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"CI workflows validation failed:\n{r.stderr}"
    assert "WORKFLOWS_OK" in r.stdout, "Workflows validation did not complete"


def test_repo_git_hooks_exist():
    """Git hooks directory exists with required hooks (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
from pathlib import Path

# Check hooks exist
pre_commit = Path('.github/hooks/pre-commit')
commit_msg = Path('.github/hooks/commit-msg')

assert pre_commit.exists(), 'pre-commit hook missing'
assert commit_msg.exists(), 'commit-msg hook missing'

# Check they have content
assert len(pre_commit.read_text()) > 100, 'pre-commit hook too short'
assert len(commit_msg.read_text()) > 100, 'commit-msg hook too short'

print('GIT_HOOKS_OK')
"""], capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Git hooks validation failed:\n{r.stderr}"
    assert "GIT_HOOKS_OK" in r.stdout, "Git hooks validation did not complete"


def test_repo_dockerfile_valid():
    """Dockerfile exists and has required content (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
from pathlib import Path

dockerfile = Path('Dockerfile')
assert dockerfile.exists(), 'Dockerfile missing'

content = dockerfile.read_text()
assert 'FROM' in content, 'Missing FROM in Dockerfile'
assert 'ghost' in content.lower(), 'Missing ghost reference in Dockerfile'

print('DOCKERFILE_OK')
"""], capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Dockerfile validation failed:\n{r.stderr}"
    assert "DOCKERFILE_OK" in r.stdout, "Dockerfile validation did not complete"


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
# Fail-to-pass (pr_diff) - code behavior
# ---------------------------------------------------------------------------

def test_setup_script_removed():
    """The .github/scripts/setup.js file must be deleted."""
    setup_js = Path(REPO) / ".github" / "scripts" / "setup.js"
    assert not setup_js.exists(), \
        ".github/scripts/setup.js should be removed - yarn dev now handles MySQL/config setup"


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
# Must NOT run arbitrary node scripts - just yarn + submodule init
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
# Old text mentioned database initialization - must be gone
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
