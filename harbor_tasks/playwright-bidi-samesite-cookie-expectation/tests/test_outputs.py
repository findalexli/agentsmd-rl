"""
Task: playwright-bidi-samesite-cookie-expectation
Repo: playwright @ 5435c64f6d14293b2ce0dcdbfaa237b015bfd63e
PR:   40091

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/playwright"
SPEC_FILE = f"{REPO}/tests/library/browsercontext-fetch.spec.ts"
EXPECTATIONS_FILE = f"{REPO}/tests/bidi/expectations/moz-firefox-nightly-library.txt"


def _npm_install():
    """Install npm dependencies (cached)."""
    r = subprocess.run(
        ["npm", "install"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"npm install failed:\n{r.stderr[-500:]}"


def _npm_build():
    """Build the repo (required for some checks)."""
    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}"


def _ensure_built():
    """Ensure repo is installed and built."""
    marker = Path(f"{REPO}/packages/playwright-core/lib/common/types.js")
    if not marker.exists():
        _npm_install()
        _npm_build()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_spec_file_valid():
    """Modified TypeScript spec file must be non-empty with balanced braces."""
    content = Path(SPEC_FILE).read_text()
    assert len(content) > 1000, "Spec file is unexpectedly small"
    assert content.count("{") == content.count("}"), "Unbalanced braces in spec file"
    assert "browsercontext-fetch" in content.lower() or "set-cookie" in content.lower()


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_isBidi_in_test_signature():
    """The SameSite set-cookie test must include isBidi in its fixture parameters.

    The test function signature must destructure isBidi alongside browserName,
    so the test body can branch on BiDi protocol behavior.
    """
    r = subprocess.run(
        [
            "node", "-e",
            """
const fs = require('fs');
const content = fs.readFileSync(process.argv[1], 'utf-8');
const lines = content.split('\\n');
// Find the test function line for the SameSite cookie test
const sigLine = lines.find(l =>
    l.includes('SameSite') &&
    l.includes('Secure attribute') &&
    l.includes('async')
);
if (!sigLine) {
    console.error('Test function not found');
    process.exit(1);
}
if (!sigLine.includes('isBidi')) {
    console.error('isBidi missing from test signature: ' + sigLine.trim());
    process.exit(1);
}
console.log('OK: isBidi found in signature');
""",
            SPEC_FILE,
        ],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"isBidi not in test signature:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_bidi_cookie_rejection_condition():
    """The cookie rejection condition for SameSite=None must include isBidi.

    When running under BiDi protocol, cookies with SameSite=None and no Secure
    attribute should be treated the same as Chromium — they are rejected.
    The condition must be (browserName === 'chromium' || isBidi) && value === 'None'.
    """
    r = subprocess.run(
        [
            "node", "-e",
            """
const fs = require('fs');
const content = fs.readFileSync(process.argv[1], 'utf-8');
const lines = content.split('\\n');

// Find lines that check chromium + None condition
const condLines = lines.filter(l =>
    l.includes("browserName === 'chromium'") &&
    l.includes("value === 'None'")
);

if (condLines.length === 0) {
    console.error('No chromium/None condition found');
    process.exit(1);
}

// At least one of these lines must also reference isBidi
const withBidi = condLines.filter(l => l.includes('isBidi'));
if (withBidi.length === 0) {
    console.error('isBidi not found alongside chromium condition for SameSite=None');
    console.error('Found lines:');
    condLines.forEach(l => console.error('  ' + l.trim()));
    process.exit(1);
}

// Verify the condition uses OR (not AND) to combine chromium and isBidi
const joined = withBidi[0];
if (!joined.includes('|| isBidi')) {
    console.error('isBidi should be OR-combined with chromium, got: ' + joined.trim());
    process.exit(1);
}

console.log('OK: isBidi correctly OR-combined with chromium condition');
""",
            SPEC_FILE,
        ],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"isBidi condition incorrect:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_bidi_expectation_removed():
    """The BiDi expectations file must NOT list this test as failing.

    After fixing the test to handle BiDi correctly, the failing expectation
    for this specific test should be removed from the BiDi expectations list.
    """
    content = Path(EXPECTATIONS_FILE).read_text()
    # The test should not appear in the expectations file at all
    # (it was removed because it no longer fails with the correct condition)
    assert (
        "should support set-cookie with SameSite and without Secure attribute over HTTP"
        not in content
    ), "Test still listed in BiDi expectations as failing — should have been removed"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD gates
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_build():
    """Repo's build step completes successfully (pass_to_pass)."""
    _npm_install()
    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_eslint():
    """Repo's ESLint linting passes (pass_to_pass)."""
    _npm_install()
    r = subprocess.run(
        ["npm", "run", "eslint"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_tsc():
    """Repo's TypeScript type check passes (pass_to_pass)."""
    _npm_install()
    r = subprocess.run(
        ["npm", "run", "tsc"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"TypeScript check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_check_deps():
    """Repo's dependency check passes (pass_to_pass)."""
    _ensure_built()
    r = subprocess.run(
        ["npm", "run", "check-deps"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Check-deps failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_lint_packages():
    """Repo's package linting passes (pass_to_pass)."""
    _npm_install()
    r = subprocess.run(
        ["npm", "run", "lint-packages"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint-packages failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_test_types():
    """Repo's test types check passes (pass_to_pass)."""
    _ensure_built()
    r = subprocess.run(
        ["npm", "run", "test-types"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Test-types failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_lint_tests():
    """Repo's test file linting passes (pass_to_pass)."""
    _ensure_built()
    r = subprocess.run(
        ["npm", "run", "lint-tests"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint-tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_generate_channels():
    """Repo's protocol channel generation passes (pass_to_pass)."""
    _ensure_built()
    r = subprocess.run(
        ["node", "utils/generate_channels.js"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Generate channels failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_generate_types():
    """Repo's type generation passes (pass_to_pass)."""
    _ensure_built()
    r = subprocess.run(
        ["node", "utils/generate_types/index.js"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Generate types failed:\n{r.stderr[-500:]}"
