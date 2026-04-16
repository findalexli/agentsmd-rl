#!/usr/bin/env python3
"""Behavioral tests for dagster-docker PR #33330 - skip tests when credentials are not present."""

import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Path constants
REPO = Path("/workspace/dagster")
CONFTEST_PATH = REPO / "python_modules/libraries/dagster-docker/dagster_docker_tests/conftest.py"

# Ensure the conftest directory is in the path so we can import it
CONFTEST_DIR = CONFTEST_PATH.parent
sys.path.insert(0, str(CONFTEST_DIR))


class TestPytestHookExists:
    """Tests that verify the pytest hook exists and is callable."""

    def test_pytest_runtest_setup_function_exists(self):
        """Fail-to-pass: pytest_runtest_setup function must exist and be callable."""
        # Import the conftest module - this will load the hook
        import importlib.util
        spec = importlib.util.spec_from_file_location("conftest", CONFTEST_PATH)
        conftest_module = importlib.util.module_from_spec(spec)

        # The spec should have a loader
        assert spec.loader is not None, "conftest.py cannot be loaded"

        # Load and execute the module
        spec.loader.exec_module(conftest_module)

        # Verify the function exists and is callable
        assert hasattr(conftest_module, "pytest_runtest_setup"), \
            "pytest_runtest_setup function not found in conftest.py"
        assert callable(conftest_module.pytest_runtest_setup), \
            "pytest_runtest_setup is not callable"


class TestIntegrationKeywordFiltering:
    """Tests that verify the hook correctly filters on 'integration' keyword."""

    def _make_mock_item(self, with_integration_keyword):
        """Create a mock test item with or without the integration keyword."""
        item = MagicMock()
        if with_integration_keyword:
            item.keywords = {"integration": MagicMock()}
        else:
            item.keywords = {}
        return item

    def test_integration_keyword_check_exists(self):
        """Fail-to-pass: Must return early (not skip) for non-integration tests."""
        # Import conftest
        import importlib.util
        spec = importlib.util.spec_from_file_location("conftest", CONFTEST_PATH)
        conftest_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(conftest_module)

        # Create a non-integration test item
        non_integration_item = self._make_mock_item(with_integration_keyword=False)

        # With BUILDKITE set but required vars missing, non-integration tests
        # should NOT be skipped (hook should return None, not raise skip)
        with patch.dict(os.environ, {"BUILDKITE": "true"}, clear=False):
            # Set required vars to empty/none to trigger skip condition
            with patch.object(os, 'getenv', lambda k: None if k in [
                "DAGSTER_DOCKER_REPOSITORY", "DAGSTER_DOCKER_IMAGE_TAG",
                "AWS_ACCOUNT_ID", "BUILDKITE_SECRETS_BUCKET"
            ] else os.environ.get(k)):
                result = conftest_module.pytest_runtest_setup(non_integration_item)
                # For non-integration tests, result should be None (not skipped)
                assert result is None, \
                    "Non-integration tests should not be skipped - hook should return None"

    def test_hook_logic_integration_keyword_filter(self):
        """Behavioral: pytest_runtest_setup should skip integration tests with missing creds."""
        # Import conftest
        import importlib.util
        spec = importlib.util.spec_from_file_location("conftest", CONFTEST_PATH)
        conftest_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(conftest_module)

        # Create an integration test item
        integration_item = self._make_mock_item(with_integration_keyword=True)

        # With BUILDKITE set but required vars missing, integration tests SHOULD skip
        with patch.dict(os.environ, {"BUILDKITE": "true"}, clear=False):
            # os.getenv returns None for required vars
            def mock_getenv(key, default=None):
                if key in ["DAGSTER_DOCKER_REPOSITORY", "DAGSTER_DOCKER_IMAGE_TAG",
                           "AWS_ACCOUNT_ID", "BUILDKITE_SECRETS_BUCKET"]:
                    return None
                return os.environ.get(key, default)

            with patch.object(os, 'getenv', mock_getenv):
                with pytest.raises(pytest.skip.Exception) as exc_info:
                    conftest_module.pytest_runtest_setup(integration_item)

                # Verify skip message mentions Docker integration
                assert "Docker integration tests require Buildkite env vars:" in str(exc_info.value)


