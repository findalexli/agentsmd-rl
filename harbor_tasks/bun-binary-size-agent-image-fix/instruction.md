# Fix binary-size agent image name generation

## Problem

The `binary-size` CI step fails with an "Image not found" error from robobun. The error occurs because the generated AMI name is missing the `-with-docker` suffix.

**Incorrect image name generated:** `linux-aarch64-2023-amazonlinux-v29` (this AMI does not exist)  
**Correct image name expected:** `linux-aarch64-2023-amazonlinux-with-docker-v29`

The AMI name is constructed by `getImageKey()` based on platform configuration objects that should include a `features` array. When the `features` field is missing or empty, the generated image key lacks the `-with-docker` suffix, causing the image lookup to fail.

## Expected Outcome

Your solution must generate the correct image name (`linux-aarch64-2023-amazonlinux-with-docker-v29`) for the binary-size step's EC2 agent.

The implementation must:

- Use `buildPlatforms.find()` to locate the correct platform configuration
- Filter using the criteria: `p.os === "linux"`, `p.arch === "aarch64"`, and `p.distro === "amazonlinux"`
- NOT use a hand-built platform object literal containing `os: "linux"`, `arch: "aarch64"`, `distro: "amazonlinux"`, `release: "2023"`
- Return a step object containing the properties: `key`, `label`, `agents`, and `depends_on`

## Context

The codebase contains a `buildPlatforms` array with full platform specifications including `features: ["docker"]` fields. The `getImageKey()` function uses the `features` array to determine the image name suffix. Platform objects in this codebase have the structure: `{ os, arch, distro, release, features: [...] }`.

The `linux-aarch64-build-cpp` step in the CI configuration uses a platform object with `features: ["docker"]` and generates the correct image name. The binary-size step should use equivalent platform configuration.
