# Bug: UV installation in ROCm Dockerfile silently succeeds when curl fails

## Summary

In `docker/Dockerfile.rocm`, the UV package manager installation step can silently
succeed even when `curl` fails (e.g., due to a network timeout or DNS issue). This
means the Docker image builds to completion but `uv` is missing, causing mysterious
"uv: not found" errors in later build stages (e.g., `build_rixl`).

## Reproduction

Look at the UV installation step in `docker/Dockerfile.rocm` (around line 32). The
current command pipes `curl` output directly into `sh`. When `curl` times out or
encounters an SSL error, the pipe means `sh` reads empty stdin and exits with code 0.
Docker sees the successful exit code and continues the build.

This is a well-known shell anti-pattern: `curl ... | sh` masks the exit code of `curl`.

## Expected Behavior

If `curl` fails to download the UV install script, the Docker build should fail
immediately with a clear error, not proceed with a broken environment.

## Hints

- Think about how to ensure `curl` failures propagate properly
- Consider transient network issues that could benefit from retry logic
- The fix should verify that UV was actually installed successfully
