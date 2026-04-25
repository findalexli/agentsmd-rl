"""
Task: playwright-aria-snapshot-text-children
Repo: playwright @ 5a56d44a6f0d94b87e044f45f432522132da557c
PR:   40086

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/playwright"
TARGET = "packages/injected/src/ariaSnapshot.ts"
NPM_TIMEOUT = 300  # seconds for npm ci + build + command

# JavaScript helper: extracts textContributesInfo from the TS source and runs
# it against a set of {name, text} test cases, returning JSON results.
_JS_HARNESS = r"""
const fs = require('fs');

// longestCommonSubstring — copied verbatim from
// packages/playwright-core/src/utils/isomorphic/stringUtils.ts
function longestCommonSubstring(s1, s2) {
  const n = s1.length, m = s2.length;
  let maxLen = 0, endingIndex = 0;
  const dp = Array(n + 1).fill(null).map(() => Array(m + 1).fill(0));
  for (let i = 1; i <= n; i++) {
    for (let j = 1; j <= m; j++) {
      if (s1[i - 1] === s2[j - 1]) {
        dp[i][j] = dp[i - 1][j - 1] + 1;
        if (dp[i][j] > maxLen) { maxLen = dp[i][j]; endingIndex = i; }
      }
    }
  }
  return s1.slice(endingIndex - maxLen, endingIndex);
}

// Read source and extract textContributesInfo function body
const src = fs.readFileSync(process.argv[2], 'utf8');
const match = src.match(
  /function textContributesInfo\([^)]*\)[^{]*\{([\s\S]*?)\n\}/
);
if (!match) {
  console.error('textContributesInfo function not found in source');
  process.exit(2);
}

// eval in current scope so longestCommonSubstring is visible
const textContributesInfo = eval(
  '(function(node, text) {' + match[1] + '})'
);

// Run test cases from stdin
const cases = JSON.parse(fs.readFileSync('/dev/stdin', 'utf8'));
const results = {};
for (const [key, args] of Object.entries(cases)) {
  results[key] = textContributesInfo({name: args[0]}, args[1]);
}
console.log(JSON.stringify(results));
"""


def _run_text_contributes_info(test_cases):
    """Extract textContributesInfo from source, run with test_cases via Node.js.

    test_cases: dict of {label: [node_name, text_string]}
    Returns: dict of {label: bool}
    """
    fd, js_path = tempfile.mkstemp(suffix=".js")
    try:
        os.write(fd, _JS_HARNESS.encode())
        os.close(fd)
        target_path = os.path.join(REPO, TARGET)
        r = subprocess.run(
            ["node", js_path, target_path],
            input=json.dumps(test_cases).encode(),
            capture_output=True,
            timeout=30,
        )
        assert r.returncode == 0, (
            f"Node.js harness failed (rc={r.returncode}):\n{r.stderr.decode()}"
        )
        return json.loads(r.stdout.decode())
    finally:
        os.unlink(js_path)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — basic sanity
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_function_exists():
    """Source file contains the textContributesInfo function and LCS call."""
    src = Path(f"{REPO}/{TARGET}").read_text()
    assert "function textContributesInfo" in src, (
        "textContributesInfo function not found in source file"
    )
    assert "longestCommonSubstring" in src, (
        "longestCommonSubstring call not found in source file"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_text_contributes_unique_short_text():
    """Short text with unique info must be included even when name is longer."""
    results = _run_text_contributes_info({
        "numeric":  ["Alpha Beta", "7"],
        "code":     ["Some Long Name", "42"],
        "symbol":   ["Click to Submit", "!"],
    })
    for key, val in results.items():
        assert val is True, (
            f"Case '{key}': expected textContributesInfo=True (text has unique "
            f"info not in name), got {val}"
        )


# [pr_diff] fail_to_pass
def test_text_contributes_partial_overlap():
    """Text with partial name overlap but also unique info must be included."""
    results = _run_text_contributes_info({
        "alpha_7":  ["Alpha Beta", "Alpha 7"],
        "save_3":   ["Save Document", "Save 3"],
        "progress": ["Loading Progress Bar", "Loading 85%"],
    })
    for key, val in results.items():
        assert val is True, (
            f"Case '{key}': expected textContributesInfo=True (text contributes "
            f"info beyond the name), got {val}"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — preserved behavior
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_preserved_exclusions():
    """Text fully covered by name is still excluded; edge cases preserved."""
    results = _run_text_contributes_info({
        "covered_hello": ["Hello World", "Hello"],
        "covered_foo":   ["Foo Bar", "Foo"],
        "empty_text":    ["anything", ""],
        "no_name":       ["", "some text"],
    })
    # Text subsumed by name → excluded
    assert results["covered_hello"] is False, (
        "Text 'Hello' should be excluded when name is 'Hello World'"
    )
    assert results["covered_foo"] is False, (
        "Text 'Foo' should be excluded when name is 'Foo Bar'"
    )
    # Empty text → excluded
    assert results["empty_text"] is False, (
        "Empty text should always be excluded"
    )
    # No name → included
    assert results["no_name"] is True, (
        "Text should always be included when node has no name"
    )


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass tests — ensure fix doesn't break existing functionality
# ---------------------------------------------------------------------------

def _run_npm_command(cmd, timeout=300):
    """Run an npm command in the repo directory."""
    full_cmd = f"cd {REPO} && npm ci && npm run build && {cmd}"
    r = subprocess.run(
        ["bash", "-c", full_cmd],
        capture_output=True, text=True, timeout=timeout,
    )
    return r


# [repo_tests] pass_to_pass
def test_repo_eslint():
    """Repo's ESLint passes (pass_to_pass)."""
    r = _run_npm_command("npm run eslint", timeout=NPM_TIMEOUT)
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_tsc():
    """Repo's TypeScript compilation passes (pass_to_pass)."""
    r = _run_npm_command("npm run tsc", timeout=NPM_TIMEOUT)
    assert r.returncode == 0, f"TypeScript check failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_lint_tests():
    """Repo's test linting passes (pass_to_pass)."""
    r = _run_npm_command("npm run lint-tests", timeout=NPM_TIMEOUT)
    assert r.returncode == 0, f"Lint tests failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_lint_packages():
    """Repo's package consistency check passes (pass_to_pass)."""
    r = _run_npm_command("npm run lint-packages", timeout=NPM_TIMEOUT)
    assert r.returncode == 0, f"Lint packages failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_check_deps():
    """Repo's DEPS constraints check passes (pass_to_pass)."""
    r = _run_npm_command("npm run check-deps", timeout=NPM_TIMEOUT)
    assert r.returncode == 0, f"Check DEPS failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_test_types():
    """Repo's type generation and checking passes (pass_to_pass)."""
    r = _run_npm_command("npm run test-types", timeout=NPM_TIMEOUT)
    assert r.returncode == 0, f"Test types failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_doclint_js():
    """Repo's documentation JS code snippet linting passes (pass_to_pass)."""
    r = _run_npm_command("node utils/doclint/linting-code-snippets/cli.js --js-only", timeout=NPM_TIMEOUT)
    assert r.returncode == 0, f"Doclint JS snippets failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"
