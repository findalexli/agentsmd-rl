#!/usr/bin/env bash
set -euo pipefail

cd /workspace/directxtex

# Idempotency guard
if grep -qF "- **Code Style**: The project uses an .editorconfig file to enforce coding stand" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -19,7 +19,8 @@ These instructions define how GitHub Copilot should assist with this project. Th
 
 ## General Guidelines
 
-- **Code Style**: The project uses an .editorconfig file to enforce coding standards. Follow the rules defined in `.editorconfig` for indentation, line endings, and other formatting. Additional information can be found on the wiki at [Implementation](https://github.com/microsoft/DirectXTK/wiki/Implementation). The code requires C++11/C++14 features.
+- **Code Style**: The project uses an .editorconfig file to enforce coding standards. Follow the rules defined in `.editorconfig` for indentation, line endings, and other formatting. Additional information can be found on the wiki at [Implementation](https://github.com/microsoft/DirectXTK/wiki/Implementation). The library implementation is written to be compatible with C++14 features, but C++17 is required to build the project for the command-line tools which utilize C++17 filesystem for long file path support.
+> Notable `.editorconfig` rules: C/C++ files use 4-space indentation, `crlf` line endings, and `latin1` charset — avoid non-ASCII characters in source files. HLSL files have separate indent/spacing rules defined in `.editorconfig`.
 - **Documentation**: The project provides documentation in the form of wiki pages available at [Documentation](https://github.com/microsoft/DirectXTex/wiki/).
 - **Error Handling**: Use C++ exceptions for error handling and uses RAII smart pointers to ensure resources are properly managed. For some functions that return HRESULT error codes, they are marked `noexcept`, use `std::nothrow` for memory allocation, and should not throw exceptions.
 - **Testing**: Unit tests for this project are implemented in this repository [Test Suite](https://github.com/walbourn/directxtextest/) and can be run using CTest per the instructions at [Test Documentation](https://github.com/walbourn/directxtextest/wiki).
@@ -46,6 +47,7 @@ DDSTextureLoader/ # Standalone version of the DDS texture loader for Direct3D 9/
 ScreenGrab/       # Standalone version of the screenshot capture utility for Direct3D 9/11/12.
 WICTextureLoader/ # Standalone versoin of the WIC texture loader for Direct3D 9/11/12.
 Tests/            # Tests are designed to be cloned from a separate repository at this location.
+wiki/             # Local clone of the GitHub wiki documentation repository.
 ```
 
 > Note that DDSTextureLoader, ScreenGrab, and WICTextureLoader are standalone version of utilities which are also included in the *DirectX Tool Kit for DirectX 11* and *DirectX Tool Kit for DirectX 12*.
@@ -60,6 +62,74 @@ Tests/            # Tests are designed to be cloned from a separate repository a
 - Use `Microsoft::WRL::ComPtr` for COM object management.
 - Make use of anonymous namespaces to limit scope of functions and variables.
 - Make use of `assert` for debugging checks, but be sure to validate input parameters in release builds.
+- Explicitly `= delete` copy constructors and copy-assignment operators on all classes that use the pImpl idiom.
+- Explicitly utilize `= default` or `=delete` for copy constructors, assignment operators, move constructors and move-assignment operators where appropriate.
+- Use 16-byte alignment (`_aligned_malloc` / `_aligned_free`) to support SIMD operations in the implementation, but do not expose this requirement in public APIs.
+> For non-Windows support, the implementation uses C++17 `aligned_alloc` instead of `_aligned_malloc`.
+
+#### SAL Annotations
+
+All public API functions must use SAL annotations on every parameter. Use `_Use_decl_annotations_` at the top of each implementation that has SAL in the header declaration — never repeat the annotations in the `.cpp` or `.inl` file.
+
+Common annotations:
+
+| Annotation | Meaning |
+| --- | --- |
+| `_In_` | Input parameter |
+| `_Out_` | Output parameter |
+| `_Inout_` | Bidirectional parameter |
+| `_In_reads_bytes_(n)` | Input buffer with byte count |
+| `_In_reads_(n)` | Input array with element count |
+| `_In_z_` | Null-terminated input string |
+| `_Out_opt_` | Optional output parameter |
+
+Example:
+
+```cpp
+// Header (DirectXTex.h)
+DIRECTX_TEX_API HRESULT __cdecl GetMetadataFromDDSMemory(
+    _In_reads_bytes_(size) const uint8_t* pSource, _In_ size_t size,
+    _In_ DDS_FLAGS flags,
+    _Out_ TexMetadata& metadata) noexcept;
+
+// Implementation (.cpp)
+_Use_decl_annotations_
+HRESULT __cdecl GetMetadataFromDDSMemory(
+    const uint8_t* pSource, size_t size,
+    DDS_FLAGS flags,
+    TexMetadata& metadata) noexcept
+{ ... }
+```
+
+#### Calling Convention and DLL Export
+
+- All public functions use `__cdecl` explicitly for ABI stability.
+- All public function declarations are prefixed with `DIRECTX_TEX_API`, which wraps `__declspec(dllexport)` / `__declspec(dllimport)` (or the MinGW `__attribute__` equivalent) when the `DIRECTX_TEX_EXPORT` or `DIRECTX_TEX_IMPORT` preprocessor symbols are defined. CMake sets these automatically when `BUILD_SHARED_LIBS=ON`.
+
+#### `noexcept` Rules
+
+- All query and utility functions that cannot fail (e.g., `IsCompressed`, `IsCubemap`, `ComputePitch`) are marked `noexcept`.
+- All HRESULT-returning I/O and processing functions are also `noexcept` — errors are communicated via return code, never via exceptions.
+- Constructors and functions that perform heap allocation or utilize Standard C++ containers that may throw are marked `noexcept(false)`.
+
+#### Enum Flags Pattern
+
+Flags enums follow this pattern — a `uint32_t`-based unscoped enum with a `_NONE = 0x0` base case, followed by a call to `DEFINE_ENUM_FLAG_OPERATORS` (defined in `DirectXTex.inl`) to enable `|`, `&`, and `~` operators:
+
+```cpp
+enum TEX_FILTER_FLAGS : uint32_t
+{
+    TEX_FILTER_DEFAULT = 0,
+
+    TEX_FILTER_WRAP_U = 0x1,
+    // Enables wrapping addressing on U coordinate
+    ...
+};
+
+DEFINE_ENUM_FLAG_OPERATORS(TEX_FILTER_FLAGS);
+```
+
+See [this blog post](https://walbourn.github.io/modern-c++-bitmask-types/) for more information on this pattern.
 
 ### Patterns to Avoid
 
@@ -68,6 +138,50 @@ Tests/            # Tests are designed to be cloned from a separate repository a
 - Don’t put implementation logic in header files unless using templates, although the SimpleMath library does use an .inl file for performance.
 - Avoid using `using namespace` in header files to prevent polluting the global namespace.
 
+## Naming Conventions
+
+| Element | Convention | Example |
+| --- | --- | --- |
+| Classes / structs | PascalCase | `ScratchImage`, `TexMetadata` |
+| Public functions | PascalCase + `__cdecl` | `ComputePitch`, `IsCompressed` |
+| Private data members | `m_` prefix | `m_nimages`, `m_metadata` |
+| Enum type names | UPPER_SNAKE_CASE | `TEX_DIMENSION`, `CP_FLAGS` |
+| Enum values | UPPER_SNAKE_CASE | `CP_FLAGS_NONE`, `TEX_ALPHA_MODE_PREMULTIPLIED` |
+| Flag enum suffix | `_FLAGS` with `_NONE = 0x0` base | `DDS_FLAGS`, `WIC_FLAGS` |
+| Files | PascalCase | `DirectXTex.h`, `BC6HEncode.hlsl` |
+
+## File Header Convention
+
+Every source file (`.cpp`, `.h`, `.hlsl`, etc.) must begin with this block:
+
+```cpp
+//-------------------------------------------------------------------------------------
+// {FileName}
+//
+// {One-line description}
+//
+// Copyright (c) Microsoft Corporation.
+// Licensed under the MIT License.
+//
+// http://go.microsoft.com/fwlink/?LinkId=248926
+//-------------------------------------------------------------------------------------
+```
+
+Section separators within files use:
+- Major sections: `//-------------------------------------------------------------------------------------`
+- Subsections:   `//---------------------------------------------------------------------------------`
+
+The project does **not** use Doxygen. API documentation is maintained exclusively on the GitHub wiki.
+
+## HLSL Shader Compilation
+
+Shaders in `DirectXTex/Shaders/` are compiled with **FXC** (not DXC), producing embedded C++ header files (`.inc`):
+
+- Each shader is compiled twice: `cs_5_0` (primary) and `cs_4_0` with `/DEMULATE_F16C` (legacy fallback).
+- Standard compiler flags: `/nologo /WX /Ges /Zi /Zpc /Qstrip_reflect /Qstrip_debug`
+- Use `CompileShaders.cmd` in `DirectXTex/Shaders/` to regenerate the `.inc` files.
+- The CMake option `USE_PREBUILT_SHADERS` controls whether pre-compiled shaders are used.
+
 ## References
 
 - [Source git repository on GitHub](https://github.com/microsoft/DirectXTex.git)
@@ -113,6 +227,31 @@ When creating documentation:
 - The code supports building for Windows and Linux.
 - Portability and conformance of the code is validated by building with Visual C++, clang/LLVM for Windows, MinGW, and GCC for Linux.
 
+### Platform and Compiler `#ifdef` Guards
+
+Use these established guards — do not invent new ones:
+
+| Guard | Purpose |
+| --- | --- |
+| `_WIN32` | Windows platform (desktop, UWP, Xbox) |
+| `_GAMING_XBOX` | Xbox One or Xbox Series X\|S |
+| `_GAMING_XBOX_SCARLETT` | Xbox Series X\|S |
+| `_XBOX_ONE && _TITLE` | Xbox One XDK (legacy) |
+| `_MSC_VER` | MSVC-specific (and MSVC-like clang-cl) pragmas and warning suppression |
+| `__clang__` | Clang/LLVM diagnostic suppressions |
+| `__MINGW32__` | MinGW compatibility headers |
+| `__GNUC__` | MinGW/GCC DLL attribute equivalents |
+| `_M_ARM64` / `_M_X64` / `_M_IX86` | Architecture-specific code paths for MSVC (`#ifdef`) |
+| `_M_ARM64EC` | ARM64EC ABI (ARM64 code with x64 interop) for MSVC |
+| `__aarch64__` / `__x86_64__` / `__i386__` | Additional architecture-specific symbols for MinGW/GNUC (`#if`) |
+| `USING_DIRECTX_HEADERS` | External DirectX-Headers package in use |
+
+> `_M_ARM`/ `__arm__` is legacy 32-bit ARM which is deprecated.
+
+Non-Windows builds (Linux/WSL) omit WIC entirely and use `<directx/dxgiformat.h>` and `<wsl/winadapter.h>` from the DirectX-Headers package instead of the Windows SDK.
+
+### Error Codes
+
 The following symbols are not custom error codes, but aliases for `HRESULT_FROM_WIN32` error codes.
 
 | Symbol | Standard Win32 HRESULT |
PATCH

echo "Gold patch applied."
