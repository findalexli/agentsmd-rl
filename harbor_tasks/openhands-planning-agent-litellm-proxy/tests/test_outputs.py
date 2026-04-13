"""Test that _configure_llm correctly handles litellm_proxy/ model prefix.

This test validates the fix for: planning agent auth error due to missing base_url.
When a sub-conversation (planning agent) inherits llm_model from the parent,
the SDK has already transformed "openhands/model" to "litellm_proxy/model".
The _configure_llm method must check for both prefixes to set base_url correctly.
"""

import os
import sys
from unittest.mock import Mock
import pytest

# Allow short context windows for testing
os.environ['ALLOW_SHORT_CONTEXT_WINDOWS'] = 'true'

# Add repo to path
REPO = '/workspace/openhands'
sys.path.insert(0, REPO)

from openhands.app_server.app_conversation.live_status_app_conversation_service import (
    LiveStatusAppConversationService,
)
from openhands.app_server.user.user_context import UserContext


class TestConfigureLLM:
    """Tests for _configure_llm method handling of model prefixes."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create mock dependencies
        self.mock_user_context = Mock(spec=UserContext)
        self.mock_user_context.user_auth = Mock()

        # Create service instance with explicit provider base URL
        self.service = LiveStatusAppConversationService(
            init_git_in_empty_workspace=True,
            user_context=self.mock_user_context,
            app_conversation_info_service=Mock(),
            app_conversation_start_task_service=Mock(),
            event_callback_service=Mock(),
            event_service=Mock(),
            sandbox_service=Mock(),
            sandbox_spec_service=Mock(),
            jwt_service=Mock(),
            pending_message_service=Mock(),
            sandbox_startup_timeout=30,
            sandbox_startup_poll_frequency=1,
            max_num_conversations_per_sandbox=20,
            httpx_client=Mock(),
            web_url='https://test.example.com',
            openhands_provider_base_url='https://provider.example.com',
            access_token_hard_timeout=None,
            app_mode='test',
        )

        # Mock user info
        self.mock_user = Mock()
        self.mock_user.id = 'test_user_123'
        self.mock_user.llm_model = 'gpt-4'
        self.mock_user.llm_api_key = 'test_api_key'
        self.mock_user.llm_base_url = None  # Will be set per-test

    def test_litellm_proxy_model_uses_provider_base_url(self):
        """litellm_proxy/* model falls back to provider base URL.

        This is the core bug fix - sub-conversations inherit SDK-transformed
        model names like 'litellm_proxy/model' and should get the provider
        base_url just like 'openhands/model' does.
        """
        # Arrange - user has no base_url, simulating inherited model
        self.mock_user.llm_base_url = None
        model = 'litellm_proxy/minimax-2.5'

        # Act
        llm = self.service._configure_llm(self.mock_user, model)

        # Assert - should use provider base_url
        assert llm.base_url == 'https://provider.example.com', \
            f"Expected 'https://provider.example.com', got '{llm.base_url}'"

    def test_litellm_proxy_model_prefers_user_base_url(self):
        """litellm_proxy/* model uses user.llm_base_url when provided."""
        # Arrange - user provides their own base_url
        self.mock_user.llm_base_url = 'https://user-custom.example.com'
        model = 'litellm_proxy/minimax-2.5'

        # Act
        llm = self.service._configure_llm(self.mock_user, model)

        # Assert - should prefer user's base_url
        assert llm.base_url == 'https://user-custom.example.com', \
            f"Expected 'https://user-custom.example.com', got '{llm.base_url}'"

    def test_openhands_model_uses_provider_base_url(self):
        """openhands/* model falls back to provider base URL (existing behavior)."""
        # Arrange
        self.mock_user.llm_base_url = None
        model = 'openhands/o3'

        # Act
        llm = self.service._configure_llm(self.mock_user, model)

        # Assert - should use provider base_url
        assert llm.base_url == 'https://provider.example.com', \
            f"Expected 'https://provider.example.com', got '{llm.base_url}'"

    def test_openhands_model_prefers_user_base_url(self):
        """openhands/* model uses user.llm_base_url when provided."""
        # Arrange
        self.mock_user.llm_base_url = 'https://user-custom.example.com'
        model = 'openhands/o3'

        # Act
        llm = self.service._configure_llm(self.mock_user, model)

        # Assert - should prefer user's base_url
        assert llm.base_url == 'https://user-custom.example.com', \
            f"Expected 'https://user-custom.example.com', got '{llm.base_url}'"

    def test_regular_model_ignores_provider_base_url(self):
        """Non-openhands/non-litellm_proxy model ignores provider base URL."""
        # Arrange
        self.mock_user.llm_model = 'gpt-4'
        self.mock_user.llm_base_url = 'https://user-openai.example.com'

        # Act - pass None to use user's default model
        llm = self.service._configure_llm(self.mock_user, None)

        # Assert - should use user's base_url, not provider
        assert llm.base_url == 'https://user-openai.example.com', \
            f"Expected 'https://user-openai.example.com', got '{llm.base_url}'"

    def test_litellm_proxy_various_models(self):
        """litellm_proxy/ prefix works for various model names."""
        test_models = [
            'litellm_proxy/minimax-2.5',
            'litellm_proxy/gpt-4',
            'litellm_proxy/claude-3-opus',
            'litellm_proxy/custom-model',
        ]

        for model in test_models:
            self.mock_user.llm_base_url = None
            llm = self.service._configure_llm(self.mock_user, model)
            assert llm.base_url == 'https://provider.example.com', \
                f"Model '{model}': expected provider base_url, got '{llm.base_url}'"


class TestRepoUnitTests:
    """Run existing repo unit tests for _configure_llm."""

    def test_repo_configure_llm_tests(self):
        """Existing repo unit tests for configure_llm should pass."""
        import subprocess
        result = subprocess.run(
            [
                'python', '-m', 'pytest',
                'tests/unit/app_server/test_live_status_app_conversation_service.py',
                '-k', 'configure_llm',
                '-v', '--tb=short'
            ],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120
        )
        # Print output for debugging
        print(result.stdout)
        print(result.stderr)
        assert result.returncode == 0, f"Repo unit tests failed:\n{result.stderr}"


class TestPassToPassRepoTests:
    """Pass-to-pass tests: Repo CI tests that should pass on both base and fixed code."""

    def test_repo_app_server_unit_tests(self):
        """Repo's app_server unit tests pass (pass_to_pass)."""
        import subprocess
        result = subprocess.run(
            [
                'python', '-m', 'pytest',
                'tests/unit/app_server/',
                '-v', '--tb=short', '--forked', '-n', '0'
            ],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=300
        )
        print(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
        print(result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr)
        assert result.returncode == 0, f"App server unit tests failed:\n{result.stderr[-500:]}"

    def test_repo_target_file_unit_tests(self):
        """Repo unit tests for the modified file pass (pass_to_pass)."""
        import subprocess
        result = subprocess.run(
            [
                'python', '-m', 'pytest',
                'tests/unit/app_server/test_live_status_app_conversation_service.py',
                '-v', '--tb=short', '--forked', '-n', '0'
            ],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=300
        )
        print(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
        print(result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr)
        assert result.returncode == 0, f"Target file unit tests failed:\n{result.stderr[-500:]}"

    def test_repo_ruff_format(self):
        """Repo code formatting passes (pass_to_pass).

        Verifies the codebase follows the project's formatting standards
        as enforced in CI via ruff format --check.
        """
        import subprocess
        # Ensure ruff is available
        subprocess.run(['pip', 'install', '-q', 'ruff'], check=True, capture_output=True)
        result = subprocess.run(
            ['ruff', 'format', '--check', '--config', 'dev_config/python/ruff.toml', 'openhands/'],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120
        )
        print(result.stdout[-1000:] if len(result.stdout) > 1000 else result.stdout)
        print(result.stderr[-500:] if len(result.stderr) > 500 else result.stderr)
        assert result.returncode == 0, f"Ruff format check failed:\n{result.stderr[-500:]}"

    def test_repo_unit_tests_broad(self):
        """Broader repo unit tests pass (pass_to_pass).

        Runs a broader set of unit tests to ensure no regression beyond
        the immediate app_server tests. Excludes heavy runtime/integration tests.
        """
        import subprocess
        # Run unit tests but exclude runtime tests (those need Docker/special setup)
        result = subprocess.run(
            [
                'python', '-m', 'pytest',
                'tests/unit',
                '--ignore=tests/unit/runtime', '--ignore=tests/unit/frontend', '--ignore=tests/unit/mcp',
                '-v', '--tb=short', '--forked', '-n', '0', '-x'
            ],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=600
        )
        print(result.stdout[-3000:] if len(result.stdout) > 3000 else result.stdout)
        print(result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr)
        assert result.returncode == 0, f"Broad unit tests failed:\n{result.stderr[-500:]}"




class TestAdditionalPassToPass:
    """Additional pass-to-pass tests for CI/CD commands."""

    def test_repo_ruff_lint_app_conversation(self):
        """Ruff linting passes on app_conversation module (pass_to_pass).

        Verifies the modified code follows linting standards.
        Scoped to app_conversation directory with ASYNC240 ignored
        (pre-existing issue in repo base commit).
        """
        import subprocess
        import sys
        REPO = '/workspace/openhands'
        sys.path.insert(0, REPO)
        subprocess.run(['pip', 'install', '-q', 'ruff'], check=True, capture_output=True)
        result = subprocess.run(
            ['ruff', 'check', '--config', 'dev_config/python/ruff.toml', '--ignore', 'ASYNC240', 'openhands/app_server/app_conversation/'],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120
        )
        print(result.stdout[-1000:] if len(result.stdout) > 1000 else result.stdout)
        print(result.stderr[-500:] if len(result.stderr) > 500 else result.stderr)
        assert result.returncode == 0, f"Ruff lint check failed:\n{result.stderr[-500:]}"

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
