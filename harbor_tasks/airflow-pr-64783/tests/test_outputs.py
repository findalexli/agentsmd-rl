"""Tests for the install_airflow_and_providers.py fix.

This verifies that when installing pre-release versions, the `--exclude-newer`
flag is added with a current timestamp to prevent unintended package upgrades.
"""

import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from types import ModuleType
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

REPO = Path("/workspace/airflow")
TARGET_FILE = REPO / "scripts" / "in_container" / "install_airflow_and_providers.py"

# Add the scripts/in_container directory to the path
REPO_ROOT = Path("/workspace/airflow")
SCRIPTS_DIR = REPO_ROOT / "scripts" / "in_container"
sys.path.insert(0, str(SCRIPTS_DIR))


def load_module_with_mocks() -> ModuleType:
    """Load the module with necessary mocks for dependencies."""
    # Create mock for in_container_utils
    mock_utils = MagicMock()
    mock_utils.AIRFLOW_ROOT_PATH = Path("/workspace/airflow")
    mock_utils.AIRFLOW_CORE_SOURCES_PATH = Path("/workspace/airflow/airflow-core/src")
    mock_utils.AIRFLOW_DIST_PATH = Path("/workspace/airflow/dist")
    mock_utils.click = MagicMock()
    mock_utils.console = MagicMock()
    mock_utils.run_command = MagicMock(return_value=MagicMock(returncode=0))

    sys.modules["in_container_utils"] = mock_utils

    # Load the module fresh
    if "install_airflow_and_providers" in sys.modules:
        del sys.modules["install_airflow_and_providers"]

    import install_airflow_and_providers as iap

    return iap


@pytest.fixture
def iap_module():
    """Fixture to provide the install_airflow_and_providers module with mocks."""
    return load_module_with_mocks()


