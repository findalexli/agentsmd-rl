#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "Refer to the [Dockerfile](https://github.com/AFLplusplus/AFLplusplus/blob/stable" "plugins/testing-handbook-skills/skills/aflpp/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/testing-handbook-skills/skills/aflpp/SKILL.md b/plugins/testing-handbook-skills/skills/aflpp/SKILL.md
@@ -38,8 +38,8 @@ extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
 Compile and run:
 ```bash
 # Setup AFL++ wrapper script first (see Installation)
-./afl++ docker afl-clang-fast++ -DNO_MAIN -g -O2 -fsanitize=fuzzer harness.cc main.cc -o fuzz
-mkdir seeds && echo "a" > seeds/minimal_seed
+./afl++ docker afl-clang-fast++ -DNO_MAIN=1 -O2 -fsanitize=fuzzer harness.cc main.cc -o fuzz
+mkdir seeds && echo "aaaa" > seeds/minimal_seed
 ./afl++ docker afl-fuzz -i seeds -o out -- ./fuzz
 ```
 
@@ -50,24 +50,24 @@ AFL++ has many dependencies including LLVM, Python, and Rust. We recommend using
 | Method | When to Use | Supported Compilers |
 |--------|-------------|---------------------|
 | Ubuntu/Debian repos | Recent Ubuntu, basic features only | Ubuntu 23.10: Clang 14 & GCC 13<br>Debian 12: Clang 14 & GCC 12 |
-| Docker (from Docker Hub) | Specific AFL++ version, Apple Silicon support | As of 4.09c: Clang 14 & GCC 11 |
+| Docker (from Docker Hub) | Specific AFL++ version, Apple Silicon support | As of 4.35c: Clang 19 & GCC 11 |
 | Docker (from source) | Test unreleased features, apply patches | Configurable in Dockerfile |
 | From source | Avoid Docker, need specific patches | Adjustable via `LLVM_CONFIG` env var |
 
 ### Ubuntu/Debian
 
+Prior to installing afl++, check the clang version dependency of the packge with `apt-cache show afl++`, and install the matching `lld` version (e.g., `lld-17`).
+
+
 ```bash
-apt install afl++ lld-14
+apt install afl++ lld-17
 ```
 
-Installing `lld` is required for optional LTO mode. Verify with `afl-cc --version` and install the matching `lld` version (e.g., `lld-16`).
 
 ### Docker (from Docker Hub)
 
 ```bash
 docker pull aflplusplus/aflplusplus:stable
-# Or use a specific version like 4.08c
-docker pull aflplusplus/aflplusplus:4.08c
 ```
 
 ### Docker (from source)
@@ -80,7 +80,7 @@ docker build -t aflplusplus .
 
 ### From source
 
