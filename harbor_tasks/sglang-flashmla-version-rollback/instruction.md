# FlashMLA Build Incompatibility After Dependency Update

## Problem

After a recent FlashMLA dependency update in `sgl-kernel`, builds are failing on certain configurations. The newer FlashMLA version (pinned in `sgl-kernel/cmake/flashmla.cmake`) reorganized its source tree — files were moved into nested `instantiations/` subdirectories, header files were renamed, and new C++20 compilation requirements were introduced. This newer version has known runtime issues that need to be addressed by reverting to the previous stable version.

The cmake configuration currently references source files and include paths that belong to the newer FlashMLA layout. When rolling back to the stable version, the source file list, include paths, compile flags, and header file references in the SM103a patch section all need to be updated to match that version's directory structure.

Additionally, the Python wrapper (`sgl-kernel/python/sgl_kernel/flash_mla.py`) has import error guard logic in its public functions that was added as a workaround during the upgrade. These guards are unnecessary with the stable version and should be cleaned up.

## Key Files

- `sgl-kernel/cmake/flashmla.cmake` — cmake build configuration that pins the FlashMLA version and lists source files
- `sgl-kernel/python/sgl_kernel/flash_mla.py` — Python API wrapper for FlashMLA operations

## Hints

- The FlashMLA repository is at `https://github.com/sgl-project/FlashMLA`
- Compare the source tree layout between the current pinned commit and earlier tags/commits to understand the file reorganization
- The older stable version uses flat source files (e.g., `splitkv_mla.cu`, `get_mla_metadata.cu`) rather than nested instantiation directories
