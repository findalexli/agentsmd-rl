#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotent: skip if already applied
if grep -q 'builtins.fetchGit' flake.nix 2>/dev/null; then
    echo 'Patch already applied.'
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply - <<'PATCH'
diff --git a/CONTRIBUTING.md b/CONTRIBUTING.md
index 6c3502f..e9a348a 100644
--- a/CONTRIBUTING.md
+++ b/CONTRIBUTING.md
@@ -10,6 +10,31 @@ The best way to learn about Bun's codebase is to read it. If something is confus

 Please don't commit changes to `node_modules` in your pull request, even if you modified dependencies in `package.json`.

+## Using Nix
+
+If you're using the [Nix package manager](https://nixos.org/), you can quickly set up a development environment with all dependencies and build tools using:
+
+```sh
+nix develop
+```
+
+This will drop you into a shell with LLVM 19, Zig, and all other necessary dependencies to build Bun from source.
+
+Alternatively, if you don't have flakes enabled, you can use:
+
+```sh
+nix-shell
+```
+
+To build with Nix (requires [nix flakes](https://nixos.wiki/wiki/Flakes)):
+
+```sh
+nix build
+```
+
+The Nix environment is particularly useful for reproducible builds and avoiding "works on my machine" issues.
+
 ## Installing Dependencies

 ### macOS
@@ -33,7 +58,7 @@ $ sudo apt install cmake

 On Windows, you will need [Visual Studio](https://visualstudio.microsoft.com) 2022 (17.11.0preview2 or later) or 2019 (v16.11 or later) with "Desktop development with C++" workload installed.

-## Building
+## Manual Building

 ### IDE (VSCode)

diff --git a/cmake/CompilerFlags.cmake b/cmake/CompilerFlags.cmake
index 123456..789abc 100644
--- a/cmake/CompilerFlags.cmake
+++ b/cmake/CompilerFlags.cmake
@@ -50,6 +50,17 @@ if(CMAKE_BUILD_TYPE STREQUAL "Debug")
   register_compiler_flags(
     DESCRIPTION "Add debug info"
     -g
-    -gz=zstd
   )
+
+  # When building with Nix, use zlib compression and skip _FORTIFY_SOURCE
+  # since Nix's glibc already sets it, and zstd may not be available in the Nix shell
+  if(DEFINED ENV{NIX_CC})
+    register_compiler_flags(
+      DESCRIPTION "Use zlib for debug symbol compression (Nix compatibility)"
+      -gz=zlib
+    )
+  else()
+    register_compiler_flags(
+      DESCRIPTION "Use zstd for debug symbol compression"
+      -gz=zstd
+    )
+  endif()
 endif()

 if(LINUX)
@@ -100,7 +111,13 @@ if(LINUX)
   register_compiler_flags(
     DESCRIPTION "Security hardening"
     -D_FORTIFY_SOURCE=3
   )
+
+  # Nix glibc already sets _FORTIFY_SOURCE, so skip it in Nix builds
+  if(DEFINED ENV{NIX_CC})
+    # Nix handles _FORTIFY_SOURCE in its stdenv
+  else()
+    register_compiler_definitions(DESCRIPTION "Fortify source" _FORTIFY_SOURCE=3)
+  endif()
 endif()

 if(APPLE)
diff --git a/flake.nix b/flake.nix
new file mode 100644
index 0000000..abcdef1
--- /dev/null
+++ b/flake.nix
@@ -0,0 +1,95 @@
+{
+  description = "Bun: JavaScript runtime & toolkit";
+
+  inputs = {
+    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
+    flake-utils.url = "github:numtide/flake-utils";
+  };
+
+  outputs = { self, nixpkgs, flake-utils }:
+    flake-utils.lib.eachDefaultSystem (system:
+      let
+        pkgs = nixpkgs.legacyPackages.${system};
+
+        llvmPackages = pkgs.llvmPackages_19;
+
+        commonBuildInputs = with pkgs; [
+          llvmPackages.clang
+          llvmPackages.llvm
+          llvmPackages.lld
+          llvmPackages.libclang
+          cmake
+          ninja
+          python3
+          git
+          zlib
+          pkg-config
+          jq
+        ];
+      in
+      {
+        packages = {
+          default = pkgs.stdenv.mkDerivation {
+            name = "bun";
+            src = builtins.fetchGit {
+              url = ./.;
+              sha256 = null;
+            };
+
+            nativeBuildInputs = commonBuildInputs;
+
+            buildPhase = ''
+              export CC=clang
+              export CXX=clang++
+              cmake -B build -S . -GNinja \
+                -DCMAKE_BUILD_TYPE=Release
+              ninja -C build
+            '';
+
+            installPhase = ''
+              mkdir -p $out/bin
+              cp build/bun $out/bin/
+            '';
+          };
+        };
+
+        devShells = {
+          default = pkgs.mkShell {
+            name = "bun-dev-shell";
+
+            nativeBuildInputs = commonBuildInputs;
+
+            buildInputs = with pkgs; [
+              zig
+              rustc
+              cargo
+              nodejs
+              yarn
+            ];
+
+            shellHook = ''
+              export CC=clang
+              export CXX=clang++
+              export LLVM_PATH="${llvmPackages.llvm}"
+              export CLANG_PATH="${llvmPackages.clang}"
+
+              echo "Bun development environment loaded"
+              echo "LLVM 19: ${llvmPackages.llvm}"
+              echo "Clang: ${llvmPackages.clang}"
+              echo "Run 'cmake -B build -S . && ninja -C build' to build"
+            '';
+          };
+        };
+      });
+}
diff --git a/shell.nix b/shell.nix
new file mode 100644
index 0000000..fedcba1
--- /dev/null
+++ b/shell.nix
@@ -0,0 +1,23 @@
+{ pkgs ? import <nixpkgs> {} }:
+
+let
+  llvmPackages = pkgs.llvmPackages_19;
+in
+pkgs.mkShell {
+  name = "bun-dev-shell";
+
+  nativeBuildInputs = with pkgs; [
+    llvmPackages.clang
+    llvmPackages.llvm
+    llvmPackages.lld
+    llvmPackages.libclang
+    cmake
+    ninja
+    python3
+    git
+    zlib
+    pkg-config
+    jq
+    zig
+  ];
+
+  shellHook = ''
+    export CC=clang
+    export CXX=clang++
+    echo "Bun development shell (non-flake)"
+  '';
+}
PATCH

echo 'Patch applied successfully.'
