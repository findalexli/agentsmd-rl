# Bug: SYCL extension build fails on Windows with newer Intel oneAPI compilers

## Problem

When building SYCL (XPU) extensions on Windows using Intel's oneAPI DPC++ compiler version 2025.3 or higher, compilation fails due to conflicting standard library headers.

The build process passes MSVC include directory paths (obtained from the `VCToolsInstallDir` environment variable) explicitly as `-I` flags to the compiler. Starting with oneAPI 2025.3, Intel changed the include path ordering to align with MSVC behavior, so the MSVC include directories are already added as correctly-ordered implicit include paths by the Intel compiler. Passing them explicitly on the command line causes the wrong standard headers to be picked up, leading to conflicting declarations and build failures.

## Task

Add a function named `win_filter_msvc_include_dirs` to `torch/utils/cpp_extension.py` that filters MSVC include directories out of a list of preprocessor options. The function must:

1. Accept a list of preprocessor option strings (e.g., `["-DSOME_DEFINE", "-IC:\\path\\to\\include", "-O2"]`)
2. Use the existing `_get_icpx_version` helper to determine the oneAPI compiler version (it returns a string like `"20250300"` in a `YYYYMMDD00`-like format)
3. When the oneAPI version is **2025.3 or higher** (i.e., version integer >= 20250300) **and** the `VCToolsInstallDir` environment variable is set, filter out any `-I` entries whose path contains the `VCToolsInstallDir` value
4. When the oneAPI version is below 2025.3, or `VCToolsInstallDir` is not set, return the input list unchanged
5. Handle an empty input list by returning an empty list

After creating the function, integrate it into the SYCL compilation path so that preprocessor options (`pp_opts`) are passed through `win_filter_msvc_include_dirs` before being used to construct SYCL compiler flags (`sycl_cflags`).

## Constraints

- Only the SYCL compilation path should be affected; CUDA and HIP paths must remain unchanged
- The existing functions `win_cuda_flags`, `win_hip_flags`, and `win_wrap_ninja_compile` must not be removed or broken
- The module constant `_COMMON_SYCL_FLAGS` must be preserved
- The function must be a standalone named function definition (not a lambda or inline expression) so it can be extracted by name from the AST
- The file should remain syntactically valid and pass standard linting tools (pyflakes, flake8, ruff, pylint, bandit)

## Relevant context

- The target file is `torch/utils/cpp_extension.py`
- `VCToolsInstallDir` environment variable points to the Visual Studio tools installation directory (e.g., `C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC\14.38.33130`)
- The `_get_icpx_version` helper returns a string like `"20250300"` (YYYYMMDD-like format)