class TestBuildkiteConditional:
    """Tests that verify the BUILDKITE environment variable controls the check."""

    def test_buildkite_env_check_exists(self):
        """Fail-to-pass: Must not skip tests when BUILDKITE is not set."""
        # Import conftest
        import importlib.util
        spec = importlib.util.spec_from_file_location("conftest", CONFTEST_PATH)
        conftest_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(conftest_module)

        # Create an integration test item
        item = MagicMock()
        item.keywords = {"integration": MagicMock()}

        # Without BUILDKITE set, tests should NOT be skipped even if required vars are missing
        env_without_buildkite = {k: v for k, v in os.environ.items() if k != "BUILDKITE"}
        env_without_buildkite["BUILDKITE"] = ""  # Explicitly empty

        def mock_getenv(key, default=None):
            if key == "BUILDKITE":
                return None  # BUILDKITE not set
            return None  # All other required vars also not set

        with patch.dict(os.environ, env_without_buildkite, clear=True):
            with patch.object(os, 'getenv', mock_getenv):
                result = conftest_module.pytest_runtest_setup(item)
                # Should return None (not skip) when BUILDKITE is not set
                assert result is None, \
                    "Tests should not be skipped when BUILDKITE env var is not set"

    def test_hook_logic_buildkite_conditional(self):
        """Behavioral: BUILDKITE check must gate the credential verification."""
        # Import conftest
        import importlib.util
        spec = importlib.util.spec_from_file_location("conftest", CONFTEST_PATH)
        conftest_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(conftest_module)

        item = MagicMock()
        item.keywords = {"integration": MagicMock()}

        # With BUILDKITE set but required vars missing, should skip
        def mock_getenv(key, default=None):
            if key == "BUILDKITE":
                return "true"  # BUILDKITE is set
            if key in ["DAGSTER_DOCKER_REPOSITORY", "DAGSTER_DOCKER_IMAGE_TAG",
                       "AWS_ACCOUNT_ID", "BUILDKITE_SECRETS_BUCKET"]:
                return None  # Required vars missing
            return os.environ.get(key, default)

        with patch.object(os, 'getenv', mock_getenv):
            with pytest.raises(pytest.skip.Exception):
                conftest_module.pytest_runtest_setup(item)


class TestRequiredEnvVars:
    """Tests that verify all required environment variables are checked."""

    def test_required_env_vars_listed(self):
        """Fail-to-pass: Must check all four required environment variables."""
        # Import conftest
        import importlib.util
        spec = importlib.util.spec_from_file_location("conftest", CONFTEST_PATH)
        conftest_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(conftest_module)

        item = MagicMock()
        item.keywords = {"integration": MagicMock()}

        required_vars = [
            "DAGSTER_DOCKER_REPOSITORY",
            "DAGSTER_DOCKER_IMAGE_TAG",
            "AWS_ACCOUNT_ID",
            "BUILDKITE_SECRETS_BUCKET",
        ]

        # Test that each required var, when missing, causes a skip with that var in message
        for missing_var in required_vars:
            def mock_getenv(key, default=None):
                if key == "BUILDKITE":
                    return "true"
                if key == missing_var:
                    return None  # This one is missing
                return "some_value"  # Others are set
            with patch.object(os, 'getenv', mock_getenv):
                with pytest.raises(pytest.skip.Exception) as exc_info:
                    conftest_module.pytest_runtest_setup(item)
                # The missing var name should appear in the skip message
                assert missing_var in str(exc_info.value), \
                    f"Missing env var {missing_var} should be reported in skip message"

    def test_missing_vars_computed_correctly(self):
        """Fail-to-pass: Missing variables must be correctly identified."""
        # Import conftest
        import importlib.util
        spec = importlib.util.spec_from_file_location("conftest", CONFTEST_PATH)
        conftest_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(conftest_module)

        item = MagicMock()
        item.keywords = {"integration": MagicMock()}

        # Set BUILDKITE but missing DAGSTER_DOCKER_REPOSITORY and AWS_ACCOUNT_ID
        missing = ["DAGSTER_DOCKER_REPOSITORY", "AWS_ACCOUNT_ID"]

        def mock_getenv(key, default=None):
            if key == "BUILDKITE":
                return "true"
            if key in missing:
                return None
            return "value"

        with patch.object(os, 'getenv', mock_getenv):
            with pytest.raises(pytest.skip.Exception) as exc_info:
                conftest_module.pytest_runtest_setup(item)

            msg = str(exc_info.value)
            # Both missing vars should be in the message
            for var in missing:
                assert var in msg, \
                    f"Missing var {var} should appear in skip message"

    def test_pytest_skip_called_with_missing_vars(self):
        """Fail-to-pass: Must call pytest.skip when env vars are missing."""
        # This is implicitly tested by the with pytest.raises(pytest.skip.Exception) tests above
        # But we make it explicit here
        import importlib.util
        spec = importlib.util.spec_from_file_location("conftest", CONFTEST_PATH)
        conftest_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(conftest_module)

        item = MagicMock()
        item.keywords = {"integration": MagicMock()}

        def mock_getenv(key, default=None):
            if key == "BUILDKITE":
                return "true"
            return None  # All required vars missing

        with patch.object(os, 'getenv', mock_getenv):
            with pytest.raises(pytest.skip.Exception):
                conftest_module.pytest_runtest_setup(item)


