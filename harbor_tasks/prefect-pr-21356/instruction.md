# Prefect Deploy Custom Image Bug

## Problem Description

When running `prefect deploy` with `build: null` (or an empty build array) but a custom Docker image specified in `job_variables.image`, the CLI auto-generates a `set_working_directory` pull step that points to the **local machine's current working directory** (e.g., `/Users/alice/code/my-project`).

This path does not exist inside the Docker container where the flow will run, causing a `FileNotFoundError` at runtime when the worker tries to load the flow code.

### How to Reproduce

1. Create a `prefect.yaml` with:
   - An entrypoint pointing to a flow file
   - A `work_pool` with `job_variables.image` set to a custom Docker image (e.g., `my-registry/my-image:latest`)
   - No `build` section (or `build: []`)
2. Run `prefect deploy` in non-interactive mode (e.g., in CI)
3. The generated pull step will contain the local cwd path instead of a container-appropriate path

### Expected Behavior

When a custom Docker image is detected in `job_variables.image` and there is no `build_docker_image` step, the CLI should:

- **Non-interactive mode**: Use a container-appropriate default path (a well-known convention for Prefect Docker images is `/opt/prefect`) and print a warning advising the user to verify the path matches their image's WORKDIR
- **Interactive mode**: Prompt the user for the working directory inside their Docker image

### Relevant Source

The function `prefect.cli.deploy._actions._generate_default_pull_action` handles the generation of the default pull step. This is where the detection logic for custom images should be added.

### Verification

After applying the fix, when `prefect deploy` is run with a custom image and no build step in non-interactive mode:
1. The generated pull step should use a container-appropriate path, not the local cwd
2. A warning message should be printed to the console

### References

- Prefect Documentation: https://docs.prefect.io/latest
- Prefect GitHub: https://github.com/prefecthq/prefect
- Related PR: prefecthq/prefect#21356
