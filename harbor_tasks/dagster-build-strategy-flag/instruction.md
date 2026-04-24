# Add --build-strategy flag to dg plus deploy command

## Task

The `dg plus deploy` command currently only supports Docker-based builds. Add a `--build-strategy` CLI option that allows users to choose between Docker builds and PEX (Python executable) builds.

The option must appear on:
1. The `dg plus deploy` command
2. The `dg plus deploy build-and-push` subcommand

## Requirements

### CLI Option Specification

The `--build-strategy` option must:
- Accept two choices: `docker` (the default) and `python-executable`
- Support an environment variable override
- Have a default value of `"docker"`

### Build Strategy Behavior

- `docker`: Builds a Docker image. Required for Hybrid agents.
- `python-executable`: Builds PEX files (Python executables). Available for Serverless agents only.

### Validation

When `python-executable` build strategy is selected with a Hybrid agent, the code must raise a `click.UsageError` with this message:

```
Build strategy 'python-executable' is not supported for Hybrid agents. Hybrid agents require 'docker' build strategy.
```

### Implementation Notes

- Use `make_option_group` to create a reusable option group that can be applied to both commands
- The build strategy value must flow through the call chain from CLI commands to the underlying build implementation
- Function signatures in the deploy session module need to be updated to accept the build strategy parameter
- Import the BuildStrategy enum lazily inside functions where needed to maintain CLI startup performance

## Verification

1. `dg plus deploy --help` must list the `--build-strategy` option with both choices
2. `dg plus deploy build-and-push --help` must list the `--build-strategy` option
3. `make ruff` and `make check_ruff` must pass at the repo root