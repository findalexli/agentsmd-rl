"""Behavioral tests for prefect-deploy-custom-image-pull-step.

These tests exercise `prefect.cli.deploy._actions._generate_default_pull_action`
to verify the symptom described in instruction.md: when `build` is null/empty
and the user supplies a custom Docker image via `work_pool.job_variables.image`,
the generated pull step must point to a path that exists inside the container,
not the host's cwd.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

REPO = "/workspace/prefect"
if REPO not in sys.path:
    sys.path.insert(0, str(Path(REPO) / "src"))

from prefect.cli.deploy._actions import _generate_default_pull_action  # noqa: E402


@pytest.fixture
def console() -> MagicMock:
    return MagicMock()


def _make_config(
    *,
    entrypoint: str = "flows/my_flow.py:my_flow",
    image: str | None = None,
    build: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    config: dict[str, Any] = {"entrypoint": entrypoint}
    if build is not None:
        config["build"] = build
    if image is not None:
        config.setdefault("work_pool", {}).setdefault("job_variables", {})["image"] = image
    return config


# ---------------------------------------------------------------------------
# Fail-to-pass: behavior added by the fix
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_non_interactive_custom_image_uses_container_path(console: MagicMock) -> None:
    """Non-interactive deploy with custom image must NOT use the host cwd."""
    deploy_config = _make_config(image="my-registry/my-image:latest")
    result = await _generate_default_pull_action(
        console, deploy_config=deploy_config, actions={"build": []},
        is_interactive=lambda: False,
    )
    assert result == [
        {"prefect.deployments.steps.set_working_directory": {"directory": "/opt/prefect"}}
    ]
    cwd_str = str(Path.cwd().absolute().resolve())
    directory = result[0]["prefect.deployments.steps.set_working_directory"]["directory"]
    assert directory != cwd_str, (
        "pull step must NOT point at the host cwd when a custom container image is set"
    )


@pytest.mark.asyncio
async def test_non_interactive_custom_image_prints_warning(console: MagicMock) -> None:
    """Non-interactive path must warn the user about the assumed default."""
    deploy_config = _make_config(image="my-registry/my-image:latest")
    await _generate_default_pull_action(
        console, deploy_config=deploy_config, actions={"build": []},
        is_interactive=lambda: False,
    )
    assert console.print.called, "console.print was never called"
    printed = " ".join(str(c.args[0]) for c in console.print.call_args_list)
    assert "Warning" in printed
    assert "/opt/prefect" in printed
    assert "set_working_directory" in printed
    assert "prefect.yaml" in printed


@pytest.mark.asyncio
async def test_interactive_custom_image_prompts_for_directory(console: MagicMock) -> None:
    """Interactive path must call prompt() with /opt/prefect/<dirname> default."""
    deploy_config = _make_config(image="my-registry/my-image:latest")
    user_choice = "/srv/code/myapp"
    with patch(
        "prefect.cli.deploy._actions.prompt",
        return_value=user_choice,
    ) as mock_prompt:
        result = await _generate_default_pull_action(
            console, deploy_config=deploy_config, actions={"build": []},
            is_interactive=lambda: True,
        )
    assert mock_prompt.call_count == 1
    prompt_text = mock_prompt.call_args.args[0]
    assert "working directory" in prompt_text.lower()
    default = mock_prompt.call_args.kwargs.get("default")
    expected_default = f"/opt/prefect/{os.path.basename(os.getcwd())}"
    assert default == expected_default, f"prompt default {default!r} != {expected_default!r}"
    assert result == [
        {"prefect.deployments.steps.set_working_directory": {"directory": user_choice}}
    ]


@pytest.mark.asyncio
async def test_interactive_default_varies_with_cwd(console: MagicMock, tmp_path, monkeypatch) -> None:
    """The interactive default must include the cwd basename, not be hardcoded."""
    deploy_config = _make_config(image="my-registry/my-image:latest")
    custom_dir = tmp_path / "totally-unique-projectname-xyz"
    custom_dir.mkdir()
    monkeypatch.chdir(custom_dir)
    with patch(
        "prefect.cli.deploy._actions.prompt",
        return_value="/whatever",
    ) as mock_prompt:
        await _generate_default_pull_action(
            console, deploy_config=deploy_config, actions={"build": []},
            is_interactive=lambda: True,
        )
    default = mock_prompt.call_args.kwargs.get("default")
    assert default == "/opt/prefect/totally-unique-projectname-xyz", default


@pytest.mark.asyncio
async def test_no_image_falls_back_to_local_cwd(console: MagicMock) -> None:
    """Existing behavior preserved: no image, no build → local cwd path."""
    deploy_config = _make_config()
    result = await _generate_default_pull_action(
        console, deploy_config=deploy_config, actions={"build": []},
        is_interactive=lambda: False,
    )
    expected = str(Path.cwd().absolute().resolve())
    assert result == [
        {"prefect.deployments.steps.set_working_directory": {"directory": expected}}
    ]


@pytest.mark.asyncio
async def test_empty_image_string_falls_back_to_local_cwd(console: MagicMock) -> None:
    """An empty-string image is falsy and must NOT trigger the container fallback."""
    deploy_config = _make_config(image="")
    result = await _generate_default_pull_action(
        console, deploy_config=deploy_config, actions={"build": []},
        is_interactive=lambda: False,
    )
    expected = str(Path.cwd().absolute().resolve())
    assert result == [
        {"prefect.deployments.steps.set_working_directory": {"directory": expected}}
    ]


@pytest.mark.asyncio
async def test_image_in_actions_build_step_not_treated_as_custom_image(console: MagicMock) -> None:
    """A populated `actions['build']` with build_docker_image must take precedence."""
    deploy_config = _make_config(image="my-registry/my-image:latest")
    actions = {
        "build": [
            {
                "prefect_docker.deployments.steps.build_docker_image": {
                    "dockerfile": "auto"
                }
            }
        ]
    }
    result = await _generate_default_pull_action(
        console, deploy_config=deploy_config, actions=actions,
        is_interactive=lambda: False,
    )
    dir_name = os.path.basename(os.getcwd())
    assert result == [
        {
            "prefect.deployments.steps.set_working_directory": {
                "directory": f"/opt/prefect/{dir_name}"
            }
        }
    ]


# ---------------------------------------------------------------------------
# Pass-to-pass: existing repo behavior should be unaffected
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_p2p_build_docker_step_auto_dockerfile_unchanged(console: MagicMock) -> None:
    """build_docker_image with dockerfile=auto path is unchanged."""
    deploy_config = _make_config(
        build=[
            {
                "prefect_docker.deployments.steps.build_docker_image": {
                    "dockerfile": "auto"
                }
            }
        ],
    )
    result = await _generate_default_pull_action(
        console, deploy_config=deploy_config, actions={"build": []},
        is_interactive=lambda: False,
    )
    dir_name = os.path.basename(os.getcwd())
    assert result == [
        {
            "prefect.deployments.steps.set_working_directory": {
                "directory": f"/opt/prefect/{dir_name}"
            }
        }
    ]


def test_p2p_module_imports_cleanly() -> None:
    """The edited module imports without syntax/structure errors."""
    r = subprocess.run(
        [sys.executable, "-c", "import prefect.cli.deploy._actions as m; assert hasattr(m, '_generate_default_pull_action')"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"import failed:\nstdout:{r.stdout}\nstderr:{r.stderr}"


def test_p2p_ruff_check_actions_file() -> None:
    """The edited file must pass the repo's ruff lint configuration."""
    r = subprocess.run(
        ["ruff", "check", "src/prefect/cli/deploy/_actions.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"ruff check failed:\n{r.stdout}\n{r.stderr}"


def test_p2p_ruff_format_actions_file() -> None:
    """The edited file must conform to the repo's ruff formatter."""
    r = subprocess.run(
        ["ruff", "format", "--check", "src/prefect/cli/deploy/_actions.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"ruff format check failed:\n{r.stdout}\n{r.stderr}"