-Refer to the [Dockerfile](https://github.com/AFLplusplus/AFLplusplus/blob/stable/Dockerfile) for Ubuntu version requirements and dependencies. Set `LLVM_CONFIG` to specify Clang version (e.g., `llvm-config-14`).
+Refer to the [Dockerfile](https://github.com/AFLplusplus/AFLplusplus/blob/stable/Dockerfile) for Ubuntu version requirements and dependencies. Set `LLVM_CONFIG` to specify Clang version (e.g., `llvm-config-18`).
 
 ### Wrapper Script Setup
 
@@ -180,40 +180,40 @@ Choose your compilation mode:
 - **LTO mode** (`afl-clang-lto`): Best performance and instrumentation. Try this first.
 - **LLVM mode** (`afl-clang-fast`): Fall back if LTO fails to compile.
 - **GCC plugin** (`afl-gcc-fast`): For projects requiring GCC.
-- **Legacy Clang** (`afl-clang`): Last resort for compatibility.
 
 ### Basic Compilation (LLVM mode)
 
 ```bash
-./afl++ <host/docker> afl-clang-fast++ -DNO_MAIN -g -O2 -fsanitize=fuzzer harness.cc main.cc -o fuzz
+./afl++ <host/docker> afl-clang-fast++ -DNO_MAIN=1 -O2 -fsanitize=fuzzer harness.cc main.cc -o fuzz
 ```
 
 ### GCC Compilation
 
 ```bash
-./afl++ <host/docker> afl-g++-fast -DNO_MAIN -g -O2 -fsanitize=fuzzer harness.cc main.cc -o fuzz
+./afl++ <host/docker> afl-g++-fast -DNO_MAIN=1 -O2 -fsanitize=fuzzer harness.cc main.cc -o fuzz
 ```
 
 **Important:** GCC version must match the version used to compile the AFL++ GCC plugin.
 
 ### With Sanitizers
 
 ```bash
-./afl++ <host/docker> AFL_USE_ASAN=1 afl-clang-fast++ -DNO_MAIN -g -O2 -fsanitize=fuzzer harness.cc main.cc -o fuzz
+./afl++ <host/docker> AFL_USE_ASAN=1 afl-clang-fast++ -DNO_MAIN=1 -O2 -fsanitize=fuzzer harness.cc main.cc -o fuzz
 ```
 
 > **See Also:** For detailed sanitizer configuration, common issues, and advanced flags,
 > see the **address-sanitizer** and **undefined-behavior-sanitizer** technique skills.
 
 ### Build Flags
 
+Note that `-g` is not necessary, it is added by default by the AFL++ compilers.
+
 | Flag | Purpose |
 |------|---------|
-| `-DNO_MAIN` | Skip main function when using libFuzzer harness |
-| `-g` | Add debug symbols for better crash analysis |
+| `-DNO_MAIN=1` | Skip main function when using libFuzzer harness |
 | `-O2` | Production optimization level (recommended for fuzzing) |
-| `-fsanitize=fuzzer` | Enable libFuzzer compatibility mode |
-| `-fsanitize=fuzzer-no-link` | Instrument without linking fuzzer runtime (for static libraries) |
+| `-fsanitize=fuzzer` | Enable libFuzzer compatibility mode and adds the fuzzer runtime when linking executable |
+| `-fsanitize=fuzzer-no-link` | Instrument without linking fuzzer runtime (for static libraries and object files) |
 
 ## Corpus Management
 
@@ -223,7 +223,7 @@ AFL++ requires at least one non-empty seed file:
 
 ```bash
 mkdir seeds
-echo "a" > seeds/minimal_seed
+echo "aaaa" > seeds/minimal_seed
 ```
 
 For real projects, gather representative inputs:
@@ -253,7 +253,7 @@ After a campaign, minimize the corpus to keep only unique coverage:
 ### Setting Environment Variables
 
 ```bash
-./afl++ <host/docker> AFL_PIZZA_MODE=1 afl-fuzz -i seeds -o out -- ./fuzz
+./afl++ <host/docker> AFL_FAST_CAL=1 afl-fuzz -i seeds -o out -- ./fuzz
 ```
 
 ### Interpreting Output
@@ -309,7 +309,7 @@ apt install gnuplot
 | Option | Purpose |
 |--------|---------|
 | `-G 4000` | Maximum test input length (default: 1048576 bytes) |
-| `-t 10000` | Timeout in milliseconds for each test case |
+| `-t 1000` | Timeout in milliseconds for each test case (default: 1000ms) |
 | `-m 1000` | Memory limit in megabytes (default: 0 = unlimited) |
 | `-x ./dict.dict` | Use dictionary file to guide mutations |
 
@@ -376,22 +376,40 @@ Use `afl-plot` to visualize coverage over time:
 > **See Also:** For detailed coverage analysis techniques, identifying coverage gaps,
 > and systematic coverage improvement, see the **coverage-analysis** technique skill.
 
+## CMPLOG
+
+CMPLOG/RedQueen is the best path constraint solving mechanism available in any fuzzer.
+To enable it, the fuzz target needs to be instrumented for it.
+Before building the fuzzing target set the environment variable:
+
+```bash
+./afl++ <host/docker> AFL_LLVM_CMPLOG=1 make
+```
+
+No special action is needed for compiling and linking the harness.
+
+To run a fuzzer instance with a CMPLOG instrumented fuzzing target, add `-c0` to the command like arguments:
+
+```bash
+./afl++ <host/docker> afl-fuzz -c0 -S cmplog -i seeds -o state -- ./fuzz 1>secondary02.log 2>secondary02.error &
+```
+
 ## Sanitizer Integration
 
 Sanitizers are essential for finding memory corruption bugs that don't cause immediate crashes.
 
 ### AddressSanitizer (ASan)
 
 ```bash
-./afl++ <host/docker> AFL_USE_ASAN=1 afl-clang-fast++ -DNO_MAIN -g -O2 -fsanitize=fuzzer harness.cc main.cc -o fuzz
+./afl++ <host/docker> AFL_USE_ASAN=1 afl-clang-fast++ -DNO_MAIN=1 -O2 -fsanitize=fuzzer harness.cc main.cc -o fuzz
 ```
 
 **Note:** Memory limit (`-m`) is not supported with ASan due to 20TB virtual memory reservation.
 
 ### UndefinedBehaviorSanitizer (UBSan)
 
 ```bash
-./afl++ <host/docker> AFL_USE_UBSAN=1 afl-clang-fast++ -DNO_MAIN -g -O2 -fsanitize=fuzzer,undefined harness.cc main.cc -o fuzz
+./afl++ <host/docker> AFL_USE_UBSAN=1 afl-clang-fast++ -DNO_MAIN=1 -O2 -fsanitize=fuzzer,undefined harness.cc main.cc -o fuzz
 ```
 
 ### Common Sanitizer Issues
@@ -411,65 +429,18 @@ Sanitizers are essential for finding memory corruption bugs that don't cause imm
 
 | Tip | Why It Helps |
 |-----|--------------|
+| Use LLVMFuzzerTestOneInput harnesses where possible | If a fuzzing campaign has at least 85% stability then this is the most efficient fuzzing style. If not then try standard input or file input fuzzing |
 | Use dictionaries | Helps fuzzer discover format-specific keywords and magic bytes |
-| Enable persistent mode | 10-20x faster than fork server mode |
 | Set realistic timeouts | Prevents false positives from system load |
 | Limit input size | Larger inputs don't necessarily explore more space |
 | Monitor stability | Low stability indicates non-deterministic behavior |
 
-### Persistent Mode & Shared Memory
-
-Persistent mode runs test cases in a single process without forking, dramatically improving performance.
-
-For stdin-based fuzzers, enable persistent mode:
-
-```c++
-#include <stdio.h>
-#include <stdlib.h>
-#include <string.h>
-
-__AFL_FUZZ_INIT();
-
-#define MAX_BUF_SIZE 100
-
-void check_buf(char *buf, size_t buf_len) {
-    if(buf_len > 0 && buf[0] == 'a') {
-        if(buf_len > 1 && buf[1] == 'b') {
-            if(buf_len > 2 && buf[2] == 'c') {
-                abort();
-            }
-        }
-    }
-}
-
-int main() {
-#ifdef __AFL_COMPILER
-    unsigned char *input_buf;
-    __AFL_INIT();
-    input_buf = __AFL_FUZZ_TESTCASE_BUF;
-#else
-    char input_buf[MAX_BUF_SIZE];
-    if (fgets(input_buf, MAX_BUF_SIZE, stdin) == NULL) {
-        return 1;
-    }
-#endif
-
-    while (__AFL_LOOP(1000)) {
-        size_t len = strlen(input_buf);
-        check_buf(input_buf, len);
-    }
-    return 0;
-}
-```
-
-**Stability Tuning:** Use `__AFL_LOOP(1000)` for most targets. Choose smaller values (100-500) for unstable code with memory leaks or global state. Larger values (10000) don't significantly improve performance beyond 1000.
-
 ### Standard Input Fuzzing
 
 AFL++ can fuzz programs reading from stdin without a libFuzzer harness:
 
 ```bash
-./afl++ <host/docker> afl-clang-fast++ -g -O2 main_stdin.c -o fuzz_stdin
+./afl++ <host/docker> afl-clang-fast++ -O2 main_stdin.c -o fuzz_stdin
 ./afl++ <host/docker> afl-fuzz -i seeds -o out -- ./fuzz_stdin
 ```
 
@@ -480,7 +451,7 @@ This is slower than persistent mode but requires no harness code.
 For programs that read files, use `@@` placeholder:
 
 ```bash
-./afl++ <host/docker> afl-clang-fast++ -g -O2 main_file.c -o fuzz_file
+./afl++ <host/docker> afl-clang-fast++ -O2 main_file.c -o fuzz_file
 ./afl++ <host/docker> afl-fuzz -i seeds -o out -- ./fuzz_file @@
 ```
 
@@ -535,7 +506,7 @@ curl -O https://raw.githubusercontent.com/AFLplusplus/AFLplusplus/stable/utils/a
 Compile and run:
 
 ```bash
-./afl++ <host/docker> afl-clang-fast++ -g -O2 main_arg.c -o fuzz_arg
+./afl++ <host/docker> afl-clang-fast++ -O2 main_arg.c -o fuzz_arg
 ./afl++ <host/docker> afl-fuzz -i seeds -o out -- ./fuzz_arg
 ```
 
@@ -566,22 +537,25 @@ apt install zlib1g-dev
 # Configure and build static library
 export CC=afl-clang-fast CFLAGS=-fsanitize=fuzzer-no-link
 export CXX=afl-clang-fast++ CXXFLAGS="$CFLAGS"
-./afl++ <host/docker> CC="$CC" CXX="$CXX" CFLAGS="$CFLAGS" CXXFLAGS="$CFLAGS" AFL_USE_ASAN=1 ./configure --enable-shared=no
-./afl++ <host/docker> AFL_USE_ASAN=1 make
+./configure --enable-shared=no
+export AFL_LLVM_CMPLOG=1
+export AFL_USE_ASAN=1
+make
 
 # Download harness
 curl -O https://raw.githubusercontent.com/glennrp/libpng/f8e5fa92b0e37ab597616f554bee254157998227/contrib/oss-fuzz/libpng_read_fuzzer.cc
 
 # Link fuzzer
-./afl++ <host/docker> AFL_USE_ASAN=1 $CXX -fsanitize=fuzzer libpng_read_fuzzer.cc .libs/libpng16.a -lz -o fuzz
+export AFL_USE_ASAN=1
+$CXX -fsanitize=fuzzer libpng_read_fuzzer.cc .libs/libpng16.a -lz -o fuzz
 
 # Prepare seeds and dictionary
 mkdir seeds/
 curl -o seeds/input.png https://raw.githubusercontent.com/glennrp/libpng/acfd50ae0ba3198ad734e5d4dec2b05341e50924/contrib/pngsuite/iftp1n3p08.png
 curl -O https://raw.githubusercontent.com/glennrp/libpng/2fff013a6935967960a5ae626fc21432807933dd/contrib/oss-fuzz/png.dict
 
 # Start fuzzing
-./afl++ <host/docker> afl-fuzz -i seeds -o out -x png.dict -- ./fuzz
+./afl++ <host/docker> afl-fuzz -i seeds -o out -- ./fuzz
 ```
 
 ### Example: CMake-based Project
@@ -594,7 +568,7 @@ add_executable(buggy_program main.cc)
 
 add_executable(fuzz main.cc harness.cc)
 target_compile_definitions(fuzz PRIVATE NO_MAIN=1)
-target_compile_options(fuzz PRIVATE -g -O2 -fsanitize=fuzzer)
+target_compile_options(fuzz PRIVATE -O2 -fsanitize=fuzzer-no-link)
 target_link_libraries(fuzz -fsanitize=fuzzer)
 ```
 
@@ -617,9 +591,9 @@ Build and fuzz:
 
 | Problem | Cause | Solution |
 |---------|-------|----------|
-| Low exec/sec (<1k) | Not using persistent mode | Add `__AFL_LOOP()` or use libFuzzer harness |
-| Low stability (<90%) | Non-deterministic code | Check for random numbers, timestamps, uninitialized memory |
-| GCC plugin error | GCC version mismatch | Ensure system GCC matches AFL++ build |
+| Low exec/sec (<1k) | Not using persistent mode | Create a LLVMFuzzerTestOneInput style harness |
+| Low stability (<85%) | Non-deterministic code | Fuzz a program via stdin or file inputs, or create such a harness |
+| GCC plugin error | GCC version mismatch | Ensure system GCC matches AFL++ build and install gcc-$GCC_VERSION-plugin-dev |
 | No crashes found | Need sanitizers | Recompile with `AFL_USE_ASAN=1` |
 | Memory limit exceeded | ASan uses 20TB virtual | Remove `-m` flag when using ASan |
 | Docker performance loss | Virtualization overhead | Use bare metal or VM for production fuzzing |
@@ -642,7 +616,6 @@ Build and fuzz:
 |-------|------------------|
 | **libfuzzer** | Quick prototyping, single-threaded fuzzing is sufficient |
 | **libafl** | Need custom mutators or research-grade features |
-| **honggfuzz** | Hardware-based coverage feedback on Linux |
 
 ## Resources
 
@@ -651,13 +624,13 @@ Build and fuzz:
 **[AFL++ GitHub Repository](https://github.com/AFLplusplus/AFLplusplus)**
 Official repository with comprehensive documentation, examples, and issue tracker.
 
-**[Fuzzing in Depth](https://aflplus.plus/docs/fuzzing_in_depth/)**
+**[Fuzzing in Depth](https://aflplus.plus/docs/fuzzing_in_depth.md)**
 Advanced documentation by the AFL++ team covering instrumentation modes, optimization techniques, and advanced use cases.
 
 **[AFL++ Under The Hood](https://blog.ritsec.club/posts/afl-under-hood/)**
 Technical deep-dive into AFL++ internals, mutation strategies, and coverage tracking mechanisms.
 
-**[PAFL++: Combining Incremental Steps of Fuzzing Research](https://www.usenix.org/system/files/woot20-paper-fioraldi.pdf)**
+**[AFL++: Combining Incremental Steps of Fuzzing Research](https://www.usenix.org/system/files/woot20-paper-fioraldi.pdf)**
 Research paper describing AFL++ architecture and performance improvements over original AFL.
 
 ### Video Resources
PATCH

echo "Gold patch applied."
