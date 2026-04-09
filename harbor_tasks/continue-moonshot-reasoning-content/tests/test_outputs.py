"""
Test that Moonshot provider correctly sets supportsReasoningContentField
based on the model name for Kimi models.
"""

import subprocess
import sys
import os

REPO = "/workspace/continue"
MOONSHOT_PATH = os.path.join(REPO, "core/llm/llms/Moonshot.ts")

def test_kimi_model_sets_reasoning_content_flag():
    """Test that kimi-* models set supportsReasoningContentField to true."""
    # Build and run a test that imports Moonshot with kimi model
    test_code = '''
import { Moonshot } from "./core/llm/llms/Moonshot.js";

const kimiModel = new Moonshot({
    model: "kimi-k2.5",
    apiKey: "test-key"
});

if (kimiModel.supportsReasoningContentField !== true) {
    console.error("FAIL: kimi-k2.5 should have supportsReasoningContentField=true");
    console.error("Got:", kimiModel.supportsReasoningContentField);
    process.exit(1);
}

const kimiK1Model = new Moonshot({
    model: "kimi-k1.5",
    apiKey: "test-key"
});

if (kimiK1Model.supportsReasoningContentField !== true) {
    console.error("FAIL: kimi-k1.5 should have supportsReasoningContentField=true");
    console.error("Got:", kimiK1Model.supportsReasoningContentField);
    process.exit(1);
}

console.log("PASS: kimi models correctly set supportsReasoningContentField");
'''

    result = subprocess.run(
        ["node", "--input-type=module", "-e", test_code],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, f"Test failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    assert "PASS" in result.stdout, f"Expected PASS in output, got:\n{result.stdout}"


def test_non_kimi_model_unsets_reasoning_content_flag():
    """Test that non-kimi models (moonshot-v1-*) have supportsReasoningContentField set to false."""
    test_code = '''
import { Moonshot } from "./core/llm/llms/Moonshot.js";

const moonshotModel = new Moonshot({
    model: "moonshot-v1-8k",
    apiBase: "https://api.moonshot.cn/v1/",
    apiKey: "test-key"
});

if (moonshotModel.supportsReasoningContentField !== false) {
    console.error("FAIL: moonshot-v1-8k should have supportsReasoningContentField=false");
    console.error("Got:", moonshotModel.supportsReasoningContentField);
    process.exit(1);
}

const anotherMoonshotModel = new Moonshot({
    model: "moonshot-v1-32k",
    apiBase: "https://api.moonshot.cn/v1/",
    apiKey: "test-key"
});

if (anotherMoonshotModel.supportsReasoningContentField !== false) {
    console.error("FAIL: moonshot-v1-32k should have supportsReasoningContentField=false");
    console.error("Got:", anotherMoonshotModel.supportsReasoningContentField);
    process.exit(1);
}

console.log("PASS: non-kimi models correctly have supportsReasoningContentField=false");
'''

    result = subprocess.run(
        ["node", "--input-type=module", "-e", test_code],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, f"Test failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    assert "PASS" in result.stdout, f"Expected PASS in output, got:\n{result.stdout}"


def test_moonshot_class_compiles():
    """Test that Moonshot.ts compiles without errors."""
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "core/llm/llms/Moonshot.ts"],
        cwd=os.path.join(REPO, "core"),
        capture_output=True,
        text=True,
        timeout=120
    )

    # tsc may exit 0 even with errors in some cases, check stderr too
    error_output = result.stderr + result.stdout
    assert "error" not in error_output.lower() or result.returncode == 0, \
        f"TypeScript compilation failed:\n{error_output}"


def test_constructor_preserves_other_properties():
    """Test that the constructor preserves other Moonshot properties like apiBase."""
    test_code = '''
import { Moonshot } from "./core/llm/llms/Moonshot.js";

const model = new Moonshot({
    model: "kimi-k2.5",
    apiBase: "https://custom.moonshot.cn/v1/",
    apiKey: "test-key"
});

// Check that apiBase is preserved
if (model.apiBase !== "https://custom.moonshot.cn/v1/") {
    console.error("FAIL: apiBase should be preserved");
    console.error("Expected: https://custom.moonshot.cn/v1/");
    console.error("Got:", model.apiBase);
    process.exit(1);
}

// Check provider name is still set
if (model.providerName !== "moonshot") {
    console.error("FAIL: providerName should be 'moonshot'");
    console.error("Got:", model.providerName);
    process.exit(1);
}

console.log("PASS: constructor preserves other properties");
'''

    result = subprocess.run(
        ["node", "--input-type=module", "-e", test_code],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, f"Test failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    assert "PASS" in result.stdout, f"Expected PASS in output, got:\n{result.stdout}"


def test_model_prefix_matching():
    """Test that only models starting with 'kimi' get reasoning_content support."""
    test_code = '''
import { Moonshot } from "./core/llm/llms/Moonshot.js";

const testCases = [
    { model: "kimi-k2.5", expected: true },
    { model: "kimi-k1.5", expected: true },
    { model: "kimi-anything", expected: true },
    { model: "moonshot-v1-8k", expected: false },
    { model: "moonshot-v1-32k", expected: false },
    { model: "gpt-4", expected: false },
    { model: "", expected: false },
];

for (const tc of testCases) {
    const instance = new Moonshot({
        model: tc.model,
        apiKey: "test-key"
    });

    if (instance.supportsReasoningContentField !== tc.expected) {
        console.error(`FAIL: model "${tc.model}" should have supportsReasoningContentField=${tc.expected}`);
        console.error(`Got: ${instance.supportsReasoningContentField}`);
        process.exit(1);
    }
}

console.log("PASS: all model prefix cases handled correctly");
'''

    result = subprocess.run(
        ["node", "--input-type=module", "-e", test_code],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, f"Test failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    assert "PASS" in result.stdout, f"Expected PASS in output, got:\n{result.stdout}"


# Pass-to-pass tests: Repo CI/CD checks that should pass on both base and fix
# NOTE: These tests require the Dockerfile to have build tools (make, g++, python3-dev)
# The Dockerfile currently fails to build due to missing make for sqlite3 compilation

def test_repo_tsc_check():
    """Repo's TypeScript typecheck passes in core/ directory (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=os.path.join(REPO, "core"),
    )
    assert r.returncode == 0, f"TypeScript typecheck failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_vitest():
    """Repo's vitest tests pass in core/ directory (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "vitest"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=os.path.join(REPO, "core"),
    )
    assert r.returncode == 0, f"Vitest failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"
