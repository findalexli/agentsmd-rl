"""
Test_outputs.py - Benchmark tests for mlflow#22369

Tests verify that _lookup_model_info returns correct model info from bundled
providers without making network requests when no provider is given.
"""

import subprocess
import sys
from unittest import mock

import pytest

# Path to mlflow repo
REPO = "/workspace/mlflow"


class TestLookupModelInfoBundledBehavior:
    """
    Behavioral tests that _lookup_model_info returns correct bundled model info
    WITHOUT making network requests when no custom_llm_provider is given.

    The bug: When _lookup_model_info was called without a provider, it used
    _load_provider() which calls _fetch_remote_provider() (network requests).
    For unknown models, this caused O(N) network latency.

    The fix: When no provider is given, use _load_bundled_provider() which only
    reads local files, avoiding network latency.
    """

    def test_lookup_model_info_without_provider_returns_bundled_info(self):
        """
        Verify _lookup_model_info(model) without provider returns bundled model info
        from local files (no network requests).

        Behavioral test: verifies the result is correct AND no network is made.
        """
        sys.path.insert(0, REPO)
        from mlflow.utils.providers import _lookup_model_info

        # Mock _fetch_remote_provider to track if network calls are made
        # If _load_bundled_provider is used (correct fix), this should NOT be called
        with mock.patch(
            "mlflow.utils.providers._fetch_remote_provider",
            return_value=None,  # Return None to simulate network failure
        ) as mock_fetch:
            result = _lookup_model_info("gpt-4")

        # Verify _fetch_remote_provider was NOT called (no network requests)
        assert mock_fetch.call_count == 0, (
            f"_fetch_remote_provider was called {mock_fetch.call_count} times. "
            "When no provider is given, bundled providers should be used WITHOUT "
            "making network requests."
        )

        # Verify we got a valid result - the bundled providers should have test-model
        # The mock ensures we didn't go through _load_provider which would call _fetch_remote_provider
        assert result is not None, (
            "_lookup_model_info returned None even though bundled providers "
            "should contain the model info. The function should use "
            "_load_bundled_provider to find model info without network."
        )

    def test_lookup_model_info_without_provider_avoids_network(self):
        """
        Verify _lookup_model_info(model) does NOT call _fetch_remote_provider
        (i.e., no network requests) when no provider is given.

        This is a direct behavioral check: network should not be touched.
        """
        sys.path.insert(0, REPO)
        from mlflow.utils.providers import _lookup_model_info, _list_provider_names

        provider_names = _list_provider_names()
        assert len(provider_names) > 0, "Should have some bundled providers"

        with mock.patch(
            "mlflow.utils.providers._fetch_remote_provider",
            return_value=None,
        ) as mock_fetch:
            # Call with a model that exists in bundled providers
            result = _lookup_model_info("gpt-4")

        # The key behavioral assertion: NO network calls when provider is not specified
        assert mock_fetch.call_count == 0, (
            f"Expected 0 network calls, but _fetch_remote_provider was called "
            f"{mock_fetch.call_count} times. The fix should use "
            f"_load_bundled_provider (no network) not _load_provider (network)."
        )

    def test_lookup_model_info_with_provider_returns_model_info(self):
        """
        Verify _lookup_model_info(model, provider) with provider returns model info.

        This tests the fast path when a provider is specified.
        """
        sys.path.insert(0, REPO)
        from mlflow.utils.providers import _lookup_model_info

        result = _lookup_model_info("gpt-4", "openai")

        # When provider is specified, should return model info if model exists
        # The result might be None if model doesn't exist, but shouldn't error
        assert result is None or isinstance(result, dict), (
            f"Expected dict or None, got {type(result)}"
        )


class TestRepoP2P:
    """
    Pass-to-pass tests: repo's existing test suite should pass after fix.
    These verify the fix doesn't break existing functionality.
    """

    def test_repo_lint_providers_and_tracing_utils(self):
        """Run ruff linter on the two modified source files (pass_to_pass)."""
        # Install ruff==0.15.5 (pinned version used by mlflow's CI)
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "ruff==0.15.5", "-q"],
            capture_output=True, timeout=120,
        )
        r = subprocess.run(
            [sys.executable, "-m", "ruff", "check",
             f"{REPO}/mlflow/utils/providers.py",
             f"{REPO}/mlflow/tracing/utils/__init__.py"],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        assert r.returncode == 0, f"Ruff check failed:\n{r.stderr[-500:]}"

    def test_repo_test_providers(self):
        """Run the repo's own test_providers.py tests (pass_to_pass)."""
        # Install litellm for tests/tracing/utils/test_utils.py (required by tracing tests)
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "litellm", "-q"],
            capture_output=True, timeout=300,
        )
        result = subprocess.run(
            [sys.executable, "-m", "pytest",
             f"{REPO}/tests/utils/test_providers.py",
             "-v", "--tb=short", "-x"],
            capture_output=True,
            text=True,
            timeout=300,
        )
        # Print output for debugging
        if result.returncode != 0:
            print(f"STDOUT:\n{result.stdout[-2000:]}")
            print(f"STDERR:\n{result.stderr[-1000:]}")
        assert result.returncode == 0, (
            f"Repo tests failed:\n{result.stderr[-1000:]}"
        )

    def test_repo_tracing_cost_aggregation(self):
        """Run repo's tracing cost aggregation tests (pass_to_pass)."""
        # litellm must be installed for tests/tracing/utils/test_utils.py
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "litellm", "-q"],
            capture_output=True, timeout=300,
        )
        result = subprocess.run(
            [sys.executable, "-m", "pytest",
             f"{REPO}/tests/tracing/utils/test_utils.py",
             "-k", "aggregate_cost",
             "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode != 0:
            print(f"STDOUT:\n{result.stdout[-2000:]}")
            print(f"STDERR:\n{result.stderr[-1000:]}")
        assert result.returncode == 0, (
            f"Tracing cost aggregation tests failed:\n{result.stderr[-1000:]}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])