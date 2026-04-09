# Fix binary-size agent image name in CI

## Problem

The `binary-size` CI step is failing with an "Image not found" error from robobun. The issue is in how the agent configuration is constructed for this Buildkite step.

Currently, `getBinarySizeStep()` in the CI configuration file constructs a hand-built platform object when calling `getEc2Agent()`. This approach omits the `features` field that should include `["docker"]`.

Without the `features` field, `getImageKey()` generates an incorrect image name:
- **Incorrect**: `linux-aarch64-2023-amazonlinux-v29` (this AMI doesn't exist)
- **Correct**: `linux-aarch64-2023-amazonlinux-with-docker-v29`

## Expected Behavior

The `binary-size` step should use the same platform configuration as the `linux-aarch64-build-cpp` step. This configuration is available in the `buildPlatforms` array which already contains the correct platform object with all required fields including `features: ["docker"]`.

## Files to Look At

- `.buildkite/ci.mjs` — Contains `getBinarySizeStep()` function that needs to be fixed

## Hints

Look at how other steps in the same file configure their agents. The `buildPlatforms` array is defined elsewhere in the file and contains the full platform specifications. Find the entry for `linux-aarch64` with `amazonlinux` distro and reuse that instead of constructing a new object.
