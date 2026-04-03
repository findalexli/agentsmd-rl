#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotent: skip if already applied
if grep -q 'JSC_CMAKE_ARGS' cmake/tools/SetupWebKit.cmake 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/CONTRIBUTING.md b/CONTRIBUTING.md
index 750eb17a625..c55a43998c1 100644
--- a/CONTRIBUTING.md
+++ b/CONTRIBUTING.md
@@ -259,18 +259,13 @@ $ git clone https://github.com/oven-sh/WebKit vendor/WebKit
 # Check out the commit hash specified in `set(WEBKIT_VERSION <commit_hash>)` in cmake/tools/SetupWebKit.cmake
 $ git -C vendor/WebKit checkout <commit_hash>

-# Make a debug build of JSC. This will output build artifacts in ./vendor/WebKit/WebKitBuild/Debug
-# Optionally, you can use `bun run jsc:build` for a release build
-$ bun run jsc:build:debug && rm vendor/WebKit/WebKitBuild/Debug/JavaScriptCore/DerivedSources/inspector/InspectorProtocolObjects.h
-
-# After an initial run of `make jsc-debug`, you can rebuild JSC with:
-$ cmake --build vendor/WebKit/WebKitBuild/Debug --target jsc && rm vendor/WebKit/WebKitBuild/Debug/JavaScriptCore/DerivedSources/inspector/InspectorProtocolObjects.h
-
-# Build bun with the local JSC build
+# Build bun with the local JSC build — this automatically configures and builds JSC
 $ bun run build:local
 ```

-Using `bun run build:local` will build Bun in the `./build/debug-local` directory (instead of `./build/debug`), you'll have to change a couple of places to use this new directory:
+`bun run build:local` handles everything: configuring JSC, building JSC, and building Bun. On subsequent runs, JSC will incrementally rebuild if any WebKit sources changed. `ninja -Cbuild/debug-local` also works after the first build, and will build Bun+JSC.
+
+The build output goes to `./build/debug-local` (instead of `./build/debug`), so you'll need to update a couple of places:

 - The first line in [`src/js/builtins.d.ts`](/src/js/builtins.d.ts)
 - The `CompilationDatabase` line in [`.clangd` config](/.clangd) should be `CompilationDatabase: build/debug-local`
@@ -281,7 +276,7 @@ Note that the WebKit folder, including build artifacts, is 8GB+ in size.

 If you are using a JSC debug build and using VScode, make sure to run the `C/C++: Select a Configuration` command to configure intellisense to find the debug headers.

-Note that if you change make changes to our [WebKit fork](https://github.com/oven-sh/WebKit), you will also have to change [`SetupWebKit.cmake`](/cmake/tools/SetupWebKit.cmake) to point to the commit hash.
+Note that if you make changes to our [WebKit fork](https://github.com/oven-sh/WebKit), you will also have to change [`SetupWebKit.cmake`](/cmake/tools/SetupWebKit.cmake) to point to the commit hash.

 ## Troubleshooting

diff --git a/cmake/targets/BuildBun.cmake b/cmake/targets/BuildBun.cmake
index 64536cc26be..a1edfe216ea 100644
--- a/cmake/targets/BuildBun.cmake
+++ b/cmake/targets/BuildBun.cmake
@@ -1273,13 +1273,18 @@ else()
     ${WEBKIT_LIB_PATH}/libWTF.a
     ${WEBKIT_LIB_PATH}/libJavaScriptCore.a
   )
-  if(NOT APPLE OR EXISTS ${WEBKIT_LIB_PATH}/libbmalloc.a)
+  if(WEBKIT_LOCAL OR NOT APPLE OR EXISTS ${WEBKIT_LIB_PATH}/libbmalloc.a)
     target_link_libraries(${bun} PRIVATE ${WEBKIT_LIB_PATH}/libbmalloc.a)
   endif()
 endif()

 include_directories(${WEBKIT_INCLUDE_PATH})

+# When building with a local WebKit, ensure JSC is built before compiling Bun's C++ sources.
+if(WEBKIT_LOCAL AND TARGET jsc)
+  add_dependencies(${bun} jsc)
+endif()
+
 # Include the generated dependency versions header
 include_directories(${CMAKE_BINARY_DIR})

@@ -1324,9 +1329,14 @@ if(LINUX)
     target_link_libraries(${bun} PUBLIC libatomic.so)
   endif()

-  target_link_libraries(${bun} PRIVATE ${WEBKIT_LIB_PATH}/libicudata.a)
-  target_link_libraries(${bun} PRIVATE ${WEBKIT_LIB_PATH}/libicui18n.a)
-  target_link_libraries(${bun} PRIVATE ${WEBKIT_LIB_PATH}/libicuuc.a)
+  if(WEBKIT_LOCAL)
+    find_package(ICU REQUIRED COMPONENTS data i18n uc)
+    target_link_libraries(${bun} PRIVATE ICU::data ICU::i18n ICU::uc)
+  else()
+    target_link_libraries(${bun} PRIVATE ${WEBKIT_LIB_PATH}/libicudata.a)
+    target_link_libraries(${bun} PRIVATE ${WEBKIT_LIB_PATH}/libicui18n.a)
+    target_link_libraries(${bun} PRIVATE ${WEBKIT_LIB_PATH}/libicuuc.a)
+  endif()
 endif()

 if(WIN32)
diff --git a/cmake/tools/SetupWebKit.cmake b/cmake/tools/SetupWebKit.cmake
index 46444d0789e..2f3e5ee8b48 100644
--- a/cmake/tools/SetupWebKit.cmake
+++ b/cmake/tools/SetupWebKit.cmake
@@ -3,6 +3,7 @@

 option(WEBKIT_VERSION "The version of WebKit to use")
 option(WEBKIT_LOCAL "If a local version of WebKit should be used instead of downloading")
+option(WEBKIT_BUILD_TYPE "The build type for local WebKit (defaults to CMAKE_BUILD_TYPE)")

 if(NOT WEBKIT_VERSION)
   set(WEBKIT_VERSION 515344bc5d65aa2d4f9ff277b5fb944f0e051dcd)
@@ -15,7 +16,10 @@ string(SUBSTRING ${WEBKIT_VERSION} 0 16 WEBKIT_VERSION_PREFIX)
 string(SUBSTRING ${WEBKIT_VERSION} 0 8 WEBKIT_VERSION_SHORT)

 if(WEBKIT_LOCAL)
-  set(DEFAULT_WEBKIT_PATH ${VENDOR_PATH}/WebKit/WebKitBuild/${CMAKE_BUILD_TYPE})
+  if(NOT WEBKIT_BUILD_TYPE)
+    set(WEBKIT_BUILD_TYPE ${CMAKE_BUILD_TYPE})
+  endif()
+  set(DEFAULT_WEBKIT_PATH ${VENDOR_PATH}/WebKit/WebKitBuild/${WEBKIT_BUILD_TYPE})
 else()
   set(DEFAULT_WEBKIT_PATH ${CACHE_PATH}/webkit-${WEBKIT_VERSION_PREFIX})
 endif()
@@ -30,35 +34,153 @@ set(WEBKIT_INCLUDE_PATH ${WEBKIT_PATH}/include)
 set(WEBKIT_LIB_PATH ${WEBKIT_PATH}/lib)

 if(WEBKIT_LOCAL)
-  if(EXISTS ${WEBKIT_PATH}/cmakeconfig.h)
-    # You may need to run:
-    # make jsc-compile-debug jsc-copy-headers
-    include_directories(
-      ${WEBKIT_PATH}
-      ${WEBKIT_PATH}/JavaScriptCore/Headers
-      ${WEBKIT_PATH}/JavaScriptCore/Headers/JavaScriptCore
-      ${WEBKIT_PATH}/JavaScriptCore/PrivateHeaders
-      ${WEBKIT_PATH}/bmalloc/Headers
-      ${WEBKIT_PATH}/WTF/Headers
-      ${WEBKIT_PATH}/JavaScriptCore/PrivateHeaders/JavaScriptCore
-      ${WEBKIT_PATH}/JavaScriptCore/DerivedSources/inspector
-    )
+  set(WEBKIT_SOURCE_DIR ${VENDOR_PATH}/WebKit)

-    # On Windows, add ICU include path from vcpkg
-    if(WIN32)
-      # Auto-detect vcpkg triplet
-      set(VCPKG_ARM64_PATH ${VENDOR_PATH}/WebKit/vcpkg_installed/arm64-windows-static)
-      set(VCPKG_X64_PATH ${VENDOR_PATH}/WebKit/vcpkg_installed/x64-windows-static)
-      if(EXISTS ${VCPKG_ARM64_PATH})
-        set(VCPKG_ICU_PATH ${VCPKG_ARM64_PATH})
+  if(WIN32)
+    # --- Build ICU from source (Windows only) ---
+    # On macOS, ICU is found automatically (Homebrew icu4c for headers, system for libs).
+    # On Linux, ICU is found automatically from system packages (e.g. libicu-dev).
+    # On Windows, there is no system ICU, so we build it from source.
+    set(ICU_LOCAL_ROOT ${VENDOR_PATH}/WebKit/WebKitBuild/icu)
+    if(NOT EXISTS ${ICU_LOCAL_ROOT}/lib/sicudt.lib)
+      message(STATUS "Building ICU from source...")
+      if(CMAKE_SYSTEM_PROCESSOR MATCHES "arm64|ARM64|aarch64|AARCH64")
+        set(ICU_PLATFORM "ARM64")
       else()
-        set(VCPKG_ICU_PATH ${VCPKG_X64_PATH})
+        set(ICU_PLATFORM "x64")
       endif()
-      if(EXISTS ${VCPKG_ICU_PATH}/include)
-        include_directories(${VCPKG_ICU_PATH}/include)
-        message(STATUS "Using ICU from vcpkg: ${VCPKG_ICU_PATH}/include")
+      execute_process(
+        COMMAND powershell -ExecutionPolicy Bypass -File
+          ${WEBKIT_SOURCE_DIR}/build-icu.ps1
+          -Platform ${ICU_PLATFORM}
+          -BuildType ${WEBKIT_BUILD_TYPE}
+          -OutputDir ${ICU_LOCAL_ROOT}
+        RESULT_VARIABLE ICU_BUILD_RESULT
+      )
+      if(NOT ICU_BUILD_RESULT EQUAL 0)
+        message(FATAL_ERROR "Failed to build ICU (exit code: ${ICU_BUILD_RESULT}).")
       endif()
     endif()
+
+    # Copy ICU libs to WEBKIT_LIB_PATH with the names BuildBun.cmake expects.
+    # Prebuilt WebKit uses 's' prefix (static) and 'd' suffix (debug).
+    file(MAKE_DIRECTORY ${WEBKIT_LIB_PATH})
+    if(WEBKIT_BUILD_TYPE STREQUAL "Debug")
+      set(ICU_SUFFIX "d")
+    else()
+      set(ICU_SUFFIX "")
+    endif()
+    file(COPY_FILE ${ICU_LOCAL_ROOT}/lib/sicudt.lib ${WEBKIT_LIB_PATH}/sicudt${ICU_SUFFIX}.lib ONLY_IF_DIFFERENT)
+    file(COPY_FILE ${ICU_LOCAL_ROOT}/lib/icuin.lib ${WEBKIT_LIB_PATH}/sicuin${ICU_SUFFIX}.lib ONLY_IF_DIFFERENT)
+    file(COPY_FILE ${ICU_LOCAL_ROOT}/lib/icuuc.lib ${WEBKIT_LIB_PATH}/sicuuc${ICU_SUFFIX}.lib ONLY_IF_DIFFERENT)
+  endif()
+
+  # --- Configure JSC ---
+  message(STATUS "Configuring JSC from local WebKit source at ${WEBKIT_SOURCE_DIR}...")
+
+  set(JSC_CMAKE_ARGS
+    -S ${WEBKIT_SOURCE_DIR}
+    -B ${WEBKIT_PATH}
+    -G ${CMAKE_GENERATOR}
+    -DPORT=JSCOnly
+    -DENABLE_STATIC_JSC=ON
+    -DUSE_THIN_ARCHIVES=OFF
+    -DENABLE_FTL_JIT=ON
+    -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
+    -DUSE_BUN_JSC_ADDITIONS=ON
+    -DUSE_BUN_EVENT_LOOP=ON
+    -DENABLE_BUN_SKIP_FAILING_ASSERTIONS=ON
+    -DALLOW_LINE_AND_COLUMN_NUMBER_IN_BUILTINS=ON
+    -DCMAKE_BUILD_TYPE=${WEBKIT_BUILD_TYPE}
+    -DCMAKE_C_COMPILER=${CMAKE_C_COMPILER}
+    -DCMAKE_CXX_COMPILER=${CMAKE_CXX_COMPILER}
+    -DENABLE_REMOTE_INSPECTOR=ON
+  )
+
+  if(WIN32)
+    # ICU paths and Windows-specific compiler/linker settings
+    list(APPEND JSC_CMAKE_ARGS
+      -DICU_ROOT=${ICU_LOCAL_ROOT}
+      -DICU_LIBRARY=${ICU_LOCAL_ROOT}/lib
+      -DICU_INCLUDE_DIR=${ICU_LOCAL_ROOT}/include
+      -DCMAKE_LINKER=lld-link
+    )
+    # Static CRT and U_STATIC_IMPLEMENTATION
+    if(WEBKIT_BUILD_TYPE STREQUAL "Debug")
+      set(JSC_MSVC_RUNTIME "MultiThreadedDebug")
+    else()
+      set(JSC_MSVC_RUNTIME "MultiThreaded")
+    endif()
+    list(APPEND JSC_CMAKE_ARGS
+      -DCMAKE_MSVC_RUNTIME_LIBRARY=${JSC_MSVC_RUNTIME}
+      "-DCMAKE_C_FLAGS=/DU_STATIC_IMPLEMENTATION"
+      "-DCMAKE_CXX_FLAGS=/DU_STATIC_IMPLEMENTATION /clang:-fno-c++-static-destructors"
+    )
+  endif()
+
+  if(ENABLE_ASAN)
+    list(APPEND JSC_CMAKE_ARGS -DENABLE_SANITIZERS=address)
+  endif()
+
+  # Pass through ccache if available
+  if(CMAKE_C_COMPILER_LAUNCHER)
+    list(APPEND JSC_CMAKE_ARGS -DCMAKE_C_COMPILER_LAUNCHER=${CMAKE_C_COMPILER_LAUNCHER})
+  endif()
+  if(CMAKE_CXX_COMPILER_LAUNCHER)
+    list(APPEND JSC_CMAKE_ARGS -DCMAKE_CXX_COMPILER_LAUNCHER=${CMAKE_CXX_COMPILER_LAUNCHER})
+  endif()
+
+  execute_process(
+    COMMAND ${CMAKE_COMMAND} ${JSC_CMAKE_ARGS}
+    RESULT_VARIABLE JSC_CONFIGURE_RESULT
+  )
+  if(NOT JSC_CONFIGURE_RESULT EQUAL 0)
+    message(FATAL_ERROR "Failed to configure JSC (exit code: ${JSC_CONFIGURE_RESULT}). "
+      "Check the output above for errors.")
+  endif()
+
+  if(WIN32)
+    set(JSC_BYPRODUCTS
+      ${WEBKIT_LIB_PATH}/JavaScriptCore.lib
+      ${WEBKIT_LIB_PATH}/WTF.lib
+      ${WEBKIT_LIB_PATH}/bmalloc.lib
+    )
+  else()
+    set(JSC_BYPRODUCTS
+      ${WEBKIT_LIB_PATH}/libJavaScriptCore.a
+      ${WEBKIT_LIB_PATH}/libWTF.a
+      ${WEBKIT_LIB_PATH}/libbmalloc.a
+    )
+  endif()
+
+  if(WIN32)
+    add_custom_target(jsc ALL
+      COMMAND ${CMAKE_COMMAND} --build ${WEBKIT_PATH} --config ${WEBKIT_BUILD_TYPE} --target jsc
+      BYPRODUCTS ${JSC_BYPRODUCTS}
+      COMMENT "Building JSC (${WEBKIT_PATH})"
+    )
+  else()
+    add_custom_target(jsc ALL
+      COMMAND ${CMAKE_COMMAND} --build ${WEBKIT_PATH} --config ${WEBKIT_BUILD_TYPE} --target jsc
+      BYPRODUCTS ${JSC_BYPRODUCTS}
+      COMMENT "Building JSC (${WEBKIT_PATH})"
+      USES_TERMINAL
+    )
+  endif()
+
+  include_directories(
+    ${WEBKIT_PATH}
+    ${WEBKIT_PATH}/JavaScriptCore/Headers
+    ${WEBKIT_PATH}/JavaScriptCore/Headers/JavaScriptCore
+    ${WEBKIT_PATH}/JavaScriptCore/PrivateHeaders
+    ${WEBKIT_PATH}/bmalloc/Headers
+    ${WEBKIT_PATH}/WTF/Headers
+    ${WEBKIT_PATH}/JavaScriptCore/PrivateHeaders/JavaScriptCore
+  )
+
+  # On Windows, add ICU headers from the local ICU build
+  if(WIN32)
+    include_directories(${ICU_LOCAL_ROOT}/include)
   endif()

   # After this point, only prebuilt WebKit is supported
diff --git a/docs/project/contributing.mdx b/docs/project/contributing.mdx
index 36353feaa0a..26271188973 100644
--- a/docs/project/contributing.mdx
+++ b/docs/project/contributing.mdx
@@ -266,18 +266,13 @@ git clone https://github.com/oven-sh/WebKit vendor/WebKit
 # Check out the commit hash specified in `set(WEBKIT_VERSION <commit_hash>)` in cmake/tools/SetupWebKit.cmake
 git -C vendor/WebKit checkout <commit_hash>

-# Make a debug build of JSC. This will output build artifacts in ./vendor/WebKit/WebKitBuild/Debug
-# Optionally, you can use `bun run jsc:build` for a release build
-bun run jsc:build:debug && rm vendor/WebKit/WebKitBuild/Debug/JavaScriptCore/DerivedSources/inspector/InspectorProtocolObjects.h
-
-# After an initial run of `make jsc-debug`, you can rebuild JSC with:
-cmake --build vendor/WebKit/WebKitBuild/Debug --target jsc && rm vendor/WebKit/WebKitBuild/Debug/JavaScriptCore/DerivedSources/inspector/InspectorProtocolObjects.h
-
-# Build bun with the local JSC build
+# Build bun with the local JSC build — this automatically configures and builds JSC
 bun run build:local
 ```

