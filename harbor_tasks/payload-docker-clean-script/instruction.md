# Fix docker:start reliability — orphan container conflicts

## Problem

Running `pnpm docker:start` fails with a container name conflict when orphan containers exist from a previous run or a different Docker Compose project. The current `docker compose down` only removes containers it manages, so leftover containers with the same names (e.g. `postgres-payload-test`, `mongodb-payload-test`) cause the `up` command to fail.

## Expected Behavior

`docker:start` should work reliably even when orphan containers exist. There should be a dedicated cleanup step that force-removes all named test containers before starting services.

This cleanup logic must live in a new Node.js script at **`scripts/docker-clean.js`** (not inline shell) so it works cross-platform. The script must:

1. Use Node.js **`child_process`** (e.g. `execSync`) to run docker commands.
2. Force-remove the named test containers using **`docker rm`**, including at minimum:
   - `postgres-payload-test`
   - `mongodb-payload-test`
3. Run **`docker compose down`** (with volume removal) for a full teardown.

The old `docker:stop` npm script should be **removed** from `package.json` and replaced with a `docker:clean` script that invokes `scripts/docker-clean.js`. The `docker:start` script must be updated to call `docker:clean` before bringing services up with `docker compose up`.

## Files to Look At

- `package.json` — the `docker:start` and `docker:stop` npm scripts
- `scripts/` — existing Node.js helper scripts for cross-platform operations
- `test/docker-compose.yml` — Docker Compose config with named containers

After fixing the code, update the relevant documentation to reflect the renamed commands. The project's agent instructions and contributor guide reference the Docker workflow commands.
