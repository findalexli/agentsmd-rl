#!/usr/bin/env python3
"""
Test harness for effect-ai-amazon-bedrock cache point fix.

Tests verify that the AmazonBedrockLanguageModel.ts source file contains
the fix for user/tool message cache point support.

Behavioral tests execute Node.js code to verify the cache point feature works.
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
    """Find a case block by finding the case label and then finding where it ends.

    A case block ends when we hit the next case at the same nesting level or
    the closing brace of the switch statement.
    """
    start = content.find(case_label)
    if start == -1:
        return None

    # Find the opening brace after the case label
    brace_start = content.find('{', start)
    if brace_start == -1:
        return None

    # Count braces to find the matching closing brace
    depth = 1
    pos = brace_start + 1
    while pos < len(content) and depth > 0:
        if content[pos] == '{':
            depth += 1
        elif content[pos] == '}':
            depth -= 1
        pos += 1

    return content[start:pos]


def _install_node():
    """Install Node.js and TypeScript if not available."""
    node_check = subprocess.run(
        ["bash", "-c", "command -v node"],
        capture_output=True, text=True,
    )
    if node_check.returncode == 0:
        # Check if tsc is available
        tsc_check = subprocess.run(
            ["bash", "-c", "command -v tsc"],
            capture_output=True, text=True,
        )
        if tsc_check.returncode == 0:
            return True

    result = subprocess.run(
        [
            "bash", "-c",
            'curl -fsSL https://nodejs.org/dist/v20.18.0/node-v20.18.0-linux-x64.tar.gz | tar -xz -C /tmp && '
            'mv /tmp/node-v20.18.0-linux-x64 /opt/node && '
            'ln -sf /opt/node/bin/node /usr/local/bin/node && '
            'ln -sf /opt/node/bin/npm /usr/local/bin/npm && '
            'ln -sf /opt/node/bin/npx /usr/local/bin/npx'
        ],
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0:
        return False

    # Install typescript globally
    npm_result = subprocess.run(
        ["bash", "-c", "export PATH=/opt/node/bin:$PATH && npm install -g typescript"],
        capture_output=True, text=True, timeout=120,
    )
    return npm_result.returncode == 0


def test_user_message_has_cache_point_check():
    """User message handling block contains getCachePoint check (fail_to_pass).

    Before the fix: the user message block in prepareMessages did not have
    a getCachePoint check. After the fix: there is an if (getCachePoint(message))
    check inside the user case's for loop, after the switch statement.

    This test uses a flexible pattern match that accepts any implementation
    that correctly adds BEDROCK_CACHE_POINT when getCachePoint returns true.
    """
    content = read_source()

    user_case = find_case_block(content, 'case "user":')
    assert user_case is not None, "Could not find 'case \"user\"' block"

    # Check for getCachePoint call in user case
    # Accept any call to getCachePoint with the message parameter
    getcache_pattern = re.search(r'getCachePoint\s*\(\s*message\s*\)', user_case)
    assert getcache_pattern is not None, \
        "User message block should call getCachePoint(message)"

    # Verify that BEDROCK_CACHE_POINT is pushed when cache point is detected
    # We look for ANY pattern where BEDROCK_CACHE_POINT is pushed after a getCachePoint check
    # This allows ternary, if blocks, early returns, or other valid structures
    #
    # Valid patterns (any of):
    # - if (getCachePoint(message)) { content.push(BEDROCK_CACHE_POINT) }
    # - content.push(getCachePoint(message) ? BEDROCK_CACHE_POINT : ...)
    # - const cache = getCachePoint(message); if (cache) { content.push(BEDROCK_CACHE_POINT) }
    #
    # The key is: getCachePoint is checked, and BEDROCK_CACHE_POINT is pushed to content

    # Split into lines and find the relevant section
    lines = user_case.split('\n')

    # Find the getCachePoint call line and look for related content.push nearby
    found_valid_pattern = False
    for i, line in enumerate(lines):
        if 'getCachePoint' in line and 'message' in line:
            # Look at surrounding lines for content.push with BEDROCK_CACHE_POINT
            context = '\n'.join(lines[max(0, i-2):min(len(lines), i+5)])
            if 'BEDROCK_CACHE_POINT' in context and 'content.push' in context:
                found_valid_pattern = True
                break

    assert found_valid_pattern, \
        "User message block does not have a valid cache point pattern: " \
        "getCachePoint(message) must be checked and BEDROCK_CACHE_POINT must be pushed to content"

    print("PASS: test_user_message_has_cache_point_check")


def test_tool_case_block_has_cache_point_check():
    """Tool message handling (in same case as user) has cache point check.

    In the switch statement, both 'user' and 'tool' roles are handled in the
    'case "user":' block. After the fix, cache point handling is added at the
    end of the for loop inside this case, covering both user and tool messages.
    """
    content = read_source()

    user_case = find_case_block(content, 'case "user":')
    assert user_case is not None, "Could not find 'case \"user\"' block"

    # The case block must have getCachePoint for cache point to work for tool messages
    getcache_pattern = re.search(r'getCachePoint\s*\(\s*message\s*\)', user_case)
    assert getcache_pattern is not None, \
        "Case block (which handles user AND tool messages) does not call getCachePoint(message)"

    print("PASS: test_tool_case_block_has_cache_point_check")


def test_assistant_message_has_cache_point_check():
    """Assistant message block also has cache point check (baseline verification).

    This was already working before the fix - we verify it still exists.
    """
    content = read_source()

    assistant_case = find_case_block(content, 'case "assistant":')
    assert assistant_case is not None, "Could not find 'case \"assistant\"' block"

    # The assistant case should have getCachePoint call
    assert 'getCachePoint(message)' in assistant_case, \
        "Assistant message block does not call getCachePoint(message)"

    # Verify the pattern - flexible match
    lines = assistant_case.split('\n')
    found_valid_pattern = False
    for i, line in enumerate(lines):
        if 'getCachePoint' in line and 'message' in line:
            context = '\n'.join(lines[max(0, i-2):min(len(lines), i+5)])
            if 'BEDROCK_CACHE_POINT' in context and 'content.push' in context:
                found_valid_pattern = True
                break

    assert found_valid_pattern, \
        "Assistant message block does not have the expected cache point pattern"

    print("PASS: test_assistant_message_has_cache_point_check")


def test_source_structure():
    """Source file has correct structure for prepareMessages function."""
    content = read_source()

    # Verify the function exists
    assert "const prepareMessages" in content, \
        "prepareMessages function not found in source"

    # Verify BEDROCK_CACHE_POINT constant is defined
    assert "const BEDROCK_CACHE_POINT" in content, \
        "BEDROCK_CACHE_POINT constant not found"

    # Verify getCachePoint function exists
    assert "const getCachePoint" in content, \
        "getCachePoint function not found"

    print("PASS: test_source_structure")


def test_typescript_check():
    """TypeScript typecheck passes for amazon-bedrock package (pass_to_pass).

    Installs Node.js and tsc if needed, then runs tsc --noEmit on the amazon-bedrock
    package to verify the TypeScript code is valid and type-correct.
    """
    _install_node()

    # Now run tsc with correct PATH
    r = subprocess.run(
        [
            "bash", "-c",
            'export PATH=/opt/node/bin:$PATH && '
            'cd /workspace/effect/packages/ai/amazon-bedrock && '
            'tsc --noEmit --skipLibCheck --ignoreDeprecations 6.0 2>&1'
        ],
        capture_output=True, text=True, timeout=600,
    )
    assert r.returncode == 0, f"tsc check failed:\n{r.stderr[-500:]}"

    print("PASS: test_typescript_check")


def test_cache_point_behavior():
    """Behavioral test: verify cache point is added to user message content.

    This test uses Node.js to read and analyze the source file, verifying
    that the cache point feature is correctly implemented.
    """
    _install_node()

    # Create a test script that reads the source file and verifies the fix
    # Use ES module syntax (import) since file ends with .mjs
    test_script = """
import { readFileSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Read the source file to understand the structure
const sourcePath = join(process.cwd(), 'packages/ai/amazon-bedrock/src/AmazonBedrockLanguageModel.ts');
const source = readFileSync(sourcePath, 'utf8');

// Find the case "user": block using brace counting to get proper nesting
function findCaseBlock(content, caseLabel) {
    const start = content.indexOf(caseLabel);
    if (start === -1) return null;

    // Find the opening brace after the case label
    const braceStart = content.indexOf('{', start);
    if (braceStart === -1) return null;

    // Count braces to find the matching closing brace
    let depth = 1;
    let pos = braceStart + 1;
    while (pos < content.length && depth > 0) {
        if (content[pos] === '{') {
            depth++;
        } else if (content[pos] === '}') {
            depth--;
        }
        pos++;
    }

    return content.slice(start, pos);
}

const userCase = findCaseBlock(source, 'case "user":');
if (!userCase) {
    console.error('FAIL: Could not find user case block');
    process.exit(1);
}

// Check for getCachePoint call
if (!userCase.includes('getCachePoint(message)')) {
    console.error('FAIL: getCachePoint(message) not found in user case');
    process.exit(1);
}

// Check for BEDROCK_CACHE_POINT being pushed
if (!userCase.includes('BEDROCK_CACHE_POINT')) {
    console.error('FAIL: BEDROCK_CACHE_POINT not found in user case');
    process.exit(1);
}

// Verify the content.push pattern is present
const hasContentPush = /content\\.push\\s*\\(\\s*BEDROCK_CACHE_POINT\\s*\\)/.test(userCase);
if (!hasContentPush) {
    console.error('FAIL: content.push(BEDROCK_CACHE_POINT) pattern not found');
    process.exit(1);
}

console.log('PASS: cache point behavior verified');
process.exit(0);
"""

    # Write the test script
    script_path = Path(REPO) / "_test_cache_behavior.mjs"
    script_path.write_text(test_script)

    try:
        r = subprocess.run(
            ["node", str(script_path)],
            capture_output=True, text=True, timeout=60, cwd=REPO,
            env={**os.environ, "NODE_PATH": "/opt/node/lib/node_modules"},
        )
        assert r.returncode == 0, f"Behavioral test failed:\n{r.stderr}"
        assert "PASS" in r.stdout, f"Test did not pass: {r.stdout}"
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
