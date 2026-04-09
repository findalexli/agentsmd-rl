# Add Missing Custom Command in airflowctl Integration Tests

The airflowctl integration test suite is missing coverage for the `auth list-envs` command. This command should be included in the `TEST_COMMANDS` list to ensure it's properly tested alongside other auth commands like `auth token`.

## Task

Add the missing `auth list-envs` command to the integration test suite in the airflowctl tests.

## Files to Modify

- `airflow-ctl-tests/tests/airflowctl_tests/test_airflowctl_commands.py`

## Details

The test file contains a `TEST_COMMANDS` list that enumerates all commands to be tested. The `auth list-envs` command needs to be added alongside the existing auth commands (like `auth token`).

Additionally, when reviewing the test functions `test_airflowctl_commands` and `test_airflowctl_commands_skip_keyring`, the `run_command` calls should use keyword arguments and dict literals for `env_vars` instead of the current style.

The agent should:
1. Locate the `TEST_COMMANDS` list
2. Add the missing `auth list-envs` command in the appropriate location (auth commands section)
3. Refactor the `run_command` calls to use keyword arguments for better code clarity

## Hints

- The `TEST_COMMANDS` list contains all the commands to be tested
- Look at how `auth token` is defined for reference on where to add the new command
- The test functions use a `run_command` fixture that accepts `command`, `env_vars`, and `skip_login` parameters
- Consider using dict literals for `env_vars` instead of building them incrementally
