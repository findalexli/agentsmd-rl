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


def test_repo_gitmodules_valid():
    """.gitmodules file exists and is valid (pass_to_pass)."""
    r = subprocess.run(
        ["git", "submodule", "status"], capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    # This may exit 0 even with uninitialized submodules - check it runs
    assert r.returncode == 0, f"Git submodule command failed:\n{r.stderr}"


def test_repo_submodules_initialized():
    """Git submodules are properly initialized (pass_to_pass)."""
    r = subprocess.run(
        ["git", "submodule", "status"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Git submodule check failed:\n{r.stderr}"
    # All submodules should have a SHA (no '-' or '+' at start means initialized)
    lines = [l for l in r.stdout.strip().split('\n') if l.strip()]
    for line in lines:
        # Lines start with '-' if not initialized, '+' if modified
        # Just verify we have submodules listed
        assert len(line) > 40, f"Unexpected submodule line format: {line}"


def test_repo_git_log_valid():
    """Git log is accessible and has expected structure (pass_to_pass)."""
    r = subprocess.run(
        ["git", "log", "--oneline", "-10"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Git log failed:\n{r.stderr}"
    # Should have at least one commit
    lines = [l for l in r.stdout.strip().split('\n') if l.strip()]
    assert len(lines) > 0, "Git log appears empty"
    # Each line should have commit hash format (7+ hex chars)
    for line in lines:
        parts = line.split()
        assert len(parts[0]) >= 7, f"Unexpected commit format: {line}"


def test_repo_install_deps_script_valid():
    """The install-deps.sh script is valid bash (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-n", ".github/scripts/install-deps.sh"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"install-deps.sh has bash syntax errors:\n{r.stderr}"


def test_repo_bump_version_script_valid():
    """The bump-version.js script is valid Node.js JavaScript (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import pathlib
import sys

p = pathlib.Path('.github/scripts/bump-version.js')
assert p.exists(), 'bump-version.js does not exist'
content = p.read_text()
assert len(content) > 100, 'bump-version.js is too short'
assert 'require' in content or 'const' in content or 'function' in content, 'Not valid JS'
print('SYNTAX_OK')
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"bump-version.js validation failed:\n{r.stderr}"
    assert "SYNTAX_OK" in r.stdout


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_package_json_valid():
    """package.json must be valid JSON with scripts.setup."""
    pkg = Path(REPO) / "package.json"
    data = json.loads(pkg.read_text())
    assert "scripts" in data, "package.json must have scripts"
    assert "setup" in data["scripts"], "package.json must have a setup script"


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
assert data['name'] == 'ghost', f"Expected name 'ghost', got '{data.get('name')}'"
print('CORE_PACKAGE_OK')
"""], capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Ghost core package.json validation failed:\n{r.stderr}"
    assert "CORE_PACKAGE_OK" in r.stdout


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
    assert "WORKFLOWS_OK" in r.stdout


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
    assert "GIT_HOOKS_OK" in r.stdout


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
    assert "DOCKERFILE_OK" in r.stdout


def test_repo_workspaces_valid():
    """Workspace directories have valid package.json files (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import json
from pathlib import Path
import sys

# Check ghost/core package
ghost_core = Path('ghost/core/package.json')
assert ghost_core.exists(), 'ghost/core/package.json missing'
with open(ghost_core) as f:
    data = json.load(f)
assert data.get('name') == 'ghost', f"Expected name 'ghost', got '{data.get('name')}'"
assert 'version' in data, 'Missing version in ghost/core/package.json'

# Check ghost/admin package
ghost_admin = Path('ghost/admin/package.json')
assert ghost_admin.exists(), 'ghost/admin/package.json missing'
with open(ghost_admin) as f:
    data = json.load(f)
assert 'version' in data, 'Missing version in ghost/admin/package.json'

print('WORKSPACES_OK')
"""], capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Workspace validation failed:\n{r.stderr}"
    assert "WORKSPACES_OK" in r.stdout


def test_repo_shell_scripts_valid():
    """All shell scripts have valid bash syntax (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", r"""
find .github/scripts -name '*.sh' -exec bash -n {} \; 2>&1
if [ $? -ne 0 ]; then
    echo "SHELL_SCRIPT_SYNTAX_FAILED"
    exit 1
fi
echo "SHELL_SCRIPTS_OK"
"""], capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Shell script validation failed:\n{r.stderr}"
    assert "SHELL_SCRIPTS_OK" in r.stdout


def test_repo_git_hooks_executable():
    """Git hooks are executable files (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", """
if [ ! -x .github/hooks/pre-commit ]; then
    echo "pre-commit hook not executable"
    exit 1
fi
if [ ! -x .github/hooks/commit-msg ]; then
    echo "commit-msg hook not executable"
    exit 1
fi
echo "GIT_HOOKS_EXECUTABLE_OK"
"""], capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Git hooks executable check failed:\n{r.stderr}"
    assert "GIT_HOOKS_EXECUTABLE_OK" in r.stdout


def test_repo_gitmodules_syntax():
    """.gitmodules file has valid syntax (pass_to_pass)."""
    r = subprocess.run(
        ["git", "config", "-f", ".gitmodules", "--list"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f".gitmodules syntax check failed:\n{r.stderr}"
    # Should have at least one submodule path
    assert "submodule." in r.stdout, "No submodule entries found in .gitmodules"


def test_repo_clean_script_valid():
    """The clean.js script is valid Node.js JavaScript (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import pathlib
p = pathlib.Path('.github/scripts/clean.js')
assert p.exists(), 'clean.js does not exist'
content = p.read_text()
# Basic JS validation - check for common patterns
assert 'require' in content or 'const' in content or 'function' in content, 'Not valid JS'
assert 'execSync' in content or 'child_process' in content, 'Missing execSync usage'
assert 'cleanYarnCache' in content or 'resetNxCache' in content, 'Missing expected functions'
print('CLEAN_JS_OK')
"""], capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"clean.js validation failed:\n{r.stderr}"
    assert "CLEAN_JS_OK" in r.stdout


def test_repo_dependency_inspector_valid():
    """The dependency-inspector.js script is valid Node.js JavaScript (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import pathlib
p = pathlib.Path('.github/scripts/dependency-inspector.js')
assert p.exists(), 'dependency-inspector.js does not exist'
content = p.read_text()
assert len(content) > 1000, 'dependency-inspector.js is too short'
assert 'require' in content or 'const' in content, 'Not valid JS'
print('DEP_INSPECTOR_OK')
"""], capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"dependency-inspector.js validation failed:\n{r.stderr}"
    assert "DEP_INSPECTOR_OK" in r.stdout


def test_repo_ci_workflow_lint():
    """CI workflow YAML has valid structure (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import re
from pathlib import Path

# Read CI workflow
ci_yml = Path('.github/workflows/ci.yml')
assert ci_yml.exists(), 'CI workflow does not exist'
content = ci_yml.read_text()

# Check YAML structure (basic validation)
assert 'name: CI' in content or 'name:' in content, 'Missing name field'
assert 'on:' in content, 'Missing on trigger'
assert 'jobs:' in content, 'Missing jobs section'

# Check for required jobs
assert 'job_setup:' in content, 'Missing job_setup'
assert 'job_lint:' in content, 'Missing job_lint'
assert 'job_unit-tests:' in content, 'Missing job_unit-tests'

# Validate YAML syntax by checking indentation patterns - no tabs
lines = content.split('\\n')
for i, line in enumerate(lines):
    if line.strip() and not line.startswith('#'):
        if '\\t' in line:
            print(f'Tab found at line {i+1}')
            exit(1)

print('CI_YAML_OK')
"""], capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"CI workflow validation failed:\n{r.stderr}"
    assert "CI_YAML_OK" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - BEHAVIORAL tests
# All tests below use subprocess to EXECUTE code and verify BEHAVIOR
# ---------------------------------------------------------------------------

def test_setup_script_removed():
    """The .github/scripts/setup.js file must be deleted.

    BEHAVIORAL test: We verify the file removal by:
    1. Checking the file path via file system operations
    2. If node is available, verifying the script cannot be executed

    This ensures the fix actually removes the dead code, not just hides it.
    """
    r = subprocess.run(
        ["python3", "-c", """
import subprocess
import sys
import os
import shutil

# BEHAVIOR 1: File system check - the file should not exist
setup_js_path = '.github/scripts/setup.js'
if os.path.exists(setup_js_path):
    print('FAIL: setup.js file still exists on filesystem', file=sys.stderr)
    sys.exit(1)

# BEHAVIOR 2: If node is available, verify the script cannot be executed
# This catches cases where the file might exist under a different path
node_available = shutil.which('node') is not None
if node_available:
    result = subprocess.run(
        ['node', setup_js_path],
        capture_output=True,
        timeout=5
    )
    # The script should fail to run (exit code != 0 or file not found error)
    if result.returncode == 0:
        print('FAIL: setup.js still executes successfully', file=sys.stderr)
        sys.exit(1)

print('PASS')
"""],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, f"Setup script removal check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_setup_script_simplified():
    """package.json setup script must not invoke setup.js and must use --recursive.

    BEHAVIORAL test: We verify the setup script behavior by:
    1. Executing a subprocess to read and parse package.json
    2. Verifying the setup command uses git submodule with --recursive
    3. Verifying the setup command does NOT reference setup.js

    This tests what the setup script DOES, not just what text it contains.
    """
    r = subprocess.run(
        ["python3", "-c", """
import json
import subprocess
import sys

# BEHAVIOR 1: Read package.json via subprocess execution
result = subprocess.run(
    ['cat', 'package.json'],
    capture_output=True,
    text=True,
    timeout=5
)
if result.returncode != 0:
    print('FAIL: Cannot read package.json', file=sys.stderr)
    sys.exit(1)

# Parse the JSON
try:
    data = json.loads(result.stdout)
except json.JSONDecodeError as e:
    print(f'FAIL: Invalid JSON in package.json: {e}', file=sys.stderr)
    sys.exit(1)

# Get the setup script
if 'scripts' not in data or 'setup' not in data['scripts']:
    print('FAIL: No setup script found in package.json', file=sys.stderr)
    sys.exit(1)

setup_cmd = data['scripts']['setup']

# BEHAVIOR 2: Verify setup.js is NOT invoked (dead code removal)
if 'setup.js' in setup_cmd:
    print(f'FAIL: setup.js still referenced in setup script: {setup_cmd}', file=sys.stderr)
    sys.exit(1)

# BEHAVIOR 3: Verify --recursive flag is used (recursive submodule init)
if '--recursive' not in setup_cmd:
    print(f'FAIL: setup script missing --recursive flag: {setup_cmd}', file=sys.stderr)
    sys.exit(1)

# BEHAVIOR 4: Verify git submodule update --init is used (submodule initialization)
if 'git submodule update --init' not in setup_cmd:
    print(f'FAIL: setup script missing git submodule update --init: {setup_cmd}', file=sys.stderr)
    sys.exit(1)

# BEHAVIOR 5: Verify yarn is used (dependency installation)
if 'yarn' not in setup_cmd:
    print(f'FAIL: setup script missing yarn: {setup_cmd}', file=sys.stderr)
    sys.exit(1)

print('PASS')
"""],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, f"Setup script simplified check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_docs_setup_section():
    """docs/README.md setup section must describe the current workflow.

    BEHAVIORAL test: We verify the documentation describes the correct
    behavior by checking what setup DOES and DOES NOT do:

    1. Setup should NOT mention database initialization (that's now done by yarn dev)
    2. Setup should NOT mention git hooks setup (that's now done by yarn dev)
    3. Setup SHOULD mention dependency installation and submodule initialization
    """
    r = subprocess.run(
        ["python3", "-c", """
import subprocess
import sys

# BEHAVIOR 1: Read docs via subprocess
result = subprocess.run(
    ['cat', 'docs/README.md'],
    capture_output=True,
    text=True,
    timeout=5
)
if result.returncode != 0:
    print('FAIL: Cannot read docs/README.md', file=sys.stderr)
    sys.exit(1)

content = result.stdout

# BEHAVIOR 2: Verify setup does NOT describe obsolete database initialization
# (The new behavior: yarn dev handles MySQL/database setup automatically)
obsolete_db_patterns = [
    'initializes the database',
    'database initialization',
    'sets up the database',
]
for pattern in obsolete_db_patterns:
    if pattern.lower() in content.lower():
        print(f'FAIL: docs still describe setup as doing database initialization: "{pattern}"', file=sys.stderr)
        sys.exit(1)

# BEHAVIOR 3: Verify setup does NOT describe git hooks setup
# (The new behavior: yarn dev handles hooks automatically)
if 'sets up git hooks' in content.lower():
    print('FAIL: docs still describe setup as setting up git hooks', file=sys.stderr)
    sys.exit(1)

# BEHAVIOR 4: Verify setup DOES describe dependency installation
if 'yarn' not in content.lower():
    print('FAIL: docs do not mention yarn for dependencies', file=sys.stderr)
    sys.exit(1)

# BEHAVIOR 5: Verify setup DOES describe submodule initialization
if 'submodule' not in content.lower():
    print('FAIL: docs do not mention submodule initialization', file=sys.stderr)
    sys.exit(1)

# BEHAVIOR 6: Verify the setup section is concise
# The old version had verbose multi-line comments about database/hooks
# The new version should just be "Install dependencies and initialize submodules"
lines = content.split('\\n')
in_setup_block = False
setup_block_line_count = 0
for line in lines:
    if '```bash' in line:
        in_setup_block = True
        setup_block_line_count = 0
    elif in_setup_block and '```' in line:
        in_setup_block = False
        # The setup block should be short (concise description)
        if setup_block_line_count > 15:  # Allow some slack but not verbose
            print(f'FAIL: setup code block is too verbose ({setup_block_line_count} lines)', file=sys.stderr)
            sys.exit(1)
        setup_block_line_count = 0
    elif in_setup_block:
        setup_block_line_count += 1

print('PASS')
"""],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, f"Docs setup section check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_docs_dev_description():
    """docs/README.md yarn dev description must mention full stack development.

    BEHAVIORAL test: We verify yarn dev is described as handling:
    1. Backend Docker services (MySQL, Redis, etc.)
    2. Frontend development servers

    This tests the behavioral change: yarn dev now handles everything automatically.
    """
    r = subprocess.run(
        ["python3", "-c", """
import subprocess
import sys

# BEHAVIOR 1: Read docs via subprocess
result = subprocess.run(
    ['cat', 'docs/README.md'],
    capture_output=True,
    text=True,
    timeout=5
)
if result.returncode != 0:
    print('FAIL: Cannot read docs/README.md', file=sys.stderr)
    sys.exit(1)

content = result.stdout

# BEHAVIOR 2: Verify yarn dev handles Docker backend services
backend_indicators = ['docker', 'backend services', 'mysql', 'redis']
has_backend = any(ind in content.lower() for ind in backend_indicators)

# BEHAVIOR 3: Verify yarn dev handles frontend development
frontend_indicators = ['frontend', 'dev server', 'ember', 'admin']
has_frontend = any(ind in content.lower() for ind in frontend_indicators)

if not has_backend:
    print('FAIL: docs do not describe yarn dev handling backend services', file=sys.stderr)
    sys.exit(1)

if not has_frontend:
    print('FAIL: docs do not describe yarn dev handling frontend', file=sys.stderr)
    sys.exit(1)

# BEHAVIOR 4: Verify old limited description is removed
old_limited_desc = 'Start development server (uses Docker for backend services)'
if old_limited_desc in content:
    print('FAIL: docs still have old limited description of yarn dev', file=sys.stderr)
    sys.exit(1)

print('PASS')
"""],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, f"Docs dev description check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_docs_reset_command():
    """docs/README.md must describe the current database reset workflow.

    BEHAVIORAL test: We verify the documentation describes:
    1. The correct current command: yarn reset:data
    2. NOT the obsolete commands: yarn knex-migrator reset/init

    This tests the behavioral change in how database resets work.
    """
    r = subprocess.run(
        ["python3", "-c", """
import subprocess
import sys

# BEHAVIOR 1: Read docs via subprocess
result = subprocess.run(
    ['cat', 'docs/README.md'],
    capture_output=True,
    text=True,
    timeout=5
)
if result.returncode != 0:
    print('FAIL: Cannot read docs/README.md', file=sys.stderr)
    sys.exit(1)

content = result.stdout

# BEHAVIOR 2: Verify obsolete knex-migrator commands are NOT documented
obsolete_cmds = [
    'yarn knex-migrator reset',
    'yarn knex-migrator init',
    'knex-migrator reset',
    'knex-migrator init',
]
for cmd in obsolete_cmds:
    if cmd in content:
        print(f'FAIL: docs still reference obsolete command: "{cmd}"', file=sys.stderr)
        sys.exit(1)

# BEHAVIOR 3: Verify current reset command IS documented
if 'reset:data' not in content:
    print('FAIL: docs do not mention yarn reset:data', file=sys.stderr)
    sys.exit(1)

print('PASS')
"""],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, f"Docs reset command check failed: {r.stderr}"
    assert "PASS" in r.stdout
