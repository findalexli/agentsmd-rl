#!/usr/bin/env bash
set -euo pipefail

cd /workspace/workerd

# Idempotent: skip if already applied
if grep -q 'pub struct FeatureFlags' src/rust/jsg/feature_flags.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/rust/AGENTS.md b/src/rust/AGENTS.md
index 4a997e6d3d9..37c5a0399d4 100644
--- a/src/rust/AGENTS.md
+++ b/src/rust/AGENTS.md
@@ -8,7 +8,7 @@

 | Crate                | Purpose                                                                                                |
 | -------------------- | ------------------------------------------------------------------------------------------------------ |
-| `jsg/`               | Rust JSG bindings: `Lock`, `Ref<T>`, `Resource`, `Struct`, `Type`, `Realm`, module registration        |
+| `jsg/`               | Rust JSG bindings: `Lock`, `Ref<T>`, `Resource`, `Struct`, `Type`, `Realm`, `FeatureFlags`, module registration |
 | `jsg-macros/`        | Proc macros: `#[jsg_struct]`, `#[jsg_method]`, `#[jsg_resource]`, `#[jsg_oneof]`                       |
 | `jsg-test/`          | Test harness (`Harness`) for JSG Rust bindings                                                         |
 | `api/`               | Rust-implemented Node.js APIs; registers modules via `register_nodejs_modules()`                       |
@@ -30,3 +30,4 @@
 - **Linting**: `just clippy <crate>` — pedantic+nursery; `allow-unwrap-in-tests`
 - **Tests**: inline `#[cfg(test)]` modules; JSG tests use `jsg_test::Harness::run_in_context()`
 - **FFI pointers**: functions receiving raw pointers must be `unsafe fn` (see `jsg/README.md`)