class TestPreReleaseExcludeNewer:
    """Test that --exclude-newer is added when pre_release is True."""

    def test_install_together_adds_exclude_newer_with_timestamp(self, iap_module):
        """F2P: When pre_release=True, command must include --pre and --exclude-newer with timestamp."""
        # Create installation spec with pre_release=True
        spec = iap_module.InstallationSpec(
            airflow_distribution=None,
            airflow_core_distribution=None,
            airflow_task_sdk_distribution=None,
            airflow_ctl_distribution=None,
            provider_distributions=[],
            pre_release=True,
            airflow_constraints_location=None,
            provider_constraints_location=None,
            airflow_ctl_constraints_location=None,
            compile_ui_assets=None,
            mount_ui_dist=False,
        )

        # Mock datetime to get predictable timestamp
        fixed_now = datetime(2024, 1, 15, 10, 30, 0)
        expected_timestamp = fixed_now.isoformat()

        with patch.object(iap_module, "datetime") as mock_datetime:
            mock_datetime.now.return_value = fixed_now
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            # Mock run_command to capture the command that would be executed
            commands_executed = []

            def capture_command(cmd, **kwargs):
                commands_executed.append(cmd)
                return MagicMock(returncode=0)

            # Patch the run_command in the module
            with patch.object(iap_module, "run_command", side_effect=capture_command):
                with patch.object(iap_module, "console"):
                    iap_module._install_airflow_and_optionally_providers_together(spec, False)

        # Verify command was captured
        assert len(commands_executed) > 0, "Expected at least one command to be executed"
        base_cmd = commands_executed[0]

        # Verify --pre is present
        assert "--pre" in base_cmd, f"Expected '--pre' in command: {base_cmd}"

        # Verify --exclude-newer is present
        assert "--exclude-newer" in base_cmd, f"Expected '--exclude-newer' in command: {base_cmd}"

        # Verify timestamp follows --exclude-newer
        exclude_newer_idx = base_cmd.index("--exclude-newer")
        assert exclude_newer_idx + 1 < len(base_cmd), "Expected timestamp after --exclude-newer"
        timestamp = base_cmd[exclude_newer_idx + 1]

        # Verify timestamp is ISO format
        iso_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?$"
        assert re.match(iso_pattern, timestamp), f"Expected ISO format timestamp, got: {timestamp}"

    def test_install_with_constraints_adds_exclude_newer_with_timestamp(self, iap_module):
        """F2P: Second function also adds --exclude-newer when pre_release=True."""
        spec = iap_module.InstallationSpec(
            airflow_distribution="/path/to/airflow.whl",
            airflow_core_distribution=None,
            airflow_task_sdk_distribution=None,
            airflow_ctl_distribution=None,
            provider_distributions=[],
            pre_release=True,
            airflow_constraints_location=None,
            provider_constraints_location=None,
            airflow_ctl_constraints_location=None,
            compile_ui_assets=None,
            mount_ui_dist=False,
        )

        fixed_now = datetime(2024, 6, 20, 14, 45, 30)

        with patch.object(iap_module, "datetime") as mock_datetime:
            mock_datetime.now.return_value = fixed_now
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)

            commands_executed = []

            def capture_command(cmd, **kwargs):
                commands_executed.append(cmd)
                return MagicMock(returncode=0)

            with patch.object(iap_module, "run_command", side_effect=capture_command):
                with patch.object(iap_module, "console"):
                    iap_module._install_only_airflow_airflow_core_task_sdk_with_constraints(spec, False)

        assert len(commands_executed) > 0, "Expected at least one command to be executed"
        base_cmd = commands_executed[0]

        # Verify --pre is present
        assert "--pre" in base_cmd, f"Expected '--pre' in command: {base_cmd}"

        # Verify --exclude-newer is present
        assert "--exclude-newer" in base_cmd, f"Expected '--exclude-newer' in command: {base_cmd}"

        # Verify timestamp follows --exclude-newer
        exclude_newer_idx = base_cmd.index("--exclude-newer")
        timestamp = base_cmd[exclude_newer_idx + 1]

        iso_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?$"
        assert re.match(iso_pattern, timestamp), f"Expected ISO format timestamp, got: {timestamp}"

    def test_non_prerelease_does_not_add_exclude_newer(self, iap_module):
        """P2P: When pre_release=False, command should NOT include --pre or --exclude-newer."""
        spec = iap_module.InstallationSpec(
            airflow_distribution=None,
            airflow_core_distribution=None,
            airflow_task_sdk_distribution=None,
            airflow_ctl_distribution=None,
            provider_distributions=["provider1.whl"],
            pre_release=False,  # Not a pre-release
            airflow_constraints_location=None,
            provider_constraints_location=None,
            airflow_ctl_constraints_location=None,
            compile_ui_assets=None,
            mount_ui_dist=False,
        )

        commands_executed = []

        def capture_command(cmd, **kwargs):
            commands_executed.append(cmd)
            return MagicMock(returncode=0)

        with patch.object(iap_module, "run_command", side_effect=capture_command):
            with patch.object(iap_module, "console"):
                iap_module._install_airflow_and_optionally_providers_together(spec, False)

        assert len(commands_executed) > 0, "Expected at least one command to be executed"
        base_cmd = commands_executed[0]

        # Verify --pre is NOT present
        assert "--pre" not in base_cmd, f"Did not expect '--pre' in non-prerelease command: {base_cmd}"

        # Verify --exclude-newer is NOT present
        assert "--exclude-newer" not in base_cmd, f"Did not expect '--exclude-newer' in non-prerelease command: {base_cmd}"

    def test_non_prerelease_with_constraints_no_exclude_newer(self, iap_module):
        """P2P: Second function also should NOT add flags when pre_release=False."""
        spec = iap_module.InstallationSpec(
            airflow_distribution="/path/to/airflow.whl",
            airflow_core_distribution=None,
            airflow_task_sdk_distribution=None,
            airflow_ctl_distribution=None,
            provider_distributions=[],
            pre_release=False,  # Not a pre-release
            airflow_constraints_location=None,
            provider_constraints_location=None,
            airflow_ctl_constraints_location=None,
            compile_ui_assets=None,
            mount_ui_dist=False,
        )

        commands_executed = []

        def capture_command(cmd, **kwargs):
            commands_executed.append(cmd)
            return MagicMock(returncode=0)

        with patch.object(iap_module, "run_command", side_effect=capture_command):
            with patch.object(iap_module, "console"):
                iap_module._install_only_airflow_airflow_core_task_sdk_with_constraints(spec, False)

        assert len(commands_executed) > 0, "Expected at least one command to be executed"
        base_cmd = commands_executed[0]

        # Verify --pre is NOT present
        assert "--pre" not in base_cmd, f"Did not expect '--pre' in non-prerelease command: {base_cmd}"

        # Verify --exclude-newer is NOT present
        assert "--exclude-newer" not in base_cmd, f"Did not expect '--exclude-newer' in non-prerelease command: {base_cmd}"

    def test_timestamp_is_current_time(self, iap_module):
        """F2P: The timestamp used should be the current time when the function runs."""
        spec = iap_module.InstallationSpec(
            airflow_distribution=None,
            airflow_core_distribution=None,
            airflow_task_sdk_distribution=None,
            airflow_ctl_distribution=None,
            provider_distributions=[],
            pre_release=True,
            airflow_constraints_location=None,
            provider_constraints_location=None,
            airflow_ctl_constraints_location=None,
            compile_ui_assets=None,
            mount_ui_dist=False,
        )

        # Get actual current time (before calling function)
        before_time = datetime.now()

        commands_executed = []

        def capture_command(cmd, **kwargs):
            commands_executed.append(cmd)
            return MagicMock(returncode=0)

        with patch.object(iap_module, "run_command", side_effect=capture_command):
            with patch.object(iap_module, "console"):
                iap_module._install_airflow_and_optionally_providers_together(spec, False)

        after_time = datetime.now()

        assert len(commands_executed) > 0, "Expected at least one command to be executed"
        base_cmd = commands_executed[0]

        # Find and parse the timestamp
        exclude_newer_idx = base_cmd.index("--exclude-newer")
        timestamp_str = base_cmd[exclude_newer_idx + 1]
        cmd_timestamp = datetime.fromisoformat(timestamp_str)

        # Verify timestamp is between before and after
        assert before_time <= cmd_timestamp <= after_time, \
            f"Timestamp {cmd_timestamp} should be between {before_time} and {after_time}"

    def test_console_message_updated_for_providers(self, iap_module):
        """Verify console message mentions 'providers' for first function."""
        spec = iap_module.InstallationSpec(
            airflow_distribution=None,
            airflow_core_distribution=None,
            airflow_task_sdk_distribution=None,
            airflow_ctl_distribution=None,
            provider_distributions=[],
            pre_release=True,
            airflow_constraints_location=None,
            provider_constraints_location=None,
            airflow_ctl_constraints_location=None,
            compile_ui_assets=None,
            mount_ui_dist=False,
        )

        print_calls = []

        class MockConsole:
            def print(self, msg=""):
                print_calls.append(msg)

        with patch.object(iap_module, "console", MockConsole()):
            with patch.object(iap_module, "run_command", return_value=MagicMock(returncode=0)):
                with patch.object(iap_module, "datetime") as mock_datetime:
                    mock_datetime.now.return_value = datetime(2024, 1, 1)
                    mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
                    iap_module._install_airflow_and_optionally_providers_together(spec, False)

        # Check that the console message mentions 'providers'
        prerelease_messages = [msg for msg in print_calls if "pre-release" in str(msg).lower()]
        assert len(prerelease_messages) > 0, f"Expected message about pre-release, got: {print_calls}"
        assert "providers" in str(prerelease_messages[0]).lower(), \
            f"Expected message to mention 'providers': {prerelease_messages[0]}"


