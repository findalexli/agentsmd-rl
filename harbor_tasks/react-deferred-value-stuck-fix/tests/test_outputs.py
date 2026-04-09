"""
Task: react-deferred-value-stuck-fix
Repo: react @ ed69815cebae33b0326cc69faa90f813bb924f3b
PR:   36134

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """Modified reconciler file must parse without JavaScript syntax errors."""
    target = f"{REPO}/packages/react-reconciler/src/ReactFiberWorkLoop.js"
    r = subprocess.run(["node", "--check", target], capture_output=True, text=True)
    assert r.returncode == 0, f"Syntax error in ReactFiberWorkLoop.js:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_fix_records_pinged_lanes():
    """pingSuspendedRoot must update workInProgressRootPingedLanes when render is in progress."""
    r = subprocess.run(
        [
            "node", "-e",
            """
const fs = require('fs');
const src = fs.readFileSync('packages/react-reconciler/src/ReactFiberWorkLoop.js', 'utf8');
const idx = src.indexOf('function pingSuspendedRoot');
if (idx === -1) { process.stderr.write('pingSuspendedRoot not found'); process.exit(1); }
const chunk = src.substring(idx, idx + 3000);

// The fix must update workInProgressRootPingedLanes with pingedLanes
// using mergeLanes (or equivalent bitwise OR) inside this function
const hasFix =
  chunk.includes('workInProgressRootPingedLanes = mergeLanes(') ||
  chunk.includes('workInProgressRootPingedLanes |= pingedLanes') ||
  chunk.includes('workInProgressRootPingedLanes = workInProgressRootPingedLanes | pingedLanes');

if (!hasFix) {
  process.stderr.write(
    'Fix missing: workInProgressRootPingedLanes not updated with pingedLanes in pingSuspendedRoot'
  );
  process.exit(1);
}

// pingedLanes must be referenced in the merge
if (!chunk.includes('pingedLanes')) {
  process.stderr.write('Fix missing: pingedLanes not used in the lane update');
  process.exit(1);
}
console.log('OK');
""",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Fix verification failed:\n{r.stderr}\n{r.stdout}"


# [pr_diff] fail_to_pass
def test_suspense_expects_retry():
    """Suspense test must expect sibling to render after synchronous ping retry."""
    test_file = (
        f"{REPO}/packages/react-reconciler/src/__tests__/"
        "ReactSuspenseWithNoopRenderer-test.js"
    )
    src = Path(test_file).read_text()

    # Find the specific test about synchronous sibling updates
    test_idx = src.find("can sync update the sibling of a suspended component")
    assert test_idx != -1, "Sync update sibling test not found"

    # Get a chunk of the test body
    chunk = src[test_idx : test_idx + 2000]

    # After the fix, assertLog must include a standalone 'B' entry indicating
    # the sibling renders after the synchronous ping retry.
    # On the base commit, assertLog only has 3 items without the retry.
    # We check that the assertLog in this test has more than 3 quoted items,
    # indicating the test was updated to expect retry behavior.
    assert_idx = chunk.find("assertLog([")
    assert assert_idx != -1, "assertLog not found in test body"
    log_section = chunk[assert_idx : assert_idx + 500]

    # Count string items in the assertLog (items like 'Suspend! [A]', 'B', etc.)
    # Each item is a quoted string on its own line or in the array
    import re

    items = re.findall(r"'([^']*?)'", log_section)
    # Filter out comment-only matches and empty strings
    real_items = [i for i in items if i and not i.startswith("//")]
    assert (
        len(real_items) >= 5
    ), f"assertLog should have >=5 items after fix (expecting retry), found {len(real_items)}: {real_items}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_reconciler_tests_pass():
    """Deferred value and suspense tests pass after the fix."""
    # Run the deferred value tests to verify no regressions
    r = subprocess.run(
        ["yarn", "test", "--silent", "--no-watchman", "ReactDeferredValue"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Deferred value tests failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_lint():
    """Repo's ESLint checks pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "lint"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_flow():
    """Repo's Flow typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "flow", "dom-node"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Flow typecheck failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_eslint_plugin():
    """ESLint plugin react-hooks tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "workspace", "eslint-plugin-react-hooks", "test"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint plugin tests failed:\n{r.stderr[-500:]}"


# [static] pass_to_pass
def test_not_stub():
    """The fix adds real lane-merging logic, not just comments or empty statements."""
    r = subprocess.run(
        [
            "node", "-e",
            """
const fs = require('fs');
const src = fs.readFileSync('packages/react-reconciler/src/ReactFiberWorkLoop.js', 'utf8');
const idx = src.indexOf('function pingSuspendedRoot');
if (idx === -1) { process.stderr.write('pingSuspendedRoot not found'); process.exit(1); }
const chunk = src.substring(idx, idx + 3000);

// Find the workInProgressRoot !== null branch
const branchIdx = chunk.indexOf('workInProgressRoot !== null');
if (branchIdx === -1) { process.stderr.write('branch not found'); process.exit(1); }

// Extract the block content between { and matching }
const braceStart = chunk.indexOf('{', branchIdx);
let depth = 0;
let end = braceStart;
for (let i = braceStart; i < chunk.length; i++) {
  if (chunk[i] === '{') depth++;
  if (chunk[i] === '}') { depth--; if (depth === 0) { end = i; break; } }
}
const block = chunk.substring(braceStart, end + 1);

// Count non-comment, non-whitespace, non-brace-only lines
const lines = block.split('\\n').filter(l => {
  const t = l.trim();
  return t && t !== '{' && t !== '}' && !t.startsWith('//');
});

// The fix adds at least 3 lines of real code (mergeLanes call)
if (lines.length < 3) {
  process.stderr.write(
    'Branch appears stub-like: only ' + lines.length + ' code lines: ' + JSON.stringify(lines)
  );
  process.exit(1);
}
console.log('OK: ' + lines.length + ' code lines');
""",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Not-stub check failed:\n{r.stderr}\n{r.stdout}"