-Using `bun run build:local` will build Bun in the `./build/debug-local` directory (instead of `./build/debug`), you'll have to change a couple of places to use this new directory:
+`bun run build:local` handles everything: configuring JSC, building JSC, and building Bun. On subsequent runs, JSC will incrementally rebuild if any WebKit sources changed. `ninja -Cbuild/debug-local` also works after the first build, and will build Bun+JSC.
+
+The build output goes to `./build/debug-local` (instead of `./build/debug`), so you'll need to update a couple of places:

 - The first line in `src/js/builtins.d.ts`
 - The `CompilationDatabase` line in `.clangd` config should be `CompilationDatabase: build/debug-local`
@@ -288,7 +283,7 @@ Note that the WebKit folder, including build artifacts, is 8GB+ in size.

 If you are using a JSC debug build and using VScode, make sure to run the `C/C++: Select a Configuration` command to configure intellisense to find the debug headers.

-Note that if you change make changes to our [WebKit fork](https://github.com/oven-sh/WebKit), you will also have to change `SetupWebKit.cmake` to point to the commit hash.
+Note that if you make changes to our [WebKit fork](https://github.com/oven-sh/WebKit), you will also have to change `SetupWebKit.cmake` to point to the commit hash.

 ## Troubleshooting

PATCH

echo "Patch applied successfully."
