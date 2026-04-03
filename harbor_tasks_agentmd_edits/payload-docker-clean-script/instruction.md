# Fix docker:start reliability — orphan container conflicts

## Problem

Running `pnpm docker:start` fails with a container name conflict when orphan containers exist from a previous run or a different Docker Compose project. The current `docker compose down` only removes containers it manages, so leftover containers with the same names (e.g. `postgres-payload-test`, `mongodb-payload-test`) cause the `up` command to fail.

## Expected Behavior

`docker:start` should work reliably even when orphan containers exist. There should be a dedicated cleanup step that force-removes all named test containers before starting services. This cleanup logic should be a Node.js script (not inline shell) so it works cross-platform — suppressing the exit code of `docker rm -f` on missing containers requires platform-specific syntax.

The old `docker:stop` script should be replaced with a `docker:clean` script that does the full cleanup (force-remove named containers + compose down with volume removal).

## Files to Look At

- `package.json` — the `docker:start` and `docker:stop` npm scripts
- `scripts/` — existing Node.js helper scripts for cross-platform operations
- `test/docker-compose.yml` — Docker Compose config with named containers

After fixing the code, update the relevant documentation to reflect the renamed commands. The project's agent instructions and contributor guide reference the Docker workflow commands.
