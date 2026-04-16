#!/usr/bin/env python3
"""
Test harness for effect-ai-amazon-bedrock cache point fix.

Tests verify that the AmazonBedrockLanguageModel.ts source file contains
the fix for user/tool message cache point support.
"""

import os
import re
import subprocess

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


def test_user_message_has_cache_point_check():
    """User message handling block contains getCachePoint check (fail_to_pass).

    Before the fix: the user message block in prepareMessages did not have
    a getCachePoint check. After the fix: there is an if (getCachePoint(message))
    check inside the user case's for loop, after the switch statement.
    """
    content = read_source()

    user_case = find_case_block(content, 'case "user":')
    assert user_case is not None, "Could not find 'case \"user\"' block"

    # The fix adds ONE getCachePoint call in the user case block (at the end of the for loop)
    # Before fix: no getCachePoint in user case
    # After fix: getCachePoint(message) is called after the inner switch

    # Check for getCachePoint in user case
    getcache_count = user_case.count('getCachePoint(message)')

    assert getcache_count >= 1, \
        f"User message block should have getCachePoint(message) call (found {getcache_count})"

    # Verify the full pattern: if (getCachePoint(message)) { content.push(BEDROCK_CACHE_POINT) }
    cache_push_pattern = re.search(
        r'if\s*\(\s*getCachePoint\s*\(\s*message\s*\)\s*\)\s*\{[^}]*content\.push\s*\(\s*BEDROCK_CACHE_POINT\s*\)',
        user_case
    )

    assert cache_push_pattern is not None, \
        "User message block does not have the expected if (getCachePoint) pattern"

    print("PASS: test_user_message_has_cache_point_check")


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

    # Verify the pattern
    cache_push_pattern = re.search(
        r'if\s*\(\s*getCachePoint\s*\(\s*message\s*\)\s*\)\s*\{[^}]*content\.push\s*\(\s*BEDROCK_CACHE_POINT\s*\)',
        assistant_case
    )

    assert cache_push_pattern is not None, \
        "Assistant message block does not have the expected if (getCachePoint) pattern"

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
    # First, ensure node and tsc are available by installing them
    install_result = subprocess.run(
        [
            "bash", "-c",
            'curl -fsSL https://nodejs.org/dist/v20.18.0/node-v20.18.0-linux-x64.tar.gz | tar -xz -C /tmp && '
            'mv /tmp/node-v20.18.0-linux-x64 /opt/node && '
            'export PATH=/opt/node/bin:$PATH && '
            'npm install -g pnpm@10.17.1 typescript'
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if install_result.returncode != 0:
        raise RuntimeError(f"Failed to install Node.js/TypeScript: {install_result.stderr[-300:]}")

    # Now run tsc with correct PATH
    r = subprocess.run(
        [
            "bash", "-c",
            'export PATH=/opt/node/bin:$PATH && '
            'cd /workspace/effect/packages/ai/amazon-bedrock && '
            'tsc --noEmit --skipLibCheck --ignoreDeprecations 6.0'
        ],
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, f"tsc check failed:\n{r.stderr[-500:]}"


if __name__ == "__main__":
    import sys

    tests = [
        ("test_source_structure", test_source_structure),
        ("test_user_message_has_cache_point_check", test_user_message_has_cache_point_check),
        ("test_assistant_message_has_cache_point_check", test_assistant_message_has_cache_point_check),
        ("test_typescript_check", test_typescript_check),
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