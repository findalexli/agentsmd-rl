# example: restore .next handling for with-docker examples

## Problem

The `examples/with-docker/Dockerfile` has a BuildKit cache mount on `.next/cache` during the build stage that causes two problems:

1. **Fetch cache is trapped**: The build-time fetch cache (e.g., from `fetch()` calls during `getStaticProps`) is stored in a BuildKit cache volume that is NOT copied to the runner stage. This means cached fetch responses from the build aren't available at runtime.

2. **No writable cache directory**: The runner stage doesn't create or own the `.next` directory, so the server can't write prerender cache or optimized images at runtime.

The `Dockerfile.bun` variant also needs the `mkdir .next && chown` fix (though it never had the BuildKit mount issue).

## Expected Behavior

1. Remove the `--mount=type=cache,target=/app/.next/cache` from the build stage to allow fetch cache to be included in the build output
2. Add `mkdir .next && chown node:node .next` in the runner stage to create a writable directory for runtime cache
3. Add a commented-out `COPY --from=builder --chown=node:node /app/.next/cache ./.next/cache` line as opt-in for persisting build-time fetch cache
4. Apply the same `mkdir .next && chown` fix to `Dockerfile.bun` (using `bun:bun` ownership)
5. Update the README to use plain markdown bullets instead of emoji checkmarks (✅) in the features list

## Files to Look At

- `examples/with-docker/Dockerfile` — Main Dockerfile with the BuildKit mount issue
- `examples/with-docker/Dockerfile.bun` — Bun variant needing the mkdir/chown fix
- `examples/with-docker/README.md` — Documentation with emoji formatting to fix

## Related Issue

Closes #90648
