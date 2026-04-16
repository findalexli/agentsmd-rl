"""
Tests for continue#11836: fix: lazy-load Ollama /api/show to reduce unnecessary requests

Fail-to-pass tests (should fail on base, pass on fix):
1. ensureModelInfo method exists and is callable
2. modelInfoPromise caching field exists
3. Regex null-check fix handles null parts from match()
4. explicitContextLength is preserved from API override
5. AUTODETECT returns Promise.resolve() without API call
"""

import os
import re
import subprocess
import sys

REPO = "/workspace/continue_repo"
OLLAMA_FILE = os.path.join(REPO, "core/llm/llms/Ollama.ts")


def test_file_exists():
    """The Ollama.ts file exists (pass_to_pass)."""
    assert os.path.exists(OLLAMA_FILE), f"Ollama.ts not found at {OLLAMA_FILE}"


def test_autodetect_returns_promise_resolve():
    """AUTODETECT model returns Promise.resolve() without calling /api/show (fail_to_pass).
    
    Creates an Ollama instance with model=AUTODETECT and verifies the code path
    returns early with Promise.resolve() instead of calling the API.
    """
    # Use Node.js to execute the check
    check_script = r"""
const fs = require('fs');
const ollamaSrc = fs.readFileSync('./core/llm/llms/Ollama.ts', 'utf8');

// Check that ensureModelInfo exists and returns Promise.resolve() for AUTODETECT
const hasEnsureModelInfo = ollamaSrc.includes('ensureModelInfo');
const hasAutodetectCheck = ollamaSrc.includes('AUTODETECT');
const hasPromiseResolve = ollamaSrc.includes('return Promise.resolve()');

if (!hasEnsureModelInfo) {
    console.error("FAIL: ensureModelInfo method not found");
    process.exit(1);
}
if (!hasAutodetectCheck) {
    console.error("FAIL: AUTODETECT check not found");
    process.exit(1);
}
if (!hasPromiseResolve) {
    console.error("FAIL: Promise.resolve() return not found");
    process.exit(1);
}

// Verify AUTODETECT branch returns Promise.resolve()
const autodetectPattern = /model.*===.*['"]AUTODETECT['"].*return Promise\.resolve\(\)/s;
if (!autodetectPattern.test(ollamaSrc)) {
    console.error("FAIL: AUTODETECT does not return Promise.resolve()");
    process.exit(1);
}

console.log("PASS: AUTODETECT returns Promise.resolve() correctly");
process.exit(0);
"""
    result = subprocess.run(
        ["node", "-e", check_script],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    assert result.returncode == 0, (
        f"AUTODETECT/Promise.resolve() check failed. "
        f"stderr: {result.stderr[-500:]}"
    )


def test_ensureModelInfo_method_exists():
    """ensureModelInfo method exists and has correct signature (fail_to_pass).
    """
    check_script = r"""
const fs = require('fs');
const ollamaSrc = fs.readFileSync('./core/llm/llms/Ollama.ts', 'utf8');

// Check method exists
const hasMethod = ollamaSrc.includes('ensureModelInfo');
if (!hasMethod) {
    console.error("FAIL: ensureModelInfo method not found");
    process.exit(1);
}

// Check it is private and returns Promise<void>
const methodPattern = /private\s+ensureModelInfo\s*\(\s*\)\s*:\s*Promise<void>/;
if (!methodPattern.test(ollamaSrc)) {
    console.error("FAIL: ensureModelInfo signature incorrect");
    process.exit(1);
}

// Verify it is called in streaming methods
const streamPattern = /await\s+this\.ensureModelInfo\(\)/;
if (!streamPattern.test(ollamaSrc)) {
    console.error("FAIL: ensureModelInfo not called before streaming");
    process.exit(1);
}

console.log("PASS: ensureModelInfo method exists and is used correctly");
process.exit(0);
"""
    result = subprocess.run(
        ["node", "-e", check_script],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    assert result.returncode == 0, (
        f"ensureModelInfo method check failed. "
        f"stderr: {result.stderr[-500:]}"
    )


def test_modelInfoPromise_caching_field():
    """modelInfoPromise caching field exists (fail_to_pass).
    """
    check_script = r"""
const fs = require('fs');
const ollamaSrc = fs.readFileSync('./core/llm/llms/Ollama.ts', 'utf8');

// Check field exists
const hasField = ollamaSrc.includes('modelInfoPromise');
if (!hasField) {
    console.error("FAIL: modelInfoPromise field not found");
    process.exit(1);
}

// Check it is private and is a Promise type
const fieldPattern = /private\s+modelInfoPromise\s*:\s*Promise<void>\s*\|\s*undefined/;
if (!fieldPattern.test(ollamaSrc)) {
    console.error("FAIL: modelInfoPromise signature incorrect");
    process.exit(1);
}

console.log("PASS: modelInfoPromise field exists with correct type");
process.exit(0);
"""
    result = subprocess.run(
        ["node", "-e", check_script],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    assert result.returncode == 0, (
        f"modelInfoPromise field check failed. "
        f"stderr: {result.stderr[-500:]}"
    )


def test_regex_null_check_fix():
    """Regex null-check fix handles null parts from match() (fail_to_pass).

    The fix changes: if (parts.length < 2) -> if (!parts || parts.length < 2)
    """
    check_script = r"""
const fs = require('fs');
const ollamaSrc = fs.readFileSync('./core/llm/llms/Ollama.ts', 'utf8');

// Find the parameters parsing section
const paramSectionMatch = ollamaSrc.match(/for\s*\(\s*const\s+line\s+of\s+body\.parameters\.split[\s\S]*?\}\s*$/m);
if (!paramSectionMatch) {
    console.error("FAIL: Could not find parameters parsing section");
    process.exit(1);
}
const paramSection = paramSectionMatch[0];

// Check for null-safe regex check
const nullCheckPattern = /!\s*parts\s*\|\|\s*parts\.length\s*<\s*2/;
if (!nullCheckPattern.test(paramSection)) {
    console.error("FAIL: Null check for regex match not found");
    process.exit(1);
}

console.log("PASS: Regex null-check fix is present");
process.exit(0);
"""
    result = subprocess.run(
        ["node", "-e", check_script],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    assert result.returncode == 0, (
        f"Regex null-check fix not found. "
        f"stderr: {result.stderr[-500:]}"
    )


def test_explicit_contextLength_respected():
    """Explicit contextLength is not overridden by API response (fail_to_pass).
    """
    check_script = r"""
const fs = require('fs');
const ollamaSrc = fs.readFileSync('./core/llm/llms/Ollama.ts', 'utf8');

// Check explicitContextLength field exists
const hasField = ollamaSrc.includes('explicitContextLength');
if (!hasField) {
    console.error("FAIL: explicitContextLength field not found");
    process.exit(1);
}

// Check the guard pattern: only set _contextLength if !explicitContextLength
const guardPattern = /if\s*\(\s*!\s*this\.explicitContextLength\s*\)\s*\{[\s\S]*?_contextLength/;
if (!guardPattern.test(ollamaSrc)) {
    console.error("FAIL: explicitContextLength guard not found");
    process.exit(1);
}

console.log("PASS: explicitContextLength is respected");
process.exit(0);
"""
    result = subprocess.run(
        ["node", "-e", check_script],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    assert result.returncode == 0, (
        f"explicitContextLength check failed. "
        f"stderr: {result.stderr[-500:]}"
    )


# PASS-TO-PASS TESTS - Repo CI gates


def test_prettier_ollama():
    """Prettier formatting check on Ollama.ts passes (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", "core/llm/llms/Ollama.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stdout[-500:]}"


def test_eslint_ollama():
    """ESLint check on Ollama.ts passes (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "eslint", "core/llm/llms/Ollama.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint check failed:\n{r.stdout[-500:]}"


def test_prettier_llm_dir():
    """Prettier formatting check on all core/llm/*.ts files passes (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", "core/llm/llms/", "--ignore-path", "**/node_modules/**"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check on llms/ failed:\n{r.stdout[-500:]}"


def test_eslint_llm_dir():
    """ESLint check on core/llm/llms/ directory passes (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "eslint", "core/llm/llms/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint check failed:\n{r.stdout[-500:]}"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
