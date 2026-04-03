#!/usr/bin/env bash
set -euo pipefail

cd /workspace/uv

# Idempotent: skip if already applied
if grep -q 'normalize-pe-timestamps' crates/uv-trampoline-builder/Cargo.toml 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# --- 1. Create normalize-pe-timestamps.rs ---
mkdir -p crates/uv-trampoline-builder/src/bin
cat > crates/uv-trampoline-builder/src/bin/normalize-pe-timestamps.rs << 'RUSTEOF'
//! Zero out non-deterministic fields in PE executables.
//!
//! Even with the `/Brepro`, the PE timestamp and debug directory GUID change
//! between builds. We have to zero out those fields so the final binaries are
//! byte-for-byte reproducible.
//!
//! Fields zeroed:
//! - COFF header `TimeDateStamp`
//! - Each `IMAGE_DEBUG_DIRECTORY` `TimeDateStamp`
//! - `CodeView` PDB70 `Signature` (GUID) and `Age`

use std::env;

use anyhow::{Context, Result, bail, format_err};
use goblin::pe::PE;
use goblin::pe::debug::{IMAGE_DEBUG_TYPE_CODEVIEW, ImageDebugDirectory};
use goblin::pe::section_table::SectionTable;
use uv_fs::Simplified;

/// Collected fixup locations from the PE parse.
struct DebugEntryFixup {
    /// File offset of this `IMAGE_DEBUG_DIRECTORY` entry.
    entry_file_offset: usize,
    /// The `IMAGE_DEBUG_DIRECTORY.data_type` field.
    data_type: u32,
    /// The `IMAGE_DEBUG_DIRECTORY.pointer_to_raw_data` field (file offset of the payload).
    pointer_to_raw_data: u32,
}

/// Resolve an RVA to a file offset using the PE section table.
fn rva_to_file_offset(sections: &[SectionTable], rva: u32) -> Option<usize> {
    sections.iter().find_map(|section| {
        if rva >= section.virtual_address && rva < section.virtual_address + section.virtual_size {
            Some((rva - section.virtual_address + section.pointer_to_raw_data) as usize)
        } else {
            None
        }
    })
}

fn parse_debug_entries(data: &mut [u8]) -> Result<(usize, Vec<DebugEntryFixup>)> {
    let pe = PE::parse(data)?;

    // COFF header: pe_pointer -> "PE\0\0" (4 bytes) -> CoffHeader fields.
    // `CoffHeader.time_date_stamp` is the second u32 field (offset 4).
    let coff_timestamp_offset = pe.header.dos_header.pe_pointer as usize + 4 + 4;

    let mut debug_entries = Vec::new();
    if let Some(debug_data_directory) = pe
        .header
        .optional_header
        .and_then(|opt| opt.data_directories.get_debug_table().copied())
    {
        if let Some(debug_data) = &pe.debug_data {
            let debug_dir_file_offset =
                rva_to_file_offset(&pe.sections, debug_data_directory.virtual_address)
                    .ok_or_else(|| format_err!("cannot resolve debug directory RVA"))?;
            let entry_size = size_of::<ImageDebugDirectory>();

            for (i, entry) in debug_data.entries().enumerate() {
                let entry = entry?;
                debug_entries.push(DebugEntryFixup {
                    entry_file_offset: debug_dir_file_offset + i * entry_size,
                    data_type: entry.data_type,
                    pointer_to_raw_data: entry.pointer_to_raw_data,
                });
            }
        }
    }

    Ok((coff_timestamp_offset, debug_entries))
}

fn clear_debug_entries(
    data: &mut [u8],
    coff_timestamp_offset: usize,
    debug_entries: &[DebugEntryFixup],
) {
    // Zero COFF header `TimeDateStamp`.
    data[coff_timestamp_offset..coff_timestamp_offset + 4].fill(0);

    // Zero debug directory timestamps and CodeView GUIDs.
    for entry in debug_entries {
        // Zero `IMAGE_DEBUG_DIRECTORY.time_date_stamp` (offset 4 in the struct).
        let timestamp_offset = entry.entry_file_offset + 4;
        data[timestamp_offset..timestamp_offset + 4].fill(0);

        if entry.data_type == IMAGE_DEBUG_TYPE_CODEVIEW {
            // PDB70 layout: magic[4] ("RSDS") | guid[16] | age[4] | filename...
            let payload = entry.pointer_to_raw_data as usize;
            data[payload + 4..payload + 20].fill(0); // Signature (GUID)
            data[payload + 20..payload + 24].fill(0); // Age
        }
    }
}

