# Add --build-strategy flag to dg plus deploy command

## Task

The `dg plus deploy` command only supports Docker-based builds. Extend it with a `--build-strategy` CLI option that lets users choose between Docker builds and PEX (Python executable) builds. The option must appear on both the `dg plus deploy` command and the `dg plus deploy build-and-push` subcommand.

## CLI Option Requirements

The `--build-strategy` option must:
- Accept two choices: `docker` (the default) and `python-executable`
- Support the `DAGSTER_BUILD_STRATEGY` environment variable as an override

The option should be defined in an option group variable named `build_strategy_option_group` using `make_option_group`, with the click option configured as:
- `type=click.Choice(["docker", "python-executable"])`
- `default="docker"`
- `envvar="DAGSTER_BUILD_STRATEGY"`

The `@build_strategy_option_group` decorator must be applied to both the `deploy_group` command group and the `build_and_push_command` subcommand.

## Build Strategy Semantics

- `docker`: Builds a Docker image. Required for Hybrid agents.
- `python-executable`: Builds PEX files (Python executables). Available for Serverless agents only.

The CLI choice `"python-executable"` corresponds to the `pex` value on the `BuildStrategy` enum, which is defined in `dagster_cloud_cli.commands.ci`.

## Function Signatures

The `deploy_group` function signature must include `build_strategy: str` in this position:

```
def deploy_group(
    organization: Optional[str],
    deployment: Optional[str],
    build_strategy: str,
```

The `build_and_push_command` function signature must include `build_strategy: str` in this position:

```
def build_and_push_command(
    agent_type_str: str,
    build_strategy: str,
```

## Build Strategy Flow

Both command functions must convert the string `build_strategy` to a `BuildStrategy` enum using `build_strategy_enum = BuildStrategy(build_strategy)`, importing `BuildStrategy` from `dagster_cloud_cli.commands.ci`.

The `build_artifact` function must accept `build_strategy: "BuildStrategy"` as its third parameter (after `dg_context: DgContext` and `agent_type: DgPlusAgentType`). The `_build_artifact_for_project` function must also accept `build_strategy: "BuildStrategy"` as its third parameter.

The build_strategy value must be passed through the full call chain from the CLI commands, through `build_artifact`, through `_build_artifact_for_project`, and ultimately to `build_impl` via `build_strategy=build_strategy`.

The `TYPE_CHECKING` block in the deploy session module must include:
```
from dagster_cloud_cli.commands.ci import BuildStrategy
```

## Validation

When `python-executable` build strategy is selected with a Hybrid agent, the code must raise a `click.UsageError` with this exact message:

```
Build strategy 'python-executable' is not supported for Hybrid agents. Hybrid agents require 'docker' build strategy.
```

This validation must check `if agent_type == DgPlusAgentType.HYBRID and build_strategy == BuildStrategy.pex:`.

## Verification

1. `dg plus deploy --help` must list the `--build-strategy` option with both choices
2. `dg plus deploy build-and-push --help` must list the `--build-strategy` option
3. `make ruff` and `make check_ruff` must pass at the repo root
