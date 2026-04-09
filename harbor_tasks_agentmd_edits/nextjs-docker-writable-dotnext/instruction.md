# Fix .next directory handling in Docker examples

## Problem

The Docker example at `examples/with-docker/` has a broken production setup. The runner stage cannot write prerender cache because the `.next` directory does not exist and is not writable by the application user.

Additionally, the builder stage uses a BuildKit cache mount on `/app/.next/cache` which traps the fetch cache in a Docker volume, making it unreachable in the final runner image. This means cached fetch responses from build time are silently discarded.

## Expected Behavior

After fixing, the Docker example should:
- Create a writable `.next` directory in the runner stage so the server can write prerender cache and optimized images at runtime
- Remove the cache mount that prevents fetch cache from reaching the runner stage (but leave an optional way to re-enable it for build speed)
- Apply the same fix to both `Dockerfile` (Node.js) and `Dockerfile.bun` (Bun)

## Files to Look At

- `examples/with-docker/Dockerfile` — the main Dockerfile; the builder stage's RUN command and the runner stage need changes
- `examples/with-docker/Dockerfile.bun` — the Bun variant; needs the same runner-stage fix
- `examples/with-docker/README.md` — the example's documentation; update the Highlights section to describe the writable `.next` directory and the optional cache mount approach
- `examples/with-docker-export-output/README.md` — related example README that also needs style updates

The project's AGENTS.md instructs that README files in subdirectories should be consulted before editing. Make sure to update the relevant documentation to reflect your changes.
