# Bug: Hard-float detection fails on aarch64 kernels running armv7 userspace

## Context

When running `uv` inside an armv7l container on an aarch64 host (or on 32-bit Raspberry Pi OS atop 64-bit hardware), `uv` incorrectly selects the soft-float (`gnueabi`) Python variant instead of the hard-float (`gnueabihf`) variant.

## Symptoms

- `uv python install` downloads a `gnueabi` (soft-float) build even though the hardware fully supports hardware floating-point.
- This only occurs when an ARM 32-bit userspace runs on a 64-bit ARM kernel.

## Root cause area

The hardware floating-point detection logic lives in `crates/uv-platform/src/cpuinfo.rs`, in the function `detect_hardware_floating_point_support`. It reads `/proc/cpuinfo` to determine whether the CPU supports hardware floating-point operations, which dictates whether the `gnueabihf` or `gnueabi` ABI is selected.

The problem is that the feature flags reported by `/proc/cpuinfo` differ between native ARM kernels and aarch64 kernels running 32-bit userspace. On a native 32-bit ARM kernel, hardware float support is indicated by one set of flags, but on an aarch64 kernel the same capability is advertised with a different flag name. The current detection only checks for the native ARM flag.

## What to fix

Update the feature detection logic in `crates/uv-platform/src/cpuinfo.rs` so that it correctly identifies hardware floating-point support in both:

1. Native ARM 32-bit systems
2. ARM 32-bit userspace running on an aarch64 64-bit kernel

Be careful to avoid false positives from unrelated flags that happen to share character sequences with the target flags.
