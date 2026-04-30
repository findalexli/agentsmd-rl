#!/usr/bin/env python3
"""
Test harness for effect-ai-amazon-bedrock cache point fix.

Tests verify that the AmazonBedrockLanguageModel.ts source file contains
the fix for user/tool message cache point support.
"""

import os
import re
import subprocess
from pathlib import Path

REPO = "/workspace/effect"
PACKAGE_DIR = f"{REPO}/packages/ai/amazon-bedrock"
SOURCE_FILE = f"{PACKAGE_DIR}/src/AmazonBedrockLanguageModel.ts"


def read_source():
    """Read the source file content."""
    with open(SOURCE_FILE, "r") as f:
        return f.read()


def find_case_block(content, case_label):
    """Find a case block by brace-counting from the case label."""
    start = content.find(case_label)
    if start == -1:
        return None

    brace_start = content.find('{', start)
    if brace_start == -1:
        return None

    depth = 1
    pos = brace_start + 1
    while pos < len(content) and depth > 0:
        if content[pos] == '{':
            depth += 1
        elif content[pos] == '}':
            depth -= 1
        pos += 1

    return content[start:pos]


def _node_available():
    """Check if Node.js is available."""
    r = subprocess.run(
        ["bash", "-c", "command -v node && command -v tsc"],
        capture_output=True, text=True,
    )
    return r.returncode == 0


def test_source_structure():
    """Source file has correct structure (pass_to_pass)."""
    content = read_source()

    assert "const prepareMessages" in content, \
        "prepareMessages function not found in source"
    assert "const BEDROCK_CACHE_POINT" in content, \
        "BEDROCK_CACHE_POINT constant not found"
    assert "const getCachePoint" in content, \
        "getCachePoint function not found"

    print("PASS: test_source_structure")


def test_user_message_has_cache_point_check():
    """User message handling block contains getCachePoint check (fail_to_pass)."""
    content = read_source()

    user_case = find_case_block(content, 'case "user":')
    assert user_case is not None, "Could not find 'case \"user\":' block"

    getcache_pattern = re.search(r'getCachePoint\s*\(\s*message\s*\)', user_case)
    assert getcache_pattern is not None, \
        "User message block should call getCachePoint(message)"

    # Verify BEDROCK_CACHE_POINT is pushed to content near the getCachePoint call
    lines = user_case.split('\n')
    found_valid_pattern = False
    for i, line in enumerate(lines):
        if 'getCachePoint' in line and 'message' in line:
            context = '\n'.join(lines[max(0, i - 2):min(len(lines), i + 5)])
            if 'BEDROCK_CACHE_POINT' in context and 'content.push' in context:
                found_valid_pattern = True
                break

    assert found_valid_pattern, \
        "User message block does not push BEDROCK_CACHE_POINT to content when getCachePoint is checked"

    print("PASS: test_user_message_has_cache_point_check")


def test_tool_case_block_has_cache_point_check():
    """Tool message handling in case block has cache point check (fail_to_pass).

    Both 'user' and 'tool' roles are handled in 'case "user":' block.
    After the fix, cache point handling covers both message types.
    """
    content = read_source()

    user_case = find_case_block(content, 'case "user":')
    assert user_case is not None, "Could not find 'case \"user\":' block"

    getcache_pattern = re.search(r'getCachePoint\s*\(\s*message\s*\)', user_case)
    assert getcache_pattern is not None, \
        "Case block (which handles user AND tool messages) does not call getCachePoint(message)"

    print("PASS: test_tool_case_block_has_cache_point_check")


def test_assistant_message_has_cache_point_check():
    """Assistant message block has cache point check (pass_to_pass regression guard)."""
    content = read_source()

    assistant_case = find_case_block(content, 'case "assistant":')
    assert assistant_case is not None, "Could not find 'case \"assistant\":' block"

    assert 'getCachePoint(message)' in assistant_case, \
        "Assistant message block does not call getCachePoint(message)"

    lines = assistant_case.split('\n')
    found_valid_pattern = False
    for i, line in enumerate(lines):
        if 'getCachePoint' in line and 'message' in line:
            context = '\n'.join(lines[max(0, i - 2):min(len(lines), i + 5)])
            if 'BEDROCK_CACHE_POINT' in context and 'content.push' in context:
                found_valid_pattern = True
                break

    assert found_valid_pattern, \
        "Assistant message block does not have the expected cache point pattern"

    print("PASS: test_assistant_message_has_cache_point_check")


