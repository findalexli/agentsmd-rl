#!/usr/bin/env bash
set -euo pipefail

cd /workspace/workerd

# Idempotent: skip if already applied
if grep -q 'Member::StaticMethod' src/rust/jsg-macros/lib.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/docs/reference/rust-review-checklist.md b/docs/reference/rust-review-checklist.md
index 7d659b91510..2a6dac169c0 100644
--- a/docs/reference/rust-review-checklist.md
+++ b/docs/reference/rust-review-checklist.md
@@ -64,6 +64,8 @@ Rust types exposed to JavaScript via the JSG bindings follow these patterns:
   pointers used by the C++ JSG layer to wrap/unwrap the Rust object.
 - **`#[jsg_resource]`** on the impl block registers the type as a JS-visible resource.
 - **`#[jsg_method]`** auto-converts Rust `snake_case` method names to JavaScript `camelCase`.
+  Methods with a receiver (`&self`/`&mut self`) are registered as instance methods on the prototype;
+  methods without a receiver are registered as static methods on the constructor.
   Verify the converted name is correct and matches the intended API surface.
 - **`#[jsg_struct]`** is for value types (passed by value across the JS boundary).
 - **`#[jsg_oneof]`** is for union/variant types (mapped from JS values by trying each variant).
diff --git a/src/rust/AGENTS.md b/src/rust/AGENTS.md
index 87cbaab9067..4a997e6d3d9 100644
--- a/src/rust/AGENTS.md
+++ b/src/rust/AGENTS.md
@@ -25,7 +25,7 @@
 - **CXX bridge**: `#[cxx::bridge(namespace = "workerd::rust::<crate>")]` with companion `ffi.c++`/`ffi.h` files
 - **Namespace**: always `workerd::rust::*` except `python-parser` → `edgeworker::rust::python_parser`
 - **Errors**: `thiserror` for library crates; `jsg::Error` with `ExceptionType` for JSG-facing crates
-- **JSG resources**: must include `_state: jsg::ResourceState` field; `#[jsg_method]` auto-converts `snake_case` → `camelCase`
+- **JSG resources**: must include `_state: jsg::ResourceState` field; `#[jsg_method]` auto-converts `snake_case` → `camelCase`; methods with `&self`/`&mut self` become instance methods, methods without a receiver become static methods
 - **Formatting**: `rustfmt.toml` — `group_imports = "StdExternalCrate"`, `imports_granularity = "Item"` (one `use` per import)
 - **Linting**: `just clippy <crate>` — pedantic+nursery; `allow-unwrap-in-tests`
 - **Tests**: inline `#[cfg(test)]` modules; JSG tests use `jsg_test::Harness::run_in_context()`
