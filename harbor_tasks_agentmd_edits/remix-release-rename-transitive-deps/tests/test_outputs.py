"""
Task: remix-release-rename-transitive-deps
Repo: remix-run/remix @ 130fbdc7b808a2d313363458dabc00caf036f482
PR:   11000

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/remix"


def _run_node(code, timeout=30):
    """Execute JavaScript code via Node in the repo directory."""
    script = Path(REPO) / "_eval_tmp.cjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Core TypeScript utility files must exist and be non-empty."""
    files = [
        "scripts/utils/changes.ts",
        "scripts/utils/packages.ts",
        "scripts/publish.ts",
    ]
    for f in files:
        p = Path(REPO) / f
        assert p.exists(), f"{f} must exist"
        content = p.read_text()
        assert len(content) > 100, f"{f} must have substantial content"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_release_pr_import_chain():
    """release-pr.ts exists, old files removed, import to utils/release-pr.ts resolves."""
    r = _run_node("""
var fs = require('fs');
var path = require('path');
var base = '/workspace/remix';

// New files must exist
if (!fs.existsSync(path.join(base, 'scripts/release-pr.ts'))) {
  console.error('scripts/release-pr.ts must exist');
  process.exit(1);
}
if (!fs.existsSync(path.join(base, 'scripts/utils/release-pr.ts'))) {
  console.error('scripts/utils/release-pr.ts must exist');
  process.exit(1);
}

// Old files must be removed
if (fs.existsSync(path.join(base, 'scripts/changes-version-pr.ts'))) {
  console.error('scripts/changes-version-pr.ts should be removed');
  process.exit(1);
}
if (fs.existsSync(path.join(base, 'scripts/utils/version-pr.ts'))) {
  console.error('scripts/utils/version-pr.ts should be removed');
  process.exit(1);
}

// Verify import chain: release-pr.ts must import from ./utils/release-pr
var content = fs.readFileSync(path.join(base, 'scripts/release-pr.ts'), 'utf-8');
if (content.indexOf('./utils/release-pr') === -1) {
  console.error('release-pr.ts must import from ./utils/release-pr');
  process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Import chain failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_pr_config_values():
    """release-pr.ts sets prTitle='Release' and prBranch='release-pr/main'."""
    r = _run_node(r"""
var fs = require('fs');
var p = '/workspace/remix/scripts/release-pr.ts';
if (!fs.existsSync(p)) {
  console.error('scripts/release-pr.ts does not exist');
  process.exit(1);
}
var content = fs.readFileSync(p, 'utf-8');

var titleMatch = content.match(/prTitle\s*=\s*['"](.+?)['"]/);
if (!titleMatch || titleMatch[1] !== 'Release') {
  console.error('prTitle must be "Release", got: ' + (titleMatch ? titleMatch[1] : 'not found'));
  process.exit(1);
}

var branchMatch = content.match(/prBranch\s*=\s*['"](.+?)['"]/);
if (!branchMatch || branchMatch[1] !== 'release-pr/main') {
  console.error('prBranch must be "release-pr/main", got: ' + (branchMatch ? branchMatch[1] : 'not found'));
  process.exit(1);
}

if (content.indexOf('Version Packages') !== -1) {
  console.error('release-pr.ts must not reference "Version Packages"');
  process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"PR config failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_commit_subject_is_release():
    """generateCommitMessage in changes.ts uses 'Release' as commit subject."""
    r = _run_node(r"""
var fs = require('fs');
var content = fs.readFileSync('/workspace/remix/scripts/utils/changes.ts', 'utf-8');

var m = content.match(/function\s+generateCommitMessage[\s\S]*?let\s+subject\s*=\s*['"](.+?)['"]/);
if (!m) {
  console.error('Could not find subject in generateCommitMessage');
  process.exit(1);
}
if (m[1] !== 'Release') {
  console.error('Commit subject must be "Release", got: "' + m[1] + '"');
  process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Commit subject failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_git_tag_and_release_url():
    """getGitTag and getGitHubReleaseUrl produce correct output when executed."""
    r = _run_node(r"""
var fs = require('fs');
var content = fs.readFileSync('/workspace/remix/scripts/utils/packages.ts', 'utf-8');

// Extract GITHUB_REPO_URL constant
var urlMatch = content.match(/GITHUB_REPO_URL\s*=\s*['"](.+?)['"]/);
if (!urlMatch) {
  console.error('GITHUB_REPO_URL not found in packages.ts');
  process.exit(1);
}
var GITHUB_REPO_URL = urlMatch[1];

// Extract and execute getPackageShortName
var shortNameMatch = content.match(/function getPackageShortName\(packageName[^)]*\)[^{]*\{([\s\S]*?)\n\}/);
if (!shortNameMatch) {
  console.error('getPackageShortName function not found');
  process.exit(1);
}
var getPackageShortName = new Function('packageName', shortNameMatch[1]);

// Test getPackageShortName
var r1 = getPackageShortName('@remix-run/headers');
if (r1 !== 'headers') {
  console.error('getPackageShortName("@remix-run/headers") = "' + r1 + '", expected "headers"');
  process.exit(1);
}
var r2 = getPackageShortName('remix');
if (r2 !== 'remix') {
  console.error('getPackageShortName("remix") = "' + r2 + '", expected "remix"');
  process.exit(1);
}

// Extract and execute getGitTag
var gitTagMatch = content.match(/function getGitTag\(packageName[^,]*, version[^)]*\)[^{]*\{([\s\S]*?)\n\}/);
if (!gitTagMatch) {
  console.error('getGitTag function not found');
  process.exit(1);
}
var getGitTag = new Function('packageName', 'version',
  'var getPackageShortName = ' + getPackageShortName.toString() + ';\n' + gitTagMatch[1]);

var r3 = getGitTag('@remix-run/headers', '0.11.0');
if (r3 !== 'headers@0.11.0') {
  console.error('getGitTag("@remix-run/headers", "0.11.0") = "' + r3 + '"');
  process.exit(1);
}
var r4 = getGitTag('remix', '3.0.0');
if (r4 !== 'remix@3.0.0') {
  console.error('getGitTag("remix", "3.0.0") = "' + r4 + '"');
  process.exit(1);
}

// Extract and execute getGitHubReleaseUrl
var releaseUrlMatch = content.match(/function getGitHubReleaseUrl\(packageName[^,]*, version[^)]*\)[^{]*\{([\s\S]*?)\n\}/);
if (!releaseUrlMatch) {
  console.error('getGitHubReleaseUrl function not found');
  process.exit(1);
}
var getGitHubReleaseUrl = new Function('packageName', 'version',
  'var GITHUB_REPO_URL = ' + JSON.stringify(GITHUB_REPO_URL) + ';\n' +
  'var getGitTag = ' + getGitTag.toString() + ';\n' +
  releaseUrlMatch[1]);

var r5 = getGitHubReleaseUrl('@remix-run/headers', '0.11.0');
var expected = GITHUB_REPO_URL + '/releases/tag/headers@0.11.0';
if (r5 !== expected) {
  console.error('getGitHubReleaseUrl = "' + r5 + '", expected: "' + expected + '"');
  process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Git tag/URL execution failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_dependency_bump_type_and_field():
    """DependencyBump interface with required fields and dependencyBumps in PackageRelease."""
    r = _run_node(r"""
var fs = require('fs');
var content = fs.readFileSync('/workspace/remix/scripts/utils/changes.ts', 'utf-8');

// Verify DependencyBump interface with required fields
var ifaceMatch = content.match(/interface\s+DependencyBump\s*\{([\s\S]*?)\}/);
if (!ifaceMatch) {
  console.error('DependencyBump interface not found in changes.ts');
  process.exit(1);
}
var body = ifaceMatch[1];
var fields = ['packageName', 'version', 'releaseUrl'];
for (var i = 0; i < fields.length; i++) {
  if (body.indexOf(fields[i]) === -1) {
    console.error('DependencyBump missing field: ' + fields[i]);
    process.exit(1);
  }
}

// Verify PackageRelease has dependencyBumps field
var releaseMatch = content.match(/interface\s+PackageRelease\s*\{([\s\S]*?)\}/);
if (!releaseMatch) {
  console.error('PackageRelease interface not found');
  process.exit(1);
}
if (releaseMatch[1].indexOf('dependencyBumps') === -1) {
  console.error('PackageRelease missing dependencyBumps field');
  process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"DependencyBump check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_transitive_dependents_exported():
    """packages.ts exports getTransitiveDependents, buildReverseDependencyGraph, getPackageDependencies."""
    r = _run_node("""
var fs = require('fs');
var content = fs.readFileSync('/workspace/remix/scripts/utils/packages.ts', 'utf-8');

var required = [
  'getTransitiveDependents',
  'buildReverseDependencyGraph',
  'getPackageDependencies',
];

for (var i = 0; i < required.length; i++) {
  if (content.indexOf('export function ' + required[i]) === -1) {
    console.error('Missing exported function: ' + required[i]);
    process.exit(1);
  }
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Export check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_workflow_renamed():
    """Workflow renamed from changes-version-pr.yaml to release-pr.yaml."""
    r = _run_node("""
var fs = require('fs');
var path = require('path');
var base = '/workspace/remix/.github/workflows';
var newPath = path.join(base, 'release-pr.yaml');
var oldPath = path.join(base, 'changes-version-pr.yaml');

if (!fs.existsSync(newPath)) {
  console.error('release-pr.yaml must exist');
  process.exit(1);
}
if (fs.existsSync(oldPath)) {
  console.error('changes-version-pr.yaml should be removed');
  process.exit(1);
}

var content = fs.readFileSync(newPath, 'utf-8');
if (content.indexOf('release-pr') === -1) {
  console.error('Workflow must reference release-pr script');
  process.exit(1);
}
if (content.indexOf('changes-version-pr') !== -1) {
  console.error('Workflow must not reference old changes-version-pr');
  process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Workflow rename failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_agents_md_updated():
    """AGENTS.md references release-pr workflow and 'Release' PR naming."""
    r = _run_node("""
var fs = require('fs');
var content = fs.readFileSync('/workspace/remix/AGENTS.md', 'utf-8');

if (content.indexOf('release-pr') === -1) {
  console.error('AGENTS.md must reference release-pr');
  process.exit(1);
}
if (content.indexOf('changes-version-pr') !== -1) {
  console.error('AGENTS.md must not reference changes-version-pr');
  process.exit(1);
}
if (content.indexOf('"Release" PR') === -1 && content.indexOf("'Release' PR") === -1) {
  console.error('AGENTS.md must describe the PR as "Release"');
  process.exit(1);
}
if (content.indexOf('release-pr.ts') === -1) {
  console.error('AGENTS.md must reference release-pr.ts');
  process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"AGENTS.md check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_contributing_md_updated():
    """CONTRIBUTING.md uses 'Release' naming and release-pr references throughout."""
    r = _run_node("""
var fs = require('fs');
var content = fs.readFileSync('/workspace/remix/CONTRIBUTING.md', 'utf-8');

if (content.indexOf('"Release" PR') === -1) {
  console.error('CONTRIBUTING.md must reference "Release" PR');
  process.exit(1);
}
if (content.indexOf('release-pr') === -1) {
  console.error('CONTRIBUTING.md must reference release-pr');
  process.exit(1);
}
if (content.indexOf('changes-version-pr') !== -1) {
  console.error('CONTRIBUTING.md must not reference changes-version-pr');
  process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"CONTRIBUTING.md check failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_workflow_references_consistent():
    """Workflow YAML and scripts use consistent naming."""
    new_workflow = Path(REPO) / ".github" / "workflows" / "release-pr.yaml"
    old_workflow = Path(REPO) / ".github" / "workflows" / "changes-version-pr.yaml"
    has_new = new_workflow.exists()
    has_old = old_workflow.exists()
    assert has_new or has_old, "A workflow file must exist"

    if has_new:
        content = new_workflow.read_text()
        assert "release-pr" in content, "New workflow must reference release-pr"
        script = Path(REPO) / "scripts" / "release-pr.ts"
        assert script.exists(), "release-pr.ts must exist when release-pr.yaml exists"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - CI commands that run actual repo tooling
# Dependencies must be installed first via pnpm install
# ---------------------------------------------------------------------------

def _ensure_deps_installed():
    """Ensure pnpm is installed and dependencies are available."""
    # Check if node_modules exists
    if not (Path(REPO) / "node_modules").exists():
        # Install pnpm globally
        r = subprocess.run(
            ["npm", "install", "-g", "pnpm"],
            capture_output=True, text=True, timeout=120, cwd=REPO,
        )
        if r.returncode != 0:
            raise RuntimeError(f"Failed to install pnpm: {r.stderr}")
        # Install dependencies
        r = subprocess.run(
            ["pnpm", "install", "--frozen-lockfile"],
            capture_output=True, text=True, timeout=300, cwd=REPO,
        )
        if r.returncode != 0:
            raise RuntimeError(f"Failed to install dependencies: {r.stderr}")


# [repo_tests] pass_to_pass
def test_repo_changes_validate():
    """Repo's change file validation passes (pass_to_pass)."""
    _ensure_deps_installed()
    r = subprocess.run(
        ["node", "./scripts/changes-validate.ts"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"changes:validate failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_format_check():
    """Repo's prettier format check passes (pass_to_pass).
    Note: Files modified by the fix are auto-formatted after patch application."""
    _ensure_deps_installed()
    # Format the files that may have been modified by the patch
    subprocess.run(
        ["npx", "prettier", "--write", "scripts/utils/changes.ts", "scripts/utils/packages.ts",
         "scripts/release-pr.ts", "scripts/utils/release-pr.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        ["npx", "prettier", "--check", "."],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"format:check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_lint():
    """Repo's eslint linting passes (pass_to_pass)."""
    _ensure_deps_installed()
    r = subprocess.run(
        ["npx", "eslint", ".", "--max-warnings=0"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"lint failed:\n{r.stderr[-500:]}"
