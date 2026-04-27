#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "**[Fuzzing in Depth](https://raw.githubusercontent.com/AFLplusplus/AFLplusplus/r" "plugins/testing-handbook-skills/skills/aflpp/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/testing-handbook-skills/skills/aflpp/SKILL.md b/plugins/testing-handbook-skills/skills/aflpp/SKILL.md
@@ -519,74 +519,6 @@ Compile and run:
 | `-G` input size limit | Smaller = faster, but may miss bugs |
 | ASan ratio | 1 ASan job per 4-8 non-ASan jobs |
 
-## Real-World Examples
-
-### Example: libpng
-
-Fuzzing libpng demonstrates fuzzing a C project with static libraries:
-
-```bash
-# Get source
-curl -L -O https://downloads.sourceforge.net/project/libpng/libpng16/1.6.37/libpng-1.6.37.tar.xz
-tar xf libpng-1.6.37.tar.xz
-cd libpng-1.6.37/
-
-# Install dependencies
-apt install zlib1g-dev
-
-# Configure and build static library
-export CC=afl-clang-fast CFLAGS=-fsanitize=fuzzer-no-link
-export CXX=afl-clang-fast++ CXXFLAGS="$CFLAGS"
-./configure --enable-shared=no
-export AFL_LLVM_CMPLOG=1
-export AFL_USE_ASAN=1
-make
-
-# Download harness
-curl -O https://raw.githubusercontent.com/glennrp/libpng/f8e5fa92b0e37ab597616f554bee254157998227/contrib/oss-fuzz/libpng_read_fuzzer.cc
-
-# Link fuzzer
-export AFL_USE_ASAN=1
-$CXX -fsanitize=fuzzer libpng_read_fuzzer.cc .libs/libpng16.a -lz -o fuzz
-
-# Prepare seeds and dictionary
-mkdir seeds/
-curl -o seeds/input.png https://raw.githubusercontent.com/glennrp/libpng/acfd50ae0ba3198ad734e5d4dec2b05341e50924/contrib/pngsuite/iftp1n3p08.png
-curl -O https://raw.githubusercontent.com/glennrp/libpng/2fff013a6935967960a5ae626fc21432807933dd/contrib/oss-fuzz/png.dict
-
-# Start fuzzing
-./afl++ <host/docker> afl-fuzz -i seeds -o out -- ./fuzz
-```
-
-### Example: CMake-based Project
-
-```cmake
-project(BuggyProgram)
-cmake_minimum_required(VERSION 3.0)
-
-add_executable(buggy_program main.cc)
-
-add_executable(fuzz main.cc harness.cc)
-target_compile_definitions(fuzz PRIVATE NO_MAIN=1)
-target_compile_options(fuzz PRIVATE -O2 -fsanitize=fuzzer-no-link)
-target_link_libraries(fuzz -fsanitize=fuzzer)
-```
-
-Build and fuzz:
-
-```bash
-# Build non-instrumented binary
-./afl++ <host/docker> cmake -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ .
-./afl++ <host/docker> cmake --build . --target buggy_program
-
-# Build fuzzer
-./afl++ <host/docker> cmake -DCMAKE_C_COMPILER=afl-clang-fast -DCMAKE_CXX_COMPILER=afl-clang-fast++ .
-./afl++ <host/docker> cmake --build . --target fuzz
-
-# Fuzz
-./afl++ <host/docker> afl-fuzz -i seeds -o out -- ./fuzz
-```
-
 ## Troubleshooting
 
 | Problem | Cause | Solution |
@@ -624,7 +556,7 @@ Build and fuzz:
 **[AFL++ GitHub Repository](https://github.com/AFLplusplus/AFLplusplus)**
 Official repository with comprehensive documentation, examples, and issue tracker.
 
-**[Fuzzing in Depth](https://aflplus.plus/docs/fuzzing_in_depth.md)**
+**[Fuzzing in Depth](https://raw.githubusercontent.com/AFLplusplus/AFLplusplus/refs/heads/stable/docs/fuzzing_in_depth.md)**
 Advanced documentation by the AFL++ team covering instrumentation modes, optimization techniques, and advanced use cases.
 
 **[AFL++ Under The Hood](https://blog.ritsec.club/posts/afl-under-hood/)**
PATCH

echo "Gold patch applied."