diff --git a/src/rust/jsg-macros/README.md b/src/rust/jsg-macros/README.md
index a5880c92199..c1e179f4880 100644
--- a/src/rust/jsg-macros/README.md
+++ b/src/rust/jsg-macros/README.md
@@ -24,6 +24,11 @@ pub struct MyRecord {

 Generates FFI callback functions for JSG resource methods. The `name` parameter is optional and defaults to converting the method name from `snake_case` to `camelCase`.

+The macro automatically detects whether a method is an instance method or a static method based on the presence of a receiver (`&self` or `&mut self`):
+
+- **Instance methods** (with `&self`/`&mut self`) are placed on the prototype, called on instances (e.g., `obj.getName()`).
+- **Static methods** (without a receiver) are placed on the constructor, called on the class itself (e.g., `MyClass.create()`).
+
 Parameters and return values are handled via the `jsg::Wrappable` trait. Any type implementing `Wrappable` can be used as a parameter or return value:

 - `Option<T>` - accepts `T` or `undefined`, rejects `null`
@@ -32,19 +37,27 @@ Parameters and return values are handled via the `jsg::Wrappable` trait. Any typ

 ```rust
 impl DnsUtil {
+    // Instance method: called as obj.parseCaaRecord(...)
     #[jsg_method(name = "parseCaaRecord")]
     pub fn parse_caa_record(&self, record: String) -> Result<CaaRecord, DnsParserError> {
         // Errors are thrown as JavaScript exceptions
     }

+    // Instance method: called as obj.getName()
     #[jsg_method]
     pub fn get_name(&self) -> String {
         self.name.clone()
     }

+    // Instance method: void methods return undefined in JavaScript
     #[jsg_method]
     pub fn reset(&self) {
-        // Void methods return undefined in JavaScript
+    }
+
+    // Static method: called as DnsUtil.create(...)
+    #[jsg_method]
+    pub fn create(name: String) -> Result<String, jsg::Error> {
+        Ok(name)
     }
 }
 ```
@@ -70,12 +83,17 @@ pub struct MyUtil {
 impl DnsUtil {
     #[jsg_method]
     pub fn parse_caa_record(&self, record: String) -> Result<CaaRecord, DnsParserError> {
-        // implementation
+        // Instance method on the prototype
+    }
+
+    #[jsg_method]
+    pub fn create(name: String) -> Result<String, jsg::Error> {
+        // Static method on the constructor (no &self)
     }
 }
 ```

-On struct definitions, generates `jsg::Type`, wrapper struct, and `ResourceTemplate` implementations. On impl blocks, scans for `#[jsg_method]` attributes and generates the `Resource` trait implementation.
+On struct definitions, generates `jsg::Type`, wrapper struct, and `ResourceTemplate` implementations. On impl blocks, scans for `#[jsg_method]` attributes and generates the `Resource` trait implementation. Methods with a receiver (`&self`/`&mut self`) are registered as instance methods; methods without a receiver are registered as static methods.

 ## `#[jsg_oneof]`

diff --git a/src/rust/jsg-macros/lib.rs b/src/rust/jsg-macros/lib.rs
index 86553c0ff72..7ffee3c1409 100644
--- a/src/rust/jsg-macros/lib.rs
+++ b/src/rust/jsg-macros/lib.rs
@@ -128,6 +128,13 @@ pub fn jsg_method(_attr: TokenStream, item: TokenStream) -> TokenStream {
     let fn_block = &input_fn.block;
     let callback_name = syn::Ident::new(&format!("{fn_name}_callback"), fn_name.span());

+    // Methods with a receiver (&self, &mut self) become instance methods on the prototype.
+    // Methods without a receiver become static methods on the constructor.
+    let has_self = fn_sig
+        .inputs
+        .iter()
+        .any(|arg| matches!(arg, FnArg::Receiver(_)));
+
     let params: Vec<_> = fn_sig
         .inputs
         .iter()
@@ -179,6 +186,18 @@ pub fn jsg_method(_attr: TokenStream, item: TokenStream) -> TokenStream {
         }
     };

+    let invocation = if has_self {
+        quote! {
+            let this = args.this();
+            let self_ = jsg::unwrap_resource::<Self>(&mut lock, this);
+            let result = self_.#fn_name(#(#arg_exprs),*);
+        }
+    } else {
+        quote! {
+            let result = Self::#fn_name(#(#arg_exprs),*);
+        }
+    };
+
     quote! {
         #fn_vis #fn_sig { #fn_block }

@@ -187,9 +206,7 @@ pub fn jsg_method(_attr: TokenStream, item: TokenStream) -> TokenStream {
             let mut lock = unsafe { jsg::Lock::from_args(args) };
             let mut args = unsafe { jsg::v8::FunctionCallbackInfo::from_ffi(args) };
             #(#unwraps)*
-            let this = args.this();
-            let self_ = jsg::unwrap_resource::<Self>(&mut lock, this);
-            let result = self_.#fn_name(#(#arg_exprs),*);
+            #invocation
             #result_handling
         }
     }
@@ -291,9 +308,23 @@ fn generate_resource_impl(impl_block: &ItemImpl) -> TokenStream {
                 .unwrap_or_else(|| snake_to_camel(&rust_name.to_string()));
             let callback = syn::Ident::new(&format!("{rust_name}_callback"), rust_name.span());

-            Some(quote! {
-                jsg::Member::Method { name: #js_name.to_owned(), callback: Self::#callback }
-            })
+            // Methods with a receiver (&self, &mut self) become instance methods on the prototype.
+            // Methods without a receiver become static methods on the constructor.
+            let has_self = method
+                .sig
+                .inputs
+                .iter()
+                .any(|arg| matches!(arg, FnArg::Receiver(_)));
+
+            if has_self {
+                Some(quote! {
+                    jsg::Member::Method { name: #js_name.to_owned(), callback: Self::#callback }
+                })
+            } else {
+                Some(quote! {
+                    jsg::Member::StaticMethod { name: #js_name.to_owned(), callback: Self::#callback }
+                })
+            }
         })
         .collect();

diff --git a/src/rust/jsg-test/tests/resource_callback.rs b/src/rust/jsg-test/tests/resource_callback.rs
index 3d547c05989..7a66bdd1b55 100644
--- a/src/rust/jsg-test/tests/resource_callback.rs
+++ b/src/rust/jsg-test/tests/resource_callback.rs
@@ -8,6 +8,7 @@
 use std::cell::Cell;
 use std::rc::Rc;

+use jsg::ExceptionType;
 use jsg::Number;
 use jsg::ResourceState;
 use jsg::ResourceTemplate;
@@ -172,6 +173,127 @@ fn resource_method_returns_non_result_values() {
     });
 }

+#[jsg_resource]
+struct MathResource {
+    _state: ResourceState,
+}
+
+#[jsg_resource]
+impl MathResource {
+    #[jsg_method]
+    pub fn add(a: Number, b: Number) -> Number {
+        Number::new(a.value() + b.value())
+    }
+
+    #[jsg_method]
+    pub fn greet(name: String) -> String {
+        format!("Hello, {name}!")
+    }
+
+    #[jsg_method]
+    pub fn divide(a: Number, b: Number) -> Result<Number, jsg::Error> {
+        if b.value() == 0.0 {
+            return Err(jsg::Error::new_range_error("Division by zero"));
+        }
+        Ok(Number::new(a.value() / b.value()))
+    }
+
+    #[jsg_method]
+    pub fn get_prefix(&self) -> String {
+        "math".to_owned()
+    }
+}
+
+/// Validates that methods without &self are registered as static methods on the class.
+#[test]
+fn static_method_callable_on_class() {
+    let harness = crate::Harness::new();
+    harness.run_in_context(|lock, ctx| {
+        let template = MathResourceTemplate::new(lock);
+        let constructor = template.get_constructor().as_local_function(lock);
+        ctx.set_global("MathResource", constructor.into());
+
+        let result: Number = ctx.eval(lock, "MathResource.add(2, 3)").unwrap();
+        assert!((result.value() - 5.0).abs() < f64::EPSILON);
+
+        let result: String = ctx.eval(lock, "MathResource.greet('World')").unwrap();
+        assert_eq!(result, "Hello, World!");
+        Ok(())
+    });
+}
+
+/// Validates that instance methods still work when static methods are present.
+#[test]
+fn instance_and_static_methods_coexist() {
+    let harness = crate::Harness::new();
+    harness.run_in_context(|lock, ctx| {
+        let resource = jsg::Ref::new(MathResource {
+            _state: ResourceState::default(),
+        });
+        let mut template = MathResourceTemplate::new(lock);
+
+        // Expose the class constructor as a global
+        let constructor = template.get_constructor().as_local_function(lock);
+        ctx.set_global("MathResource", constructor.into());
+
+        // Expose an instance as a global
+        let wrapped = unsafe { jsg::wrap_resource(lock, resource, &mut template) };
+        ctx.set_global("math", wrapped);
+
+        // Instance method works on the object
+        let result: String = ctx.eval(lock, "math.getPrefix()").unwrap();
+        assert_eq!(result, "math");
+
+        // Static method works on the class
+        let result: Number = ctx.eval(lock, "MathResource.add(10, 20)").unwrap();
+        assert!((result.value() - 30.0).abs() < f64::EPSILON);
+
+        // Static methods are NOT on the instance
+        let is_undefined: bool = ctx.eval(lock, "typeof math.add === 'undefined'").unwrap();
+        assert!(is_undefined);
+        Ok(())
+    });
+}
+
+/// Validates that static methods with Result return type work on the success path.
+#[test]
+fn static_method_result_return_type() {
+    let harness = crate::Harness::new();
+    harness.run_in_context(|lock, ctx| {
+        let template = MathResourceTemplate::new(lock);
+        let constructor = template.get_constructor().as_local_function(lock);
+        ctx.set_global("MathResource", constructor.into());
+
+        let result: String = ctx.eval(lock, "MathResource.greet('Rust')").unwrap();
+        assert_eq!(result, "Hello, Rust!");
+        Ok(())
+    });
+}
+
+/// Validates that static methods propagate JS exceptions from `Result::Err`.
+#[test]
+fn static_method_throws_exception() {
+    let harness = crate::Harness::new();
+    harness.run_in_context(|lock, ctx| {
+        let template = MathResourceTemplate::new(lock);
+        let constructor = template.get_constructor().as_local_function(lock);
+        ctx.set_global("MathResource", constructor.into());
+
+        // Valid call succeeds
+        let result: Number = ctx.eval(lock, "MathResource.divide(10, 2)").unwrap();
+        assert!((result.value() - 5.0).abs() < f64::EPSILON);
+
+        // Division by zero throws a RangeError
+        let err = ctx
+            .eval::<Number>(lock, "MathResource.divide(1, 0)")
+            .unwrap_err()
+            .unwrap_jsg_err(lock);
+        assert_eq!(err.name, ExceptionType::RangeError);
+        assert!(err.message.contains("Division by zero"));
+        Ok(())
+    });
+}
+
 /// Validates that Option<T> returns null for None.
 #[test]
 fn resource_method_returns_null_for_none() {
diff --git a/src/rust/jsg/ffi.c++ b/src/rust/jsg/ffi.c++
index d684c2f988b..92b900a5b1a 100644
--- a/src/rust/jsg/ffi.c++
+++ b/src/rust/jsg/ffi.c++
@@ -484,6 +484,15 @@ Global create_resource_template(Isolate* isolate, const ResourceDescriptor& desc
   return to_ffi(v8::Global<v8::FunctionTemplate>(isolate, result));
 }

+// FunctionTemplate
+Local function_template_get_function(Isolate* isolate, const Global& tmpl) {
+  auto& global_tmpl = global_as_ref_from_ffi<v8::FunctionTemplate>(tmpl);
+  auto local_tmpl = v8::Local<v8::FunctionTemplate>::New(isolate, global_tmpl);
+  auto function = ::workerd::jsg::check(local_tmpl->GetFunction(isolate->GetCurrentContext()));
+  return to_ffi(kj::mv(function));
+}
+
+// Realm
 Realm* realm_from_isolate(Isolate* isolate) {
   auto* realm =
       static_cast<Realm*>(isolate->GetData(::workerd::jsg::SetDataIndex::SET_DATA_RUST_REALM));
diff --git a/src/rust/jsg/ffi.h b/src/rust/jsg/ffi.h
index 387b0eff37a..eba06f0148a 100644
--- a/src/rust/jsg/ffi.h
+++ b/src/rust/jsg/ffi.h
@@ -144,6 +144,9 @@ inline void register_add_builtin_module(ModuleRegistry& registry,

 Global create_resource_template(Isolate* isolate, const ResourceDescriptor& descriptor);

+// FunctionTemplate
+Local function_template_get_function(Isolate* isolate, const Global& tmpl);
+
 // Realm
 Realm* realm_from_isolate(Isolate* isolate);

diff --git a/src/rust/jsg/v8.rs b/src/rust/jsg/v8.rs
index 37545bb94f9..75325bd9503 100644
--- a/src/rust/jsg/v8.rs
+++ b/src/rust/jsg/v8.rs
@@ -312,6 +312,11 @@ pub mod ffi {
             isolate: *mut Isolate,
             value: Local, /* v8::LocalValue */
         ) -> usize /* R* */;
+
+        pub unsafe fn function_template_get_function(
+            isolate: *mut Isolate,
+            constructor: &Global, /* v8::Global<FunctionTemplate> */
+        ) -> Local /* v8::Local<Function> */;
     }

     unsafe extern "C++" {
@@ -365,6 +370,7 @@ impl Display for Local<'_, Value> {
 }
 #[derive(Debug)]
 pub struct Object;
+pub struct Function;
 pub struct FunctionTemplate;
 pub struct Array;
 pub struct TypedArray;
@@ -611,6 +617,12 @@ impl<'a> From<Local<'a, Object>> for Local<'a, Value> {
     }
 }

+impl<'a> From<Local<'a, Function>> for Local<'a, Value> {
+    fn from(value: Local<'a, Function>) -> Self {
+        unsafe { Self::from_ffi(value.isolate, value.into_ffi()) }
+    }
+}
+
 // TODO: We need to figure out a smart way of avoiding duplication.
 impl<'a> From<Local<'a, FunctionTemplate>> for Local<'a, Value> {
     fn from(value: Local<'a, FunctionTemplate>) -> Self {
@@ -1080,6 +1092,25 @@ impl<T> From<Local<'_, T>> for Global<T> {
     }
 }

+impl Global<FunctionTemplate> {
+    /// Returns the constructor function for this function template.
+    ///
+    /// This is the V8 `Function` object that can be called as a constructor or
+    /// used to access static methods, analogous to a JavaScript class reference
+    /// (e.g., `URL`, `TextEncoder`).
+    pub fn as_local_function<'a>(&self, lock: &mut Lock) -> Local<'a, Function> {
+        // SAFETY: `lock` guarantees the isolate is locked and a HandleScope is active.
+        // `self.handle` is a valid `Global<FunctionTemplate>` created by `create_resource_template`.
+        // The returned `Local` is tied to the current HandleScope via the `'a` lifetime.
+        unsafe {
+            Local::from_ffi(
+                lock.isolate(),
+                ffi::function_template_get_function(lock.isolate().as_ffi(), &self.handle),
+            )
+        }
+    }
+}
+
 // Allow implicit conversion from ffi::Global
 impl<T> From<ffi::Global> for Global<T> {
     fn from(handle: ffi::Global) -> Self {

PATCH

echo "Patch applied successfully."
