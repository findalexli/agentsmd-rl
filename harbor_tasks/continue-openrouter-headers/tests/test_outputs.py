"""Tests for OpenRouter headers task.

This module tests that:
1. OPENROUTER_HEADERS are exported from openai-adapters
2. The core/llm OpenRouter class includes the default headers
3. User-configured headers take precedence over defaults
"""

import subprocess
import sys
import json

REPO = "/workspace/continue"

def test_openrouter_headers_exported():
    """Test that OPENROUTER_HEADERS is exported from openai-adapters index."""
    code = """
    const { OPENROUTER_HEADERS } = require('/workspace/continue/packages/openai-adapters/dist/index.js');
    if (!OPENROUTER_HEADERS) {
        console.log(JSON.stringify({pass: false, error: "OPENROUTER_HEADERS not exported"}));
        process.exit(1);
    }
    console.log(JSON.stringify({pass: true, headers: OPENROUTER_HEADERS}));
    """
    result = subprocess.run(
        ["node", "-e", code],
        capture_output=True,
        text=True,
        cwd=REPO
    )
    assert result.returncode == 0, f"OPENROUTER_HEADERS not exported: {result.stderr}"
    output = json.loads(result.stdout)
    assert output["pass"], "OPENROUTER_HEADERS not exported"


def test_openrouter_headers_content():
    """Test that OPENROUTER_HEADERS contains required headers."""
    code = """
    const { OPENROUTER_HEADERS } = require('/workspace/continue/packages/openai-adapters/dist/index.js');
    const expected = {
        "HTTP-Referer": "https://www.continue.dev/",
        "X-OpenRouter-Title": "Continue",
        "X-OpenRouter-Categories": "ide-extension"
    };
    const missing = [];
    for (const [key, value] of Object.entries(expected)) {
        if (OPENROUTER_HEADERS[key] !== value) {
            missing.push(`${key}: expected "${value}", got "${OPENROUTER_HEADERS[key]}"`);
        }
    }
    if (missing.length > 0) {
        console.log(JSON.stringify({pass: false, error: missing.join(", ")}));
        process.exit(1);
    }
    console.log(JSON.stringify({pass: true}));
    """
    result = subprocess.run(
        ["node", "-e", code],
        capture_output=True,
        text=True,
        cwd=REPO
    )
    assert result.returncode == 0, f"Missing or incorrect headers: {result.stderr}"
    output = json.loads(result.stdout)
    assert output["pass"], f"Header check failed: {output.get('error', '')}"


def test_core_openrouter_includes_headers():
    """Test that core/llm OpenRouter includes the OpenRouter headers in request options."""
    code = """
    // We need to check if the OpenRouter constructor properly merges headers
    // Since we can't easily instantiate the full class (requires many deps),
    // we'll check the source code structure
    const fs = require('fs');
    const path = '/workspace/continue/core/llm/llms/OpenRouter.ts';
    const content = fs.readFileSync(path, 'utf8');

    const checks = [
        { name: 'imports OPENROUTER_HEADERS', pattern: /import.*OPENROUTER_HEADERS.*from.*@continuedev\\/openai-adapters/ },
        { name: 'has constructor', pattern: /constructor\\s*\\(\\s*options\\s*:\\s*LLMOptions\\s*\\)/ },
        { name: 'spreads OPENROUTER_HEADERS', pattern: /\\.\\.\\.OPENROUTER_HEADERS/ },
        { name: 'spreads user headers', pattern: /\\.\\.\\.options\\.requestOptions\\?\\.headers/ }
    ];

    const failures = [];
    for (const check of checks) {
        if (!check.pattern.test(content)) {
            failures.push(check.name);
        }
    }

    if (failures.length > 0) {
        console.log(JSON.stringify({pass: false, error: "Missing: " + failures.join(", ")}));
        process.exit(1);
    }
    console.log(JSON.stringify({pass: true}));
    """
    result = subprocess.run(
        ["node", "-e", code],
        capture_output=True,
        text=True,
        cwd=REPO
    )
    assert result.returncode == 0, f"Core OpenRouter headers check failed: {result.stderr}"
    output = json.loads(result.stdout)
    assert output["pass"], f"Core OpenRouter missing headers integration: {output.get('error', '')}"