fn main() -> Result<()> {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        bail!("Usage: {} <file.exe> [...]", args[0]);
    }
    for path in &args[1..] {
        let mut data = fs_err::read(path)?;
        let (coff_timestamp_offset, debug_entries) = parse_debug_entries(&mut data)
            .with_context(|| format!("Failed to normalize: {}", path.user_display()))?;
        clear_debug_entries(&mut data, coff_timestamp_offset, &debug_entries);
        fs_err::write(path, &data)?;
    }
    Ok(())
}
RUSTEOF

# --- 2. Create Dockerfile for reproducible builds ---
cat > crates/uv-trampoline/Dockerfile << 'DOCKEREOF'
# Reproducible cross-compilation environment for Windows trampolines.
#
# All toolchain versions are pinned for binary reproducibility.
# This image provides the build environment; the workspace is bind-mounted
# at runtime by scripts/build-trampolines.sh.

ARG UBUNTU_SNAPSHOT=20260127T200000Z

ARG RUST_NIGHTLY=nightly-2025-11-02

ARG CARGO_XWIN_VERSION=0.21.4
ARG XWIN_SDK_VERSION=10.0.22621
ARG XWIN_CRT_VERSION=14.44.17.14

FROM ubuntu:26.04@sha256:4095ef613201918336b5d7d00be15d8b09c72ddb77c80bca249c255887a64d87 AS base

ARG RUST_NIGHTLY
ARG UBUNTU_SNAPSHOT

ENV HOME=/app
ENV CARGO_HOME=${HOME}/rust/cargo
ENV RUSTUP_HOME=${HOME}/rust/rustup
ENV XWIN_CACHE_DIR=${HOME}/xwin-cache

WORKDIR ${HOME}

