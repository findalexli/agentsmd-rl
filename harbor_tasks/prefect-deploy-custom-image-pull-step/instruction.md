# Fix `prefect deploy` pull step for custom Docker images

The Prefect repository is checked out at `/workspace/prefect` and installed in editable mode. Your task is to fix a bug in the `prefect deploy` CLI flow.

## Background

The `prefect deploy` CLI inspects a user's `prefect.yaml` and synthesizes a default *pull step* (the recipe used to fetch flow code at runtime). The relevant helper is the async coroutine `_generate_default_pull_action` in the `prefect.cli.deploy._actions` module. It returns a list with a single dict of the shape:

```python
[{"prefect.deployments.steps.set_working_directory": {"directory": "<path>"}}]
```

Today the helper handles two cases:

1. The user has a `prefect_docker.deployments.steps.build_docker_image` build step → the pull-step directory is computed relative to the container (e.g. `/opt/prefect/<dirname>`).
2. There is no build step → the pull-step directory falls back to the host's `Path.cwd().absolute().resolve()`.

## The bug

When a user runs `prefect deploy` with `build: null` **but** sets a custom image through `deploy_config["work_pool"]["job_variables"]["image"]`, the helper takes the second branch and writes the **host's** working directory into the pull step. That host path does not exist inside the user's container, so the worker fails at runtime with `FileNotFoundError`.

A reproduction looks like:

```python
deploy_config = {
    "entrypoint": "flows/my_flow.py:my_flow",
    "work_pool": {"job_variables": {"image": "my-registry/my-image:latest"}},
}
result = await _generate_default_pull_action(
    console,
    deploy_config=deploy_config,
    actions={"build": []},
    is_interactive=lambda: False,
)
# Today: result[0][...]["directory"] is the host cwd, e.g. "/Users/alice/code/my-project".
# Expected: result[0][...]["directory"] is a path that exists inside the container.
```

## What you need to do

Modify `_generate_default_pull_action` so that, **after** the existing `build_docker_image` detection but **before** the local-cwd fallback, it checks for a custom image via `deploy_config.get("work_pool", {}).get("job_variables", {}).get("image")` and, when present, returns a container-appropriate pull step instead. Behavior must split on interactivity:

### Non-interactive mode (`is_interactive() is False`)

- Return exactly:
  ```python
  [{"prefect.deployments.steps.set_working_directory": {"directory": "/opt/prefect"}}]
  ```
- Print a single warning to the console explaining the assumption. The warning text **must contain all of** the following substrings (anywhere in the message):
  - the word `Warning`
  - the path `/opt/prefect`
  - the step name `set_working_directory`
  - the filename `prefect.yaml`
- Do not invoke `prompt()`.

### Interactive mode (`is_interactive() is True`)

- Call `prompt(...)` once with:
  - first positional argument: a question whose lowercased text contains the phrase `working directory`
  - keyword argument `default=` set to **exactly** `f"/opt/prefect/{os.path.basename(os.getcwd())}"`
  - keyword argument `console=` set to the supplied `console`
- Wrap the user's response and return:
  ```python
  [{"prefect.deployments.steps.set_working_directory": {"directory": <prompt-result>}}]
  ```

### Other inputs must keep their old behavior

- A falsy `image` (missing key, `None`, or empty string `""`) must continue to fall through to the local-cwd branch.
- A populated `actions["build"]` containing `prefect_docker.deployments.steps.build_docker_image` must still take precedence over the new code path.

## File to edit

`src/prefect/cli/deploy/_actions.py` — the only production file you should need to touch.

## Code Style Requirements

The repository enforces formatting and linting via **ruff**. Your changes must pass:

- `ruff check src/prefect/cli/deploy/_actions.py`
- `ruff format --check src/prefect/cli/deploy/_actions.py`

Follow the surrounding style: top-level imports only (no deferred imports inside the function), modern Python 3.10+ type hints, no `from __future__ import annotations` additions, and use `console.print(...)` for any console output (Rich-style markup like `[yellow]...[/yellow]` is fine).

## How your fix is graded

The grader exercises `_generate_default_pull_action` directly with a mock `console`, asserting:

1. Non-interactive + custom image → returns the `/opt/prefect` step exactly as shown above.
2. Non-interactive + custom image → `console.print` is called with text that contains every required substring listed above.
3. Interactive + custom image → `prompt(...)` is called once, the question contains "working directory", and `default` equals `/opt/prefect/<basename of cwd>`; the returned step uses the prompt's return value.
4. Interactive default tracks `os.getcwd()` (verified by `chdir`-ing into a directory with a unique name).
5. No image (or empty-string image) → unchanged local-cwd fallback.
6. `actions["build"]` containing `build_docker_image` with `dockerfile=auto` → unchanged `/opt/prefect/<basename>` behavior.
7. The repo's pre-existing ruff lint and format checks still pass on the edited file.
