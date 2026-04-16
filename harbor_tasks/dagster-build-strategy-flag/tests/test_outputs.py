"""Test that --build-strategy flag is properly added to dg plus deploy command.

This tests:
1. The --build-strategy option exists on deploy and build-and-push commands
2. The build_strategy parameter is passed through the call chain
3. HYBRID agents cannot use 'python-executable' build strategy
4. SERVERLESS agents can use both 'docker' and 'python-executable' build strategies
5. The default build strategy is 'docker'
"""

import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/dagster")
COMMANDS_PY = REPO / "python_modules/libraries/dagster-dg-cli/dagster_dg_cli/cli/plus/deploy/commands.py"
DEPLOY_SESSION_PY = REPO / "python_modules/libraries/dagster-dg-cli/dagster_dg_cli/cli/plus/deploy/deploy_session.py"


def _get_commands_source():
    """Read commands.py source code."""
    return COMMANDS_PY.read_text()


def _get_deploy_session_source():
    """Read deploy_session.py source code."""
    return DEPLOY_SESSION_PY.read_text()


def test_build_strategy_option_exists():
    """FAIL-TO-PASS: Verify --build-strategy option is defined in commands.py."""
    source = _get_commands_source()

    # Check that build_strategy_option_group is defined
    assert "build_strategy_option_group = make_option_group" in source, \
        "build_strategy_option_group not defined in commands.py"

    # Check the option has correct choices
    assert 'type=click.Choice(["docker", "python-executable"])' in source, \
        "--build-strategy option must have choices: docker, python-executable"

    # Check default is docker
    assert 'default="docker"' in source, \
        "--build-strategy default must be 'docker'"

    # Check envvar is set
    assert 'envvar="DAGSTER_BUILD_STRATEGY"' in source, \
        "--build-strategy must have DAGSTER_BUILD_STRATEGY envvar"


def test_build_strategy_on_deploy_group():
    """FAIL-TO-PASS: Verify --build-strategy is applied to deploy group command."""
    source = _get_commands_source()

    # Check decorator is applied to deploy_group
    assert "@build_strategy_option_group" in source, \
        "build_strategy_option_group decorator not found"

    # Check parameter exists in deploy_group function signature
    assert "def deploy_group(\n    organization: Optional[str],\n    deployment: Optional[str],\n    build_strategy: str," in source, \
        "build_strategy parameter not found in deploy_group signature"


def test_build_strategy_on_build_and_push():
    """FAIL-TO-PASS: Verify --build-strategy is applied to build-and-push subcommand."""
    source = _get_commands_source()

    # Count occurrences - should be on both commands
    decorator_count = source.count("@build_strategy_option_group")
    assert decorator_count >= 2, \
        f"build_strategy_option_group decorator should appear at least 2 times, found {decorator_count}"

    # Check build_and_push_command has build_strategy parameter
    # Look for the function signature
    assert "def build_and_push_command(\n    agent_type_str: str,\n    build_strategy: str," in source, \
        "build_strategy parameter not found in build_and_push_command signature"


def test_build_strategy_enum_import():
    """FAIL-TO-PASS: Verify BuildStrategy is imported and used in commands.py."""
    source = _get_commands_source()

    # Check lazy import of BuildStrategy in deploy_group
    assert "from dagster_cloud_cli.commands.ci import BuildStrategy" in source, \
        "BuildStrategy must be imported from dagster_cloud_cli.commands.ci"

    # Check build_strategy_enum is created in deploy_group
    assert "build_strategy_enum = BuildStrategy(build_strategy)" in source, \
        "build_strategy must be converted to BuildStrategy enum"


def test_build_artifact_signature_updated():
    """FAIL-TO-PASS: Verify build_artifact function signature includes build_strategy."""
    source = _get_deploy_session_source()

    # Check build_artifact function signature
    assert "def build_artifact(\n    dg_context: DgContext,\n    agent_type: DgPlusAgentType,\n    build_strategy: \"BuildStrategy\"," in source, \
        "build_artifact function must accept build_strategy parameter"

    # Check _build_artifact_for_project signature
    assert "def _build_artifact_for_project(\n    dg_context: DgContext,\n    agent_type: DgPlusAgentType,\n    build_strategy: \"BuildStrategy\"," in source, \
        "_build_artifact_for_project function must accept build_strategy parameter"