def test_user_headers_take_precedence():
    """Test that user-configured headers take precedence over defaults."""
    code = """
    const fs = require('fs');
    const path = '/workspace/continue/core/llm/llms/OpenRouter.ts';
    const content = fs.readFileSync(path, 'utf8');

    // Check that user headers come AFTER default headers in the spread
    // This ensures user headers override defaults
    const constructorMatch = content.match(/constructor\\s*\\(\\s*options\\s*:\\s*LLMOptions\\s*\\)[^{]*{([^}]*)}/s);
    if (!constructorMatch) {
        console.log(JSON.stringify({pass: false, error: "Could not find constructor"}));
        process.exit(1);
    }

    // Check the super() call structure - user headers should come after OPENROUTER_HEADERS
    const superCallMatch = content.match(/super\\s*\\(\\s*{[\\s\\S]*?headers\\s*:\\s*{[\\s\\S]*?}\\s*}/);
    if (!superCallMatch) {
        // Try alternate pattern for the headers object
        const headersPattern = /headers\\s*:\\s*{[\\s\\S]*?\\.\\.\\.OPENROUTER_HEADERS[\\s\\S]*?\\.\\.\\.options\\.requestOptions\\?\\.headers[\\s\\S]*?}/;
        if (!headersPattern.test(content)) {
            console.log(JSON.stringify({pass: false, error: "User headers don't override defaults (should come after OPENROUTER_HEADERS spread)"}));
            process.exit(1);
        }
    }

    console.log(JSON.stringify({pass: true}));
    """
    result = subprocess.run(
        ["node", "-e", code],
        capture_output=True,
        text=True,
        cwd=REPO
    )
    assert result.returncode == 0, f"User headers precedence check failed: {result.stderr}"
    output = json.loads(result.stdout)
    assert output["pass"], f"User headers don't take precedence: {output.get('error', '')}"


def test_x_title_updated_to_x_openrouter_title():
    """Test that X-Title header was updated to X-OpenRouter-Title."""
    code = """
    const { OPENROUTER_HEADERS } = require('/workspace/continue/packages/openai-adapters/dist/index.js');

    // Check that X-Title is NOT present (old header name)
    if ("X-Title" in OPENROUTER_HEADERS) {
        console.log(JSON.stringify({pass: false, error: "Old X-Title header should not be present"}));
        process.exit(1);
    }

    // Check that X-OpenRouter-Title IS present (new header name)
    if (!("X-OpenRouter-Title" in OPENROUTER_HEADERS)) {
        console.log(JSON.stringify({pass: false, error: "X-OpenRouter-Title header should be present"}));
        process.exit(1);
    }

    // Check the value is "Continue"
    if (OPENROUTER_HEADERS["X-OpenRouter-Title"] !== "Continue") {
        console.log(JSON.stringify({pass: false, error: `X-OpenRouter-Title should be "Continue", got "${OPENROUTER_HEADERS["X-OpenRouter-Title"]}"`}));
        process.exit(1);
    }

    console.log(JSON.stringify({pass: true}));
    """
    result = subprocess.run(
        ["node", "-e", code],
        capture_output=True,
        text=True,
        cwd=REPO
    )
    assert result.returncode == 0, f"X-Title update check failed: {result.stderr}"
    output = json.loads(result.stdout)
    assert output["pass"], f"X-Title not properly updated: {output.get('error', '')}"


def test_x_openrouter_categories_header():
    """Test that X-OpenRouter-Categories header is present with correct value."""
    code = """
    const { OPENROUTER_HEADERS } = require('/workspace/continue/packages/openai-adapters/dist/index.js');

    if (!("X-OpenRouter-Categories" in OPENROUTER_HEADERS)) {
        console.log(JSON.stringify({pass: false, error: "X-OpenRouter-Categories header not found"}));
        process.exit(1);
    }

    if (OPENROUTER_HEADERS["X-OpenRouter-Categories"] !== "ide-extension") {
        console.log(JSON.stringify({
            pass: false,
            error: `X-OpenRouter-Categories should be "ide-extension", got "${OPENROUTER_HEADERS["X-OpenRouter-Categories"]}"`
        }));
        process.exit(1);
    }

    console.log(JSON.stringify({pass: true}));
    """
    result = subprocess.run(
        ["node", "-e", code],
        capture_output=True,
        text=True,
        cwd=REPO
    )
    assert result.returncode == 0, f"X-OpenRouter-Categories check failed: {result.stderr}"
    output = json.loads(result.stdout)
    assert output["pass"], f"X-OpenRouter-Categories header issue: {output.get('error', '')}"


def test_http_referer_header():
    """Test that HTTP-Referer header is present with correct value."""
    code = """
    const { OPENROUTER_HEADERS } = require('/workspace/continue/packages/openai-adapters/dist/index.js');

    if (!("HTTP-Referer" in OPENROUTER_HEADERS)) {
        console.log(JSON.stringify({pass: false, error: "HTTP-Referer header not found"}));
        process.exit(1);
    }

    if (OPENROUTER_HEADERS["HTTP-Referer"] !== "https://www.continue.dev/") {
        console.log(JSON.stringify({
            pass: false,
            error: `HTTP-Referer should be "https://www.continue.dev/", got "${OPENROUTER_HEADERS["HTTP-Referer"]}"`
        }));
        process.exit(1);
    }

    console.log(JSON.stringify({pass: true}));
    """
    result = subprocess.run(
        ["node", "-e", code],
        capture_output=True,
        text=True,
        cwd=REPO
    )
    assert result.returncode == 0, f"HTTP-Referer check failed: {result.stderr}"
    output = json.loads(result.stdout)
    assert output["pass"], f"HTTP-Referer header issue: {output.get('error', '')}"
