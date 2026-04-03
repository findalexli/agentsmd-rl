#!/usr/bin/env bash
set -euo pipefail

cd /workspace/workerd

# Idempotent: skip if already applied
if grep -q 'jsg_static_constant' src/rust/jsg-macros/lib.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/docs/reference/rust-review-checklist.md b/docs/reference/rust-review-checklist.md
index 2a6dac169c0..6454184cf2e 100644
--- a/docs/reference/rust-review-checklist.md
+++ b/docs/reference/rust-review-checklist.md
@@ -67,6 +67,9 @@ Rust types exposed to JavaScript via the JSG bindings follow these patterns:
   Methods with a receiver (`&self`/`&mut self`) are registered as instance methods on the prototype;
   methods without a receiver are registered as static methods on the constructor.
   Verify the converted name is correct and matches the intended API surface.
+- **`#[jsg_static_constant]`** on a `const` item inside a `#[jsg_resource]` impl block exposes it
+  as a read-only numeric constant on both the constructor and prototype (Rust equivalent of
+  `JSG_STATIC_CONSTANT`). The name is used as-is (no camelCase conversion).
 - **`#[jsg_struct]`** is for value types (passed by value across the JS boundary).
 - **`#[jsg_oneof]`** is for union/variant types (mapped from JS values by trying each variant).
 - **Type mappings**: `jsg::Number` wraps JS numbers (distinct from `f64`). `Vec<u8>` maps to
diff --git a/src/rust/AGENTS.md b/src/rust/AGENTS.md
index 37c5a0399d4..48f3b9ff6fc 100644
--- a/src/rust/AGENTS.md
+++ b/src/rust/AGENTS.md
@@ -9,7 +9,7 @@
 | Crate                | Purpose                                                                                                |
 | -------------------- | ------------------------------------------------------------------------------------------------------ |
 | `jsg/`               | Rust JSG bindings: `Lock`, `Ref<T>`, `Resource`, `Struct`, `Type`, `Realm`, `FeatureFlags`, module registration |
-| `jsg-macros/`        | Proc macros: `#[jsg_struct]`, `#[jsg_method]`, `#[jsg_resource]`, `#[jsg_oneof]`                       |
+| `jsg-macros/`        | Proc macros: `#[jsg_struct]`, `#[jsg_method]`, `#[jsg_resource]`, `#[jsg_oneof]`, `#[jsg_static_constant]` |
 | `jsg-test/`          | Test harness (`Harness`) for JSG Rust bindings                                                         |
 | `api/`               | Rust-implemented Node.js APIs; registers modules via `register_nodejs_modules()`                       |
 | `dns/`               | DNS record parsing (CAA, NAPTR) via CXX bridge; legacy duplicate of `api/dns.rs`, pending removal      |
@@ -25,7 +25,7 @@
 - **CXX bridge**: `#[cxx::bridge(namespace = "workerd::rust::<crate>")]` with companion `ffi.c++`/`ffi.h` files
 - **Namespace**: always `workerd::rust::*` except `python-parser` → `edgeworker::rust::python_parser`
 - **Errors**: `thiserror` for library crates; `jsg::Error` with `ExceptionType` for JSG-facing crates
-- **JSG resources**: must include `_state: jsg::ResourceState` field; `#[jsg_method]` auto-converts `snake_case` → `camelCase`; methods with `&self`/`&mut self` become instance methods, methods without a receiver become static methods
+- **JSG resources**: must include `_state: jsg::ResourceState` field; `#[jsg_method]` auto-converts `snake_case` → `camelCase`; methods with `&self`/`&mut self` become instance methods, methods without a receiver become static methods; `#[jsg_static_constant]` on `const` items exposes read-only numeric constants on both constructor and prototype (name kept as-is, no camelCase)
 - **Formatting**: `rustfmt.toml` — `group_imports = "StdExternalCrate"`, `imports_granularity = "Item"` (one `use` per import)
 - **Linting**: `just clippy <crate>` — pedantic+nursery; `allow-unwrap-in-tests`
 - **Tests**: inline `#[cfg(test)]` modules; JSG tests use `jsg_test::Harness::run_in_context()`
