# Docker Image Cache Corruption in CI Builds

## Problem

The Next.js CI pipeline uses turborepo's remote cache to cache Docker images for native SWC builds. The caching works by:

1. Running a turbo task (`build-docker-image` in `packages/next-swc`) that builds the image and saves it as `target/docker-image.tar`
2. Turbo caches this tar file via remote cache
3. A post-turbo step (`node scripts/docker-image-cache.js --load`) loads the tar into Docker

However, the turborepo cache frequently corrupts or truncates the Docker image tar file. When this happens, `docker load` fails with corrupt data, causing the entire CI build to fail. The tar files are large (~2.8GB), and turbo's caching mechanism doesn't reliably handle artifacts of this size.

## Relevant Files

- `scripts/docker-image-cache.js` — The main caching script (both turbo task and post-turbo loader)
- `scripts/docker-native-build.js` — Invokes the docker image build via turbo task
- `.github/workflows/build_and_deploy.yml` — CI workflow that orchestrates the build
- `packages/next-swc/package.json` — Contains the `build-docker-image` script
- `packages/next-swc/turbo.jsonc` — Turbo configuration for the docker task

## Expected Behavior

Docker images should be cached and restored reliably in CI without corruption.

## Current Behavior

The turbo remote cache intermittently corrupts or truncates the Docker image tar file, causing `docker load` to fail and breaking CI builds.

## Hints

- The corruption originates in the caching layer, not in the Docker build itself
- Consider whether the current two-step flow (turbo task + post-turbo load) is necessary
- The cache key should be derived from files that determine Docker image content
- Think about how to make the caching more robust for large binary artifacts
