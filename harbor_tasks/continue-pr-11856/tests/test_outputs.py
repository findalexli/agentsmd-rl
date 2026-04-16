"""
Test outputs for continue#11856 - OpenRouter Gemini 3 tool support, suffix stripping,
thought_signature, and autocomplete endpoint fix.

These tests verify that the OpenRouter provider correctly:
1. Recognizes google/gemini-3-pro-preview as a tool-supporting model
2. Strips :free, :extended, :beta suffixes before matching model patterns
3. Correctly identifies unsupported and excluded model patterns
"""

import subprocess
import os
import json

REPO = "/workspace/continue"


def test_tool_support_gemini_3():
    """
    Fail-to-pass: google/gemini-3-pro-preview should be recognized as tool-supporting.

    On base commit: returns false (gemini-3 not in supported prefixes)
    On gold: returns true (gemini-3 is in supported prefixes)
    """
    r = subprocess.run(
        ["npx", "tsx", "-e", """
import { PROVIDER_TOOL_SUPPORT } from "./core/llm/toolSupport.ts";
const result = PROVIDER_TOOL_SUPPORT["openrouter"]("google/gemini-3-pro-preview");
console.log(JSON.stringify({ result }));
"""],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    output = r.stdout.strip()
    try:
        data = json.loads(output)
        result = data.get("result", False)
    except (json.JSONDecodeError, KeyError):
        result = False

    assert result is True, (
        f"google/gemini-3-pro-preview should be recognized as tool-supporting. "
        f"On base commit this returns false (gemini-3 not in supported prefixes). "
        f"Output: {r.stdout[:500]}, Error: {r.stderr[:500]}"
    )


def test_tool_support_suffix_stripping():
    """
    Fail-to-pass: Model suffixes (:free, :extended, :beta) should be stripped
    before matching against supported patterns.

    On base commit: meta-llama/llama-3.2-3b-instruct:free returns false
    On gold: meta-llama/llama-3.2-3b-instruct:free returns true (suffix stripped)
    """
    r = subprocess.run(
        ["npx", "tsx", "-e", """
import { PROVIDER_TOOL_SUPPORT } from "./core/llm/toolSupport.ts";
const result = PROVIDER_TOOL_SUPPORT["openrouter"]("meta-llama/llama-3.2-3b-instruct:free");
console.log(JSON.stringify({ result }));
"""],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    output = r.stdout.strip()
    try:
        data = json.loads(output)
        result = data.get("result", False)
    except (json.JSONDecodeError, KeyError):
        result = False

    assert result is True, (
        f"meta-llama/llama-3.2-3b-instruct:free should be recognized as tool-supporting "
        f"(suffix :free should be stripped). On base commit this returns false. "
        f"Output: {r.stdout[:500]}, Error: {r.stderr[:500]}"
    )


def test_tool_support_excluded_patterns():
    """
    Pass-to-pass: Models with excluded patterns (vision, math, guard) should
    return false on both base and gold.
    """
    r = subprocess.run(
        ["npx", "tsx", "-e", """
import { PROVIDER_TOOL_SUPPORT } from "./core/llm/toolSupport.ts";
const tests = [
    ["some/vision-model", false],
    ["some/math-model", false],
    ["some/guard-model", false],
];
const results = tests.map(([model, expected]) => ({
    model,
    result: PROVIDER_TOOL_SUPPORT["openrouter"](model),
    expected
}));
console.log(JSON.stringify({ results }));
"""],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    output = r.stdout.strip()
    try:
        data = json.loads(output)
        results = data.get("results", [])
        for item in results:
            assert item["result"] == item["expected"], (
                f"{item['model']} should return {item['expected']} but returned {item['result']}"
            )
    except (json.JSONDecodeError, KeyError, AssertionError) as e:
        assert False, (
            f"Excluded patterns test failed. "
            f"Output: {r.stdout[:500]}, Error: {r.stderr[:500]}, Exception: {e}"
        )


def test_tool_support_unsupported_models():
    """
    Pass-to-pass: Unknown/random models should return false on both base and gold.
    """
    r = subprocess.run(
        ["npx", "tsx", "-e", """
import { PROVIDER_TOOL_SUPPORT } from "./core/llm/toolSupport.ts";
const tests = [
    ["unknown/random-model", false],
    ["some-provider/vision-model", false],
];
const results = tests.map(([model, expected]) => ({
    model,
    result: PROVIDER_TOOL_SUPPORT["openrouter"](model),
    expected
}));
console.log(JSON.stringify({ results }));
"""],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    output = r.stdout.strip()
    try:
        data = json.loads(output)
        results = data.get("results", [])
        for item in results:
            assert item["result"] == item["expected"], (
                f"{item['model']} should return {item['expected']} but returned {item['result']}"
            )
    except (json.JSONDecodeError, KeyError, AssertionError) as e:
        assert False, (
            f"Unsupported models test failed. "
            f"Output: {r.stdout[:500]}, Error: {r.stderr[:500]}, Exception: {e}"
        )


def test_repo_jest_all_tests():
    """
    Pass-to-pass: All toolSupport tests should pass.

    On base: all existing tests pass
    On gold: all tests (including new ones) should pass
    """
    r = subprocess.run(
        ["./node_modules/.bin/jest", "--testPathPattern", "toolSupport.test.ts"],
        cwd=f"{REPO}/core",
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "NODE_OPTIONS": "--experimental-vm-modules"},
    )

    output = r.stdout + r.stderr
    assert r.returncode == 0, (
        f"All toolSupport tests should pass. "
        f"Output: {output[-1500:]}"
    )


def test_repo_typescript_check():
    """TypeScript type checking passes (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        cwd=f"{REPO}/core",
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"TypeScript check failed:\n{r.stderr[-1000:]}"


def test_repo_lint():
    """ESLint linting passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint"],
        cwd=f"{REPO}/core",
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-1000:]}"


def test_repo_prettier():
    """Prettier formatting check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", "core/**/*.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-1000:]}"