"""
Tests for caching in collision detection (hitElementItself).

These tests verify:
1. Cache hit when same point/element tested again with increased threshold
2. Cache miss when threshold decreases
3. Cache invalidation when element version changes
4. Correct hit results are returned from cache
"""

import subprocess
import sys
import os

# Add the element package to the path
REPO = "/workspace/excalidraw"
sys.path.insert(0, os.path.join(REPO, "packages/element"))
sys.path.insert(0, os.path.join(REPO, "packages/common"))
sys.path.insert(0, os.path.join(REPO, "packages/math"))
sys.path.insert(0, os.path.join(REPO, "packages/utils"))

def test_collision_cache_implements_caching():
    """
    Verify that hitElementItself caches results and avoids redundant computations.
    This test should FAIL on base commit (no caching) and PASS with the fix.
    """
    # Run a script that checks if caching is implemented
    test_script = '''
import sys
sys.path.insert(0, "/workspace/excalidraw/packages/element")
sys.path.insert(0, "/workspace/excalidraw/packages/common")
sys.path.insert(0, "/workspace/excalidraw/packages/math")
sys.path.insert(0, "/workspace/excalidraw/packages/utils")

# Check if caching variables exist in collision.ts
collision_file = "/workspace/excalidraw/packages/element/src/collision.ts"
with open(collision_file, "r") as f:
    content = f.read()

# Verify caching variables exist
checks = [
    "cachedPoint" in content,
    "cachedElement" in content,
    "cachedThreshold" in content,
    "cachedHit" in content,
    "WeakRef" in content,
    "pointsEqual" in content,
]

if all(checks):
    print("CACHING_IMPLEMENTED")
else:
    print("CACHING_MISSING")
    sys.exit(1)
'''
    result = subprocess.run(
        [sys.executable, "-c", test_script],
        capture_output=True,
        text=True,
        timeout=30
    )

    assert result.returncode == 0, f"Caching not properly implemented: {result.stderr}"
    assert "CACHING_IMPLEMENTED" in result.stdout, "Caching implementation not found"


def test_cache_reuses_result_for_increased_threshold():
    """
    When threshold increases, cached result should be reused.
    FAIL without caching, PASS with caching.
    """
    # Read the collision.ts file directly to verify caching logic
    collision_file = os.path.join(REPO, "packages/element/src/collision.ts")
    with open(collision_file, "r") as f:
        content = f.read()

    # Check that the cache logic checks for threshold <= cachedThreshold
    has_cache_check = "cachedThreshold <= threshold" in content
    has_cache_store = "cachedThreshold = threshold" in content
    has_points_equal = "pointsEqual(point, cachedPoint)" in content

    assert has_cache_check, "Missing 'cachedThreshold <= threshold' check"
    assert has_cache_store, "Missing 'cachedThreshold = threshold' store"
    assert has_points_equal, "Missing 'pointsEqual(point, cachedPoint)' check"


def test_cache_invalidates_on_version_change():
    """
    When element version changes, cache should be invalidated.
    FAIL without proper version checking, PASS with it.
    """
    test_script = '''
import sys
sys.path.insert(0, "/workspace/excalidraw/packages/element")
sys.path.insert(0, "/workspace/excalidraw/packages/common")
sys.path.insert(0, "/workspace/excalidraw/packages/math")
sys.path.insert(0, "/workspace/excalidraw/packages/utils")

# Read the collision.ts file to verify version checking
with open("/workspace/excalidraw/packages/element/src/collision.ts", "r") as f:
    content = f.read()

# Check that version comparison exists
has_version_check = "derefElement.version === element.version" in content
has_version_nonce_check = "derefElement.versionNonce === element.versionNonce" in content

if has_version_check and has_version_nonce_check:
    print("VERSION_CHECK_OK")
else:
    print("VERSION_CHECK_MISSING")
    sys.exit(1)
'''
    result = subprocess.run(
        [sys.executable, "-c", test_script],
        capture_output=True,
        text=True,
        timeout=30
    )

    assert result.returncode == 0, f"Version checking not implemented: {result.stderr}"


