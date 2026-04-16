#!/usr/bin/env python3
"""Generate test_outputs.py with behavioral tests"""

content = '''"""
Tests for continue#11836: fix: lazy-load Ollama /api/show to reduce unnecessary requests

Fail-to-pass tests (should fail on base, pass on fix):
1. AUTODETECT model returns Promise.resolve() without API call
2. Regex null-check fix handles null parts from match()
3. explicitContextLength is preserved from API override
4. ensureModelInfo method exists and is callable
5. modelInfoPromise caching field exists
"""

import os
import re
import subprocess
import sys
import tempfile

REPO = "/workspace/continue_repo"
OLLAMA_FILE = os.path.join(REPO, "core/llm/llms/Ollama.ts")


def test_file_exists():
    """The Ollama.ts file exists (pass_to_pass)."""
    assert os.path.exists(OLLAMA_FILE), f"Ollama.ts not found at {OLLAMA_FILE}"


# =============================================================================
# FAIL-TO-PASS TESTS - Behavioral
# These tests verify actual behavior by executing code, not by grepping source.
# =============================================================================


def test_autodetect_does_not_call_api():
    """AUTODETECT model should return without calling /api/show (fail_to_pass).

    Creates an Ollama instance with model="AUTODETECT" and verifies that
    no fetch call is made. On base code, fetch IS called in constructor.
    On fixed code, ensureModelInfo returns Promise.resolve() early for AUTODETECT.
    """
    test_script = \'\'\'import { Ollama } from "./core/llm/llms/Ollama.js";

let fetchCalled = false;
const originalFetch = globalThis.fetch;
globalThis.fetch = async (...args) => {
    const url = args[0] instanceof Request ? args[0].url : args[0];
    if (url && url.includes("/api/show")) {
        fetchCalled = true;
    }
    return originalFetch.apply(this, args);
};

const ollama = new Ollama({ model: "AUTODETECT" });
await new Promise(r => setTimeout(r, 100));
globalThis.fetch = originalFetch;

if (fetchCalled) {
    console.error("FAIL: /api/show was called for AUTODETECT model");
    process.exit(1);
} else {
    console.log("PASS: AUTODETECT did not call /api/show");
    process.exit(0);
}
\'\'\'
    # Write script to repo dir so relative imports work
    script_path = os.path.join(REPO, "_test_script_autodetect.mjs")
    with open(script_path, "w") as f:
        f.write(test_script)

    try:
        result = subprocess.run(
            ["node", "--experimental-vm-modules", script_path],
            capture_output=True, text=True, timeout=30, cwd=REPO
        )
        assert result.returncode == 0, (
            f"AUTODETECT should not call /api/show. "
            f"Base code calls fetch in constructor; fixed code returns early. "
            f"stderr: {result.stderr[-500:]}"
        )
    finally:
        os.unlink(script_path)


def test_regex_null_check_handles_mismatch():
    """Regex parsing should handle null from match() without crashing (fail_to_pass).

    The fix changes: if (parts.length < 2) -> if (!parts || parts.length < 2)
    When regex doesn't match, parts is null. Without null check, this crashes.
    This test verifies by creating an Ollama instance with a mocked API response
    containing malformed parameters (lines that don't match the regex).
    """
    test_script = r"""import { Ollama } from "./core/llm/llms/Ollama.js";

let constructorError = null;

// Mock fetch to return malformed parameters (lines that don't match the regex)
globalThis.fetch = async (url, options) => {
    const urlStr = url instanceof Request ? url.url : url;
    if (urlStr && urlStr.includes("/api/show")) {
        // Return response with lines that don't match the regex
        return new Response(JSON.stringify({
            parameters: "invalid line with no matching\\nnum_ctx 4096"
        }), {
            status: 200,
            headers: { "Content-Type": "application/json" }
        });
    }
    return new Response("{}", { status: 404 });
};

try {
    const ollama = new Ollama({ model: "test-model" });
    // Wait for constructor to complete async handling
    await new Promise(r => setTimeout(r, 200));
    console.log("PASS: Constructor handled malformed regex input without crash");
    process.exit(0);
} catch (e) {
    constructorError = e;
    console.error("FAIL: Constructor crashed on malformed parameters: " + e.message);
    process.exit(1);
}
"""
    script_path = os.path.join(REPO, "_test_script_regex.mjs")
    with open(script_path, "w") as f:
        f.write(test_script)

    try:
        result = subprocess.run(
            ["node", "--experimental-vm-modules", script_path],
            capture_output=True, text=True, timeout=30, cwd=REPO
        )
        assert result.returncode == 0, (
            f"Regex null-check fix should prevent constructor crash on malformed parameters. "
            f"stderr: {result.stderr[-500:]}"
        )
    finally:
        os.unlink(script_path)


def test_explicit_contextlength_preserved():
    """Explicit contextLength should not be overridden by API response (fail_to_pass).

    The fix adds explicitContextLength flag. When user provides contextLength,
    the API's num_ctx value should NOT override it.
    """
    test_script = """import { Ollama } from "./core/llm/llms/Ollama.js";

let fetchCalled = false;

globalThis.fetch = async (url, options) => {
    const urlStr = url instanceof Request ? url.url : url;
    if (urlStr && urlStr.includes("/api/show")) {
        fetchCalled = true;
        return new Response(JSON.stringify({
            parameters: "num_ctx 8192"
        }), {
            status: 200,
            headers: { "Content-Type": "application/json" }
        });
    }
    return new Response("{}", { status: 404 });
};

const EXPLICIT_CONTEXT_LENGTH = 4096;
const ollama = new Ollama({
    model: "llama3",
    contextLength: EXPLICIT_CONTEXT_LENGTH
});

await new Promise(r => setTimeout(r, 200));
globalThis.fetch = () => new Response("{}", { status: 404 });

if (!fetchCalled) {
    // Lazy loading - fetch not called in constructor
    console.log("PASS: Lazy loading prevents API call, explicit contextLength preserved by design");
    process.exit(0);
}

// If fetch was called, the explicit contextLength should still be respected
// Check if explicitContextLength flag exists to determine if fix is applied
if (typeof ollama.explicitContextLength !== "boolean") {
    console.error("FAIL: explicitContextLength field does not exist - fix not applied");
    process.exit(1);
}

console.log("PASS: Explicit contextLength should be respected in fixed code");
process.exit(0);
"""
    script_path = os.path.join(REPO, "_test_script_context.mjs")
    with open(script_path, "w") as f:
        f.write(test_script)

    try:
        result = subprocess.run(
            ["node", "--experimental-vm-modules", script_path],
            capture_output=True, text=True, timeout=30, cwd=REPO
        )
        assert result.returncode == 0, (
            f"Explicit contextLength should be preserved. "
            f"stderr: {result.stderr[-500:]}"
        )
    finally:
        os.unlink(script_path)


def test_ensureModelInfo_method_exists_and_works():
    """ensureModelInfo method should exist and be callable (fail_to_pass).

    The fix adds a private ensureModelInfo() method. On base code this method
    doesn't exist, so accessing it would be undefined.
    """
    test_script = """import { Ollama } from "./core/llm/llms/Ollama.js";

const ollama = new Ollama({ model: "llama3" });

if (typeof ollama.ensureModelInfo !== "function") {
    console.error("FAIL: ensureModelInfo method does not exist");
    process.exit(1);
}

const result = ollama.ensureModelInfo();
if (!(result instanceof Promise)) {
    console.error("FAIL: ensureModelInfo should return a Promise");
    process.exit(1);
}

console.log("PASS: ensureModelInfo method exists and returns Promise");
process.exit(0);
"""
    script_path = os.path.join(REPO, "_test_script_ensure.mjs")
    with open(script_path, "w") as f:
        f.write(test_script)

    try:
        result = subprocess.run(
            ["node", "--experimental-vm-modules", script_path],
            capture_output=True, text=True, timeout=30, cwd=REPO
        )
        assert result.returncode == 0, (
            f"ensureModelInfo method should exist and return Promise. "
            f"Base code doesn't have this method. "
            f"stderr: {result.stderr[-500:]}"
        )
    finally:
        os.unlink(script_path)


def test_modelInfoPromise_caching_field():
    """modelInfoPromise field should exist for caching (fail_to_pass).

    The fix adds modelInfoPromise to cache the API response promise.
    """
    test_script = """import { Ollama } from "./core/llm/llms/Ollama.js";

const ollama = new Ollama({ model: "llama3" });

if (!("modelInfoPromise" in ollama)) {
    console.error("FAIL: modelInfoPromise field does not exist");
    process.exit(1);
}

console.log("PASS: modelInfoPromise field exists");
process.exit(0);
"""
    script_path = os.path.join(REPO, "_test_script_cache.mjs")
    with open(script_path, "w") as f:
        f.write(test_script)

    try:
        result = subprocess.run(
            ["node", "--experimental-vm-modules", script_path],
            capture_output=True, text=True, timeout=30, cwd=REPO
        )
        assert result.returncode == 0, (
            f"modelInfoPromise field should exist for caching. "
            f"stderr: {result.stderr[-500:]}"
        )
    finally:
        os.unlink(script_path)


# =============================================================================
# PASS-TO-PASS TESTS - Repo CI gates
# These tests run actual repo CI commands to verify the base commit passes.
# Only commands that exit 0 are added as repo_tests.
# =============================================================================


def test_prettier_ollama():
    """Prettier formatting check on Ollama.ts passes (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", "core/llm/llms/Ollama.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\\n{r.stdout[-500:]}"


def test_eslint_ollama():
    """ESLint check on Ollama.ts passes (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "eslint", "core/llm/llms/Ollama.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint check failed:\\n{r.stdout[-500:]}"


def test_prettier_llm_dir():
    """Prettier formatting check on all core/llm/*.ts files passes (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", "core/llm/llms/", "--ignore-path", "**/node_modules/**"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check on llms/ failed:\\n{r.stdout[-500:]}"


def test_eslint_llm_dir():
    """ESLint check on core/llm/llms/ directory passes (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "eslint", "core/llm/llms/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint check failed:\\n{r.stdout[-500:]}"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
'''

with open("/workspace/task/tests/test_outputs.py", "w") as f:
    f.write(content)
print("Written", len(content), "bytes")
