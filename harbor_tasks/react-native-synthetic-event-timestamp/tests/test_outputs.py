"""
Task: react-native-synthetic-event-timestamp
Repo: facebook/react @ 074d96b9dd57ea748f2e869959a436695bbc88bf
PR:   35912

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"
TARGET = "packages/react-native-renderer/src/legacy-events/SyntheticEvent.js"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """SyntheticEvent.js must parse without syntax errors."""
    r = subprocess.run(
        ["node", "--check", TARGET],
        cwd=REPO, capture_output=True, timeout=30,
    )
    assert r.returncode == 0, f"Syntax error:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_lowercase_timestamp_returned():
    """event.timestamp (lowercase) must be returned when event.timeStamp is absent.

    Native platforms send the timestamp as lowercase `timestamp`. The old code
    only checked camelCase `timeStamp` and fell back to Date.now(), discarding
    valid native timestamps.
    """
    # Extract the timeStamp getter body and execute it with test events.
    # This is behavioral: we actually run the extracted function logic.
    script = r"""
const fs = require('fs');
const path = require('path');
const content = fs.readFileSync(path.join(process.env.REPO, process.env.TARGET), 'utf-8');

// Extract the return statement from the timeStamp getter function
const match = content.match(/timeStamp:\s*function\s*\(event\)\s*\{[\s\n]*([\s\S]*?)[\s\n]*\}/);
if (!match) {
  console.error('Could not find timeStamp getter');
  process.exit(1);
}

const funcBody = match[1].trim();

// Build the function; inject currentTimeStamp in case the fix uses it
const currentTimeStamp = () => 9_999_999;
let fn;
try {
  fn = new Function('event', 'currentTimeStamp', funcBody);
} catch (e) {
  console.error('Could not build function from body: ' + funcBody + '\n' + e);
  process.exit(1);
}

// Cases: event has ONLY lowercase timestamp (not camelCase)
const cases = [
  [{ timestamp: 100 },   100],
  [{ timestamp: 500 },   500],
  [{ timestamp: 12345 }, 12345],
];

let failed = false;
for (const [event, expected] of cases) {
  const result = fn(event, currentTimeStamp);
  if (result !== expected) {
    console.error(`FAIL: event=${JSON.stringify(event)}, expected=${expected}, got=${result}`);
    failed = true;
  }
}
if (failed) process.exit(1);
console.log('PASS');
"""
    env = {"REPO": REPO, "TARGET": TARGET, "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"}
    r = subprocess.run(
        ["node", "-e", script],
        cwd=REPO, capture_output=True, timeout=30, env=env,
    )
    assert r.returncode == 0, (
        f"Lowercase timestamp not returned:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_performance_now_fallback_used():
    """Fallback must use performance.now() for a monotonic clock when available.

    The old code always fell back to Date.now(), which is non-monotonic and can
    skip or jump if the system clock changes.
    """
    content = Path(f"{REPO}/{TARGET}").read_text()
    assert "performance.now()" in content, (
        "Fix must use performance.now() for monotonic fallback (not just Date.now())"
    )


# [pr_diff] fail_to_pass
def test_performance_availability_checked():
    """Code must guard performance.now() usage with an availability check.

    Using performance.now() without checking availability throws in environments
    where performance is not defined (e.g., some React Native runtimes).
    """
    import re
    content = Path(f"{REPO}/{TARGET}").read_text()
    has_guard = (
        "typeof performance" in content
        or "performance?.now" in content
        or bool(re.search(r"performance\s*!==\s*null", content))
        or bool(re.search(r"performance\s*!=\s*null", content))
    )
    assert has_guard, (
        "Fix must check performance availability (typeof performance, performance?.now, etc.) "
        "before calling performance.now()"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_eventinterface_structure_preserved():
    """The EventInterface object shape must not be broken by the fix."""
    content = Path(f"{REPO}/{TARGET}").read_text()
    assert "const EventInterface" in content, "EventInterface declaration missing"
    assert "timeStamp:" in content, "timeStamp key missing from EventInterface"
    assert "bubbles:" in content, "bubbles key missing from EventInterface"
    assert "defaultPrevented:" in content, "defaultPrevented key missing from EventInterface"


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_lint():
    """Repo's ESLint checks pass (pass_to_pass)."""
    # Run the repo's lint task (checks all files but is fast enough)
    r = subprocess.run(
        ["node", "./scripts/tasks/eslint"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_flow():
    """Repo's Flow type checks pass on react-native-renderer package (pass_to_pass)."""
    # Run flow check on the react-native-renderer package
    r = subprocess.run(
        ["yarn", "flow", "native"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Flow check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_tests():
    """Repo's unit tests for react-native-renderer pass (pass_to_pass)."""
    # Run tests for react-native-renderer specifically
    r = subprocess.run(
        ["bash", "-c", "NODE_ENV=development yarn test packages/react-native-renderer --ci --shard=1/1"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_prettier():
    """Repo's Prettier formatting check passes on modified file (pass_to_pass)."""
    # Run prettier check only on the modified file to keep it fast
    r = subprocess.run(
        ["npx", "prettier", "--check", TARGET],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"
