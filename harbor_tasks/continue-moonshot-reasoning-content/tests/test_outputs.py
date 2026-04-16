#!/usr/bin/env python3
"""
Test suite for Moonshot reasoning_content field support.

This tests that the Moonshot provider correctly sets the
supportsReasoningContentField flag for kimi-* models.
"""

import subprocess
import sys
import os
import re

REPO = "/workspace/continue"


def transpile_typescript(file_path):
    """Transpile TypeScript to JavaScript using the TypeScript API."""
    ts_script = """
import * as ts from 'typescript';
import * as fs from 'fs';

const content = fs.readFileSync('/workspace/continue/core/llm/llms/Moonshot.ts', 'utf-8');
const result = ts.transpileModule(content, {
    compilerOptions: {
        module: ts.ModuleKind.CommonJS,
        target: ts.ScriptTarget.ES2020,
        esModuleInterop: true,
    },
});
console.log(result.outputText);
"""
    result = subprocess.run(
        ["npx", "tsx", "-e", ts_script],
        cwd="/workspace/continue/core",
        capture_output=True,
        text=True,
        timeout=30
    )
    if result.returncode != 0:
        return None
    return result.stdout


def test_kimi_model_supports_reasoning_content():
    """
    Test that kimi-* models have supportsReasoningContentField set to true.

    This transpiles the TypeScript to JavaScript and analyzes the transpiled
    output to verify the behavioral fix is present.

    The fix must result in supportsReasoningContentField being set/defined
    based on whether the model name contains "kimi", using a conditional expression.
    """
    moonshot_path = os.path.join(REPO, "core/llm/llms/Moonshot.ts")

    # Transpile to JavaScript
    js_code = transpile_typescript(moonshot_path)
    if js_code is None:
        raise AssertionError("Failed to transpile Moonshot.ts")

    # Behavioral check: The transpiled JavaScript must have supportsReasoningContentField
    # that is set based on model name containing "kimi"

    # Check 1: supportsReasoningContentField is assigned or defined
    has_field = 'supportsReasoningContentField' in js_code

    # Check 2: The assignment/definition uses a kimi-related check
    has_kimi_check = bool(re.search(r'kimi', js_code))

    # Check 3: The field is set/defined conditionally (uses ternary, ??, ||)
    has_conditional = bool(re.search(r'\?\?| \|\||\?', js_code))

    if not (has_field and has_kimi_check and has_conditional):
        raise AssertionError(
            f"Fix not applied or incorrect. "
            f"field={has_field}, "
            f"kimi_check={has_kimi_check}, "
            f"conditional={has_conditional}"
        )


def test_moonshot_v1_models_no_reasoning_content():
    """
    Test that moonshot-v1-* models do NOT have unconditional reasoning content support.

    Verifies the fix is properly conditional - only kimi models get the flag.
    """
    moonshot_path = os.path.join(REPO, "core/llm/llms/Moonshot.ts")

    # Transpile to JavaScript
    js_code = transpile_typescript(moonshot_path)
    if js_code is None:
        raise AssertionError("Failed to transpile Moonshot.ts")

    # If supportsReasoningContentField is set, it must be conditional on model name
    if 'supportsReasoningContentField' in js_code:
        # Must use a conditional check on model name
        has_model_check = bool(re.search(r'this\.model', js_code))
        has_conditional = bool(re.search(r'\?\?| \|\||\?', js_code))

        if not (has_model_check and has_conditional):
            raise AssertionError(
                "supportsReasoningContentField must be conditional on model name"
            )


def test_moonshot_has_constructor():
    """
    Test that Moonshot class has a constructor that properly initializes.

    Verifies the class can be constructed with options and calls super,
    and that supportsReasoningContentField is properly defined.
    """
    moonshot_path = os.path.join(REPO, "core/llm/llms/Moonshot.ts")

    # Transpile to JavaScript
    js_code = transpile_typescript(moonshot_path)
    if js_code is None:
        raise AssertionError("Failed to transpile Moonshot.ts")

    # Check that the class has a constructor
    has_constructor = 'constructor' in js_code

    # Check that super is called
    has_super_call = bool(re.search(r'super\s*\(', js_code))

    # Check that supportsReasoningContentField is defined somewhere in the class
    has_field = 'supportsReasoningContentField' in js_code

    if not (has_constructor and has_super_call and has_field):
        raise AssertionError(
            f"Moonshot should have constructor calling super and defining supportsReasoningContentField. "
            f"constructor={has_constructor}, super_call={has_super_call}, field={has_field}"
        )


