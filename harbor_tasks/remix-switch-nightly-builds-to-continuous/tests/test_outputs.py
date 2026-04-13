"""
Task: remix-switch-nightly-builds-to-continuous
Repo: remix-run/remix @ 721dac4c6704d5b3e8428887af21accdcb3b23ea
PR:   11003

Switch nightly builds (cron-scheduled to a `nightly` branch) to continuous
preview builds (push-triggered to a `preview` branch).  The CI workflow,
build script, and documentation must all be updated consistently.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/remix"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Key modified files must exist and be non-empty."""
    files = [
        ".github/workflows/preview.yml",
        "CONTRIBUTING.md",
        "README.md",
        "scripts/setup-installable-branch.ts",
    ]
    for f in files:
        p = Path(REPO) / f
        assert p.exists(), f"{f} must exist"
        assert p.stat().st_size > 0, f"{f} must be non-empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests using subprocess
# ---------------------------------------------------------------------------

def test_nightly_workflow_removed():
    """The old nightly.yml workflow must be deleted."""
    p = Path(REPO) / ".github/workflows/nightly.yml"
    assert not p.exists(), "nightly.yml should be removed — its functionality moves to preview.yml"


def test_preview_workflow_push_trigger():
    """preview.yml must contain a push trigger targeting main — parsed via subprocess."""
    r = subprocess.run(
        ["python3", "-c", """
import sys

content = open('.github/workflows/preview.yml').read()
lines = content.splitlines()

# Find the 'push:' trigger line
push_idx = -1
for i, line in enumerate(lines):
    if line.strip() == 'push:':
        push_idx = i
        break

if push_idx < 0:
    print('FAIL: no push: trigger found in preview.yml')
    sys.exit(1)

# Check that 'main' appears in the branches list following push:
nearby = lines[push_idx:push_idx + 5]
has_main = any('- main' in l for l in nearby)
if not has_main:
    print('FAIL: push trigger does not target main branch')
    sys.exit(1)

print('PASS')
"""],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, f"Workflow parsing failed: {r.stderr}"
    assert "PASS" in r.stdout, f"Push trigger test failed: {r.stdout}"


def test_script_no_branch_flag():
    """setup-installable-branch.ts parseArgs config must reject --branch flag."""
    r = subprocess.run(
        ["node", "-e", """
const util = require('util');
const fs = require('fs');
const script = fs.readFileSync('scripts/setup-installable-branch.ts', 'utf8');

// Extract the parseArgs config using balanced parenthesis matching
const start = script.indexOf('util.parseArgs(');
if (start === -1) {
    console.log('FAIL: no util.parseArgs call found');
    process.exit(1);
}

let depth = 0, configStr = '', inside = false;
for (let i = start + 'util.parseArgs'.length; i < script.length; i++) {
    if (script[i] === '(') { depth++; if (depth === 1) { inside = true; continue; } }
    if (script[i] === ')') { depth--; if (depth === 0) break; }
    if (inside) configStr += script[i];
}

// Evaluate the config object literal (pure JS, no TS annotations)
const config = eval('(' + configStr + ')');

// Actually call util.parseArgs with the extracted config + --branch flag
// Old config defines 'branch' option -> accepts it
// New config has no options -> rejects it with ERR_PARSE_ARGS_UNKNOWN_OPTION
try {
    util.parseArgs({ ...config, args: ['--branch', 'nightly'] });
    console.log('FAIL: --branch flag was accepted by parseArgs config');
    process.exit(1);
} catch (e) {
    if (e.code === 'ERR_PARSE_ARGS_UNKNOWN_OPTION') {
        console.log('PASS');
    } else {
        console.log('FAIL: unexpected error: ' + e.message);
        process.exit(1);
    }
}
"""],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, f"Node execution failed: {r.stderr}"
    assert "PASS" in r.stdout, f"--branch flag test failed: {r.stdout}"


def test_script_requires_branch_name():
    """setup-installable-branch.ts must not silently default to a branch name."""
    r = subprocess.run(
        ["node", "-e", """
const util = require('util');
const fs = require('fs');
const script = fs.readFileSync('scripts/setup-installable-branch.ts', 'utf8');

// Extract the parseArgs config
const start = script.indexOf('util.parseArgs(');
if (start === -1) {
    console.log('FAIL: no util.parseArgs call found');
    process.exit(1);
}

let depth = 0, configStr = '', inside = false;
for (let i = start + 'util.parseArgs'.length; i < script.length; i++) {
    if (script[i] === '(') { depth++; if (depth === 1) { inside = true; continue; } }
    if (script[i] === ')') { depth--; if (depth === 0) break; }
    if (inside) configStr += script[i];
}

const config = eval('(' + configStr + ')');

// Call parseArgs with no arguments — simulating the no-arg invocation
const result = util.parseArgs({ ...config, args: [] });

// Reconstruct the script's branch resolution logic
// Old: positionals[0] || values.branch || 'nightly' -> resolves to 'nightly'
// New: positionals[0] -> undefined (then script throws)
let installableBranch;
if (script.includes("|| 'nightly'")) {
    installableBranch = result.positionals[0]
        || (result.values && result.values.branch)
        || 'nightly';
} else {
    installableBranch = result.positionals[0];
}

if (installableBranch) {
    console.log('FAIL: script resolves to "' + installableBranch + '" with no args');
    process.exit(1);
}

console.log('PASS');
"""],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, f"Node execution failed: {r.stderr}"
    assert "PASS" in r.stdout, f"Branch requirement test failed: {r.stdout}"


def test_script_removes_overwrite_protection():
    """setup-installable-branch.ts must remove the nightly-specific overwrite protection."""
    script = (Path(REPO) / "scripts/setup-installable-branch.ts").read_text()
    assert "allowedOverwrites" not in script, \
        "The allowedOverwrites branch-protection logic should be removed"
    assert "remoteBranches" not in script or "git branch -r" not in script, \
        "The remote branch check should be removed"


def test_preview_workflow_builds_on_push():
    """preview.yml must build and push a preview branch on push-to-main events."""
    workflow = (Path(REPO) / ".github/workflows/preview.yml").read_text()
    assert "setup-installable-branch preview" in workflow, \
        "Workflow must call setup-installable-branch with 'preview' for push events"
    assert re.search(r"git push.*origin preview", workflow), \
        "Workflow must push to origin preview branch"


def test_script_comments_reference_preview():
    """setup-installable-branch.ts JSDoc must reference preview branch, not nightly."""
    script = (Path(REPO) / "scripts/setup-installable-branch.ts").read_text()
    assert 'remix#preview&path:packages/remix' in script, \
        "Script JSDoc should show preview in the install example"
    assert '(usually `nightly`)' not in script, \
        "Script JSDoc should not reference nightly as the default"


def test_readme_nightly_to_preview():
    """README.md install instructions must reference preview branch, not nightly."""
    readme = (Path(REPO) / "README.md").read_text()
    assert 'remix#preview&path:packages/remix' in readme, \
        "README.md should have preview install command"
    assert 'remix#nightly' not in readme, \
        "README.md install commands should reference preview, not nightly"


def test_contributing_nightly_to_preview():
    """CONTRIBUTING.md must reference preview builds, not nightly builds."""
    contributing = (Path(REPO) / "CONTRIBUTING.md").read_text()
    assert "## Preview builds" in contributing, \
        "CONTRIBUTING.md should have a 'Preview builds' section heading"
    assert 'remix#nightly' not in contributing, \
        "CONTRIBUTING.md install commands should reference preview, not nightly"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo CI/CD tests
# ---------------------------------------------------------------------------

def test_repo_format_check():
    """Repo's Prettier formatting check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "install", "-g", "pnpm@10.26.0"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # pnpm install must succeed before we can run format check
    r = subprocess.run(
        ["pnpm", "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"pnpm install failed:\n{r.stderr[-500:]}"

    r = subprocess.run(
        ["pnpm", "format:check"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stderr[-500:]}"


def test_repo_lint():
    """Repo's ESLint passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "install", "-g", "pnpm@10.26.0"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        ["pnpm", "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"pnpm install failed:\n{r.stderr[-500:]}"

    r = subprocess.run(
        ["pnpm", "lint"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}"


def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "install", "-g", "pnpm@10.26.0"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        ["pnpm", "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"pnpm install failed:\n{r.stderr[-500:]}"

    r = subprocess.run(
        ["pnpm", "typecheck"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}"


def test_repo_changes_validate():
    """Repo's change file validation passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "install", "-g", "pnpm@10.26.0"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        ["pnpm", "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"pnpm install failed:\n{r.stderr[-500:]}"

    r = subprocess.run(
        ["pnpm", "changes:validate"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Changes validation failed:\n{r.stderr[-500:]}"


def test_repo_build():
    """Repo's build passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "install", "-g", "pnpm@10.26.0"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        ["pnpm", "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"pnpm install failed:\n{r.stderr[-500:]}"

    r = subprocess.run(
        ["pnpm", "build"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

def test_preview_workflow_retains_pr_previews():
    """PR preview branches (preview/{number}) must still be supported."""
    workflow = (Path(REPO) / ".github/workflows/preview.yml").read_text()
    assert "pull_request" in workflow, "Workflow must still handle pull_request events"
    assert "preview/" in workflow, "Workflow must still reference preview/ branches for PRs"


def test_preview_workflow_retains_cleanup():
    """Workflow must still clean up PR preview branches when PRs close."""
    workflow = (Path(REPO) / ".github/workflows/preview.yml").read_text()
    assert "closed" in workflow, "Workflow must still handle closed PR events"
    assert "cleanup" in workflow.lower() or "Cleanup" in workflow, \
        "Workflow must retain the branch cleanup step"
