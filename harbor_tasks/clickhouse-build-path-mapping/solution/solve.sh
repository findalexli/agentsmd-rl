#!/bin/bash
set -e

cd /workspace/ClickHouse

# Apply the gold patch for build path mapping improvements
patch -p1 <<'PATCH'
diff --git a/CMakeLists.txt b/CMakeLists.txt
index 9232e962b7fb..5a734514156d 100644
--- a/CMakeLists.txt
+++ b/CMakeLists.txt
@@ -262,8 +262,11 @@ endif()
 option (ENABLE_BUILD_PATH_MAPPING "Enable remapping of file source paths in debug info, predefined preprocessor macros, and __builtin_FILE(). It's used to generate reproducible builds. See https://reproducible-builds.org/docs/build-path" ${ENABLE_BUILD_PATH_MAPPING_DEFAULT})

 if (ENABLE_BUILD_PATH_MAPPING)
-    set (COMPILER_FLAGS "${COMPILER_FLAGS} -ffile-prefix-map=${PROJECT_SOURCE_DIR}=.")
-    set (CMAKE_ASM_FLAGS "${CMAKE_ASM_FLAGS} -ffile-prefix-map=${PROJECT_SOURCE_DIR}=.")
+    # Fix DW_AT_comp_dir to "." regardless of the build directory location, then strip the source
+    # directory prefix from all file paths (trailing slash ensures the separator is stripped too,
+    # leaving bare relative paths like "src/Foo.cpp" that the symbolizer resolves to "./src/Foo.cpp").
+    set (COMPILER_FLAGS "${COMPILER_FLAGS} -fdebug-compilation-dir=. -ffile-prefix-map=${PROJECT_SOURCE_DIR}/=")
+    set (CMAKE_ASM_FLAGS "${CMAKE_ASM_FLAGS} -fdebug-compilation-dir=. -ffile-prefix-map=${PROJECT_SOURCE_DIR}/=")
 endif ()

 option (ENABLE_BUILD_PROFILING "Enable profiling of build time" OFF)
diff --git a/src/Common/Dwarf.cpp b/src/Common/Dwarf.cpp
index 04d9c3d45e10..68dece01ad9d 100644
--- a/src/Common/Dwarf.cpp
+++ b/src/Common/Dwarf.cpp
@@ -2247,7 +2247,9 @@ Dwarf::Path Dwarf::LineNumberVM::getFullFileName(uint64_t index) const
     // Program Header and relies on the CU's DW_AT_comp_dir.
     // DWARF 5: the current directory is explicitly present.
     const std::string_view base_dir = version_ == 5 ? "" : compilationDirectory_;
-    return Path(base_dir, getIncludeDirectory(fn.directoryIndex), fn.relativeName);
+    const std::string_view include_dir = getIncludeDirectory(fn.directoryIndex);
+    // A directory entry of "." is the current directory and adds no meaningful prefix.
+    return Path(base_dir, include_dir == "." ? std::string_view{} : include_dir, fn.relativeName);
 }

 bool Dwarf::LineNumberVM::findAddress(uintptr_t target, Path & file, uint64_t & line, uint64_t & column)
PATCH

# Idempotency check - verify the patch was applied
echo "Checking if patch was applied..."
if grep -q "include_dir == \".\" ? std::string_view{}" src/Common/Dwarf.cpp; then
    echo "SUCCESS: Dwarf.cpp patch applied correctly"
else
    echo "ERROR: Dwarf.cpp patch was not applied"
    exit 1
fi

if grep -q "fdebug-compilation-dir=." CMakeLists.txt; then
    echo "SUCCESS: CMakeLists.txt patch applied correctly"
else
    echo "ERROR: CMakeLists.txt patch was not applied"
    exit 1
fi

echo "Gold patch applied successfully."