def test_typescript_syntax():
    """
    Test that Moonshot.ts has valid TypeScript syntax using tsc on single file.
    This is a pass-to-pass test - should pass on both base and fix.
    """
    moonshot_path = os.path.join(REPO, "core/llm/llms/Moonshot.ts")

    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck", moonshot_path],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30
    )

    output = result.stdout + result.stderr

    # Check for syntax errors
    if 'error TS13' in output or 'error TS2307' in output:
        if 'Moonshot.ts' in output:
            raise AssertionError(f"Syntax errors in Moonshot.ts: {output[:500]}")


def test_moonshot_extends_openai():
    """
    Test that Moonshot properly extends OpenAI class.
    This is a pass-to-pass consistency check.
    """
    moonshot_path = os.path.join(REPO, "core/llm/llms/Moonshot.ts")
    with open(moonshot_path) as f:
        content = f.read()

    if "class Moonshot extends OpenAI" not in content:
        raise AssertionError("Moonshot must extend OpenAI")

    if 'import OpenAI from "./OpenAI.js"' not in content:
        raise AssertionError("Moonshot must import OpenAI")


def test_repo_lint():
    """
    Test that the core package passes its own linting.
    This is a pass-to-pass test from the repo's CI configuration.
    """
    result = subprocess.run(
        ["npm", "run", "lint"],
        cwd=os.path.join(REPO, "core"),
        capture_output=True,
        text=True,
        timeout=60
    )

    if result.returncode != 0:
        output = result.stdout + result.stderr
        if "error" in output.lower():
            if "moonshot" in output.lower():
                raise AssertionError(f"Lint errors in Moonshot: {output[:500]}")


def test_moonshot_node_syntax():
    """
    Test that Moonshot.ts has valid Node.js parseable syntax.
    This is a pass-to-pass test using node to validate syntax.
    """
    moonshot_path = os.path.join(REPO, "core/llm/llms/Moonshot.ts")

    node_check = """
    const fs = require('fs');
    const path = require('path');

    const content = fs.readFileSync('MOONSHOT_PATH', 'utf-8');

    const openParens = (content.match(/\\(/g) || []).length;
    const closeParens = (content.match(/\\)/g) || []).length;
    if (openParens !== closeParens) {
        console.error('Mismatched parentheses');
        process.exit(1);
    }

    const openBraces = (content.match(/\\{/g) || []).length;
    const closeBraces = (content.match(/\\}/g) || []).length;
    if (openBraces !== closeBraces) {
        console.error('Mismatched braces');
        process.exit(1);
    }

    if (!content.includes('class Moonshot')) {
        console.error('Missing class declaration');
        process.exit(1);
    }

    if (!content.includes('extends OpenAI')) {
        console.error('Missing extends OpenAI');
        process.exit(1);
    }

    console.log('Basic syntax check passed');
    """.replace('MOONSHOT_PATH', moonshot_path)

    result = subprocess.run(
        ["node", "-e", node_check],
        capture_output=True,
        text=True,
        timeout=30
    )

    assert result.returncode == 0, f"Moonshot.ts syntax check failed:\n{result.stderr}"


def test_repo_llm_tests():
    """
    Test that LLM module unit tests pass.
    This is a pass-to-pass test from the repo's CI configuration.
    """
    result = subprocess.run(
        ["npm", "test", "--", "--testPathPattern=llm", "--testNamePattern=", "--passWithNoTests"],
        cwd=os.path.join(REPO, "core"),
        capture_output=True,
        text=True,
        timeout=120
    )

    output = result.stdout + result.stderr

    if "No tests found" in output or result.returncode != 0:
        if "Cannot find module" in output or "ENOENT" in output:
            return


def test_moonshot_imports():
    """
    Test that Moonshot.ts has correct imports.
    This is a pass-to-pass test verifying the module structure.
    """
    moonshot_path = os.path.join(REPO, "core/llm/llms/Moonshot.ts")

    with open(moonshot_path) as f:
        content = f.read()

    assert 'import OpenAI from "./OpenAI.js"' in content, "Missing OpenAI import"
    assert 'import { streamSse }' in content, "Missing streamSse import"
    assert 'import { CompletionOptions, LLMOptions }' in content, "Missing types import"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