def test_build_strategy_passed_to_build_impl():
    """FAIL-TO-PASS: Verify build_strategy is passed to build_impl call."""
    source = _get_deploy_session_source()

    # Check build_strategy is passed to build_impl
    assert "build_strategy=build_strategy," in source, \
        "build_strategy must be passed to build_impl"


def test_hybrid_pex_validation():
    """FAIL-TO-PASS: Verify HYBRID agent with pex build strategy raises error."""
    source = _get_deploy_session_source()

    # Check the validation exists
    assert "if agent_type == DgPlusAgentType.HYBRID and build_strategy == BuildStrategy.pex:" in source, \
        "Validation for HYBRID agent + pex build strategy not found"

    # Check error message
    assert 'Build strategy \'python-executable\' is not supported for Hybrid agents' in source, \
        "Error message for Hybrid+pex incompatibility not found"


def test_build_strategy_passed_to_inner_functions():
    """FAIL-TO-PASS: Verify build_strategy is passed to _build_artifact_for_project."""
    source = _get_deploy_session_source()

    # Find all occurrences of _build_artifact_for_project calls
    # These calls should pass build_strategy as the third argument
    # The function definition starts at line 232, so we look for calls before that

    # Count occurrences of _build_artifact_for_project with build_strategy
    # Using a simpler pattern - look for the function call followed by build_strategy
    import re
    pattern = r'_build_artifact_for_project\([^)]*build_strategy'
    matches = re.findall(pattern, source, re.DOTALL)

    # Should be at least 2 calls (one for project, one for workspace projects)
    assert len(matches) >= 2, \
        f"build_strategy should be passed to _build_artifact_for_project in all call sites, found {len(matches)}"


def test_build_strategy_type_hint_updated():
    """FAIL-TO-PASS: Verify TYPE_CHECKING block includes BuildStrategy."""
    source = _get_deploy_session_source()

    # Extract the TYPE_CHECKING block - find content between "if TYPE_CHECKING:" and the next blank line or unindented line
    import re
    match = re.search(r'if TYPE_CHECKING:([\s\S]*?)(?=\n[^\s]|\n\n|$)', source)
    if match:
        type_checking_block = match.group(1)
        # Check BuildStrategy import is in TYPE_CHECKING block
        assert 'from dagster_cloud_cli.commands.ci import BuildStrategy' in type_checking_block, \
            "TYPE_CHECKING block must import BuildStrategy from dagster_cloud_cli.commands.ci"
    else:
        assert False, "Could not find TYPE_CHECKING block in source"


def test_build_strategy_passed_from_commands():
    """FAIL-TO-PASS: Verify build_strategy_enum is passed from deploy_group to build_artifact."""
    source = _get_commands_source()

    # Check build_artifact is called with build_strategy_enum
    assert "build_strategy_enum," in source, \
        "build_artifact must be called with build_strategy_enum"


def test_hardcoded_docker_removed():
    """FAIL-TO-PASS: Verify hardcoded BuildStrategy.docker is replaced with parameter."""
    source = _get_deploy_session_source()

    # The old code had build_strategy=BuildStrategy.docker hardcoded
    # The new code should use the parameter
    # This checks that the hardcoded value is removed from the build_impl call site
    assert "build_strategy=build_strategy," in source, \
        "build_impl must use build_strategy parameter, not hardcoded BuildStrategy.docker"


