# Fix Docker image digests and revert Node.js supervisor upgrade

## Problem

The Docker images in this repository are using architecture-specific digests instead of multiplatform/index digests. This causes CI build failures when builds run on different architectures (e.g., a digest pinned for `linux/amd64` fails on `linux/arm64` build runners).

Additionally, the Node.js supervisor was recently upgraded to v22.22.0, but this upgrade needs to be reverted back to the previous version (v22.12.0) due to compatibility issues.

## What needs to change

1. **`docker/Dockerfile`** — The `NODE_IMAGE` ARG uses a node 20 image with an architecture-specific digest. Replace it with the correct multiplatform digest. Also use the minor version tag (e.g., `20.20`) instead of the full patch version (`20.20.0`).

2. **`apps/supervisor/Containerfile`** — The FROM line pins to `node:22.22.0-alpine` with an architecture-specific digest. Revert to a non-patch-pinned tag (e.g., `node:22-alpine`) and use the correct multiplatform digest.

3. **`apps/supervisor/.nvmrc`** — Revert the Node.js version from `v22.22.0` back to `v22.12.0`.

4. After making these fixes, update the project's `CLAUDE.md` to document Docker image guidelines so future contributors know to always use multiplatform/index digests rather than architecture-specific ones. This will prevent the same mistake from happening again.

## Files to Look At

- `docker/Dockerfile` — Main Docker image definition
- `apps/supervisor/Containerfile` — Supervisor container definition
- `apps/supervisor/.nvmrc` — Node.js version for supervisor
- `CLAUDE.md` — Project guidelines for contributors and AI agents
