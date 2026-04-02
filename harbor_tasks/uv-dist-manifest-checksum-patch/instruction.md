# Missing checksum verification in release installer scripts

## Problem

The uv release workflow builds platform-specific archives (`.tar.gz`, `.zip`) via custom jobs outside of cargo-dist. Each archive has a corresponding `.sha256` sidecar file uploaded as a build artifact. However, the generated installer shell scripts (`install.sh`) do **not** embed checksums for verifying downloaded archives.

cargo-dist supports embedding SHA-256 checksums into its generated installer scripts, but only if the checksums appear in the `dist-manifest.json` under each artifact's `"checksums"` field. Since the custom build jobs produce archives outside cargo-dist's control, the local dist manifest is missing these checksums.

## What needs to happen

1. A script is needed at `scripts/patch-dist-manifest-checksums.py` that:
   - Reads a cargo-dist local manifest JSON file
   - Scans an artifacts directory for `*.sha256` sidecar files
   - For each sidecar, looks up the matching artifact in the manifest (by stripping the `.sha256` suffix)
   - Injects the checksum into the artifact's `"checksums"` map under the `"sha256"` key
   - Writes the patched manifest back
   - Returns exit code 1 if no checksums were patched (safety check)
   - Warns on stderr about `.sha256` files that don't match any manifest artifact

2. The release workflow (`.github/workflows/release.yml`) needs a new job that:
   - Runs after the custom build jobs complete
   - Downloads the cached `dist` binary and all build artifacts
   - Generates a local dist manifest via `dist manifest`
   - Runs the patching script against that manifest and the artifacts directory
   - Uploads the patched manifest so the global artifact builder picks it up

3. The CI workflow (`.github/workflows/ci.yml`) needs its change-detection updated to recognize the new script and workflow file.

## Relevant files

- `scripts/patch-dist-manifest-checksums.py` (new)
- `.github/workflows/release.yml`
- `.github/workflows/ci.yml`