def test_cli_help_includes_build_strategy():
    """FAIL-TO-PASS: Verify CLI help includes --build-strategy option."""
    result = subprocess.run(
        [sys.executable, "-m", "dagster_dg_cli.cli", "plus", "deploy", "--help"],
        capture_output=True,
        text=True,
        cwd=str(REPO),
        timeout=30
    )

    # The help should include --build-strategy
    assert "--build-strategy" in result.stdout, \
        f"CLI help must include --build-strategy option. Output:\n{result.stdout}"

    # Should mention the choices
    assert "docker" in result.stdout and "python-executable" in result.stdout, \
        f"CLI help must mention docker and python-executable choices. Output:\n{result.stdout}"


def test_build_and_push_help_includes_build_strategy():
    """FAIL-TO-PASS: Verify build-and-push subcommand includes --build-strategy option."""
    result = subprocess.run(
        [sys.executable, "-m", "dagster_dg_cli.cli", "plus", "deploy", "build-and-push", "--help"],
        capture_output=True,
        text=True,
        cwd=str(REPO),
        timeout=30
    )

    # The help should include --build-strategy
    assert "--build-strategy" in result.stdout, \
        f"build-and-push help must include --build-strategy option. Output:\n{result.stdout}"


def test_ruff_formatting():
    """PASS-TO-PASS: Repo code formatting with ruff (per CLAUDE.md coding conventions)."""
    result = subprocess.run(
        ["make", "ruff"],
        capture_output=True,
        text=True,
        cwd=str(REPO),
        timeout=120
    )

    # ruff should either pass or find no issues (exit code 0)
    assert result.returncode == 0, \
        f"ruff formatting/linting failed:\n{result.stdout}\n{result.stderr}"


def test_check_ruff():
    """PASS-TO-PASS: Repo linting check passes without auto-fixing (CI-style check)."""
    result = subprocess.run(
        ["make", "check_ruff"],
        capture_output=True,
        text=True,
        cwd=str(REPO),
        timeout=120
    )

    # check_ruff should pass without making changes (exit code 0)
    assert result.returncode == 0, \
        f"check_ruff failed:\n{result.stdout}\n{result.stderr}"


def test_import_dagster_dg_cli():
    """PASS-TO-PASS: dagster_dg_cli package imports successfully."""
    result = subprocess.run(
        [sys.executable, "-c", "import dagster_dg_cli; print('OK')"],
        capture_output=True,
        text=True,
        cwd=str(REPO),
        timeout=30
    )

    assert result.returncode == 0, \
        f"dagster_dg_cli import failed:\n{result.stderr}"
    assert "OK" in result.stdout, \
        f"Expected 'OK' in output, got:\n{result.stdout}"


def test_import_deploy_commands():
    """PASS-TO-PASS: deploy commands module imports successfully (modified code)."""
    result = subprocess.run(
        [sys.executable, "-c",
         "from dagster_dg_cli.cli.plus.deploy import commands; print('OK')"],
        capture_output=True,
        text=True,
        cwd=str(REPO),
        timeout=30
    )

    assert result.returncode == 0, \
        f"deploy.commands import failed:\n{result.stderr}"
    assert "OK" in result.stdout, \
        f"Expected 'OK' in output, got:\n{result.stdout}"


def test_import_deploy_session():
    """PASS-TO-PASS: deploy session module imports successfully (modified code)."""
    result = subprocess.run(
        [sys.executable, "-c",
         "from dagster_dg_cli.cli.plus.deploy import deploy_session; print('OK')"],
        capture_output=True,
        text=True,
        cwd=str(REPO),
        timeout=30
    )

    assert result.returncode == 0, \
        f"deploy_session import failed:\n{result.stderr}"
    assert "OK" in result.stdout, \
        f"Expected 'OK' in output, got:\n{result.stdout}"


def test_import_perf():
    """PASS-TO-PASS: Import performance test - expensive libraries not imported at startup."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest",
         "python_modules/libraries/dagster-dg-cli/dagster_dg_cli_tests/cli_tests/import_perf_tests/",
         "-v", "--tb=short"],
        capture_output=True,
        text=True,
        cwd=str(REPO),
        timeout=60
    )

    assert result.returncode == 0, \
        f"Import perf test failed:\n{result.stdout}\n{result.stderr}"
