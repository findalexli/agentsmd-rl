# Docker Image Cache Corruption via Turborepo

## Problem

The turborepo remote cache is corrupting or truncating the Docker image tarball (`target/docker-image.tar`) that is used to build Next.js native (SWC/Turbopack) binaries. When turbo restores the cached artifact, the resulting tar file is incomplete, causing `docker load` to fail silently or produce a broken image. This makes CI builds unreliable — the Docker image build step intermittently fails on cache hits.

The current architecture has the Docker image build wired as a turbo task (`build-docker-image` in `packages/next-swc/`), which saves a ~2.8GB tar to disk for turbo to cache as an output artifact. A separate post-turbo step (`--load`) then loads the tar into Docker. This two-phase approach through turborepo is where the corruption occurs.

## Expected Behavior

The Docker image caching should bypass turborepo task caching entirely and instead interact with the turbo remote cache API directly. The script should:
- Compute a deterministic cache key from the input files (Dockerfile, toolchain config, etc.)
- Check the turbo remote cache API for a hit
- On hit: stream the compressed image directly into `docker load`
- On miss: build the image, compress with zstd, and upload to the cache API
- No longer use turbo task runner for the Docker image build step

## Files to Look At

- `scripts/docker-image-cache.js` — Current Docker image build/cache script (needs rewrite)
- `scripts/docker-native-build.js` — Orchestrates Docker-based native builds, calls the cache script
- `packages/next-swc/package.json` — Contains the `build-docker-image` script entry
- `packages/next-swc/turbo.jsonc` — Turbo task configuration for the Docker image build
- `.github/workflows/build_and_deploy.yml` — CI workflow that triggers the Docker image build