diff --git a/src/rust/jsg-macros/README.md b/src/rust/jsg-macros/README.md
index c1e179f4880..9c95f4a9153 100644
--- a/src/rust/jsg-macros/README.md
+++ b/src/rust/jsg-macros/README.md
@@ -93,7 +93,36 @@ impl DnsUtil {
 }
 ```

-On struct definitions, generates `jsg::Type`, wrapper struct, and `ResourceTemplate` implementations. On impl blocks, scans for `#[jsg_method]` attributes and generates the `Resource` trait implementation. Methods with a receiver (`&self`/`&mut self`) are registered as instance methods; methods without a receiver are registered as static methods.
+On struct definitions, generates `jsg::Type`, wrapper struct, and `ResourceTemplate` implementations. On impl blocks, scans for `#[jsg_method]` and `#[jsg_static_constant]` attributes and generates the `Resource` trait implementation. Methods with a receiver (`&self`/`&mut self`) are registered as instance methods; methods without a receiver are registered as static methods.
+
+## `#[jsg_static_constant]`
+
+Exposes a Rust `const` item as a read-only static constant on both the JavaScript constructor and prototype. This is the Rust equivalent of `JSG_STATIC_CONSTANT` in C++ JSG.
+
+The constant name is used as-is for the JavaScript property name (no camelCase conversion), matching the convention that constants are `UPPER_SNAKE_CASE` in both Rust and JavaScript. Only numeric types are supported (`i8`..`i64`, `u8`..`u64`, `f32`, `f64`).
+
+```rust
+#[jsg_resource]
+impl WebSocket {
+    #[jsg_static_constant]
+    pub const CONNECTING: i32 = 0;
+
+    #[jsg_static_constant]
+    pub const OPEN: i32 = 1;
+
+    #[jsg_static_constant]
+    pub const CLOSING: i32 = 2;
+
+    #[jsg_static_constant]
+    pub const CLOSED: i32 = 3;
+}
+// In JavaScript:
+//   WebSocket.CONNECTING === 0
+//   WebSocket.OPEN === 1
+//   new WebSocket(...).CLOSING === 2  (also on instances via prototype)
+```
+
+Per Web IDL, constants are `{writable: false, enumerable: true, configurable: false}`.

 ## `#[jsg_oneof]`

diff --git a/src/rust/jsg-macros/lib.rs b/src/rust/jsg-macros/lib.rs
index 7ffee3c1409..39df6aedc01 100644
--- a/src/rust/jsg-macros/lib.rs
+++ b/src/rust/jsg-macros/lib.rs
@@ -328,6 +328,34 @@ fn generate_resource_impl(impl_block: &ItemImpl) -> TokenStream {
         })
         .collect();