# Install build dependencies
RUN apt install -y --update ca-certificates && \
    apt install -y --update --snapshot ${UBUNTU_SNAPSHOT} \
        curl \
        llvm \
        clang \
        lld \
    && ln -s /usr/bin/llvm-mt /usr/bin/mt.exe \
    && rm -rf /var/lib/apt/lists/*

# Install Rust nightly toolchain with Windows targets
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | \
    sh -s -- -y --default-toolchain=${RUST_NIGHTLY} --profile=minimal

ENV PATH="${CARGO_HOME}/bin:${PATH}"

RUN rustup component add rust-src --toolchain ${RUST_NIGHTLY}-x86_64-unknown-linux-gnu && \
    rustup target add --toolchain ${RUST_NIGHTLY} \
        i686-pc-windows-msvc \
        x86_64-pc-windows-msvc \
        aarch64-pc-windows-msvc

# Install cargo-xwin and prefetch the Windows SDK/CRT
FROM base AS xwin-cache

ARG CARGO_XWIN_VERSION
ARG XWIN_SDK_VERSION
ARG XWIN_CRT_VERSION

RUN cargo install cargo-xwin@${CARGO_XWIN_VERSION}

RUN cargo xwin cache xwin \
      --xwin-sdk-version ${XWIN_SDK_VERSION} \
      --xwin-crt-version ${XWIN_CRT_VERSION} \
      --xwin-arch x86,x86_64,aarch64

FROM base

COPY --chmod=a+rwX --from=xwin-cache ${HOME}/xwin-cache ${HOME}/xwin-cache
RUN chmod a+w ${HOME}/xwin-cache
COPY --from=xwin-cache ${CARGO_HOME}/bin/cargo-xwin ${CARGO_HOME}/bin/cargo-xwin
DOCKEREOF

# --- 3. Create build script ---
cat > scripts/build-trampolines.sh << 'SCRIPTEOF'
#!/bin/bash
# Build all Windows trampoline executables reproducibly using Docker.
#
# Extra arguments are forwarded to the docker build command

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TRAMPOLINE_DIR="$REPO_ROOT/crates/uv-trampoline"
OUTPUT_DIR="$REPO_ROOT/crates/uv-trampoline-builder/trampolines"

# Read the nightly toolchain from rust-toolchain.toml
TOOLCHAIN="$(grep '^channel' "$TRAMPOLINE_DIR/rust-toolchain.toml" | sed 's/.*"\(.*\)"/\1/')"

# Build the pinned toolchain image.
docker buildx build -t uv-trampoline-builder --load \
    -f "$TRAMPOLINE_DIR/Dockerfile" "$TRAMPOLINE_DIR" \
    "$@"

# Build trampolines inside the container with the workspace bind-mounted.
# The working directory must be the trampoline crate so cargo picks up
# .cargo/config.toml (which enables build-std).
docker run --rm \
    -v "$REPO_ROOT:/workspace:ro" \
    -v "$OUTPUT_DIR:/output" \
    -w /workspace/crates/uv-trampoline \
    uv-trampoline-builder \
    bash -c '
        set -euo pipefail
        export CARGO_TARGET_DIR=/tmp/target

        cargo +"'"$TOOLCHAIN"'" xwin build --xwin-arch x86 --release --target i686-pc-windows-msvc
        cargo +"'"$TOOLCHAIN"'" xwin build --release --target x86_64-pc-windows-msvc
        cargo +"'"$TOOLCHAIN"'" xwin build --release --target aarch64-pc-windows-msvc

        for arch in i686 x86_64 aarch64; do
            for variant in console gui; do
                cp /tmp/target/$arch-pc-windows-msvc/release/uv-trampoline-$variant.exe \
                    /output/uv-trampoline-$arch-$variant.exe
            done
        done
    '

# Zero out non-deterministic PE fields (timestamps, debug GUIDs) so that
# builds are byte-for-byte reproducible despite LLVM non-determinism.
cargo run --quiet -p uv-trampoline-builder --bin normalize-pe-timestamps -- "$OUTPUT_DIR"/*.exe

echo "Done. Trampolines written to $OUTPUT_DIR"
SCRIPTEOF
chmod +x scripts/build-trampolines.sh

# --- 4. Append /Brepro flag to .cargo/config.toml ---
cat >> crates/uv-trampoline/.cargo/config.toml << 'TOMLEOF'

# Make PE binaries reproducible: replace timestamps and debug GUIDs with
# content hashes so identical source produces identical bytes.
[target.'cfg(windows)']
rustflags = ["-C", "link-arg=/Brepro"]
TOMLEOF

# --- 5. Add pe32/pe64 features to goblin in root Cargo.toml ---
sed -i '/"endian_fd",/a\  "pe32",\n  "pe64",' Cargo.toml

# --- 6. Update uv-trampoline-builder/Cargo.toml ---
# Add [[bin]] section before [lints]
sed -i '/^\[lints\]$/i\[[bin]]\nname = "normalize-pe-timestamps"\n' crates/uv-trampoline-builder/Cargo.toml

# Add anyhow and goblin dependencies
sed -i '/^fs-err = { workspace = true }$/i\anyhow = { workspace = true }' crates/uv-trampoline-builder/Cargo.toml
sed -i '/^fs-err = { workspace = true }$/a\goblin = { workspace = true }' crates/uv-trampoline-builder/Cargo.toml

# --- 7. Update README.md to document Docker-based build ---
python3 << 'PYEOF'
p = "crates/uv-trampoline/README.md"
c = open(p).read()
insert = """
The trampolines checked into the repo use a reproducible dockerfile for auditing.

```shell
scripts/build-trampolines.sh
```

The other build options exist for local development.

"""
c = c.replace(
    "## Building\n\n### Cross-compiling",
    "## Building\n" + insert + "### Cross-compiling",
)
open(p, "w").write(c)
PYEOF

echo "Patch applied successfully."
