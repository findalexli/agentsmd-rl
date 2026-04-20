"""
Test suite for continue#11852 - MCP tool args coercion bug fix.

This tests the coerceArgsToSchema function which fixes MCP tools receiving
parsed JSON objects instead of strings when the tool's input schema
defines a parameter as `type: "string"`.
"""

import subprocess
import os
import sys
import json

REPO = "/workspace/continue"


def test_coerceArgsToSchema_exists():
    """coerceArgsToSchema function is exported from parseArgs.ts"""
    parseArgs_path = os.path.join(REPO, "core/tools/parseArgs.ts")
    with open(parseArgs_path, "r") as f:
        content = f.read()
    assert "export function coerceArgsToSchema" in content, \
        "coerceArgsToSchema function must be exported from parseArgs.ts"


def test_coerceArgsToSchema_imported_in_callTool():
    """coerceArgsToSchema is imported and used in callTool.ts"""
    callTool_path = os.path.join(REPO, "core/tools/callTool.ts")
    with open(callTool_path, "r") as f:
        content = f.read()
    assert "coerceArgsToSchema" in content, \
        "coerceArgsToSchema must be used in callTool.ts"
    assert "extras.tool?.function?.parameters" in content, \
        "coerceArgsToSchema must be called with tool schema parameters"