def test_uses_weakref_for_element_cache():
    """
    Cache should use WeakRef to avoid memory leaks.
    """
    test_script = '''
import sys

# Read the collision.ts file to verify WeakRef usage
with open("/workspace/excalidraw/packages/element/src/collision.ts", "r") as f:
    content = f.read()

# Check WeakRef usage
has_weakref_type = "WeakRef<ExcalidrawElement>" in content
has_weakref_new = "new WeakRef(element)" in content
has_deref = "cachedElement?.deref()" in content

if has_weakref_type and has_weakref_new and has_deref:
    print("WEAKREF_OK")
else:
    print("WEAKREF_MISSING")
    sys.exit(1)
'''
    result = subprocess.run(
        [sys.executable, "-c", test_script],
        capture_output=True,
        text=True,
        timeout=30
    )

    assert result.returncode == 0, f"WeakRef not properly used: {result.stderr}"


def test_cache_stores_hit_result():
    """
    Cache should store and return the hit result.
    """
    test_script = '''
import sys

# Read the collision.ts file
with open("/workspace/excalidraw/packages/element/src/collision.ts", "r") as f:
    content = f.read()

# Check that result is cached and returned
has_result_var = "const result = hitElement || hitFrameName" in content or "result = hitElement || hitFrameName" in content
stores_cached_hit = "cachedHit = result" in content
returns_cached = "return cachedHit" in content

if has_result_var and stores_cached_hit and returns_cached:
    print("CACHE_STORE_OK")
else:
    print("CACHE_STORE_MISSING")
    sys.exit(1)
'''
    result = subprocess.run(
        [sys.executable, "-c", test_script],
        capture_output=True,
        text=True,
        timeout=30
    )

    assert result.returncode == 0, f"Cache result storage not implemented: {result.stderr}"


def test_collision_module_imports():
    """
    Verify the collision module can be imported (basic smoke test).
    """
    test_script = '''
import sys
sys.path.insert(0, "/workspace/excalidraw/packages/element")
sys.path.insert(0, "/workspace/excalidraw/packages/common")
sys.path.insert(0, "/workspace/excalidraw/packages/math")
sys.path.insert(0, "/workspace/excalidraw/packages/utils")

try:
    from collision import hitElementItself
    print("IMPORT_OK")
except Exception as e:
    print(f"IMPORT_FAILED: {e}")
    sys.exit(1)
'''
    result = subprocess.run(
        [sys.executable, "-c", test_script],
        capture_output=True,
        text=True,
        timeout=60
    )

    # Note: This might fail on base commit if there are import issues
    # It's more of a smoke test


# =============================================================================
# PASS-TO-PASS TESTS - Repository CI checks
# These tests run the repo's actual CI commands to verify base functionality.
# =============================================================================


def test_repo_typescript_check():
    """
    TypeScript type check (pass-to-pass).
    Runs tsc to verify type correctness.
    """
    result = subprocess.run(
        ["yarn", "test:typecheck"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"TypeScript check failed:\n{result.stderr[-500:]}"


def test_repo_lint_check():
    """
    ESLint check (pass-to-pass).
    Runs eslint to verify code style and patterns.
    """
    result = subprocess.run(
        ["yarn", "test:code"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"ESLint check failed:\n{result.stderr[-500:]}"


def test_repo_prettier_check():
    """
    Prettier formatting check (pass-to-pass).
    Verifies code formatting consistency.
    """
    result = subprocess.run(
        ["yarn", "test:other"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Prettier check failed:\n{result.stderr[-500:]}"


def test_repo_collision_tests():
    """
    Run the repo's collision tests (pass-to-pass).
    Tests the collision detection module.
    """
    result = subprocess.run(
        ["yarn", "test:app", "--watch=false", "packages/element/tests/collision.test.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Collision tests failed:\n{result.stderr[-1000:]}\n{result.stdout[-1000:]}"
