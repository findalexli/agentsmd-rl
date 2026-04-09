"""
Test suite for TanStack/router#6886 - useStore deepEqual fix

This PR adds deepEqual as the comparator for useStore calls in Scripts.tsx
and headContentUtils.tsx to prevent unnecessary re-renders.
"""

import subprocess
import sys
import os

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
    with open(SCRIPTS_FILE, 'r') as f:
        content = f.read()

    # Check for the deepEqual import
    assert "import { deepEqual } from '@tanstack/router-core'" in content, \
        "Scripts.tsx should import deepEqual from @tanstack/router-core"


def test_scripts_use_store_calls_have_deep_equal():
    """Verify all useStore calls in Scripts.tsx have deepEqual as third argument."""
    with open(SCRIPTS_FILE, 'r') as f:
        content = f.read()

    # Count useStore calls - there should be 2 with deepEqual
    use_store_count = content.count('useStore(')
    deep_equal_in_use_store = content.count('useStore(\n    router.stores.activeMatchesSnapshot,')

    # Each useStore call should be followed by 3 arguments including deepEqual
    # Check that deepEqual is used with the assetScripts useStore call
    assert "getAssetScripts,\n    deepEqual," in content, \
        "assetScripts useStore call should have deepEqual as third argument"

    # Check that deepEqual is used with the scripts useStore call
    assert "getScripts,\n    deepEqual," in content, \
        "scripts useStore call should have deepEqual as third argument"


def test_head_content_utils_has_deep_equal_import():
    """Verify headContentUtils.tsx imports deepEqual from @tanstack/router-core."""
    with open(HEAD_UTILS_FILE, 'r') as f:
        content = f.read()

    # Check that deepEqual is imported alongside escapeHtml
    assert "deepEqual, escapeHtml" in content or "escapeHtml, deepEqual" in content, \
        "headContentUtils.tsx should import deepEqual from @tanstack/router-core"


def test_use_tags_use_store_calls_have_deep_equal():
    """Verify useTags hook useStore calls in headContentUtils.tsx have deepEqual."""
    with open(HEAD_UTILS_FILE, 'r') as f:
        content = f.read()

    # There are 5 useStore calls in useTags that should have deepEqual
    # 1. routeMeta useStore
    assert "routeMeta = useStore(" in content and "deepEqual," in content, \
        "routeMeta useStore call should have deepEqual"

    # 2. links useStore
    links_section = content[content.find("const links = useStore("):content.find("const preloadLinks")]
    assert "deepEqual," in links_section, \
        "links useStore call should have deepEqual"

    # 3. preloadLinks useStore
    preload_section = content[content.find("const preloadLinks = useStore("):content.find("const styles")]
    assert "deepEqual," in preload_section, \
        "preloadLinks useStore call should have deepEqual"

    # 4. styles useStore
    styles_section = content[content.find("const styles = useStore("):content.find("const scripts")]
    assert "deepEqual," in styles_section, \
        "styles useStore call should have deepEqual"

    # 5. scripts useStore
    scripts_section = content[content.find("const scripts = useStore("):content.find("return uniqBy")]
    assert "deepEqual," in scripts_section, \
        "scripts useStore call should have deepEqual"


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
    assert result.returncode == 0, \
        f"Unit tests failed:\nstdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-500:]}"


def test_p2p_react_router_types():
    """Repo's TypeScript type check for react-router passes (pass_to_pass).

    Command: pnpm nx run @tanstack/react-router:test:types
    Discovered from: package.json test:types script and CI workflow
    """
    result = run_repo_command(
        ["pnpm", "nx", "run", "@tanstack/react-router:test:types"],
        timeout=120,
    )
    assert result.returncode == 0, \
        f"TypeScript type check failed:\nstdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-500:]}"


def test_p2p_react_router_build():
    """Repo's build for react-router package passes (pass_to_pass).

    Command: pnpm nx run @tanstack/react-router:build
    Discovered from: package.json build script and CI workflow
    """
    result = run_repo_command(
        ["pnpm", "nx", "run", "@tanstack/react-router:build"],
        timeout=120,
    )
    assert result.returncode == 0, \
        f"Build failed:\nstdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-500:]}"


# Note: ESLint test was NOT added as pass_to_pass because it has pre-existing
# failures on the base commit (9 errors, 98 warnings). This is a known issue
# in the repo and not related to the fix being tested.
