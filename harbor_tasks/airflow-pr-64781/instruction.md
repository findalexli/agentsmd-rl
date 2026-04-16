# Fix breeze ci upgrade command ordering

## Problem

The `breeze ci upgrade` command in `dev/breeze/src/airflow_breeze/commands/ci_commands.py` has incorrect execution ordering. The `upgrade` function currently runs commands in an order that causes `update-uv-lock` to use a stale CI image.

## Symptoms

- Commands that modify Dockerfiles (`autoupdate`, `update-chart-dependencies`, `upgrade-important-versions`) run after the CI image is built
- The `update-uv-lock` step runs inside the CI container and therefore uses an image that doesn't reflect recent Dockerfile changes
- The complete sequence of commands that must run during upgrade includes:
  - `prek autoupdate --cooldown-days 4 --freeze`
  - `prek --all-files --show-diff-on-failure --color always --verbose update-chart-dependencies --stage manual`
  - `prek --all-files --show-diff-on-failure --color always --verbose --stage manual upgrade-important-versions`
  - `breeze ci-image build --python 3.10`
  - `prek --all-files --show-diff-on-failure --color always --verbose update-uv-lock --stage manual`

## Expected behavior

The `upgrade` function must execute commands in this order:

1. First, commands that may update Dockerfiles must complete. These commands modify files that affect the CI image build:
   - `autoupdate`: `prek autoupdate --cooldown-days 4 --freeze`
   - `update-chart-dependencies`: `prek --all-files --show-diff-on-failure --color always --verbose update-chart-dependencies --stage manual`
   - `upgrade-important-versions`: `prek --all-files --show-diff-on-failure --color always --verbose --stage manual upgrade-important-versions`

2. Then, build the CI image: `breeze ci-image build --python 3.10`

3. Finally, commands that run inside the CI container must execute. The only such command is:
   - `update-uv-lock`: `prek --all-files --show-diff-on-failure --color always --verbose update-uv-lock --stage manual`