# =============================================================================
# Pass-to-Pass Tests (repo CI/CD checks)
# These verify the repo's existing checks pass on both base and fixed commits
# =============================================================================


def test_repo_python_syntax():
    """Python syntax check passes on install_airflow_and_providers.py (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "py_compile", str(TARGET_FILE)],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr}"


def test_repo_ast_parsing():
    """AST parsing succeeds on install_airflow_and_providers.py (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-c",
         f"import ast; ast.parse(open('{TARGET_FILE}').read()); print('AST OK')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"AST parsing failed:\n{r.stderr}"


def test_repo_ruff_critical():
    """Ruff critical checks (E9,F) pass on install_airflow_and_providers.py (pass_to_pass)."""
    # First install ruff
    install_r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert install_r.returncode == 0, f"Failed to install ruff: {install_r.stderr}"

    # Run ruff with only critical checks (syntax errors, undefined names)
    r = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "--select", "E9,F", str(TARGET_FILE)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff critical checks failed:\n{r.stdout}\n{r.stderr}"


def test_repo_ruff_format():
    """Ruff format check passes on install_airflow_and_providers.py (pass_to_pass)."""
    # First install ruff
    install_r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert install_r.returncode == 0, f"Failed to install ruff: {install_r.stderr}"

    # Run ruff format check
    r = subprocess.run(
        [sys.executable, "-m", "ruff", "format", "--check", str(TARGET_FILE)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_ruff_imports():
    """Ruff import checks (I) pass on install_airflow_and_providers.py (pass_to_pass)."""
    # First install ruff
    install_r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert install_r.returncode == 0, f"Failed to install ruff: {install_r.stderr}"

    # Run ruff import checks
    r = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "--select", "I", str(TARGET_FILE)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff import checks failed:\n{r.stdout}\n{r.stderr}"


def test_repo_shellcheck_scripts():
    """Shell scripts in in_container pass shellcheck (pass_to_pass)."""
    # Find shell scripts in the in_container directory
    shell_scripts = list((REPO / "scripts" / "in_container").glob("*.sh"))

    if not shell_scripts:
        pytest.skip("No shell scripts found to check")

    # Install shellcheck if available
    install_r = subprocess.run(
        ["apt-get", "update", "-qq"],
        capture_output=True, text=True, timeout=30,
    )
    # Try to install shellcheck, but don't fail if it doesn't work
    subprocess.run(
        ["apt-get", "install", "-y", "shellcheck", "-qq"],
        capture_output=True, text=True, timeout=60,
    )

    # Check if shellcheck is available
    check_r = subprocess.run(
        ["which", "shellcheck"],
        capture_output=True, text=True, timeout=10,
    )
    if check_r.returncode != 0:
        pytest.skip("shellcheck not available")

    # Run shellcheck on each script (only fail on errors/warnings, not info)
    for script in shell_scripts[:3]:  # Limit to first 3 scripts to save time
        r = subprocess.run(
            ["shellcheck", "--severity=warning", str(script)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"shellcheck failed for {script}:\n{r.stdout}\n{r.stderr}"


def test_repo_yaml_lint():
    """Basic YAML linting passes on workflow files (pass_to_pass)."""
    # Install yamllint
    install_r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "yamllint", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert install_r.returncode == 0, f"Failed to install yamllint: {install_r.stderr}"

    # Run yamllint on a simple workflow file
    workflow_file = REPO / ".github" / "workflows" / "basic-tests.yml"
    if not workflow_file.exists():
        pytest.skip("Workflow file not found")

    r = subprocess.run(
        [sys.executable, "-m", "yamllint", "-c", str(REPO / "yamllint-config.yml"), str(workflow_file)],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"yamllint failed:\n{r.stdout}\n{r.stderr}"


# =============================================================================
# New Pass-to-Pass Tests (CI/CD repo_tests)
# These run actual CI commands found in the repo's CI configuration
# =============================================================================


def test_repo_scripts_pytest():
    """Repo's scripts CI prek tests pass (pass_to_pass)."""
    # Install required dependencies for scripts tests
    install_r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "pytest", "python-dateutil",
         "pyyaml", "rich", "rich-click", "packaging", "tabulate",
         "jsonschema", "astor", "requests", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert install_r.returncode == 0, f"Failed to install dependencies: {install_r.stderr}"

    # Run the scripts tests (CI checks from basic-tests.yml)
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "scripts/tests/ci/prek/",
         "-v", "--tb=short", "-x"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Scripts tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_common_prek_utils():
    """Repo's common_prek_utils tests pass (pass_to_pass)."""
    # Install required dependencies
    install_r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "pytest", "python-dateutil",
         "pyyaml", "rich", "rich-click", "packaging", "tabulate",
         "jsonschema", "astor", "requests", "libcst", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert install_r.returncode == 0, f"Failed to install dependencies: {install_r.stderr}"

    # Run the common_prek_utils tests specifically (core CI utilities)
    r = subprocess.run(
        [sys.executable, "-m", "pytest",
         "scripts/tests/ci/prek/test_common_prek_utils.py",
         "-v", "--tb=short", "-x"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Common prek utils tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_py_compile():
    """Python syntax check via py_compile passes on target file (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "py_compile", str(TARGET_FILE)],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr}"


def test_repo_ruff_full():
    """Ruff full check passes on install_airflow_and_providers.py (pass_to_pass)."""
    # Install ruff
    install_r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert install_r.returncode == 0, f"Failed to install ruff: {install_r.stderr}"

    # Run full ruff check (excluding line-length and ambiguous variable names)
    r = subprocess.run(
        [sys.executable, "-m", "ruff", "check",
         "--select", "E,W,F,I",
         "--ignore", "E501,E741",
         str(TARGET_FILE)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_ruff_format_full():
    """Ruff format check passes on install_airflow_and_providers.py (pass_to_pass)."""
    # Install ruff
    install_r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert install_r.returncode == 0, f"Failed to install ruff: {install_r.stderr}"

    # Run ruff format check
    r = subprocess.run(
        [sys.executable, "-m", "ruff", "format", "--check", str(TARGET_FILE)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
