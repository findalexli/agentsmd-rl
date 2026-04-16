#!/bin/bash
set -e

cd /workspace/bun

# Gold patch: Remove sccache, use ccache only
# PR: oven-sh/bun#25682

# Check if patch already applied (idempotency check)
if [ ! -f cmake/tools/SetupSccache.cmake ]; then
    echo "Patch already applied (SetupSccache.cmake already removed)"
    exit 0
fi

echo "Applying gold patch..."

# 1. Remove SetupSccache.cmake
rm -f cmake/tools/SetupSccache.cmake
echo "Removed cmake/tools/SetupSccache.cmake"

# 2. Simplify SetupCcache.cmake - remove REQUIRED flag
# Read the current file and modify it
cat > /tmp/ccache_new.cmake << 'EOF'
optionx(ENABLE_CCACHE BOOL "If ccache should be enabled" DEFAULT ON)

if(NOT ENABLE_CCACHE OR CACHE_STRATEGY STREQUAL "none")
  setenv(CCACHE_DISABLE 1)
  return()
endif()

if (CI AND NOT APPLE)
  setenv(CCACHE_DISABLE 1)
  return()
endif()

find_command(
  VARIABLE
    CCACHE_PROGRAM
  COMMAND
    ccache
)

if(NOT CCACHE_PROGRAM)
  return()
endif()

set(CCACHE_ARGS CMAKE_C_COMPILER_LAUNCHER CMAKE_CXX_COMPILER_LAUNCHER)
foreach(arg ${CCACHE_ARGS})
  setx(${arg} ${CCACHE_PROGRAM})
  list(APPEND CMAKE_ARGS -D${arg}=${${arg}})
endforeach()

setenv(CCACHE_DIR ${CACHE_PATH}/ccache)
setenv(CCACHE_BASEDIR ${CWD})
setenv(CCACHE_NOHASHDIR 1)

if(CACHE_STRATEGY STREQUAL "read-only")
  setenv(CCACHE_READONLY 1)
elseif(CACHE_STRATEGY STREQUAL "write-only")
  setenv(CCACHE_RECACHE 1)
endif()

setenv(CCACHE_FILECLONE 1)
setenv(CCACHE_STATSLOG ${BUILD_PATH}/ccache.log)

if(CI)
else()
  setenv(CCACHE_MAXSIZE 100G)
  setenv(CCACHE_SLOPPINESS "pch_defines,time_macros,locale,random_seed,clang_index_store,gcno_cwd")
endif()
EOF
cp /tmp/ccache_new.cmake cmake/tools/SetupCcache.cmake
echo "Updated cmake/tools/SetupCcache.cmake (removed REQUIRED)"

# 3. Remove scripts/build-cache directory
rm -rf scripts/build-cache
echo "Removed scripts/build-cache/ directory"

# 4. Update CMakeLists.txt - remove include(SetupSccache)
if [ -f CMakeLists.txt ]; then
    # Remove the line that includes SetupSccache.cmake
    sed -i '/include(SetupSccache)/d' CMakeLists.txt || true
    sed -i '/SetupSccache\.cmake/d' CMakeLists.txt || true
    echo "Updated CMakeLists.txt (removed SetupSccache include)"
fi

# 5. Update CONTRIBUTING.md - replace sccache references with ccache
if [ -f CONTRIBUTING.md ]; then
    # Remove sccache from macOS brew install line, add ccache
    sed -i 's/brew install automake cmake coreutils gnu-sed go icu4c libiconv libtool ninja pkg-config rust ruby sccache/brew install automake ccache cmake coreutils gnu-sed go icu4c libiconv libtool ninja pkg-config rust ruby/g' CONTRIBUTING.md || true

    # Replace the sccache section with ccache section
    # First, find and remove the "### Optional: Install sccache" section through "## Install LLVM"
    sed -i '/### Optional: Install `sccache`/,/## Install LLVM/{ /## Install LLVM/!d; s/## Install LLVM/### Optional: Install `ccache`\n\nccache is used to cache compilation artifacts, significantly speeding up builds:\n\n```bash\n# For macOS\n$ brew install ccache\n\n# For Ubuntu\/Debian\n$ sudo apt install ccache\n\n# For Arch\n$ sudo pacman -S ccache\n\n# For Fedora\n$ sudo dnf install ccache\n\n# For openSUSE\n$ sudo zypper install ccache\n```\n\nOur build scripts will automatically detect and use `ccache` if available. You can check cache statistics with `ccache --show-stats`.\n\n## Install LLVM/ }' CONTRIBUTING.md || true

    # Remove the entire AWS credentials section (from "#### Registering AWS" to the end of that section)
    sed -i '/Registering AWS Credentials/,/## Install LLVM/{ /## Install LLVM/!d; }' CONTRIBUTING.md || true
    sed -i '/#### Registering AWS Credentials/,/## Install LLVM/{ /## Install LLVM/!d; }' CONTRIBUTING.md || true

    echo "Updated CONTRIBUTING.md"
fi

# 6. Update docs/project/contributing.mdx
if [ -f docs/project/contributing.mdx ]; then
    # Remove sccache from macOS brew install line, add ccache
    sed -i 's/brew install automake cmake coreutils gnu-sed go icu4c libiconv libtool ninja pkg-config rust ruby sccache/brew install automake ccache cmake coreutils gnu-sed go icu4c libiconv libtool ninja pkg-config rust ruby/g' docs/project/contributing.mdx || true

    # Replace sccache section with ccache section
    sed -i '/### Optional: Install `sccache`/,/## Install LLVM/{ /## Install LLVM/!d; s/## Install LLVM/### Optional: Install `ccache`\n\nccache is used to cache compilation artifacts, significantly speeding up builds:\n\n```bash\n# For macOS\n$ brew install ccache\n\n# For Ubuntu\/Debian\n$ sudo apt install ccache\n\n# For Arch\n$ sudo pacman -S ccache\n\n# For Fedora\n$ sudo dnf install ccache\n\n# For openSUSE\n$ sudo zypper install ccache\n```\n\nOur build scripts will automatically detect and use `ccache` if available. You can check cache statistics with `ccache --show-stats`.\n\n## Install LLVM/ }' docs/project/contributing.mdx || true

    echo "Updated docs/project/contributing.mdx"
fi

# 7. Update docs/project/building-windows.mdx - change sccache to ccache
if [ -f docs/project/building-windows.mdx ]; then
    sed -i 's/scoop install nodejs-lts go rust nasm ruby perl sccache/scoop install nodejs-lts go rust nasm ruby perl ccache/g' docs/project/building-windows.mdx || true
    echo "Updated docs/project/building-windows.mdx"
fi

echo "Gold patch applied successfully!"