+    let constant_registrations: Vec<_> = impl_block
+        .items
+        .iter()
+        .filter_map(|item| {
+            let syn::ImplItem::Const(constant) = item else {
+                return None;
+            };
+            let attr = constant.attrs.iter().find(|a| {
+                a.path().is_ident("jsg_static_constant")
+                    || a.path()
+                        .segments
+                        .last()
+                        .is_some_and(|s| s.ident == "jsg_static_constant")
+            })?;
+
+            let rust_name = &constant.ident;
+            let js_name = extract_name_attribute(&attr.meta.to_token_stream().to_string())
+                .unwrap_or_else(|| rust_name.to_string());
+
+            Some(quote! {
+                jsg::Member::StaticConstant {
+                    name: #js_name.to_owned(),
+                    value: jsg::ConstantValue::from(Self::#rust_name),
+                }
+            })
+        })
+        .collect();
+
     let type_name = match &**self_ty {
         syn::Type::Path(p) => p
             .path
@@ -350,7 +378,7 @@ fn generate_resource_impl(impl_block: &ItemImpl) -> TokenStream {
         #[automatically_derived]
         impl jsg::Resource for #self_ty {
             fn members() -> Vec<jsg::Member> where Self: Sized {
-                vec![#(#method_registrations,)*]
+                vec![#(#method_registrations,)* #(#constant_registrations,)*]
             }

             fn get_drop_fn(&self) -> unsafe extern "C" fn(*mut jsg::v8::ffi::Isolate, *mut std::os::raw::c_void) {
@@ -410,6 +438,34 @@ fn is_result_type(ty: &syn::Type) -> bool {
     false
 }

+/// Marks a `const` item inside a `#[jsg_resource]` impl block as a static constant
+/// exposed to JavaScript on both the constructor and prototype.
+///
+/// The constant name is used as-is for the JavaScript property name (no camelCase
+/// conversion), matching the convention that constants are `UPPER_SNAKE_CASE` in
+/// both Rust and JavaScript.
+///
+/// Only numeric types are supported (`i8`..`i64`, `u8`..`u64`, `f32`, `f64`).
+///
+/// # Example
+///
+/// ```ignore
+/// #[jsg_resource]
+/// impl MyResource {
+///     #[jsg_static_constant]
+///     pub const MAX_SIZE: u32 = 1024;
+///
+///     #[jsg_static_constant]
+///     pub const STATUS_OK: i32 = 0;
+/// }
+/// // In JavaScript: MyResource.MAX_SIZE === 1024
+/// ```
+#[proc_macro_attribute]
+pub fn jsg_static_constant(_attr: TokenStream, item: TokenStream) -> TokenStream {
+    // Marker attribute — the actual registration is handled by #[jsg_resource] on the impl block.
+    item
+}
+
 /// Generates `jsg::Type` and `jsg::FromJS` implementations for union types.
 ///
 /// This macro automatically implements the traits needed for enums with
diff --git a/src/rust/jsg-test/tests/resource_callback.rs b/src/rust/jsg-test/tests/resource_callback.rs
index 7a66bdd1b55..2c08501ac3d 100644
--- a/src/rust/jsg-test/tests/resource_callback.rs
+++ b/src/rust/jsg-test/tests/resource_callback.rs
@@ -14,6 +14,7 @@ use jsg::ResourceState;
 use jsg::ResourceTemplate;
 use jsg_macros::jsg_method;
 use jsg_macros::jsg_resource;
+use jsg_macros::jsg_static_constant;

 #[jsg_resource]
 struct EchoResource {
@@ -313,3 +314,130 @@ fn resource_method_returns_null_for_none() {
         Ok(())
     });
 }
+
+// =============================================================================
+// Static constant tests
+// =============================================================================
+
+#[jsg_resource]
+struct ConstantResource {
+    _state: ResourceState,
+}
+
+#[jsg_resource]
+impl ConstantResource {
+    #[jsg_static_constant]
+    pub const MAX_SIZE: u32 = 1024;
+
+    #[jsg_static_constant]
+    pub const STATUS_OK: i32 = 0;
+
+    #[jsg_static_constant]
+    pub const STATUS_ERROR: i32 = -1;
+
+    #[jsg_static_constant]
+    pub const SCALE_FACTOR: f64 = 2.5;
+
+    #[jsg_method]
+    pub fn get_name(&self) -> String {
+        "constant_resource".to_owned()
+    }
+}
+
+/// Validates that static constants are accessible on the constructor.
+#[test]
+fn static_constant_accessible_on_constructor() {
+    let harness = crate::Harness::new();
+    harness.run_in_context(|lock, ctx| {
+        let template = ConstantResourceTemplate::new(lock);
+        let constructor = template.get_constructor().as_local_function(lock);
+        ctx.set_global("ConstantResource", constructor.into());
+
+        let result: Number = ctx.eval(lock, "ConstantResource.MAX_SIZE").unwrap();
+        assert!((result.value() - 1024.0).abs() < f64::EPSILON);
+
+        let result: Number = ctx.eval(lock, "ConstantResource.STATUS_OK").unwrap();
+        assert!((result.value() - 0.0).abs() < f64::EPSILON);
+
+        let result: Number = ctx.eval(lock, "ConstantResource.STATUS_ERROR").unwrap();
+        assert!((result.value() - (-1.0)).abs() < f64::EPSILON);
+
+        let result: Number = ctx.eval(lock, "ConstantResource.SCALE_FACTOR").unwrap();
+        assert!((result.value() - 2.5).abs() < f64::EPSILON);
+        Ok(())
+    });
+}
+
+/// Validates that static constants are also accessible on instances (via prototype).
+#[test]
+fn static_constant_accessible_on_instance() {
+    let harness = crate::Harness::new();
+    harness.run_in_context(|lock, ctx| {
+        let resource = jsg::Ref::new(ConstantResource {
+            _state: ResourceState::default(),
+        });
+        let mut template = ConstantResourceTemplate::new(lock);
+        let wrapped = unsafe { jsg::wrap_resource(lock, resource, &mut template) };
+        ctx.set_global("obj", wrapped);
+
+        let result: Number = ctx.eval(lock, "obj.MAX_SIZE").unwrap();
+        assert!((result.value() - 1024.0).abs() < f64::EPSILON);
+
+        let result: Number = ctx.eval(lock, "obj.STATUS_OK").unwrap();
+        assert!((result.value() - 0.0).abs() < f64::EPSILON);
+        Ok(())
+    });
+}
+
+/// Validates that static constants are read-only (not writable).
+#[test]
+fn static_constant_is_read_only() {
+    let harness = crate::Harness::new();
+    harness.run_in_context(|lock, ctx| {
+        let template = ConstantResourceTemplate::new(lock);
+        let constructor = template.get_constructor().as_local_function(lock);
+        ctx.set_global("ConstantResource", constructor.into());
+
+        // Attempt to overwrite should silently fail (strict mode would throw).
+        // The value should remain unchanged.
+        let result: Number = ctx
+            .eval(
+                lock,
+                "ConstantResource.MAX_SIZE = 9999; ConstantResource.MAX_SIZE",
+            )
+            .unwrap();
+        assert!((result.value() - 1024.0).abs() < f64::EPSILON);
+        Ok(())
+    });
+}
+
+/// Validates that static constants coexist with methods.
+#[test]
+fn static_constant_coexists_with_methods() {
+    let harness = crate::Harness::new();
+    harness.run_in_context(|lock, ctx| {
+        let resource = jsg::Ref::new(ConstantResource {
+            _state: ResourceState::default(),
+        });
+        let mut template = ConstantResourceTemplate::new(lock);
+
+        let constructor = template.get_constructor().as_local_function(lock);
+        ctx.set_global("ConstantResource", constructor.into());
+
+        let wrapped = unsafe { jsg::wrap_resource(lock, resource, &mut template) };
+        ctx.set_global("obj", wrapped);
+
+        // Instance method works
+        let result: String = ctx.eval(lock, "obj.getName()").unwrap();
+        assert_eq!(result, "constant_resource");
+
+        // Static constant works on constructor
+        let result: Number = ctx.eval(lock, "ConstantResource.MAX_SIZE").unwrap();
+        assert!((result.value() - 1024.0).abs() < f64::EPSILON);
+
+        // Static constant works on instance
+        let result: Number = ctx.eval(lock, "obj.MAX_SIZE").unwrap();
+        assert!((result.value() - 1024.0).abs() < f64::EPSILON);
+        Ok(())
+    });
+}
diff --git a/src/rust/jsg/README.md b/src/rust/jsg/README.md
index 2df98470cf0..3d0d7f23b87 100644
--- a/src/rust/jsg/README.md
+++ b/src/rust/jsg/README.md
@@ -71,3 +71,23 @@ if lock.feature_flags().get_node_js_compat() {
 | C++ call site | `src/workerd/io/worker.c++` (`initIsolate`) |
 | Cap'n Proto schema | `src/workerd/io/compatibility-date.capnp` |
 | Generated Rust bindings | `//src/workerd/io:compatibility-date_capnp_rust` (Bazel target) |
+
+## Static Constants
+
+To expose numeric constants on a resource class (equivalent to `JSG_STATIC_CONSTANT` in C++), use `#[jsg_static_constant]` on `const` items inside a `#[jsg_resource]` impl block:
+
+```rust
+use jsg_macros::jsg_static_constant;
+
+#[jsg_resource]
+impl WebSocket {
+    #[jsg_static_constant]
+    pub const CONNECTING: i32 = 0;
+
+    #[jsg_static_constant]
+    pub const OPEN: i32 = 1;
+}
+// JS: WebSocket.CONNECTING === 0, instance.OPEN === 1
+```
+
+Constants are set on both the constructor and prototype as read-only, non-configurable properties per Web IDL. The name is used as-is (no camelCase conversion). Only numeric types are supported (`i8`..`i64`, `u8`..`u64`, `f32`, `f64`).
diff --git a/src/rust/jsg/ffi.c++ b/src/rust/jsg/ffi.c++
index 92b900a5b1a..56026070cef 100644
--- a/src/rust/jsg/ffi.c++
+++ b/src/rust/jsg/ffi.c++
@@ -480,6 +480,20 @@ Global create_resource_template(Isolate* isolate, const ResourceDescriptor& desc
     prototype->Set(name, functionTemplate);
   }

+  for (const auto& constant: descriptor.static_constants) {
+    auto name = ::workerd::jsg::check(v8::String::NewFromUtf8(
+        isolate, constant.name.data(), v8::NewStringType::kInternalized, constant.name.size()));
+    auto value = v8::Number::New(isolate, constant.value);
+
+    // Per Web IDL, constants are {writable: false, enumerable: true, configurable: false}.
+    auto attrs = ::workerd::jsg::getSpecCompliantPropertyAttributes(isolate)
+        ? static_cast<v8::PropertyAttribute>(
+              v8::PropertyAttribute::ReadOnly | v8::PropertyAttribute::DontDelete)
+        : v8::PropertyAttribute::ReadOnly;
+    constructor->Set(name, value, attrs);
+    prototype->Set(name, value, attrs);
+  }
+
   auto result = scope.Escape(constructor);
   return to_ffi(v8::Global<v8::FunctionTemplate>(isolate, result));
 }
diff --git a/src/rust/jsg/lib.rs b/src/rust/jsg/lib.rs
index 8e8d9a236b6..7aa890e63aa 100644
--- a/src/rust/jsg/lib.rs
+++ b/src/rust/jsg/lib.rs
@@ -59,6 +59,7 @@ fn get_resource_descriptor<R: Resource>() -> v8::ffi::ResourceDescriptor {
         constructor: KjMaybe::None,
         methods: Vec::new(),
         static_methods: Vec::new(),
+        static_constants: Vec::new(),
     };

     for m in R::members() {
@@ -87,6 +88,15 @@ fn get_resource_descriptor<R: Resource>() -> v8::ffi::ResourceDescriptor {
                         callback: callback as usize,
                     });
             }
+            Member::StaticConstant { name, value } => {
+                let ConstantValue::Number(number_value) = value;
+                descriptor
+                    .static_constants
+                    .push(v8::ffi::StaticConstantDescriptor {
+                        name,
+                        value: number_value,
+                    });
+            }
         }
     }

@@ -748,6 +758,41 @@ pub trait Type: Sized {
     fn is_exact(value: &v8::Local<v8::Value>) -> bool;
 }

+/// Represents a constant value that can be exposed to JavaScript.
+pub enum ConstantValue {
+    Number(f64),
+}
+
+macro_rules! impl_constant_value_from_lossless {
+    ($($t:ty),*) => {
+        $(
+            impl From<$t> for ConstantValue {
+                fn from(v: $t) -> Self {
+                    Self::Number(f64::from(v))
+                }
+            }
+        )*
+    };
+}
+
+impl_constant_value_from_lossless!(i8, i16, i32, u8, u16, u32, f32, f64);
+
+// i64/u64 can lose precision in f64 (52-bit mantissa), but JavaScript numbers are
+// always f64 so this is inherent to the language boundary.
+impl From<i64> for ConstantValue {
+    #[expect(clippy::cast_precision_loss)]
+    fn from(v: i64) -> Self {
+        Self::Number(v as f64)
+    }
+}
+
+impl From<u64> for ConstantValue {
+    #[expect(clippy::cast_precision_loss)]
+    fn from(v: u64) -> Self {
+        Self::Number(v as f64)
+    }
+}
+
 pub enum Member {
     Constructor {
         callback: unsafe extern "C" fn(*mut v8::ffi::FunctionCallbackInfo),
@@ -765,6 +810,10 @@ pub enum Member {
         name: String,
         callback: unsafe extern "C" fn(*mut v8::ffi::FunctionCallbackInfo),
     },
+    StaticConstant {
+        name: String,
+        value: ConstantValue,
+    },
 }

 /// Tracks the V8 wrapper object for a Rust resource.
diff --git a/src/rust/jsg/v8.rs b/src/rust/jsg/v8.rs
index 75325bd9503..e9f7104f7c5 100644
--- a/src/rust/jsg/v8.rs
+++ b/src/rust/jsg/v8.rs
@@ -287,11 +287,17 @@ pub mod ffi {
         callback: usize,
     }

+    pub struct StaticConstantDescriptor {
+        pub name: String,
+        pub value: f64, /* number */
+    }
+
     pub struct ResourceDescriptor {
         pub name: String,
         pub constructor: KjMaybe<ConstructorDescriptor>,
         pub methods: Vec<MethodDescriptor>,
         pub static_methods: Vec<StaticMethodDescriptor>,
+        pub static_constants: Vec<StaticConstantDescriptor>,
     }

     // Resources

PATCH

echo "Patch applied successfully."
