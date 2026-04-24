# Docker Image Cache Corruption via Turborepo

## Problem

The turborepo remote cache is corrupting or truncating the Docker image tarball (`target/docker-image.tar`) that is used to build Next.js native (SWC/Turbopack) binaries. When turbo restores the cached artifact, the resulting tar file is incomplete, causing `docker load` to fail silently or produce a broken image. This makes CI builds unreliable — the Docker image build step intermittently fails on cache hits.

The current architecture has the Docker image build wired as a turbo task (`build-docker-image` in `packages/next-swc/`), which saves a ~2.8GB tar to disk for turbo to cache as an output artifact. A separate post-turbo step (`--load`) then loads the tar into Docker. This two-phase approach through turborepo is where the corruption occurs.

## Expected Behavior

The Docker image caching should bypass turborepo task caching entirely and instead interact with the turbo remote cache API directly. The solution should:

- Compute a deterministic cache key from the input files (Dockerfile, toolchain config, etc.)
- Check the turbo remote cache API for a hit using a `turbo-cache.mjs` module
- On hit: stream the compressed image directly into `docker load`
- On miss: build the image, compress with zstd, and upload to the cache API
- No longer use turbo task runner for the Docker image build step

## API Contract

The `scripts/turbo-cache.mjs` module must export the following functions for use by `docker-image-cache.js`:

| Export | Description |
|--------|-------------|
| `artifactUrl(key)` | Returns the full artifact URL for a given cache key |
| `exists(key)` | Returns `true` if the artifact exists in cache |
| `get(key)` | Downloads artifact, returns `Buffer` on hit, `null` on miss |
| `getStream(key)` | Downloads artifact as a Node.js `Readable` stream |
| `put(key, data)` | Uploads artifact; `data` can be a `Buffer` or a file path string |
| `healthCheck()` | Verifies read/write access to the cache |

### URL Format Requirements

The `artifactUrl()` function must produce URLs with the correct path format depending on the `TURBO_API` hostname:

- **Vercel (TURBO_API = "https://vercel.com")**: URL must include the path `/api/v8/artifacts/{key}` and append `?teamId={team}` when `TURBO_TEAM` is set
- **Self-hosted servers**: URL must include the path `/v8/artifacts/{key}` (no `/api/` prefix) and append `?slug={team}` when `TURBO_TEAM` is set

The key used in path segments and query parameters must be the raw hex string passed to `artifactUrl()`.

## Script Requirements

### docker-image-cache.js

- Must be directly executable as a Node.js script (`#!/usr/bin/env node` shebang)
- Must use Node.js `parseArgs` from `node:util` to parse CLI arguments
- Must support a `--force` flag (via parseArgs `force` option) to bypass cache and always rebuild
- Must have a `buildImage()` function (not arrow function) that performs the actual `docker build` or `docker buildx` command
- Must import from `./turbo-cache.mjs` for all cache operations
- On cache miss: after building, compress with zstd (`docker save | zstd`) and upload via `turbo-cache.put()`
- On cache hit: decompress with zstd (`zstd -d`) and stream directly into `docker load`
- Must only import built-in Node.js modules (no external npm packages)

### docker-native-build.js

- Must call `docker-image-cache.js` directly via `node` + script path (e.g., `execFileSync('node', [path.join(__dirname, 'docker-image-cache.js'), ...])`)
- Must NOT invoke `pnpm -F @next/swc build-docker-image` (the turbo task invocation)

## Configuration Changes

- The `build-docker-image` script entry must be removed from `packages/next-swc/package.json`
- The `build-docker-image` task definition must be removed from `packages/next-swc/turbo.jsonc`
- The CI workflow (`build_and_deploy.yml`) should invoke `node scripts/docker-image-cache.js` directly, not via turbo

## Files to Look At

- `scripts/docker-image-cache.js` — Current Docker image build/cache script (needs rewrite)
- `scripts/docker-native-build.js` — Orchestrates Docker-based native builds, calls the cache script
- `scripts/turbo-cache.mjs` — New module providing turbo remote cache API client
- `packages/next-swc/package.json` — Contains the `build-docker-image` script entry
- `packages/next-swc/turbo.jsonc` — Turbo task configuration for the Docker image build
- `.github/workflows/build_and_deploy.yml` — CI workflow that triggers the Docker image build

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