+- **Feature flags**: `Lock::feature_flags()` returns a capnp `compatibility_flags::Reader` for the current worker. Use `lock.feature_flags().get_node_js_compat()`. Flags are parsed once and stored in the `Realm` at construction; C++ passes canonical capnp bytes to `realm_create()`. Schema: `src/workerd/io/compatibility-date.capnp`, generated Rust bindings: `compatibility_date_capnp` crate.
diff --git a/src/rust/jsg-test/BUILD.bazel b/src/rust/jsg-test/BUILD.bazel
index 020dc54b3b9..0c07ba40cac 100644
--- a/src/rust/jsg-test/BUILD.bazel
+++ b/src/rust/jsg-test/BUILD.bazel
@@ -18,6 +18,8 @@ wd_cc_library(
     srcs = ["ffi.c++"],
     implementation_deps = [
         ":lib.rs@cxx",
+        "//src/workerd/io:compatibility-date_capnp",
+        "@capnp-cpp//src/capnp:capnp",
     ],
     visibility = ["//visibility:public"],
     deps = [
diff --git a/src/rust/jsg-test/ffi.c++ b/src/rust/jsg-test/ffi.c++
index a65016fcfe1..e681347773b 100644
--- a/src/rust/jsg-test/ffi.c++
+++ b/src/rust/jsg-test/ffi.c++
@@ -1,5 +1,6 @@
 #include "ffi.h"

+#include <workerd/io/compatibility-date.capnp.h>
 #include <workerd/jsg/setup.h>
 #include <workerd/rust/jsg-test/lib.rs.h>
 #include <workerd/rust/jsg/ffi-inl.h>
@@ -9,6 +10,7 @@

 #include <v8.h>

+#include <capnp/message.h>
 #include <kj/common.h>

 using namespace kj_rs;
@@ -38,7 +40,14 @@ TestHarness::TestHarness(::workerd::jsg::V8StackScope&)
     : isolate(kj::heap<TestIsolate>(getV8System(), kj::heap<::workerd::jsg::IsolateObserver>())),
       locker(isolate->getIsolate()),
       isolateScope(isolate->getIsolate()),
-      realm(::workerd::rust::jsg::realm_create(isolate->getIsolate())) {
+      realm([&] {
+        // Build default (all-false) feature flags for the test realm.
+        capnp::MallocMessageBuilder flagsMessage;
+        flagsMessage.initRoot<CompatibilityFlags>();
+        auto words = capnp::canonicalize(flagsMessage.getRoot<CompatibilityFlags>().asReader());
+        return ::workerd::rust::jsg::realm_create(
+            isolate->getIsolate(), words.asBytes().as<Rust>());
+      }()) {
   isolate->getIsolate()->SetData(::workerd::jsg::SetDataIndex::SET_DATA_RUST_REALM, &*realm);
 }

diff --git a/src/rust/jsg/BUILD.bazel b/src/rust/jsg/BUILD.bazel
index 5c243aeb7f4..0dc9cd6d0fa 100644
--- a/src/rust/jsg/BUILD.bazel
+++ b/src/rust/jsg/BUILD.bazel
@@ -12,7 +12,11 @@ wd_rust_crate(
     ],
     cxx_bridge_tags = ["no-clang-tidy"],
     visibility = ["//visibility:public"],
-    deps = [":ffi"],
+    deps = [
+        ":ffi",
+        "//src/workerd/io:compatibility-date_capnp_rust",
+        "@crates_vendor//:capnp",
+    ],
 )

 wd_cc_library(
diff --git a/src/rust/jsg/README.md b/src/rust/jsg/README.md
index 0b67a13e8b5..2df98470cf0 100644
--- a/src/rust/jsg/README.md
+++ b/src/rust/jsg/README.md
@@ -7,7 +7,10 @@ Rust bindings for the JSG (JavaScript Glue) layer, enabling Rust code to integra
 Functions exposed to C++ via FFI that receive raw pointers must be marked as `unsafe fn`. The `unsafe` keyword indicates to callers that the function deals with raw pointers and requires careful handling.

 ```rust
-pub unsafe fn realm_create(isolate: *mut v8::ffi::Isolate) -> Box<Realm> {
+pub unsafe fn realm_create(
+    isolate: *mut v8::ffi::Isolate,
+    feature_flags_data: &[u8],
+) -> Box<Realm> {
     // implementation
 }
 ```
@@ -38,3 +41,33 @@ pub fn process(&self, value: StringOrNumber) -> Result<String, jsg::Error> {
 ```

 This is similar to `kj::OneOf<>` in C++ JSG.
+
+## Feature Flags (Compatibility Flags)
+
+`Lock::feature_flags()` provides Rust-native access to the worker's compatibility flags, backed by the Cap'n Proto Rust crate (`capnp`). The flags are deserialized from the `CompatibilityFlags` schema in `src/workerd/io/compatibility-date.capnp`.
+
+### Reading flags
+
+```rust
+if lock.feature_flags().get_node_js_compat() {
+    // Node.js compatibility behavior
+}
+```
+
+`feature_flags()` returns a capnp-generated `compatibility_flags::Reader` with a getter for each boolean flag (e.g., `get_node_js_compat()`, `get_url_standard()`, `get_fetch_refuses_unknown_protocols()`).
+
+### How it works
+
+1. During worker initialization, C++ canonicalizes the worker's `CompatibilityFlags` via `capnp::canonicalize()` and passes the bytes to `realm_create()`, which parses them once and stores the result in the per-context `Realm`.
+2. `lock.feature_flags()` reads the cached `FeatureFlags` and returns its capnp reader. No copies or re-parsing on access.
+
+### Key types and files
+
+| Item | Location |
+|------|----------|
+| `FeatureFlags` struct | `src/rust/jsg/feature_flags.rs` |
+| `Lock::feature_flags()` | `src/rust/jsg/lib.rs` |
+| `realm_create()` FFI | `src/rust/jsg/lib.rs` (CXX bridge) |
+| C++ call site | `src/workerd/io/worker.c++` (`initIsolate`) |
+| Cap'n Proto schema | `src/workerd/io/compatibility-date.capnp` |
+| Generated Rust bindings | `//src/workerd/io:compatibility-date_capnp_rust` (Bazel target) |
diff --git a/src/rust/jsg/feature_flags.rs b/src/rust/jsg/feature_flags.rs
new file mode 100644
index 00000000000..ae3d7bb5021
--- /dev/null
+++ b/src/rust/jsg/feature_flags.rs
@@ -0,0 +1,123 @@
+//! Rust-native access to workerd compatibility flags.
+//!
+//! ```ignore
+//! if lock.feature_flags().get_node_js_compat() {
+//!     // Node.js compatibility behavior
+//! }
+//! ```
+
+use capnp::message::ReaderOptions;
+pub use compatibility_date_capnp::compatibility_flags;
+
+/// Provides access to the current worker's compatibility flags.
+///
+/// Parsed once from canonical Cap'n Proto bytes during Realm construction
+/// and stored in the per-context [`Realm`](crate::Realm). Access via
+/// [`Lock::feature_flags()`](crate::Lock::feature_flags).
+pub struct FeatureFlags {
+    message: capnp::message::Reader<Vec<Vec<u8>>>,
+}
+
+impl FeatureFlags {
+    /// Create from canonical (single-segment, no segment table) Cap'n Proto bytes.
+    ///
+    /// On the C++ side, produce these via `capnp::canonicalize(reader)`.
+    ///
+    /// # Panics
+    ///
+    /// Panics if `data` is empty or not word-aligned.
+    pub(crate) fn from_bytes(data: &[u8]) -> Self {
+        assert!(!data.is_empty(), "FeatureFlags data must not be empty");
+        assert!(
+            data.len().is_multiple_of(8),
+            "FeatureFlags data must be word-aligned (got {} bytes)",
+            data.len()
+        );
+        let segments = vec![data.to_vec()];
+        let message = capnp::message::Reader::new(segments, ReaderOptions::new());
+        Self { message }
+    }
+
+    /// Returns the `CompatibilityFlags` reader.
+    ///
+    /// The reader has a getter for each flag defined in `compatibility-date.capnp`
+    /// (e.g., `get_node_js_compat()`).
+    ///
+    /// # Panics
+    ///
+    /// Panics if the stored message has an invalid capnp root (should never happen
+    /// when constructed via `from_bytes`).
+    pub fn reader(&self) -> compatibility_flags::Reader<'_> {
+        self.message
+            .get_root::<compatibility_flags::Reader<'_>>()
+            .expect("Invalid FeatureFlags capnp root")
+    }
+}
+
+#[cfg(test)]
+mod tests {
+    use super::*;
+
+    /// Helper: build a `CompatibilityFlags` capnp message with the given flag setter,
+    /// return the raw single-segment bytes (no wire-format header).
+    fn build_flags<F>(setter: F) -> Vec<u8>
+    where
+        F: FnOnce(compatibility_flags::Builder<'_>),
+    {
+        let mut message = capnp::message::Builder::new_default();
+        {
+            let flags = message.init_root::<compatibility_flags::Builder<'_>>();
+            setter(flags);
+        }
+        let output = message.get_segments_for_output();
+        output[0].to_vec()
+    }
+
+    #[test]
+    fn from_bytes_roundtrip() {
+        let bytes = build_flags(|mut f| {
+            f.set_node_js_compat(true);
+        });
+        let ff = FeatureFlags::from_bytes(&bytes);
+        assert!(ff.reader().get_node_js_compat());
+    }
+
+    #[test]
+    #[should_panic(expected = "FeatureFlags data must not be empty")]
+    fn from_bytes_empty_panics() {
+        FeatureFlags::from_bytes(&[]);
+    }
+
+    #[test]
+    fn default_flags_are_false() {
+        let bytes = build_flags(|_| {});
+        let ff = FeatureFlags::from_bytes(&bytes);
+        assert!(!ff.reader().get_node_js_compat());
+        assert!(!ff.reader().get_node_js_compat_v2());
+        assert!(!ff.reader().get_fetch_refuses_unknown_protocols());
+    }
+
+    #[test]
+    fn multiple_flags() {
+        let bytes = build_flags(|mut f| {
+            f.set_node_js_compat(true);
+            f.set_node_js_compat_v2(true);
+            f.set_fetch_refuses_unknown_protocols(false);
+        });
+        let ff = FeatureFlags::from_bytes(&bytes);
+        assert!(ff.reader().get_node_js_compat());
+        assert!(ff.reader().get_node_js_compat_v2());
+        assert!(!ff.reader().get_fetch_refuses_unknown_protocols());
+    }
+
+    #[test]
+    fn reader_called_multiple_times() {
+        let bytes = build_flags(|mut f| {
+            f.set_node_js_compat(true);
+        });
+        let ff = FeatureFlags::from_bytes(&bytes);
+        // Reader can be obtained multiple times from the same FeatureFlags.
+        assert!(ff.reader().get_node_js_compat());
+        assert!(ff.reader().get_node_js_compat());
+    }
+}
diff --git a/src/rust/jsg/lib.rs b/src/rust/jsg/lib.rs
index f3eaa15d244..8e8d9a236b6 100644
--- a/src/rust/jsg/lib.rs
+++ b/src/rust/jsg/lib.rs
@@ -9,10 +9,12 @@ use std::rc::Rc;

 use kj_rs::KjMaybe;

+pub mod feature_flags;
 pub mod modules;
 pub mod v8;
 mod wrappable;

+pub use feature_flags::FeatureFlags;
 pub use v8::BigInt64Array;
 pub use v8::BigUint64Array;
 pub use v8::Float32Array;
@@ -32,8 +34,11 @@ mod ffi {
     extern "Rust" {
         type Realm;

+        /// Create a fully-initialized Realm with feature flags.
+        /// `feature_flags_data` is canonical (single-segment, no segment table) Cap'n Proto
+        /// bytes produced by `capnp::canonicalize()` on the C++ side.
         #[expect(clippy::unnecessary_box_returns)]
-        unsafe fn realm_create(isolate: *mut Isolate) -> Box<Realm>;
+        unsafe fn realm_create(isolate: *mut Isolate, feature_flags_data: &[u8]) -> Box<Realm>;
     }

     unsafe extern "C++" {
@@ -630,10 +635,21 @@ impl Lock {
         todo!()
     }

-    fn realm(&mut self) -> &mut Realm {
+    pub(crate) fn realm(&mut self) -> &mut Realm {
         unsafe { &mut *crate::ffi::realm_from_isolate(self.isolate().as_ffi()) }
     }

+    /// Returns the current worker's compatibility flags reader.
+    ///
+    /// ```ignore
+    /// if lock.feature_flags().get_node_js_compat() {
+    ///     // Node.js compatibility behavior
+    /// }
+    /// ```
+    pub fn feature_flags(&mut self) -> compatibility_date_capnp::compatibility_flags::Reader<'_> {
+        self.realm().feature_flags.reader()
+    }
+
     /// Throws an error as a V8 exception.
     pub fn throw_exception(&mut self, err: &Error) {
         unsafe {
@@ -876,14 +892,17 @@ pub unsafe fn drop_resource<R: Resource>(_isolate: *mut ffi::Isolate, this: *mut
 pub struct Realm {
     isolate: v8::IsolatePtr,
     resources: Vec<*mut ResourceState>,
+    /// Parsed `CompatibilityFlags` capnp message, initialized at construction.
+    feature_flags: FeatureFlags,
 }

 impl Realm {
-    /// Creates a new Realm from a V8 isolate.
-    pub fn from_isolate(isolate: v8::IsolatePtr) -> Self {
+    /// Creates a new Realm with its feature flags.
+    pub fn new(isolate: v8::IsolatePtr, feature_flags: FeatureFlags) -> Self {
         Self {
             isolate,
             resources: Vec::new(),
+            feature_flags,
         }
     }

@@ -928,6 +947,7 @@ impl Drop for Realm {
 }

 #[expect(clippy::unnecessary_box_returns)]
-unsafe fn realm_create(isolate: *mut v8::ffi::Isolate) -> Box<Realm> {
-    unsafe { Box::new(Realm::from_isolate(v8::IsolatePtr::from_ffi(isolate))) }
+unsafe fn realm_create(isolate: *mut v8::ffi::Isolate, feature_flags_data: &[u8]) -> Box<Realm> {
+    let feature_flags = FeatureFlags::from_bytes(feature_flags_data);
+    unsafe { Box::new(Realm::new(v8::IsolatePtr::from_ffi(isolate), feature_flags)) }
 }
diff --git a/src/workerd/io/worker.c++ b/src/workerd/io/worker.c++
index aaa7e562048..143c597ec72 100644
--- a/src/workerd/io/worker.c++
+++ b/src/workerd/io/worker.c++
@@ -732,9 +732,12 @@ struct Worker::Isolate::Impl {
     kj::Maybe<std::unique_ptr<v8_inspector::V8Inspector>> inspector;
     jsg::runInV8Stack([&](jsg::V8StackScope& stackScope) {
       auto lock = api.lock(stackScope);
-      realm = ::workerd::rust::jsg::realm_create(lock->v8Isolate);
+      auto featureFlagsWords = capnp::canonicalize(api.getFeatureFlags());
+      realm = ::workerd::rust::jsg::realm_create(
+          lock->v8Isolate, featureFlagsWords.asBytes().as<kj_rs::Rust>());
       lock->v8Isolate->SetData(
           ::workerd::jsg::SetDataIndex::SET_DATA_RUST_REALM, &*KJ_REQUIRE_NONNULL(realm));
+
       limitEnforcer.customizeIsolate(lock->v8Isolate);
       if (inspectorPolicy != InspectorPolicy::DISALLOW) {
         // We just created our isolate, so we don't need to use Isolate::Impl::Lock.

PATCH

echo "Patch applied successfully."
