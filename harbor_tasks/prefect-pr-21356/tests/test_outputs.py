"""
Tests for prefect deploy custom image pull step fix.

Verifies that when `prefect deploy` is run with a custom Docker image
in job_variables but no build step, the generated pull step uses a
container-appropriate path (/opt/prefect) instead of the local cwd.
"""
import asyncio
import subprocess
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Import from the installed prefect package
from prefect.cli.deploy._actions import _generate_default_pull_action


REPO = Path("/workspace/prefect")
TARGET_FILE = REPO / "src/prefect/cli/deploy/_actions.py"


def _make_deploy_config(
    *,
    entrypoint: str = "flows/my_flow.py:my_flow",
    image: str | None = None,
    build: list | None = None,
):
    """Helper to build a deploy config dict matching prefect.yaml structure."""
    config = {"entrypoint": entrypoint}
    if build is not None:
        config["build"] = build
    if image is not None:
        config.setdefault("work_pool", {}).setdefault("job_variables", {})["image"] = (
            image
        )
    return config


def test_non_interactive_custom_image_uses_opt_prefect():
    """
    When build is empty and job_variables.image is set, non-interactive
    mode should return /opt/prefect as the working directory, not the
    local cwd (which doesn't exist inside the container).
    """
    console = MagicMock()
    deploy_config = _make_deploy_config(image="my-registry/my-image:latest")
    actions = {"build": []}

    result = asyncio.run(
        _generate_default_pull_action(
            console,
            deploy_config=deploy_config,
            actions=actions,
            is_interactive=lambda: False,
        )
    )

    assert result == [
        {
            "prefect.deployments.steps.set_working_directory": {
                "directory": "/opt/prefect"
            }
        }
    ]


def test_non_interactive_custom_image_prints_warning():
    """
    In non-interactive mode with a custom image, a warning should be
    printed advising the user to verify the path matches their image's WORKDIR.
    """
    console = MagicMock()
    deploy_config = _make_deploy_config(image="my-registry/my-image:latest")
    actions = {"build": []}

    asyncio.run(
        _generate_default_pull_action(
            console,
            deploy_config=deploy_config,
            actions=actions,
            is_interactive=lambda: False,
        )
    )

    console.print.assert_called_once()
    printed = console.print.call_args[0][0]
    # Verify a non-empty message was printed containing the container path
    assert printed, "Expected a warning message to be printed"
    assert "/opt/prefect" in printed, "Warning should mention the /opt/prefect path"


def test_no_custom_image_preserves_local_cwd():
    """
    When there is no custom image in job_variables, the existing
    behavior (local cwd) should be preserved.
    """
    console = MagicMock()
    deploy_config = _make_deploy_config()
    actions = {"build": []}

    result = asyncio.run(
        _generate_default_pull_action(
            console,
            deploy_config=deploy_config,
            actions=actions,
            is_interactive=lambda: False,
        )
    )

    expected_dir = str(Path.cwd().absolute().resolve())
    assert result == [
        {
            "prefect.deployments.steps.set_working_directory": {
                "directory": expected_dir
            }
        }
    ]


def test_ruff_lint_passes():
    """Repo's linter passes on the modified file (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", str(TARGET_FILE)],
        capture_output=True,
        text=True,
        cwd=REPO,
        timeout=60,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


def test_ruff_check_deploy_module():
    """Repo linter passes on the entire deploy CLI module (pass_to_pass)."""
    r = subprocess.run(
        ["ruff", "check", "src/prefect/cli/deploy/"],
        capture_output=True,
        text=True,
        cwd=REPO,
        timeout=120,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout[-500:]}"


def test_deploy_actions_module_compiles():
    """The deploy _actions module compiles without syntax errors (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "py_compile", "src/prefect/cli/deploy/_actions.py"],
        capture_output=True,
        text=True,
        cwd=REPO,
        timeout=60,
    )
    assert r.returncode == 0, f"py_compile failed:\n{r.stderr[-500:]}"


def test_deploy_actions_imports():
    """The deploy _actions module imports successfully (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-c", "from prefect.cli.deploy._actions import _generate_default_pull_action; print('import ok')"],
        capture_output=True,
        text=True,
        cwd=REPO,
        timeout=60,
    )
    assert r.returncode == 0, f"Import failed:\n{r.stderr[-500:]}"
    assert "import ok" in r.stdout


def test_deploy_actions_syntax_valid():
    """The deploy _actions module has valid Python syntax (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-c", "import ast; ast.parse(open('src/prefect/cli/deploy/_actions.py').read())"],
        capture_output=True,
        text=True,
        cwd=REPO,
        timeout=60,
    )
    assert r.returncode == 0, f"Syntax check failed:\n{r.stderr[-500:]}"
