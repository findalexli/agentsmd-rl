# Fix docker:start reliability by adding a docker:clean script

## Problem

`pnpm docker:start` fails with a container name conflict when orphan containers exist from a previous run or a different compose project. The current `docker compose down` only removes containers it manages, so stale named containers (e.g. `postgres-payload-test`, `mongodb-payload-test`) cause startup to fail.

## Expected Behavior

There should be a dedicated `docker:clean` script that forcefully removes all named test containers before running `docker compose down`. The `docker:start` script should call this clean step first to ensure a reliable fresh start. The old `docker:stop` script should be replaced by `docker:clean`.

The clean script should be a Node.js script (not inline shell) because suppressing the exit code of `docker rm -f` on missing containers requires platform-specific syntax.

## Files to Look At

- `package.json` — npm scripts for `docker:start`, `docker:stop`, `docker:clean`
- `scripts/` — where utility scripts live (see `scripts/delete-recursively.js` for an existing example)
- `test/docker-compose.yml` — defines the named containers and compose services

After making the code changes, update the relevant documentation to reflect the new command names. The project's `CLAUDE.md`, `CONTRIBUTING.md`, and `test/docker-compose.yml` comments all reference the Docker workflow commands and should be kept in sync.
