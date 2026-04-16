# Task: Skip dagster-docker integration tests when credentials are not present

## Problem

When running dagster-docker integration tests in Buildkite CI, the tests fail if the required Docker registry credentials are not available. This happens in fork PRs or when the CI environment doesn't have access to the necessary secrets.

The tests at `python_modules/libraries/dagster-docker/dagster_docker_tests/` require several Buildkite-specific environment variables to authenticate with Docker registries. When these variables are missing, the tests should be skipped with the message containing the text `"Docker integration tests require Buildkite env vars:"` followed by a comma-separated list of missing variable names.

## Your Task

Modify `python_modules/libraries/dagster-docker/dagster_docker_tests/conftest.py` to implement a pytest hook that conditionally skips integration tests when required credentials are unavailable.

The implementation must satisfy the following requirements:

1. **Only apply to integration tests**: Integration tests are identified by having the `integration` keyword. Non-integration tests should not be affected by the credential check.

2. **Only apply in Buildkite CI**: The credential check should only occur when the `BUILDKITE` environment variable is set. The check must use `os.getenv("BUILDKITE")` to determine if running in Buildkite.

3. **Verify all required environment variables**: The implementation must check for the following four environment variables:
   - `DAGSTER_DOCKER_REPOSITORY`
   - `DAGSTER_DOCKER_IMAGE_TAG`
   - `AWS_ACCOUNT_ID`
   - `BUILDKITE_SECRETS_BUCKET`

4. **Identify missing variables**: The implementation must compute which required variables are not set by checking `os.getenv(var)` for each required variable.

5. **Skip with descriptive message**: When any required variables are missing, tests must be skipped with a message that includes the literal text `"Docker integration tests require Buildkite env vars:"` followed by the comma-separated list of missing variable names.

## Key Files

- `python_modules/libraries/dagster-docker/dagster_docker_tests/conftest.py` - Add the pytest hook here

## Context

The conftest.py file already contains test fixtures for dagster-docker tests. You need to add a pytest hook function that runs before each test and conditionally skips integration tests when credentials are unavailable.

Use pytest's built-in `pytest.skip()` function to skip tests. Check pytest documentation for how hooks work if you're unfamiliar.

## After Making Changes

After any code changes, run `make ruff` from the repo root to ensure code quality.
