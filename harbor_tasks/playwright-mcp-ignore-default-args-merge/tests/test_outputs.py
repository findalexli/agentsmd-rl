"""
Task: playwright-mcp-ignore-default-args-merge
Repo: playwright @ c7d0163db5580377d6e94953d593adb799d32c22
PR:   40026

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/playwright"

BROWSER_FACTORY_TS = "packages/playwright-core/src/tools/mcp/browserFactory.ts"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    return subprocess.run(
        ["node", "-e", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / existence checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript file must exist and contain valid content."""
    p = Path(REPO) / BROWSER_FACTORY_TS
    assert p.is_file(), f"Missing: {p}"
    content = p.read_text()
    assert len(content) > 100, f"File too small: {p}"
    assert "import" in content, f"No imports in {p.name}"
    assert "createPersistentBrowser" in content, "Missing createPersistentBrowser function"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_array_args_preserved():
    """User-provided ignoreDefaultArgs array must be merged with persistent mode defaults."""
    r = _run_node(r"""
const fs = require('fs');
const src = fs.readFileSync('packages/playwright-core/src/tools/mcp/browserFactory.ts', 'utf8');

// The fix must extract config value before using it
if (!src.includes('configIgnoreDefaultArgs'))
    throw new Error('Missing configIgnoreDefaultArgs extraction');

// The fix must handle array case with Array.isArray
if (!src.includes('Array.isArray(configIgnoreDefaultArgs)'))
    throw new Error('Missing Array.isArray check for array merge');

// Simulate the merge logic as implemented in the fix
function mergeIgnoreDefaultArgs(userArgs) {
    if (userArgs === true) return true;
    const builtIn = ['--disable-extensions'];
    const userArr = Array.isArray(userArgs) ? userArgs : [];
    return [...builtIn, ...userArr];
}

// Test: user provides multiple args — all must be present
const result1 = mergeIgnoreDefaultArgs(['--password-store=basic', '--force-color-profile=srgb']);
if (!Array.isArray(result1)) throw new Error('Expected array for array input');
if (!result1.includes('--disable-extensions'))
    throw new Error('Missing --disable-extensions (built-in)');
if (!result1.includes('--password-store=basic'))
    throw new Error('Missing --password-store=basic (user arg)');
if (!result1.includes('--force-color-profile=srgb'))
    throw new Error('Missing --force-color-profile=srgb (user arg)');

// Test: single user arg
const result2 = mergeIgnoreDefaultArgs(['--test-type']);
if (!result2.includes('--disable-extensions'))
    throw new Error('Missing built-in with single user arg');
if (!result2.includes('--test-type'))
    throw new Error('Missing --test-type');

// Test: empty array — should still have built-in
const result3 = mergeIgnoreDefaultArgs([]);
if (result3.length !== 1) throw new Error('Empty array should still have built-in');
if (result3[0] !== '--disable-extensions')
    throw new Error('Empty array fallback should be --disable-extensions');

console.log('PASS');
""")
    assert r.returncode == 0, f"Array merge test failed:\n{r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_true_passthrough():
    """When user sets ignoreDefaultArgs: true, it must pass through unchanged (not replaced with array)."""
    r = _run_node(r"""
const fs = require('fs');
const src = fs.readFileSync('packages/playwright-core/src/tools/mcp/browserFactory.ts', 'utf8');

// Must have explicit true check
if (!src.includes('configIgnoreDefaultArgs === true'))
    throw new Error('Missing true passthrough check');

// Must have ternary that returns true on true input
// Pattern: ...configIgnoreDefaultArgs === true ? true : [...]
const ternaryMatch = src.match(/configIgnoreDefaultArgs\s*===\s*true\s*\?\s*true/);
if (!ternaryMatch) throw new Error('Must use ternary: true ? true : array');

// Simulate the logic
function resolveIgnoreDefaultArgs(userArgs) {
    return userArgs === true ? true : [
        '--disable-extensions',
        ...(Array.isArray(userArgs) ? userArgs : []),
    ];
}

// true must pass through as boolean true, not become an array
const result = resolveIgnoreDefaultArgs(true);
if (result !== true) throw new Error('true must pass through as boolean, got: ' + typeof result);
if (Array.isArray(result)) throw new Error('true should NOT become an array');

// Verify array inputs still produce arrays
if (!Array.isArray(resolveIgnoreDefaultArgs(['--test'])))
    throw new Error('Array input should produce array');

// Verify undefined produces array with just built-in
const defaultResult = resolveIgnoreDefaultArgs(undefined);
if (!Array.isArray(defaultResult)) throw new Error('undefined should produce array');
if (defaultResult.length !== 1) throw new Error('undefined should produce single-element array');

console.log('PASS');
""")
    assert r.returncode == 0, f"True passthrough test failed:\n{r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_config_extracted_before_spread():
    """config.browser.launchOptions.ignoreDefaultArgs must be extracted BEFORE the spread operator."""
    r = _run_node(r"""
const fs = require('fs');
const src = fs.readFileSync('packages/playwright-core/src/tools/mcp/browserFactory.ts', 'utf8');

// Find the createPersistentBrowser function body
const fnMatch = src.match(/async function createPersistentBrowser\([\s\S]*?\nfunction /);
if (!fnMatch) throw new Error('Could not find createPersistentBrowser function');
const fnBody = fnMatch[0];

// The extraction line must come before the launchOptions object construction
const extractionIdx = fnBody.indexOf('configIgnoreDefaultArgs');
const spreadIdx = fnBody.indexOf('...config.browser.launchOptions');

if (extractionIdx === -1) throw new Error('Missing configIgnoreDefaultArgs extraction');
if (spreadIdx === -1) throw new Error('Missing spread of config.browser.launchOptions');

// Extraction MUST come before the spread (otherwise user value gets overwritten)
if (extractionIdx > spreadIdx)
    throw new Error('configIgnoreDefaultArgs must be extracted BEFORE the spread');

// Must use the extracted variable, not re-read from config
const ignoreLine = fnBody.match(/ignoreDefaultArgs\s*:\s*([^,\n]+)/);
if (!ignoreLine) throw new Error('Could not find ignoreDefaultArgs assignment');

// Should reference configIgnoreDefaultArgs, NOT config.browser.launchOptions.ignoreDefaultArgs
const assignExpr = ignoreLine[1];
if (!assignExpr.includes('configIgnoreDefaultArgs'))
    throw new Error('ignoreDefaultArgs must use extracted configIgnoreDefaultArgs variable');

console.log('PASS');
""")
    assert r.returncode == 0, f"Config extraction order test failed:\n{r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD gates
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_eslint():
    """Repo's ESLint passes on the modified file (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "npm install --legacy-peer-deps 2>&1 >/dev/null && npx eslint packages/playwright-core/src/tools/mcp/browserFactory.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_lint_packages():
    """Repo's workspace lint passes (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "npm install --legacy-peer-deps 2>&1 >/dev/null && npm run lint-packages"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint packages failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """createPersistentBrowser must have real implementation, not a stub."""
    r = _run_node(r"""
const fs = require('fs');
const src = fs.readFileSync('packages/playwright-core/src/tools/mcp/browserFactory.ts', 'utf8');

// Find the createPersistentBrowser function body
const fnMatch = src.match(/async function createPersistentBrowser\([\s\S]*?\nfunction /);
if (!fnMatch) throw new Error('Could not find createPersistentBrowser function');
const fnBody = fnMatch[0];

// Must call launchPersistentContext (real browser launch, not a stub)
if (!fnBody.includes('launchPersistentContext'))
    throw new Error('Function must call launchPersistentContext');

// Must have error handling with try/catch
if (!fnBody.includes('try {'))
    throw new Error('Function must have try block');
if (!fnBody.includes('catch'))
    throw new Error('Function must have catch block');

// Must construct launchOptions object with real properties
if (!fnBody.includes('ignoreDefaultArgs'))
    throw new Error('Function must set ignoreDefaultArgs in launchOptions');

// Must have handleSIGINT/handleSIGTERM (real browser lifecycle management)
if (!fnBody.includes('handleSIGINT'))
    throw new Error('Function must handle signals');

console.log('PASS');
""")
    assert r.returncode == 0, f"Anti-stub test failed:\n{r.stdout}\n{r.stderr}"
    assert "PASS" in r.stdout
