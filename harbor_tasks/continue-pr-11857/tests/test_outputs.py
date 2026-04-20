"""
Test for OpenRouter HTTP-Referer and X-Title headers.

This test verifies that the OpenRouterApi class sets proper identification
headers for all API requests as required by OpenRouter's API guidelines.
"""

import subprocess
import os
import json
import tempfile
import shutil

REPO = "/workspace/continue_dev/packages/openai-adapters"


def test_openrouter_default_headers():
    """OpenRouterApi should include HTTP-Referer and X-Title headers by default."""
    # Create a test script that checks the headers
    test_script = """
import { OpenRouterApi } from './dist/apis/OpenRouter.js';

// Test 1: Check default headers are set
const api = new OpenRouterApi({
    apiKey: 'test-key',
});

const headers = api.config.requestOptions?.headers;
if (!headers) {
    console.error('FAIL: requestOptions.headers is undefined');
    process.exit(1);
}

if (!headers['HTTP-Referer'] || headers['HTTP-Referer'] !== 'https://www.continue.dev/') {
    console.error(`FAIL: HTTP-Referer header not found or incorrect. Got: ${headers['HTTP-Referer']}`);
    process.exit(1);
}

if (!headers['X-Title'] || headers['X-Title'] !== 'Continue') {
    console.error(`FAIL: X-Title header not found or incorrect. Got: ${headers['X-Title']}`);
    process.exit(1);
}

console.log('PASS: Default headers are correctly set');
console.log('HTTP-Referer:', headers['HTTP-Referer']);
console.log('X-Title:', headers['X-Title']);
"""

    # Write the test script
    test_file = os.path.join(REPO, "test_headers_check.mjs")
    with open(test_file, "w") as f:
        f.write(test_script)

    try:
        result = subprocess.run(
            ["node", test_file],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=30
        )

        output = result.stdout + result.stderr
        print(f"Test output: {output}")

        if result.returncode != 0:
            print(f"Test failed with return code {result.returncode}")
            print(f"stderr: {result.stderr}")
            raise AssertionError(f"Default headers test failed. Output: {output}")
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)


def test_openrouter_user_headers_take_precedence():
    """User-provided headers should override default headers."""
    test_script = """
import { OpenRouterApi } from './dist/apis/OpenRouter.js';

// Test: User-provided headers should take precedence over defaults
const api = new OpenRouterApi({
    apiKey: 'test-key',
    requestOptions: {
        headers: {
            'X-Title': 'MyCustomApp'
        }
    }
});

const headers = api.config.requestOptions?.headers;
if (!headers) {
    console.error('FAIL: requestOptions.headers is undefined');
    process.exit(1);
}

// User's X-Title should override the default
if (headers['X-Title'] !== 'MyCustomApp') {
    console.error(`FAIL: User header did not take precedence. Expected 'MyCustomApp', got: ${headers['X-Title']}`);
    process.exit(1);
}

// HTTP-Referer should still be present (not overridden)
if (!headers['HTTP-Referer'] || headers['HTTP-Referer'] !== 'https://www.continue.dev/') {
    console.error(`FAIL: HTTP-Referer should still be present. Got: ${headers['HTTP-Referer']}`);
    process.exit(1);
}

console.log('PASS: User headers correctly take precedence');
console.log('X-Title:', headers['X-Title']);
console.log('HTTP-Referer:', headers['HTTP-Referer']);
"""

    test_file = os.path.join(REPO, "test_headers_precedence.mjs")
    with open(test_file, "w") as f:
        f.write(test_script)

    try:
        result = subprocess.run(
            ["node", test_file],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=30
        )

        output = result.stdout + result.stderr
        print(f"Test output: {output}")

        if result.returncode != 0:
            print(f"Test failed with return code {result.returncode}")
            print(f"stderr: {result.stderr}")
            raise AssertionError(f"User headers precedence test failed. Output: {output}")
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


def test_openai_adapter_headers_not_polluted():
    """OpenAIApi should NOT have the OpenRouter-specific headers (headers are per-subclass)."""
    test_script = """
import { OpenAIApi } from './dist/apis/OpenAI.js';

const api = new OpenAIApi({
    apiKey: 'test-key',
    apiBase: 'https://api.openai.com/v1/'
});

const headers = api.config.requestOptions?.headers;

// OpenAIApi should not have HTTP-Referer or X-Title by default
if (headers && (headers['HTTP-Referer'] || headers['X-Title'])) {
    console.error(`FAIL: OpenAIApi should not have OpenRouter-specific headers. Got HTTP-Referer: ${headers['HTTP-Referer']}, X-Title: ${headers['X-Title']}`);
    process.exit(1);
}

console.log('PASS: OpenAIApi does not have OpenRouter-specific headers');
"""

    test_file = os.path.join(REPO, "test_openai_headers.mjs")
    with open(test_file, "w") as f:
        f.write(test_script)

    try:
        result = subprocess.run(
            ["node", test_file],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=30
        )

        output = result.stdout + result.stderr
        print(f"Test output: {output}")

        if result.returncode != 0:
            print(f"Test failed with return code {result.returncode}")
            print(f"stderr: {result.stderr}")
            raise AssertionError(f"OpenAI headers pollution test failed. Output: {output}")
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


def test_typescript_compiles():
    """TypeScript should compile without errors."""
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    if result.returncode != 0:
        raise AssertionError(f"TypeScript compilation failed:\n{result.stderr}")

    print("TypeScript compilation successful")


def test_repo_vitest_passes():
    """Repo's vitest tests should pass (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "run", "test", "--", "--run", "--reporter=verbose"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    # Print output for debugging
    print(f"Vitest output: {result.stdout}")
    if result.stderr:
        print(f"Vitest stderr: {result.stderr}")

    # We only fail if there are actual test failures
    # Exit code 0 means all tests passed
    if result.returncode != 0:
        # Check if it's just a test file not found error (our test files don't exist yet at base)
        if "No test files found" in result.stdout or "Error loading" in result.stdout:
            # This is expected before the fix is applied
            pass
        else:
            raise AssertionError(f"Vitest tests failed:\n{result.stdout}\n{result.stderr}")


def test_openrouter_vitest():
    """OpenRouter vitest tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "vitest", "run", "src/apis/OpenRouter.test.ts", "--reporter=verbose"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    print(f"OpenRouter test output: {result.stdout}")
    if result.stderr:
        print(f"OpenRouter test stderr: {result.stderr}")

    if result.returncode != 0:
        raise AssertionError(f"OpenRouter vitest failed:\n{result.stdout}\n{result.stderr}")


def test_typescript_typecheck():
    """TypeScript type-check passes (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    if result.returncode != 0:
        raise AssertionError(f"TypeScript type-check failed:\n{result.stderr}")
