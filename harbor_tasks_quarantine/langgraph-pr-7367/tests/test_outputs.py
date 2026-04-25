"""Test that ensure_config no longer propagates config items to metadata."""

import sys
import subprocess

REPO = "/workspace/langgraph/libs/langgraph"

def test_config_items_not_propagated_to_metadata():
    """
    Config items should NOT be automatically added to metadata.
    This is a fail-to-pass test: it fails on base, passes after fix.
    """
    # Import the function under test
    sys.path.insert(0, REPO)
    from langgraph._internal._config import ensure_config

    config = {
        "configurable": {
            "a-key": "foo",            # contains "key"
            "somesecretval": "bar",    # contains "secret"
            "sometoken": "thetoken",   # contains "token"
            "__dontinclude": "bar",    # starts with __
            "includeme": "hi",         # should NOT be in metadata after fix
            "andme": 42,               # should NOT be in metadata after fix
            "nested": {"foo": "bar"},  # not primitive
            "nooverride": -2,          # already in metadata
        },
        "metadata": {"nooverride": 18},
    }

    merged = ensure_config(config)
    metadata = merged["metadata"]

    # After the fix, only original metadata keys remain
    # Config items should NOT be propagated to metadata
    expected = {"nooverride"}
    assert metadata.keys() == expected, (
        f"Expected metadata keys {expected}, got {set(metadata.keys())}. "
        "Config items are still being propagated to metadata."
    )
    assert metadata["nooverride"] == 18, "Metadata value should not be overridden"


def test_config_items_still_in_configurable():
    """
    Config items should remain in the configurable dict.
    This is a fail-to-pass test: it fails on base, passes after fix.
    """
    sys.path.insert(0, REPO)
    from langgraph._internal._config import ensure_config
    from langgraph._internal._constants import CONF

    config = {
        "configurable": {
            "includeme": "hi",
            "andme": 42,
        },
        "metadata": {"existing": "value"},
    }

    merged = ensure_config(config)

    # Config items should still be in configurable
    assert CONF in merged, "configurable should be in merged config"
    assert merged[CONF]["includeme"] == "hi", "includeme should be in configurable"
    assert merged[CONF]["andme"] == 42, "andme should be in configurable"

    # But NOT in metadata
    metadata = merged["metadata"]
    assert "includeme" not in metadata, "includeme should NOT be in metadata"
    assert "andme" not in metadata, "andme should NOT be in metadata"
    assert set(metadata.keys()) == {"existing"}, "Only existing metadata keys should remain"


def test_sensitive_keys_not_in_metadata():
    """
    Keys containing sensitive terms should NOT be in metadata (and no keys at all after fix).
    This test verifies the fix doesn't accidentally expose sensitive values.
    """
    sys.path.insert(0, REPO)
    from langgraph._internal._config import ensure_config

    config = {
        "configurable": {
            "api_key": "secret123",      # contains "key"
            "auth_token": "token456",    # contains "token"
            "password_hash": "hash789",  # contains "password"
            "my_secret": "shh",           # contains "secret"
            "auth_header": "Bearer",     # contains "auth"
        },
        "metadata": {},
    }

    merged = ensure_config(config)
    metadata = merged["metadata"]

    # After fix, no config items in metadata at all
    assert len(metadata) == 0, (
        f"Expected empty metadata, got {dict(metadata)}. "
        "Config items (including sensitive ones) should NOT be in metadata."
    )


def test_varied_config_types():
    """
    Test with varied config values to ensure robustness.
    Uses multiple input variations.
    """
    sys.path.insert(0, REPO)
    from langgraph._internal._config import ensure_config

    test_cases = [
        # (config, expected_metadata_keys)
        (
            {"configurable": {"foo": "bar"}, "metadata": {}},
            set(),  # No keys expected after fix
        ),
        (
            {"configurable": {"foo": "bar"}, "metadata": {"existing": 1}},
            {"existing"},  # Only existing key
        ),
        (
            {"configurable": {"a": 1, "b": 2, "c": 3}, "metadata": {"d": 4}},
            {"d"},  # Only 'd' from metadata, not a/b/c from configurable
        ),
        (
            {"configurable": {"key": "value"}, "metadata": {"user": "alice"}},
            {"user"},  # Only user from metadata
        ),
    ]

    for config, expected_keys in test_cases:
        merged = ensure_config(config)
        metadata = merged["metadata"]
        actual_keys = set(metadata.keys())
        assert actual_keys == expected_keys, (
            f"Expected metadata keys {expected_keys}, got {actual_keys} "
            f"for config {config}"
        )


def test_repo_test_suite():
    """
    Verify the repo's test expectation is updated correctly.
    This test directly imports and runs the test logic.
    """
    sys.path.insert(0, REPO)
    from langgraph._internal._config import ensure_config

    # This is the exact test from test_utils.py
    config = {
        "configurable": {
            "a-key": "foo",
            "somesecretval": "bar",
            "sometoken": "thetoken",
            "__dontinclude": "bar",
            "includeme": "hi",
            "andme": 42,
            "nested": {"foo": "bar"},
            "nooverride": -2,
        },
        "metadata": {"nooverride": 18},
    }
    expected = {"nooverride"}  # Updated expectation: only metadata keys
    merged = ensure_config(config)
    metadata = merged["metadata"]
    assert metadata.keys() == expected, (
        f"Expected metadata keys {expected}, got {set(metadata.keys())}"
    )


# =============================================================================
# Pass-to-Pass Tests - Repo CI Tests (run on base commit, should pass)
# =============================================================================

def test_p2p_repo_unit_tests():
    """Repo's unit tests for test_utils.py pass (pass_to_pass)."""
    r = subprocess.run(
        ["uv", "run", "pytest", "tests/test_utils.py", "-x"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-500:]}"


def test_p2p_repo_config_tests():
    """Repo's config async tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["uv", "run", "pytest", "tests/test_config_async.py", "-x"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Config tests failed:\n{r.stderr[-500:]}"


def test_p2p_repo_channel_tests():
    """Repo's channel tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["uv", "run", "pytest", "tests/test_channels.py", "-x"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Channel tests failed:\n{r.stderr[-500:]}"


def test_p2p_repo_lint():
    """Repo's ruff linter passes on langgraph package (pass_to_pass)."""
    r = subprocess.run(
        ["uv", "run", "ruff", "check", "langgraph/"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}"


def test_p2p_repo_typecheck():
    """Repo's mypy typecheck on _config.py passes (pass_to_pass)."""
    r = subprocess.run(
        ["uv", "run", "mypy", "langgraph/_internal/_config.py", "--cache-dir", ".mypy_cache"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}"


def test_p2p_repo_format():
    """Repo's ruff format check on _config.py passes (pass_to_pass)."""
    r = subprocess.run(
        ["uv", "run", "ruff", "format", "--check", "langgraph/_internal/_config.py"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stderr[-500:]}"


def test_p2p_configurable_metadata_test():
    """Repo's specific test_configurable_metadata test passes (pass_to_pass).

    Note: This test passes on base because the old behavior (propagating config
    items to metadata) is still in place. After the fix, this test expectation
    changes, making this a fail_to_pass test, but we verify the original
    test runs successfully as part of p2p validation.
    """
    r = subprocess.run(
        ["uv", "run", "pytest", "tests/test_utils.py::test_configurable_metadata", "-x"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"test_configurable_metadata failed:\n{r.stderr[-500:]}"

