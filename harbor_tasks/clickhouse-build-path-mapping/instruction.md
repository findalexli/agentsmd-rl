# Fix Build Path Mapping for Clean Stack Traces

## Problem

Stack traces in ClickHouse show polluted paths that include the build directory, like:
```
./ci/tmp/fast_build/./src/Common/Exception.cpp:139:7
```

Instead of clean bare relative paths like:
```
src/Common/Exception.cpp:139:7
```

## Root Cause

The `ENABLE_BUILD_PATH_MAPPING` option in CMakeLists.txt currently uses a single flag that maps source paths to `./src/Foo.cpp` but leaves `DW_AT_comp_dir` pointing at the build directory. When the symbolizer joins them, it produces paths like `./ci/tmp/fast_build/./src/Foo.cpp` in out-of-tree CI builds.

Additionally, in `src/Common/Dwarf.cpp`, the `getFullFileName` function handles DWARF 5 line number programs where the compilation directory is stored as an explicit entry with value `.`. When this directory is prepended to the path, it creates inconsistent results: `.cpp` translation units produce `./src/Foo.cpp` while inlined header frames show as `src/Common/Foo.h`.

## Expected Behavior

1. **CMakeLists.txt**: The compiler should emit debug info where:
   - `DW_AT_comp_dir` is set to `.` (current directory), regardless of build directory location
   - Source file paths are relative without any leading `./` or build-directory prefix

2. **src/Common/Dwarf.cpp**: The `getFullFileName` function in the DWARF parser should produce consistent relative paths, treating a directory entry of `.` (current directory) as equivalent to an empty directory - it adds no meaningful prefix and should not cause path inconsistencies between `.cpp` and `.h` files.

## Files to Modify

- `CMakeLists.txt` — contains the `ENABLE_BUILD_PATH_MAPPING` option and associated compiler flags
- `src/Common/Dwarf.cpp` — contains the `getFullFileName` function in the `Dwarf::LineNumberVM` class

## Notes

- Use Allman-style braces (opening brace on a new line)
- The DWARF 5 format stores the current directory explicitly, which requires handling separately from earlier DWARF versions
- Test that paths are clean by checking that source files resolve to bare relative paths like `src/Foo.cpp` rather than `./src/Foo.cpp`