def test_coerceArgsToSchema_stringifies_object():
    """Object values are stringified when schema expects string"""
    # Use tsx to run TypeScript directly
    result = subprocess.run(
        ["npx", "tsx", "-e", """
            import { coerceArgsToSchema } from './core/tools/parseArgs';
            const args = { content: { key: "value", number: 123 } };
            const schema = {
                type: "object",
                properties: {
                    content: { type: "string" }
                }
            };
            const result = coerceArgsToSchema(args, schema);
            console.log(JSON.stringify(result));
        """],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    # On base: this should fail (no such module/function)
    # After fix: should return stringified JSON
    assert result.returncode == 0, f"Module loading failed:\n{result.stderr}"
    output = json.loads(result.stdout.strip())
    assert isinstance(output["content"], str), \
        f"Object should be stringified, got {type(output['content'])}"
    assert '{"key":"value","number":123}' == output["content"], \
        f"Expected serialized object, got {output['content']}"


def test_coerceArgsToSchema_stringifies_array():
    """Array values are stringified when schema expects string"""
    result = subprocess.run(
        ["npx", "tsx", "-e", """
            import { coerceArgsToSchema } from './core/tools/parseArgs';
            const args = { content: ["item1", "item2"] };
            const schema = {
                type: "object",
                properties: {
                    content: { type: "string" }
                }
            };
            const result = coerceArgsToSchema(args, schema);
            console.log(JSON.stringify(result));
        """],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Module loading failed:\n{result.stderr}"
    output = json.loads(result.stdout.strip())
    assert isinstance(output["content"], str), \
        f"Array should be stringified, got {type(output['content'])}"
    assert '["item1","item2"]' == output["content"], \
        f"Expected serialized array, got {output['content']}"


def test_coerceArgsToSchema_preserves_strings():
    """String values are left unchanged when schema expects string"""
    result = subprocess.run(
        ["npx", "tsx", "-e", """
            import { coerceArgsToSchema } from './core/tools/parseArgs';
            const args = { content: "hello world" };
            const schema = {
                type: "object",
                properties: {
                    content: { type: "string" }
                }
            };
            const result = coerceArgsToSchema(args, schema);
            console.log(JSON.stringify(result));
        """],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Module loading failed:\n{result.stderr}"
    output = json.loads(result.stdout.strip())
    assert output["content"] == "hello world", \
        f"String should remain unchanged, got {output['content']}"


def test_coerceArgsToSchema_does_not_coerce_numbers():
    """Numbers are NOT coerced to strings (would hide type errors)"""
    result = subprocess.run(
        ["npx", "tsx", "-e", """
            import { coerceArgsToSchema } from './core/tools/parseArgs';
            const args = { content: 42 };
            const schema = {
                type: "object",
                properties: {
                    content: { type: "string" }
                }
            };
            const result = coerceArgsToSchema(args, schema);
            console.log(JSON.stringify(result));
        """],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Module loading failed:\n{result.stderr}"
    output = json.loads(result.stdout.strip())
    # Numbers should NOT be converted to strings - they should remain as numbers
    # This allows type errors to surface properly
    assert output["content"] == 42, \
        f"Number should NOT be stringified, got {output['content']}"
    assert isinstance(output["content"], int), \
        f"Number should remain number type, got {type(output['content'])}"


def test_coerceArgsToSchema_does_not_mutate_original():
    """Original args object is not mutated"""
    result = subprocess.run(
        ["npx", "tsx", "-e", """
            import { coerceArgsToSchema } from './core/tools/parseArgs';
            const originalArgs = { content: { key: "value" } };
            const schema = {
                type: "object",
                properties: {
                    content: { type: "string" }
                }
            };
            coerceArgsToSchema(originalArgs, schema);
            console.log(JSON.stringify(originalArgs));
        """],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Module loading failed:\n{result.stderr}"
    output = json.loads(result.stdout.strip())
    # Original should still be an object, not stringified
    assert isinstance(output["content"], dict), \
        f"Original args should not be mutated, got {output['content']}"


def test_coerceArgsToSchema_handles_missing_schema():
    """Args returned unchanged when no schema provided"""
    result = subprocess.run(
        ["npx", "tsx", "-e", """
            import { coerceArgsToSchema } from './core/tools/parseArgs';
            const inputArgs = { content: { key: "value" } };
            const result = coerceArgsToSchema(inputArgs, undefined);
            console.log(JSON.stringify(result));
        """],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Module loading failed:\n{result.stderr}"
    output = json.loads(result.stdout.strip())
    # Without schema, should return args unchanged (object stays object)
    assert output["content"] == {"key": "value"}, \
        "Without schema, args should be returned unchanged"


def test_parseArgs_typescript_compiles():
    """TypeScript compilation of parseArgs.ts succeeds"""
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "tools/parseArgs.ts"],
        cwd=os.path.join(REPO, "core"),
        capture_output=True,
        text=True,
        timeout=120
    )
    # Only check for errors in parseArgs.ts
    output = result.stderr + result.stdout
    if "parseArgs.ts" in output:
        # Filter to only parseArgs.ts errors
        parseArgs_errors = [line for line in output.split('\n') if 'parseArgs.ts' in line]
        assert result.returncode == 0, f"parseArgs.ts TypeScript errors:\n{chr(10).join(parseArgs_errors)}"


def test_vitest_passes():
    """Vitest unit tests for parseArgs pass"""
    result = subprocess.run(
        ["npm", "run", "vitest", "--", "parseArgs.vitest.ts", "--run"],
        cwd=os.path.join(REPO, "core"),
        capture_output=True,
        text=True,
        timeout=300
    )
    # Check for test pass output
    output = result.stderr + result.stdout
    assert "pass" in output.lower() or result.returncode == 0, \
        f"Vitest tests should pass:\n{output[-1000:]}"


def test_repo_vitest_parseArgs():
    """Repo's vitest tests for parseArgs pass (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "tools/parseArgs.vitest.ts"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/core",
    )
    assert r.returncode == 0, f"parseArgs vitest failed:\n{r.stderr[-500:]}"


def test_repo_vitest_applyToolOverrides():
    """Repo's vitest tests for applyToolOverrides pass (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "tools/applyToolOverrides.vitest.ts"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/core",
    )
    assert r.returncode == 0, f"applyToolOverrides vitest failed:\n{r.stderr[-500:]}"


def test_repo_vitest_mcpToolName():
    """Repo's vitest tests for mcpToolName pass (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "tools/mcpToolName.vitest.ts"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/core",
    )
    assert r.returncode == 0, f"mcpToolName vitest failed:\n{r.stderr[-500:]}"


if __name__ == "__main__":
    # Run pytest with verbose output
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))