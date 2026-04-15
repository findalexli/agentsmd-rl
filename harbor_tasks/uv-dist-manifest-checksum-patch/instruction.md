# Missing checksum verification in release installer scripts

## Problem

The uv release workflow builds platform-specific archives (`.tar.gz`, `.zip`) via custom jobs outside of cargo-dist. Each archive has a corresponding `.sha256` sidecar file uploaded as a build artifact. However, the generated installer shell scripts (`install.sh`) do **not** embed checksums for verifying downloaded archives.

cargo-dist supports embedding SHA-256 checksums into its generated installer scripts, but only if the checksums appear in the `dist-manifest.json` under each artifact's `"checksums"` field. Since the custom build jobs produce archives outside cargo-dist's control, the local dist manifest is missing these checksums.

## What needs to happen

1. A Python script at `scripts/patch-dist-manifest-checksums.py` that:
   - Accepts `--manifest` (path to a JSON manifest file) and `--artifacts-dir` (path to directory containing sidecar files) as required CLI arguments
   - Reads the manifest JSON file, which has this top-level structure:
     ```json
     {
       "artifacts": {
         "<artifact-filename>": {
           "name": "<artifact-filename>",
           "kind": "<kind-string>"
         }
       }
     }
     ```
     Each entry in the `"artifacts"` map is keyed by filename and contains at minimum `"name"` and `"kind"` fields.
   - Scans the artifacts directory for `*.sha256` sidecar files
   - Each sidecar file uses BSD-style checksum format: `<checksum>  <filename>\n` (the 64-character hex checksum followed by two spaces and the filename, one entry per line). The script reads the first whitespace-delimited token as the checksum value.
   - For each sidecar, looks up the matching artifact in the manifest by stripping the `.sha256` suffix from the sidecar filename
   - **Validates** each sidecar before injection:
     - If a sidecar file is empty (no content after stripping whitespace), the script must exit with a non-zero exit code
     - If the checksum value is not exactly 64 hex characters (the expected length of a SHA-256 hash), the script must exit with a non-zero exit code
   - Injects the checksum into the matching artifact entry under the key path `["checksums"]["sha256"]`, preserving all other existing fields on the artifact (such as `"name"`, `"kind"`, and any others)
   - Writes the patched manifest back to the same file as formatted JSON (2-space indented, with a trailing newline)
   - **Idempotent**: running the script twice on the same manifest and artifacts directory must produce an identical output manifest
   - Returns exit code 1 if no checksums were successfully patched (safety check — for example, when no sidecar files match any manifest artifact)
   - Prints a warning to stderr about `.sha256` files that don't match any manifest artifact, including the unmatched sidecar filename in the warning message so operators can identify stale or misnamed checksum files

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
