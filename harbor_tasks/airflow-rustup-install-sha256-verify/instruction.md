# Task: Add rustup and cargo installation with SHA256 verification

## Problem

The Airflow build images need to install rustup and cargo to build Python wheels that have Rust components. The installation must meet the following requirements:

### Security Requirements

1. Download the rustup-init binary from `https://static.rust-lang.org/rustup/archive/${RUSTUP_VERSION}/${target}/rustup-init`
2. Verify the downloaded binary using SHA256 checksums before execution:
   - For x86_64 (amd64): `4acc9acc76d5079515b46346a485974457b5a79893cfb01112423c89aeb5aa10`
   - For aarch64 (arm64): `9732d6c5e2a098d3521fca8145d826ae0aaa067ef2385ead08e6feac88fa5792`
3. Use secure curl flags for downloading (`--proto '=https' --tlsv1.2`)

### Architecture Support

4. Support both amd64 and arm64 architectures (detect with `dpkg --print-architecture`)
5. Map amd64 architecture to the `x86_64-unknown-linux-gnu` target
6. Map arm64 architecture to the `aarch64-unknown-linux-gnu` target
7. Include error handling for unsupported architectures — output must be: `Unsupported architecture for rustup`

### Environment Variables

8. Set `RUSTUP_HOME` to `/usr/local/rustup`
9. Set `CARGO_HOME` to `/usr/local/cargo`
10. Set `RUSTUP_VERSION` with default value `1.29.0`
11. Set `RUSTUP_DEFAULT_TOOLCHAIN` with default value `stable`
12. Update `PATH` to include cargo's bin directory

### CI Workflow Adjustments

13. Extend the CI image build timeout from its current value to 25 minutes
14. Update the CI max-time parameter from 900 seconds to 1320 seconds

### Bug Fix

15. The CI Dockerfile currently has an incorrect cargo bin path in the PATH environment variable. The PATH should not include `/root/.cargo/bin`.

## Files to Modify

The changes should be made in:
- `scripts/docker/install_os_dependencies.sh` - implement rustup installation logic
- `Dockerfile` - set environment variables and call rustup installation
- `Dockerfile.ci` - set environment variables, call rustup installation, and fix PATH
- `.github/workflows/additional-ci-image-checks.yml` - update timeout values