def test_typescript_check():
    """TypeScript typecheck passes for amazon-bedrock package (pass_to_pass).

    Runs tsc --noEmit scoped to the amazon-bedrock package, equivalent to the
    CI 'Types' job's pnpm check step.
    """
    assert _node_available(), "Node.js or tsc not available"

    r = subprocess.run(
        [
            "bash", "-c",
            "cd /workspace/effect/packages/ai/amazon-bedrock && "
            "tsc --noEmit --skipLibCheck --ignoreDeprecations 6.0 2>&1"
        ],
        capture_output=True, text=True, timeout=600,
    )
    assert r.returncode == 0, f"tsc check failed (returncode={r.returncode}):\n{r.stderr[-800:]}"

    print("PASS: test_typescript_check")


def test_cache_point_behavior():
    """Behavioral test: verify cache point is added to user message content (fail_to_pass).

    Uses Node.js to inspect the source file and verify the cache point
    feature is correctly wired in the user message handling block.
    """
    assert _node_available(), "Node.js not available"

    test_script = """
import { readFileSync } from 'fs';
import { join } from 'path';

const sourcePath = join(
    process.cwd(),
    'packages/ai/amazon-bedrock/src/AmazonBedrockLanguageModel.ts'
);
const source = readFileSync(sourcePath, 'utf8');

function findCaseBlock(content, caseLabel) {
    const start = content.indexOf(caseLabel);
    if (start === -1) return null;
    const braceStart = content.indexOf('{', start);
    if (braceStart === -1) return null;
    let depth = 1;
    let pos = braceStart + 1;
    while (pos < content.length && depth > 0) {
        if (content[pos] === '{') depth++;
        else if (content[pos] === '}') depth--;
        pos++;
    }
    return content.slice(start, pos);
}

const userCase = findCaseBlock(source, 'case "user":');
if (!userCase) {
    console.error('FAIL: Could not find user case block');
    process.exit(1);
}

if (!userCase.includes('getCachePoint(message)')) {
    console.error('FAIL: getCachePoint(message) not found in user case');
    process.exit(1);
}

if (!userCase.includes('BEDROCK_CACHE_POINT')) {
    console.error('FAIL: BEDROCK_CACHE_POINT not found in user case');
    process.exit(1);
}

const hasContentPush = /content\\.push\\s*\\(\\s*BEDROCK_CACHE_POINT\\s*\\)/.test(userCase);
if (!hasContentPush) {
    console.error('FAIL: content.push(BEDROCK_CACHE_POINT) pattern not found');
    process.exit(1);
}

console.log('PASS: cache point behavior verified');
process.exit(0);
"""

    script_path = Path(REPO) / "_test_cache_behavior.mjs"
    script_path.write_text(test_script)

    try:
        r = subprocess.run(
            ["node", str(script_path)],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        assert r.returncode == 0, f"Behavioral test failed:\n{r.stderr}"
        assert "PASS" in r.stdout, f"Test did not output PASS: {r.stdout}"
    finally:
        script_path.unlink(missing_ok=True)

    print("PASS: test_cache_point_behavior")


if __name__ == "__main__":
    import sys

    tests = [
        ("test_source_structure", test_source_structure),
        ("test_user_message_has_cache_point_check", test_user_message_has_cache_point_check),
        ("test_tool_case_block_has_cache_point_check", test_tool_case_block_has_cache_point_check),
        ("test_assistant_message_has_cache_point_check", test_assistant_message_has_cache_point_check),
        ("test_typescript_check", test_typescript_check),
        ("test_cache_point_behavior", test_cache_point_behavior),
    ]

    results = []
    for name, fn in tests:
        try:
            fn()
            results.append((name, "PASS"))
        except AssertionError as e:
            results.append((name, f"FAIL: {e}"))
        except Exception as e:
            results.append((name, f"ERROR: {e}"))

    for name, status in results:
        print(f"{status} {name}")

    if any("FAIL" in s or "ERROR" in s for _, s in results):
        sys.exit(1)
    sys.exit(0)

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_pnpm():
    """pass_to_pass | CI job 'Build' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm docgen'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_pnpm():
    """pass_to_pass | CI job 'Lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm circular'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_pnpm_2():
    """pass_to_pass | CI job 'Lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_pnpm_3():
    """pass_to_pass | CI job 'Lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm codegen'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_check_for_codegen_changes():
    """pass_to_pass | CI job 'Lint' → step 'Check for codegen changes'"""
    r = subprocess.run(
        ["bash", "-lc", 'git diff --exit-code'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check for codegen changes' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")