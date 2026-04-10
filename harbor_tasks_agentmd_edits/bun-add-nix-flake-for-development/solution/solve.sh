#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotent: skip if already applied
if [ -f flake.nix ] && grep -q 'builtins.fetchGit' flake.nix 2>/dev/null; then
    echo 'Patch already applied.'
    exit 0
fi

# Create flake.nix
cat > flake.nix << 'FLAKE_EOF'
{
  description = "Bun: JavaScript runtime & toolkit";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        llvmPackages = pkgs.llvmPackages_19;

        commonBuildInputs = with pkgs; [
          llvmPackages.clang
          llvmPackages.llvm
          llvmPackages.lld
          llvmPackages.libclang
          cmake
          ninja
          python3
          git
          zlib
          pkg-config
          jq
        ];
      in
      {
        packages = {
          default = pkgs.stdenv.mkDerivation {
            name = "bun";
            src = builtins.fetchGit {
              url = ./.;
              sha256 = null;
            };

            nativeBuildInputs = commonBuildInputs;

            buildPhase = ''
              export CC=clang
              export CXX=clang++
              cmake -B build -S . -GNinja \
                -DCMAKE_BUILD_TYPE=Release
              ninja -C build
            '';

            installPhase = ''
              mkdir -p $out/bin
              cp build/bun $out/bin/
            '';
          };
        };

        devShells = {
          default = pkgs.mkShell {
            name = "bun-dev-shell";

            nativeBuildInputs = commonBuildInputs;

            buildInputs = with pkgs; [
              zig
              rustc
              cargo
              nodejs
              yarn
            ];

            shellHook = ''
              export CC=clang
              export CXX=clang++
              export LLVM_PATH="${llvmPackages.llvm}"
              export CLANG_PATH="${llvmPackages.clang}"

              echo "Bun development environment loaded"
              echo "LLVM 19: ${llvmPackages.llvm}"
              echo "Clang: ${llvmPackages.clang}"
              echo "Run 'cmake -B build -S . && ninja -C build' to build"
            '';
          };
        };
      });
}
FLAKE_EOF

# Create shell.nix
cat > shell.nix << 'SHELL_EOF'
{ pkgs ? import <nixpkgs> {} }:

let
  llvmPackages = pkgs.llvmPackages_19;
in
pkgs.mkShell {
  name = "bun-dev-shell";

  nativeBuildInputs = with pkgs; [
    llvmPackages.clang
    llvmPackages.llvm
    llvmPackages.lld
    llvmPackages.libclang
    cmake
    ninja
    python3
    git
    zlib
    pkg-config
    jq
    zig
  ];

  shellHook = ''
    export CC=clang
    export CXX=clang++
    echo "Bun development shell (non-flake)"
  '';
}
SHELL_EOF

# Now we need to modify cmake/CompilerFlags.cmake
# Read the current file and create modified version
python3 << 'PYTHON_EOF'
import re

# Read the original file
with open('cmake/CompilerFlags.cmake', 'r') as f:
    content = f.read()

# Fix 1: Make the debug symbol compression conditional
# Find the section with -gz=zstd and make it conditional
old_debug_section = '''  register_compiler_flags(
    DESCRIPTION "Enable debug symbols"
    -g3 -gz=zstd ${DEBUG}
    -g1 ${RELEASE}
  )'''

new_debug_section = '''  # When building with Nix, use zlib compression and skip _FORTIFY_SOURCE
  # since Nix's glibc already sets it, and zstd may not be available in the Nix shell
  if(DEFINED ENV{NIX_CC})
    register_compiler_flags(
      DESCRIPTION "Enable debug symbols (Nix compatibility)"
      -g3 -gz=zlib ${DEBUG}
      -g1 ${RELEASE}
    )
  else()
    register_compiler_flags(
      DESCRIPTION "Enable debug symbols"
      -g3 -gz=zstd ${DEBUG}
      -g1 ${RELEASE}
    )
  endif()'''

if old_debug_section in content:
    content = content.replace(old_debug_section, new_debug_section)
    print("Updated debug symbols section")
else:
    print("WARNING: Could not find debug symbols section to replace")

# Fix 2: Make _FORTIFY_SOURCE conditional in the assertions section
# Find and wrap the _FORTIFY_SOURCE definition with NIX_CC guard
old_fortify = '''  register_compiler_definitions(
    DESCRIPTION "Enable fortified sources"
    _FORTIFY_SOURCE=3
  )'''

new_fortify = '''  # Nix glibc already sets _FORTIFY_SOURCE, so skip it in Nix builds
  if(DEFINED ENV{NIX_CC})
    # Nix handles _FORTIFY_SOURCE in its stdenv
  else()
    register_compiler_definitions(
      DESCRIPTION "Enable fortified sources"
      _FORTIFY_SOURCE=3
    )
  endif()'''

if old_fortify in content:
    content = content.replace(old_fortify, new_fortify)
    print("Updated _FORTIFY_SOURCE section")
else:
    print("WARNING: Could not find _FORTIFY_SOURCE section to replace")

# Write the modified file
with open('cmake/CompilerFlags.cmake', 'w') as f:
    f.write(content)

print("cmake/CompilerFlags.cmake updated successfully")
PYTHON_EOF

# Modify CONTRIBUTING.md to add Nix section
python3 << 'PYTHON_EOF'
import re

# Read the original file
with open('CONTRIBUTING.md', 'r') as f:
    content = f.read()

# Find the position after the "don't commit changes to node_modules" note
# and before "## Installing Dependencies"
nix_section = '''## Using Nix

If you're using the [Nix package manager](https://nixos.org/), you can quickly set up a development environment with all dependencies and build tools using:

```sh
nix develop
```

This will drop you into a shell with LLVM 19, Zig, and all other necessary dependencies to build Bun from source.

Alternatively, if you don't have flakes enabled, you can use:

```sh
nix-shell
```

To build with Nix (requires [nix flakes](https://nixos.wiki/wiki/Flakes)):

```sh
nix build
```

The Nix environment is particularly useful for reproducible builds and avoiding "works on my machine" issues.

'''

# Insert before "## Install Dependencies"
if '## Using Nix' not in content:
    content = content.replace('## Install Dependencies', nix_section + '## Install Dependencies')
    print("Added Nix section to CONTRIBUTING.md")
else:
    print("Nix section already exists in CONTRIBUTING.md")

# Rename "## Building" to "## Manual Building"
if '## Building' in content and '## Manual Building' not in content:
    content = content.replace('## Building', '## Manual Building')
    print("Renamed '## Building' to '## Manual Building'")

# Write the modified file
with open('CONTRIBUTING.md', 'w') as f:
    f.write(content)

print("CONTRIBUTING.md updated successfully")
PYTHON_EOF

echo 'All changes applied successfully.'
