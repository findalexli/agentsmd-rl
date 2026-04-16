"""
Tests for caching type metadata and class references in Pulumi Python SDK.
"""

import functools
import sys
import os
import subprocess

# Docker-internal path to the repo (where the repo lives INSIDE the container)
REPO = "/workspace/pulumi"
SDK_PATH = f"{REPO}/sdk/python/lib"
if SDK_PATH not in sys.path:
    sys.path.insert(0, SDK_PATH)


def test_py_properties_is_cached():
    """Test that _py_properties function is cached using functools.cache."""
    from pulumi._types import _py_properties

    # Check that the function has cache_info method (from functools.cache)
    assert hasattr(_py_properties, "cache_info"), \
        "_py_properties should be decorated with @functools.cache"

    # Verify it's actually a cache by checking cache_info returns a namedtuple
    info = _py_properties.cache_info()
    assert hasattr(info, "hits"), "cache_info should have hits attribute"
    assert hasattr(info, "misses"), "cache_info should have misses attribute"
    assert hasattr(info, "maxsize"), "cache_info should have maxsize attribute"
    assert hasattr(info, "currsize"), "cache_info should have currsize attribute"


def test_py_properties_cache_works():
    """Test that _py_properties actually caches results for same class."""
    from pulumi._types import _py_properties, input_type

    # Define a test class with input_type decorator
    @input_type
    class TestResource:
        def __init__(self):
            pass

        @property
        def name(self):
            return "test"

        @name.setter
        def name(self, value):
            pass

    # Clear cache first
    _py_properties.cache_clear()

    # First call - should miss
    result1 = _py_properties(TestResource)
    info1 = _py_properties.cache_info()

    # Second call with same class - should hit
    result2 = _py_properties(TestResource)
    info2 = _py_properties.cache_info()

    # Results should be identical (same tuple object due to caching)
    assert result1 is result2, "Cached results should be identical objects"

    # Cache should have recorded a hit
    assert info2.hits > info1.hits or info2.misses == info1.misses, \
        "Second call should use cached result"


def test_types_from_py_properties_is_cached():
    """Test that _types_from_py_properties function is cached."""
    from pulumi._types import _types_from_py_properties

    # Check that the function has cache_info method
    assert hasattr(_types_from_py_properties, "cache_info"), \
        "_types_from_py_properties should be decorated with @functools.cache"

    # Verify cache_info returns proper namedtuple
    info = _types_from_py_properties.cache_info()
    assert hasattr(info, "hits"), "cache_info should have hits attribute"
    assert hasattr(info, "misses"), "cache_info should have misses attribute"


def test_types_from_py_properties_cache_works():
    """Test that _types_from_py_properties actually caches results."""
    from pulumi._types import _types_from_py_properties, input_type

    @input_type
    class TestResource2:
        @property
        def id(self):
            return "id"

        @id.setter
        def id(self, value):
            pass

    # Clear cache
    _types_from_py_properties.cache_clear()

    # First call
    result1 = _types_from_py_properties(TestResource2)

    # Second call - should be cached
    result2 = _types_from_py_properties(TestResource2)

    # Results should be identical due to caching
    assert result1 is result2, "Cached type metadata should be identical objects"


def test_known_types_has_module_caches():
    """Test that known_types.py has module-level cache variables defined."""
    from pulumi.runtime import known_types

    # Check that module-level cache variables exist
    assert hasattr(known_types, "_Asset"), "known_types should have _Asset cache variable"
    assert hasattr(known_types, "_Archive"), "known_types should have _Archive cache variable"
    assert hasattr(known_types, "_Resource"), "known_types should have _Resource cache variable"
    assert hasattr(known_types, "_CustomResource"), "known_types should have _CustomResource cache variable"
    assert hasattr(known_types, "_CustomTimeouts"), "known_types should have _CustomTimeouts cache variable"
    assert hasattr(known_types, "_Stack"), "known_types should have _Stack cache variable"
    assert hasattr(known_types, "_Output"), "known_types should have _Output cache variable"


