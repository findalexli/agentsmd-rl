# Bug: SYCL extension build fails on Windows with newer Intel oneAPI compilers

## Problem

When building SYCL (XPU) extensions on Windows using Intel's oneAPI DPC++ compiler version 2025.3 or higher, compilation fails due to conflicting standard library headers.

The build process passes MSVC include directory paths (obtained from the `VCToolsInstallDir` environment variable) explicitly as `-I` flags to the compiler. Starting with oneAPI 2025.3, Intel changed the include path ordering to align with MSVC behavior, so the MSVC include directories are already added as correctly-ordered implicit include paths by the Intel compiler. Passing them explicitly on the command line causes the wrong standard headers to be picked up, leading to conflicting declarations and build failures.

## Task

Create a new standalone function called `win_filter_msvc_include_dirs` in `torch/utils/cpp_extension.py` that filters MSVC include directories out of a list of preprocessor options. The function must:

1. Accept a list of preprocessor option strings (e.g., `["-DSOME_DEFINE", "-IC:\\path\\to\\include", "-O2"]`)
2. Use the existing `_get_icpx_version()` helper (which returns a version string like `"20250300"` in a `YYYYMMDD00`-like format) to determine the oneAPI compiler version
3. When the oneAPI version is **2025.3 or higher** (i.e., version string `>= "20250300"`) **and** the `VCToolsInstallDir` environment variable is set, filter out any `-I` entries whose path contains the `VCToolsInstallDir` value
4. When the oneAPI version is below 2025.3, or `VCToolsInstallDir` is not set, return the input list unchanged
5. Handle an empty input list by returning an empty list

After creating the function, integrate it into the SYCL compilation path in the same file so that preprocessor options are passed through this filter before being used to construct SYCL compiler flags. The function should wrap the preprocessor options (not be concatenated as raw lists).

## Constraints

- Only the SYCL compilation path should be affected; CUDA and HIP paths must remain unchanged
- The function must be a standalone, top-level-or-nested named function definition (not a lambda or inline expression) so it can be extracted by name
- The file should remain syntactically valid and pass standard linting tools

## Relevant context

- `VCToolsInstallDir` environment variable points to the Visual Studio tools installation directory (e.g., `C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.38.33130`)
- `_get_icpx_version()` returns a version string like `"20250300"` (`YYYYMMDD`-like format)
