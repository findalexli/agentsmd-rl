# Fix docker:start reliability — orphan container conflicts

## Problem

Running `pnpm docker:start` fails with a container name conflict when orphan containers exist from a previous run or a different Docker Compose project. The current `docker compose down` only removes containers it manages, so leftover containers with the same names cause the `up` command to fail.

## Expected Behavior

`docker:start` should work reliably even when orphan containers exist. There should be a dedicated cleanup step that force-removes all named test containers before starting services.

The cleanup logic must live in a new **Node.js script** (not inline shell) so it works cross-platform. The script must:

1. Use Node.js **`child_process`** to run docker commands.
2. Force-remove the named test containers using **docker rm**.
3. Run **`docker compose down`** (with volume removal) for a full teardown.

The old npm script that just stops services should be **removed** from `package.json` and replaced with a new cleanup script. The `docker:start` script must be updated to call the cleanup step before bringing services up.

## Files to Look At

- `package.json` — the docker npm scripts
- `scripts/` — existing Node.js helper scripts for cross-platform operations
- `test/docker-compose.yml` — Docker Compose config with named containers

After fixing the code, update the relevant documentation to reflect any renamed commands. The project's agent instructions and contributor guide reference the Docker workflow commands.