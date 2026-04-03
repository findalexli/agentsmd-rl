# Reproducible Windows Trampoline Builds

## Problem

The Windows trampoline executables (`.exe` files in `crates/uv-trampoline-builder/trampolines/`) are built by cross-compiling the `crates/uv-trampoline` crate, but the builds are not reproducible. Even with identical source code, each build produces different binaries because the MSVC linker embeds non-deterministic data into the PE format: the COFF header timestamp, debug directory timestamps, and the CodeView PDB70 signature GUID all change between builds.

This means there's no way to audit whether the committed `.exe` files were actually built from the expected source, and CI cannot verify reproducibility.

## Expected Behavior

The trampoline build process should be fully reproducible — identical source must always produce byte-for-byte identical output:

1. A containerized build environment with pinned toolchain versions ensures the same compiler, linker, and SDK are used every build.
2. Non-deterministic PE fields (timestamps, debug GUIDs) must be zeroed out post-build so identical source always produces identical bytes. This requires a dedicated tool that parses PE structure, locates the relevant fields via RVA-to-file-offset resolution, and clears them.
3. A single entry-point script should orchestrate the Docker build and post-processing for all three target architectures (`i686-pc-windows-msvc`, `x86_64-pc-windows-msvc`, `aarch64-pc-windows-msvc`).
4. The Rust compiler's `/Brepro` linker flag should be enabled to use content-based hashes instead of timestamps where possible.

## Files to Look At

- `crates/uv-trampoline/` — the trampoline crate (source, cargo config, build settings)
- `crates/uv-trampoline-builder/` — houses the prebuilt trampoline executables and build tooling; the PE normalization binary should live here
- `Cargo.toml` — workspace dependency configuration (the `goblin` crate is already used for ELF parsing and can be extended with PE features)
- `crates/uv-trampoline/README.md` — build instructions that should be updated to document the new primary build method

After implementing the reproducible build infrastructure, update the trampoline README to document the Docker-based build as the primary method for producing the committed executables. The existing cross-compilation docs for local development should be preserved.
