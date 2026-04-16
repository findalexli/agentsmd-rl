# Add Rust Toolchain Support to Docker Build

## Problem

The Apache Airflow Docker build infrastructure cannot compile Python packages that have Rust native extensions (e.g., `cryptography`, `pydantic-core`). When `pip install` encounters such a package, the build fails because `cargo` and `rustc` are missing from the Docker build environment.

The `check-that-image-builds-quickly` CI job currently has a `timeout-minutes` of 17 and a Breeze `--max-time` of 900 seconds, which are insufficient once the Rust toolchain installation is added — the job times out before completing.

## Existing Pattern

The repository already installs the Go toolchain in its Docker build configuration. The Rust toolchain addition should follow the same structural conventions (function definition style, variable setup, invocation within the build flow). Note that unlike Go (which is only needed for CI builds), Rust is required for all development builds.

## Relevant Files

- `Dockerfile`
- `Dockerfile.ci`
- `scripts/docker/install_os_dependencies.sh`
- `.github/workflows/additional-ci-image-checks.yml`

## Rustup Reference

Rust is installed via **rustup** (the installer binary is `rustup-init`).

**Version:** 1.29.0

**Architecture to Rust target triple mapping:**

| Debian arch | Rust target |
|---|---|
| amd64 | `x86_64-unknown-linux-gnu` |
| arm64 | `aarch64-unknown-linux-gnu` |

**SHA-256 checksums** for rustup-init 1.29.0 (available at `https://static.rust-lang.org/rustup/archive/1.29.0/{target}/rustup-init.sha256`):
- amd64: `4acc9acc76d5079515b46346a485974457b5a79893cfb01112423c89aeb5aa10`
- arm64: `9732d6c5e2a098d3521fca8145d826ae0aaa067ef2385ead08e6feac88fa5792`

**Security:** Downloads must use HTTPS-only with TLS 1.2+ via curl flags `--proto '=https'` and `--tlsv1.2`. The downloaded binary must be verified against its expected SHA-256 checksum using `sha256sum --check` before execution.

## Environment Setup

The Rust/Cargo directories should be configured as environment variables in the Dockerfiles:
- `RUSTUP_HOME` → `/usr/local/rustup`
- `CARGO_HOME` → `/usr/local/cargo`
- `PATH` must include the Cargo bin directory

Follow the same ENV declaration style used for Go toolchain variables.

## CI Timeout

Increase the `check-that-image-builds-quickly` job's `timeout-minutes` to 25 and the Breeze shell `--max-time` to 1320 seconds.
