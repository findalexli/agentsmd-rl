"""
Test suite for TanStack/router#6886 - useStore deepEqual fix

This PR adds deepEqual as the comparator for useStore calls in Scripts.tsx
and headContentUtils.tsx to prevent unnecessary re-renders.
"""

import subprocess
import sys
import os
import re

REPO_PATH = "/workspace/router"
SCRIPTS_FILE = f"{REPO_PATH}/packages/react-router/src/Scripts.tsx"
HEAD_UTILS_FILE = f"{REPO_PATH}/packages/react-router/src/headContentUtils.tsx"


def run_repo_command(cmd, timeout=120):
    """Run a command in the repo directory with proper environment."""
    env = {**os.environ, "CI": "1", "NX_DAEMON": "false"}
    return subprocess.run(
        cmd,
        cwd=REPO_PATH,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )


def test_scripts_has_deep_equal_import():
    """Verify Scripts.tsx imports deepEqual from @tanstack/router-core."""
    with open(SCRIPTS_FILE, "r") as f:
        content = f.read()

    # Check for the deepEqual import
    assert (
        "import { deepEqual } from '@tanstack/router-core'" in content
    ), "Scripts.tsx should import deepEqual from @tanstack/router-core"


def test_scripts_use_store_calls_have_deep_equal():
    """Verify all useStore calls in Scripts.tsx have deepEqual as third argument."""
    with open(SCRIPTS_FILE, "r") as f:
        content = f.read()

    # Check that deepEqual is used with the assetScripts useStore call
    assert "getAssetScripts,\n    deepEqual," in content, \
        "assetScripts useStore call should have deepEqual as third argument"

    # Check that deepEqual is used with the scripts useStore call
    assert "getScripts,\n    deepEqual," in content, \
        "scripts useStore call should have deepEqual as third argument"


def test_head_content_utils_has_deep_equal_import():
    """Verify headContentUtils.tsx imports deepEqual from @tanstack/router-core."""
    with open(HEAD_UTILS_FILE, "r") as f:
        content = f.read()

    # Check that deepEqual is imported alongside escapeHtml
    assert (
        "deepEqual, escapeHtml" in content or "escapeHtml, deepEqual" in content
    ), "headContentUtils.tsx should import deepEqual from @tanstack/router-core"


def test_use_tags_use_store_calls_have_deep_equal():
    """Verify useTags hook useStore calls in headContentUtils.tsx have deepEqual."""
    with open(HEAD_UTILS_FILE, "r") as f:
        content = f.read()

    # Find the useTags function and check useStore calls within it
    use_tags_match = re.search(r'export const useTags = \(\) => \{', content)
    assert use_tags_match, "Could not find useTags function"

    use_tags_start = use_tags_match.end()
    # Find the return statement at the end of useTags (uniqBy call)
    return_match = re.search(r'return uniqBy\(\s*\[', content[use_tags_start:])
    assert return_match, "Could not find return uniqBy in useTags"
    use_tags_section = content[use_tags_start:use_tags_start + return_match.start()]

    # Verify there are exactly 5 useStore calls in useTags function
    # Pattern matches: const varName = useStore( OR const varName: Type = useStore(
    use_store_calls = re.findall(r'const \w+(?::[^=]+)? = useStore\(', use_tags_section)
    assert len(use_store_calls) == 5, f"Expected 5 useStore calls in useTags, found {len(use_store_calls)}"

    # Simple check: count occurrences of "deepEqual," in the useTags section
    # Each useStore call in useTags should have deepEqual as the third argument
    deep_equal_count = use_tags_section.count("deepEqual,")
    assert deep_equal_count == 5, \
        f"Expected 5 deepEqual usages in useTags useStore calls, found {deep_equal_count}"


# Pass-to-pass tests (verify CI checks pass on both base and after fix)
# These are the repo's actual CI/CD tests that should pass before and after the fix


def test_p2p_react_router_unit_tests():
    """Repo's unit tests for react-router pass (pass_to_pass).

    Command: pnpm nx run @tanstack/react-router:test:unit -- --run
    Discovered from: package.json test:unit script and CI workflow
    """
    result = run_repo_command(
        ["pnpm", "nx", "run", "@tanstack/react-router:test:unit", "--", "--run"],
        timeout=120,
    )
    assert result.returncode == 0, (
        f"Unit tests failed:\nstdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-500:]}"
    )


def test_p2p_react_router_types():
    """Repo's TypeScript type check for react-router passes (pass_to_pass).

    Command: pnpm nx run @tanstack/react-router:test:types
    Discovered from: package.json test:types script and CI workflow
    """
    result = run_repo_command(
        ["pnpm", "nx", "run", "@tanstack/react-router:test:types"],
        timeout=120,
    )
    assert result.returncode == 0, (
        f"TypeScript type check failed:\nstdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-500:]}"
    )


def test_p2p_react_router_build():
    """Repo's build for react-router package passes (pass_to_pass).

    Command: pnpm nx run @tanstack/react-router:build
    Discovered from: package.json build script and CI workflow
    """
    result = run_repo_command(
        ["pnpm", "nx", "run", "@tanstack/react-router:build"],
        timeout=120,
    )
    assert result.returncode == 0, (
        f"Build failed:\nstdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-500:]}"
    )


def test_p2p_react_router_test_build():
    """Repo's build validation passes (publint + attw) (pass_to_pass).

    Command: pnpm nx run @tanstack/react-router:test:build
    Discovered from: package.json test:build script (publint --strict && attw)
    """
    result = run_repo_command(
        ["pnpm", "nx", "run", "@tanstack/react-router:test:build"],
        timeout=120,
    )
    assert result.returncode == 0, (
        f"Build validation failed:\nstdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-500:]}"
    )


def test_p2p_prettier_check():
    """Repo's Prettier formatting check passes (pass_to_pass).

    Command: pnpm prettier --experimental-cli --check 'packages/react-router/src/**/*.tsx'
    Discovered from: prettier.config.js and CI workflow
    """
    result = run_repo_command(
        ["pnpm", "prettier", "--experimental-cli", "--check", "packages/react-router/src/**/*.tsx"],
        timeout=60,
    )
    assert result.returncode == 0, (
        f"Prettier check failed:\nstdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-500:]}"
    )


def test_p2p_docs_links():
    """Repo's documentation link verification passes (pass_to_pass).

    Command: pnpm test:docs
    Discovered from: package.json test:docs script
    """
    result = run_repo_command(
        ["pnpm", "test:docs"],
        timeout=120,
    )
    assert result.returncode == 0, (
        f"Docs link check failed:\nstdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-500:]}"
    )


# Note: ESLint test was NOT added as pass_to_pass because it has pre-existing
# failures on the base commit (9 errors, 98 warnings). This is a known issue
# in the repo and not related to the fix being tested.
