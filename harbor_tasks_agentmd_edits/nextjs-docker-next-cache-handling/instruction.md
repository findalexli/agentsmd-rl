# Fix Docker example .next cache handling and documentation

## Problem

The `examples/with-docker/Dockerfile` has a broken BuildKit cache mount configuration that causes issues with the fetch cache at runtime. The BuildKit cache mount on `.next/cache` traps the fetch cache in a volume that's unreachable by the runner stage. This means:

1. The fetch cache generated during build isn't available at runtime
2. The `.next` directory isn't writable by the `node` user, causing runtime errors when Next.js tries to write prerender cache or optimized images

## Changes Needed

You need to update the Docker example to properly handle the `.next` directory:

1. **Fix the Dockerfile** (`examples/with-docker/Dockerfile`):
   - Remove the BuildKit cache mount on `.next/cache` that traps the fetch cache
   - Add `mkdir .next` and `chown node:node .next` in the runner stage to ensure the directory is writable
   - Add a commented-out `COPY` line showing how to optionally persist the fetch cache from build

2. **Fix the Bun Dockerfile** (`examples/with-docker/Dockerfile.bun`):
   - Add the same `mkdir .next` and `chown bun:bun .next` setup in the runner stage
   - Add the same commented-out `COPY` line for optional fetch cache persistence

3. **Update the README** (`examples/with-docker/README.md`):
   - Update the "BuildKit cache mounts" documentation line to clarify it only caches package manager stores (not `.next/cache` by default)
   - Add documentation about the "Writable `.next` directory" explaining why it's created and owned by the `node` user
   - Convert the "Node.js Version Maintenance" warning from a bold warning to a proper `[!IMPORTANT]` callout block
   - Update the `Dockerfile.bun` section to mention the writable `.next` directory

4. **Update the export output README** (`examples/with-docker-export-output/README.md`):
   - Convert feature list from emoji bullets to plain bullets
   - Convert the "Version Maintenance" warning to a proper `[!IMPORTANT]` callout block

These changes fix the Docker examples to be production-ready with correct cache handling and up-to-date documentation.
