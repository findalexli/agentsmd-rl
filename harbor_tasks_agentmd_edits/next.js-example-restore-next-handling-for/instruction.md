# Fix Docker example: .next cache handling and runner permissions

## Problem

The `examples/with-docker/Dockerfile` uses a BuildKit cache mount (`--mount=type=cache,target=/app/.next/cache`) on the build step. This traps the Next.js fetch cache inside a BuildKit volume that is **not carried over** to the runner stage. As a result:

1. Fetch responses cached during `next build` are lost — they never make it into the final Docker image.
2. The runner stage has no writable `.next` directory, so the Next.js server cannot write prerender cache or optimized images at runtime. On some setups this causes permission errors or silent cache misses.

The same writable-directory issue affects `Dockerfile.bun`.

## Expected Behavior

- The build step should **not** bind the `.next/cache` directory to a BuildKit volume by default (it can be offered as an opt-in comment for users who want faster rebuilds and understand the trade-off).
- The runner stage must create a writable `.next` directory owned by the appropriate non-root user (`node` for the Node.js Dockerfile, `bun` for the Bun Dockerfile) **before** the standalone output is copied in. This lets the Next.js server write prerender cache and optimized images at runtime.
- Both Dockerfiles should offer an opt-in, commented-out `COPY` line for users who want to persist the build-time fetch cache into the final image.
- After fixing the Dockerfiles, update the relevant documentation to accurately describe the new cache behavior — in particular, the BuildKit cache mount description and the new writable `.next` directory feature.

## Files to Look At

- `examples/with-docker/Dockerfile` — Main Node.js Docker configuration
- `examples/with-docker/Dockerfile.bun` — Bun variant Docker configuration
- `examples/with-docker/README.md` — Documentation describing the Docker setup and its features