class TestSkipMessage:
    """Tests that verify the skip message format."""

    def test_skip_message_includes_missing_vars(self):
        """Behavioral: Skip message must include the list of missing environment variables."""
        import importlib.util
        spec = importlib.util.spec_from_file_location("conftest", CONFTEST_PATH)
        conftest_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(conftest_module)

        item = MagicMock()
        item.keywords = {"integration": MagicMock()}

        missing = ["DAGSTER_DOCKER_REPOSITORY", "BUILDKITE_SECRETS_BUCKET"]

        def mock_getenv(key, default=None):
            if key == "BUILDKITE":
                return "true"
            if key in missing:
                return None
            return "present"

        with patch.object(os, 'getenv', mock_getenv):
            with pytest.raises(pytest.skip.Exception) as exc_info:
                conftest_module.pytest_runtest_setup(item)

            msg = str(exc_info.value)
            # Message should contain the header
            assert "Docker integration tests require Buildkite env vars:" in msg, \
                "Skip message must include the required header text"
            # Message should list the missing vars
            for var in missing:
                assert var in msg, f"Missing var {var} not in skip message: {msg}"


class TestSyntaxAndLoading:
    """Pass-to-pass tests that verify the conftest can be loaded."""

    def test_conftest_syntax_valid(self):
        """Pass-to-pass: conftest.py must have valid Python syntax."""
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(CONFTEST_PATH)],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert result.returncode == 0, \
            f"conftest.py has syntax errors: {result.stderr}"

    def test_conftest_pytest_can_load(self):
        """Pass-to-pass: pytest can collect tests from the dagster-docker test dir."""
        # Run pytest in collect-only mode to verify conftest loads
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only",
             str(REPO / "python_modules/libraries/dagster-docker/dagster_docker_tests"),
             "-q"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(REPO),
            env={**os.environ, "BUILDKITE": ""}
        )
        # pytest should be able to collect tests without crashing
        # We just check that conftest doesn't cause import errors
        assert "conftest.py" not in result.stderr or result.returncode == 0 or "error" not in result.stderr.lower(), \
            f"conftest.py failed to load: {result.stderr[:500]}"


class TestRepoQuality:
    """Pass-to-pass tests for repo-level quality checks."""

    def test_repo_ruff_check(self):
        """Repo CI: ruff check passes on dagster-docker tests."""
        # Install the required ruff version first
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "ruff==0.11.5"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        result = subprocess.run(
            ["ruff", "check", "."],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(REPO),
        )
        assert result.returncode == 0, f"ruff check failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"

    def test_repo_ruff_format(self):
        """Repo CI: ruff format check passes on repo."""
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "ruff==0.11.5"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        result = subprocess.run(
            ["ruff", "format", "--check", "."],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(REPO),
        )
        assert result.returncode == 0, f"ruff format check failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"

    def test_dagster_docker_conftest_syntax(self):
        """Repo CI: dagster-docker conftest.py has valid Python syntax."""
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(CONFTEST_PATH)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"conftest.py syntax error:\n{result.stderr}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
