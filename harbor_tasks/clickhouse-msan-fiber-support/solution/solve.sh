#!/bin/bash
set -e

cd /workspace/ClickHouse

# Apply the gold patch for MSan fiber support
cat <<'PATCH' | git apply -
diff --git a/contrib/boost-cmake/CMakeLists.txt b/contrib/boost-cmake/CMakeLists.txt
index f0db0b4e36a0..9416e2cafcf1 100644
--- a/contrib/boost-cmake/CMakeLists.txt
+++ b/contrib/boost-cmake/CMakeLists.txt
@@ -178,6 +178,8 @@ endif()

 if (SANITIZE MATCHES "address")
     target_compile_definitions(_boost_context PUBLIC BOOST_USE_ASAN)
+elseif (SANITIZE MATCHES "memory")
+    target_compile_definitions(_boost_context PUBLIC BOOST_USE_MSAN)
 elseif (SANITIZE MATCHES "thread")
     target_compile_definitions(_boost_context PUBLIC BOOST_USE_TSAN)
 endif()
diff --git a/src/Common/Fiber.h b/src/Common/Fiber.h
index 7374f309592d..e6f87fe012db 100644
--- a/src/Common/Fiber.h
+++ b/src/Common/Fiber.h
@@ -1,6 +1,5 @@
 #pragma once
-/// defines.h should be included before fiber.hpp
-/// BOOST_USE_ASAN, BOOST_USE_TSAN and BOOST_USE_UCONTEXT should be correctly defined for sanitizers.
+/// BOOST_USE_ASAN, BOOST_USE_MSAN, BOOST_USE_TSAN and BOOST_USE_UCONTEXT are defined via CMake for sanitizer builds.
 #include <base/defines.h>
 #include <boost/context/fiber.hpp>
 #include <map>
diff --git a/src/Common/FiberStack.cpp b/src/Common/FiberStack.cpp
index a28b58934041..f150b0e2d052 100644
--- a/src/Common/FiberStack.cpp
+++ b/src/Common/FiberStack.cpp
@@ -73,12 +73,12 @@ boost::context::stack_context FiberStack::allocate() const
         }
     }

-    /// Mark the fiber stack memory as initialized for MSan.
-    /// Unlike the program's main stack (which the OS zero-initializes), fiber stacks are
-    /// heap-allocated via aligned_alloc, so MSan considers them uninitialized.
-    /// This causes false positives when stack slots are reused across function calls within
-    /// the fiber. Unpoisoning is safe because MSan's per-variable lifetime tracking
-    /// (__lifetime.start / __lifetime.end) still properly detects real uninitialized variables.
+    /// MSan doesn't track shadow for struct padding bytes through return values
+    /// (the LLVM IR shadow is per-field, not per-byte of the padded representation).
+    /// Any struct with padding returned by value will have uninitialized padding shadow
+    /// in the caller. On the main thread stack this is harmless (OS zero-inits pages),
+    /// but on heap-allocated fiber stacks the dirty shadow can propagate via stack slot
+    /// reuse and eventually trigger false positives in unrelated code.
     __msan_unpoison(data, num_bytes);

     boost::context::stack_context sctx;
diff --git a/src/Common/tests/gtest_dragonbox_msan.cpp b/src/Common/tests/gtest_dragonbox_msan.cpp
new file mode 100644
index 000000000000..293e1a92c871
--- /dev/null
+++ b/src/Common/tests/gtest_dragonbox_msan.cpp
@@ -0,0 +1,51 @@
+/// Test documenting an MSan limitation with struct padding in return values.
+///
+/// MSan tracks shadow per-field in LLVM IR, not per-byte of the padded struct.
+/// When a struct with padding is returned by value, the padding bytes have no
+/// shadow entry and appear "uninitialized" in the caller — even if the callee
+/// value-initialized the struct.
+///
+/// On the main thread stack this is harmless (OS zero-inits pages), but on
+/// heap-allocated fiber stacks the dirty padding shadow can propagate via stack
+/// slot reuse. This is why FiberStack::allocate calls __msan_unpoison.
+
+#include <base/defines.h>
+#include <base/MemorySanitizer.h>
+
+#include <Common/FiberStack.h>
+#include <Common/Fiber.h>
+
+#include <dragonbox/dragonbox.h>
+
+#include <gtest/gtest.h>
+
+
+/// Demonstrates the MSan limitation: struct padding is uninitialized in return values.
+TEST(DragonboxMSan, ReturnValuePaddingShadowIsLost)
+{
+#if defined(MEMORY_SANITIZER)
+    using FP = jkj::dragonbox::unsigned_fp_t<double>;
+    /// { uint64_t significand; int exponent; /* 4 bytes padding */ }
+    static_assert(sizeof(FP) == 16);
+
+    /// Local value-init: padding shadow IS clean.
+    {
+        FP local{};
+        local.significand = 1;
+        local.exponent = -1;
+        EXPECT_EQ(__msan_test_shadow(&local, sizeof(local)), static_cast<intptr_t>(-1))
+            << "Local value-init should have clean padding";
+    }
+
+    /// Returned from a function: padding shadow is LOST — this is the MSan limitation.
+    {
+        auto returned = jkj::dragonbox::to_decimal(0.1);
+        intptr_t first_uninit = __msan_test_shadow(&returned, sizeof(returned));
+        /// Padding starts at offset 12 (after uint64_t + int).
+        EXPECT_GE(first_uninit, static_cast<intptr_t>(12))
+            << "MSan should lose padding shadow through return values";
+    }
+#else
+    GTEST_SKIP() << "This test requires MSan";
+#endif
+}
PATCH

# Verify the patch was applied by checking for distinctive line
grep -q "BOOST_USE_MSAN" contrib/boost-cmake/CMakeLists.txt && echo "Patch applied successfully"
