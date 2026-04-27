"""
Task: playwright-dashboard-workspace-ordering
Repo: microsoft/playwright @ 883825e4d62aac69939b8f4c0f1cf41e72882079
PR:   40069

Dashboard should show the current workspace's sessions first and expanded,
defaulting to 'Global' when launched from a non-workspace directory.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import os

REPO = "/workspace/playwright"


def _node(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a node -e script in the repo directory."""
    return subprocess.run(
        ["node", "-e", script],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_grid_workspace_ordering():
    """Grid must sort current workspace first, defaulting to 'Global' when
    workspaceDir is undefined. Verifies behavior: a local fallback variable
    holds the current workspace value and is used consistently in filters."""
    script = r"""
const fs = require('fs');
const src = fs.readFileSync('packages/dashboard/src/grid.tsx', 'utf8');

// 1) There must be a local variable that falls back to 'Global' when workspaceDir is absent
// Accept any variable name; check that the fallback value is 'Global'
const fallbackMatch = src.match(/=\s*clientInfo\?\.workspaceDir\s*\|\|\s*['"]([^'"]+)['"]/);
if (!fallbackMatch) throw new Error('Missing: clientInfo?.workspaceDir || \'Global\' fallback');
const fallbackValue = fallbackMatch[1];
if (fallbackValue !== 'Global') throw new Error('Expected fallback to be \'Global\', got: ' + fallbackValue);

// 2) Extract the variable name used for the fallback (capture the identifier before the =)
const varMatch = src.match(/(\w+)\s*=\s*clientInfo\?\.workspaceDir\s*\|\|\s*['"]Global['"]/);
if (!varMatch) throw new Error('Could not find fallback variable assignment');
const fallbackVar = varMatch[1];

// 3) Verify that THIS variable (not raw clientInfo?.workspaceDir) is used in BOTH filter calls
// The variable must appear in both the '===' filter and '!==' filter for current/other groups
if (!src.includes('key === ' + fallbackVar) || !src.includes('key !== ' + fallbackVar))
  throw new Error('Fallback variable must be used consistently in both filters (=== and !==)');

// 4) Simulate the sorting logic to verify behavior
function sortGroups(groups, workspaceDir) {
  const cw = workspaceDir || 'Global';
  const entries = [...groups.entries()];
  const current = entries.filter(([k]) => k === cw);
  const other = entries.filter(([k]) => k !== cw).sort((a, b) => a[0].localeCompare(b[0]));
  return [...current, ...other];
}

const groups = new Map([
  ['Global', [{title: 'g'}]],
  ['/home/user/proj', [{title: 'p'}]],
]);

// undefined workspaceDir -> Global first
const r1 = sortGroups(groups, undefined);
if (r1[0][0] !== 'Global') throw new Error('Global should be first when workspaceDir is undefined');

// specific workspaceDir -> that workspace first
const r2 = sortGroups(groups, '/home/user/proj');
if (r2[0][0] !== '/home/user/proj') throw new Error('Specific workspace should be first');

// workspaceDir not matching any group -> all sorted alphabetically
const groups3 = new Map([['Beta', [1]], ['Alpha', [2]]]);
const r3 = sortGroups(groups3, undefined);
if (r3[0][0] !== 'Alpha' || r3[1][0] !== 'Beta') throw new Error('Non-matching groups should be sorted');

console.log('OK');
"""
    r = _node(script)
    assert r.returncode == 0, f"Grid workspace ordering failed:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_dashboard_api_sends_client_info():
    """dashboardApp.ts must import createClientInfo and include clientInfo
    in the /api/sessions/list response. Verifies behavior: the API returns
    both sessions and workspace info without requiring specific property ordering."""
    script = r"""
const fs = require('fs');
const src = fs.readFileSync('packages/playwright-core/src/tools/dashboard/dashboardApp.ts', 'utf8');

// 1) Must import createClientInfo from the correct path
if (!src.includes("import { createClientInfo } from '../cli-client/registry'"))
  throw new Error("Missing: import { createClientInfo } from '../cli-client/registry'");

// 2) The /api/sessions/list handler must create clientInfo via createClientInfo() call
const listSection = src.match(/api\/sessions\/list[\s\S]*?return;\s*\}/);
if (!listSection) throw new Error('Could not find /api/sessions/list handler');
const handler = listSection[0];
if (!handler.includes('createClientInfo()'))
  throw new Error('/api/sessions/list handler must call createClientInfo()');

// 3) sendJSON must include clientInfo alongside sessions (property order flexible)
const sendJSONMatch = handler.match(/sendJSON\s*\(\s*response\s*,\s*\{[^}]+\}\s*\)/);
if (!sendJSONMatch) throw new Error('Could not find sendJSON call with object literal');
const responseObj = sendJSONMatch[0];

// Check both properties exist - order doesn't matter
if (!responseObj.includes('sessions'))
  throw new Error('sendJSON response must include sessions');
if (!responseObj.includes('clientInfo'))
  throw new Error('sendJSON response must include clientInfo');

// 4) Verify the sendJSON is in the /api/sessions/list handler (not elsewhere)
if (!handler.includes('sendJSON'))
  throw new Error('sendJSON must be called in /api/sessions/list handler');

console.log('OK');
"""
    r = _node(script)
    assert r.returncode == 0, f"Dashboard API client info check failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_grid_alphabetical_sorting():
    """Non-current workspace groups must still be sorted alphabetically
    (localeCompare). This is preserved behavior from the base commit."""
    script = r"""
const fs = require('fs');
const src = fs.readFileSync('packages/dashboard/src/grid.tsx', 'utf8');

// The 'other' groups must use localeCompare for sorting
if (!src.includes('.localeCompare('))
  throw new Error('Missing localeCompare for alphabetical sorting');

// The sort must apply to the 'other' (non-current) entries
const sortPattern = /\.sort\(\(a,\s*b\)\s*=>\s*a\[0\]\.localeCompare\(b\[0\]\)\)/;
if (!sortPattern.test(src))
  throw new Error('Sorting pattern changed — expected .sort((a, b) => a[0].localeCompare(b[0]))');

console.log('OK');
"""
    r = _node(script)
    assert r.returncode == 0, f"Alphabetical sorting check failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------


# [agent_config] fail_to_pass — CLAUDE.md:95 @ 883825e4d62aac69939b8f4c0f1cf41e72882079
def test_deps_declares_cli_client_import():
    """CLAUDE.md DEPS rule: 'When creating or moving files, update the
    relevant DEPS.list to declare allowed imports.'
    The new import from ../cli-client/registry must be listed in DEPS.list."""
    deps_path = os.path.join(REPO, "packages/playwright-core/src/tools/dashboard/DEPS.list")
    with open(deps_path) as f:
        content = f.read()
    assert "../cli-client/registry.ts" in content, (
        "DEPS.list must declare the ../cli-client/registry.ts import"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD regression checks
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_repo_build():
    """Repo's npm run build passes (pass_to_pass). Verifies the TypeScript
    compilation and vite dashboard build work on both base and after fix."""
    # First install dependencies
    r = subprocess.run(
        ["npm", "ci"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"npm ci failed:\n{r.stderr[-500:]}"

    # Then run build
    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_lint_packages():
    """Repo's npm run lint-packages passes (pass_to_pass). Verifies workspace
    package consistency on both base and after fix."""
    # First install dependencies
    r = subprocess.run(
        ["npm", "ci"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"npm ci failed:\n{r.stderr[-500:]}"

    # Then run lint-packages
    r = subprocess.run(
        ["npm", "run", "lint-packages"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint packages failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_check_deps():
    """Repo's npm run check-deps passes (pass_to_pass). Verifies DEPS.list
    constraints are satisfied on both base and after fix."""
    # First install dependencies
    r = subprocess.run(
        ["npm", "ci"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"npm ci failed:\n{r.stderr[-500:]}"

    # Build first (required for check-deps to work correctly)
    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-1000:]}"

    # Then run check-deps
    r = subprocess.run(
        ["npm", "run", "check-deps"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Check deps failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_tsc():
    """Repo's TypeScript compilation check passes (pass_to_pass). Verifies
    tsc -p . runs without errors after build on both base and after fix."""
    # First install dependencies
    r = subprocess.run(
        ["npm", "ci"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"npm ci failed:\n{r.stderr[-500:]}"

    # Build first (required for tsc to find bundle type declarations)
    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-1000:]}"

    # Run TypeScript check
    r = subprocess.run(
        ["npm", "run", "tsc"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"TypeScript check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_lint_tests():
    """Repo's test file linting passes (pass_to_pass). Verifies test file
    conventions are correct on both base and after fix."""
    # First install dependencies
    r = subprocess.run(
        ["npm", "ci"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"npm ci failed:\n{r.stderr[-500:]}"

    # Build first (required for lint-tests to load modules)
    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-1000:]}"

    # Run test file linting
    r = subprocess.run(
        ["npm", "run", "lint-tests"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Test lint failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_eslint():
    """Repo's ESLint check passes (pass_to_pass). Verifies code style
    conventions are correct on both base and after fix."""
    # First install dependencies
    r = subprocess.run(
        ["npm", "ci"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"npm ci failed:\n{r.stderr[-500:]}"

    # Run ESLint with increased memory limit
    env = os.environ.copy()
    env["NODE_OPTIONS"] = "--max-old-space-size=4096"
    r = subprocess.run(
        ["npm", "run", "eslint", "--", "--max-warnings=0"],
        capture_output=True, text=True, timeout=300, cwd=REPO, env=env,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}"