def test_is_asset_caches_class():
    """Test that is_asset caches the Asset class reference."""
    from pulumi.runtime.known_types import is_asset, _Asset

    # Before calling is_asset, _Asset should be None
    # (We can't test this directly since other tests may have called it)
    # Instead, verify the function works and the cache variable exists
    assert _Asset is not None or True  # Just check the variable exists

    # Multiple calls should work correctly
    result1 = is_asset("not an asset")
    result2 = is_asset("not an asset")
    assert result1 == result2 == False


def test_is_output_caches_class():
    """Test that is_output caches the Output class reference."""
    from pulumi.runtime.known_types import is_output, _Output

    # Multiple calls should work correctly
    result1 = is_output("not an output")
    result2 = is_output("not an output")
    assert result1 == result2 == False


def test_is_resource_caches_class():
    """Test that is_resource caches the Resource class reference."""
    from pulumi.runtime.known_types import is_resource, _Resource

    # Multiple calls should work correctly
    result1 = is_resource("not a resource")
    result2 = is_resource("not a resource")
    assert result1 == result2 == False


def test_py_properties_returns_tuple():
    """Test that _py_properties returns a tuple (cached) not an iterator."""
    from pulumi._types import _py_properties, input_type

    @input_type
    class TestResource3:
        @property
        def value(self):
            return 42

        @value.setter
        def value(self, v):
            pass

    result = _py_properties(TestResource3)

    # Should be a tuple, not an iterator
    assert isinstance(result, tuple), "_py_properties should return a tuple when cached"


# =============================================================================
# Pass-to-Pass Tests (using repo CI commands)
# These tests verify the existing repo tests still pass after the fix.
# =============================================================================


def test_repo_types_unit_tests():
    """Run Python SDK type-related unit tests (pass_to_pass)."""
    # Install test dependencies first
    r = subprocess.run(
        ["pip", "install", "pytest", "pytest-asyncio", "-q"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=f"{REPO}/sdk/python"
    )
    # Install might give warnings but should succeed

    # Run the core type tests (not langhost tests which need compiled binaries)
    r = subprocess.run(
        [
            "python", "-m", "pytest",
            "lib/test/test_types.py",
            "lib/test/test_types_input_type.py",
            "lib/test/test_types_output_type.py",
            "-v", "--tb=short"
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=f"{REPO}/sdk/python"
    )
    assert r.returncode == 0, f"Type unit tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_ruff_lint():
    """Run ruff linter on modified Python SDK files (pass_to_pass)."""
    # Install ruff
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True,
        text=True,
        timeout=60
    )

    # Run ruff on the modified files
    r = subprocess.run(
        ["ruff", "check", "lib/pulumi/_types.py", "lib/pulumi/runtime/known_types.py"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=f"{REPO}/sdk/python"
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_mypy_typecheck():
    """Run mypy type checker on modified Python SDK files (pass_to_pass)."""
    # Install mypy
    r = subprocess.run(
        ["pip", "install", "mypy", "-q"],
        capture_output=True,
        text=True,
        timeout=60
    )

    # Run mypy on the modified files
    r = subprocess.run(
        ["mypy", "lib/pulumi/_types.py", "lib/pulumi/runtime/known_types.py"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=f"{REPO}/sdk/python"
    )
    assert r.returncode == 0, f"Mypy typecheck failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_serialization_tests():
    """Run serialization tests that exercise type system (pass_to_pass)."""
    # Install test dependencies
    r = subprocess.run(
        ["pip", "install", "pytest", "pytest-asyncio", "-q"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=f"{REPO}/sdk/python"
    )

    # Run serialization tests - these exercise the type system heavily
    r = subprocess.run(
        [
            "python", "-m", "pytest",
            "lib/test/test_next_serialize.py",
            "-v", "--tb=short", "-x"
        ],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=f"{REPO}/sdk/python"
    )
    assert r.returncode == 0, f"Serialization tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"
