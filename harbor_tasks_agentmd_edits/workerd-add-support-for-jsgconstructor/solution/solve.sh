#!/usr/bin/env bash
set -euo pipefail

cd /workspace/workerd

# Idempotent: skip if already applied
if grep -q 'pub fn jsg_constructor' src/rust/jsg-macros/lib.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/src/rust/jsg-macros/README.md b/src/rust/jsg-macros/README.md
index 56efea241b4..7dfcceda444 100644
--- a/src/rust/jsg-macros/README.md
+++ b/src/rust/jsg-macros/README.md
@@ -125,6 +125,25 @@ impl WebSocket {

 Per Web IDL, constants are `{writable: false, enumerable: true, configurable: false}`.

+## `#[jsg_constructor]`
+
+Marks a static method as the JavaScript constructor for a `#[jsg_resource]`. When JavaScript calls `new MyClass(args)`, V8 invokes this method, creates a `jsg::Rc<Self>`, and attaches it to the `this` object.
+
+```rust
+#[jsg_resource]
+impl MyResource {
+    #[jsg_constructor]
+    fn constructor(name: String) -> Self {
+        Self { name }
+    }
+}
+// JS: let r = new MyResource("hello");
+```
+
+The method must be static (no `self` receiver) and must return `Self`. Only one `#[jsg_constructor]` is allowed per impl block. The first parameter may be `&mut Lock` if the constructor needs isolate access — it is not exposed as a JS argument.
+
+If no `#[jsg_constructor]` is present, `new MyClass()` throws an `Illegal constructor` error.
+
 ## `#[jsg_oneof]`

 Generates `jsg::Type` and `jsg::FromJS` implementations for union types. Use this to accept parameters that can be one of several JavaScript types.
diff --git a/src/rust/jsg-macros/lib.rs b/src/rust/jsg-macros/lib.rs
index 6ced500706f..ecbc5adad2d 100644
--- a/src/rust/jsg-macros/lib.rs
+++ b/src/rust/jsg-macros/lib.rs
@@ -510,6 +510,10 @@ fn generate_resource_impl(impl_block: &ItemImpl) -> TokenStream {
         })
         .collect();

+    let constructor_registration = generate_constructor_registration(impl_block, self_ty);
+
+    let constructor_vec: Vec<_> = constructor_registration.into_iter().collect();
+
     quote! {
         #impl_block

@@ -520,6 +524,7 @@ fn generate_resource_impl(impl_block: &ItemImpl) -> TokenStream {
                 Self: Sized,
             {
                 vec![
+                    #(#constructor_vec,)*
                     #(#method_registrations,)*
                     #(#constant_registrations,)*
                 ]
@@ -529,6 +534,129 @@ fn generate_resource_impl(impl_block: &ItemImpl) -> TokenStream {
     .into()
 }

+/// Scans an impl block for a `#[jsg_constructor]` attribute and generates the
+/// constructor callback registration. Returns `None` if no constructor is defined.
+fn generate_constructor_registration(
+    impl_block: &ItemImpl,
+    self_ty: &syn::Type,
+) -> Option<quote::__private::TokenStream> {
+    let constructors: Vec<_> = impl_block
+        .items
+        .iter()
+        .filter_map(|item| match item {
+            syn::ImplItem::Fn(m) if m.attrs.iter().any(|a| is_attr(a, "jsg_constructor")) => {
+                Some(m)
+            }
+            _ => None,
+        })
+        .collect();
+
+    if constructors.len() > 1 {
+        return Some(quote! {
+            compile_error!("only one #[jsg_constructor] is allowed per impl block");
+        });
+    }
+
+    constructors
+        .into_iter()
+        .map(|method| {
+            let rust_method_name = &method.sig.ident;
+            let callback_name = syn::Ident::new(
+                &format!("{rust_method_name}_constructor_callback"),
+                rust_method_name.span(),
+            );
+
+            // Constructor must NOT have a self receiver.
+            let has_self = method
+                .sig
+                .inputs
+                .iter()
+                .any(|arg| matches!(arg, FnArg::Receiver(_)));
+            if has_self {
+                return quote! {
+                    compile_error!("#[jsg_constructor] must be a static method (no self receiver)");
+                };
+            }
+
+            // Constructor must return Self.
+            let returns_self = matches!(&method.sig.output,
+                syn::ReturnType::Type(_, ty) if matches!(&**ty,
+                    syn::Type::Path(p) if p.path.is_ident("Self")
+                )
+            );
+            if !returns_self {
+                return quote! {
+                    compile_error!("#[jsg_constructor] must return Self");
+                };
+            }
+
+            // Extract parameters (same pattern as jsg_method).
+            let params: Vec<_> = method
+                .sig
+                .inputs
+                .iter()
+                .filter_map(|arg| {
+                    if let FnArg::Typed(pat_type) = arg {
+                        Some((*pat_type.ty).clone())
+                    } else {
+                        None
+                    }
+                })
+                .collect();
+
+            let has_lock_param = params.first().is_some_and(is_lock_ref);
+            let js_arg_offset = usize::from(has_lock_param);
+
+            let (unwraps, arg_exprs): (Vec<_>, Vec<_>) = params
+            .iter()
+            .enumerate()
+            .skip(js_arg_offset)
+            .map(|(i, ty)| {
+                let js_index = i - js_arg_offset;
+                let var = syn::Ident::new(&format!("arg{js_index}"), method.sig.ident.span());
+                let unwrap = quote! {
+                    let #var = match <#ty as jsg::FromJS>::from_js(&mut lock, args.get(#js_index)) {
+                        Ok(v) => v,
+                        Err(e) => {
+                            lock.throw_exception(&e);
+                            return;
+                        }
+                    };
+                };
+                (unwrap, quote! { #var })
+            })
+            .unzip();
+
+            let lock_arg = if has_lock_param {
+                quote! { &mut lock, }
+            } else {
+                quote! {}
+            };
+
+            quote! {
+                jsg::Member::Constructor {
+                    callback: {
+                        unsafe extern "C" fn #callback_name(
+                            info: *mut jsg::v8::ffi::FunctionCallbackInfo,
+                        ) {
+                            // SAFETY: info is a valid V8 FunctionCallbackInfo from the constructor call.
+                            let mut args = unsafe { jsg::v8::FunctionCallbackInfo::from_ffi(info) };
+                            let mut lock = unsafe { jsg::Lock::from_args(info) };
+
+                            #(#unwraps)*
+
+                            let resource = #self_ty::#rust_method_name(#lock_arg #(#arg_exprs),*);
+                            let rc = jsg::Rc::new(resource);
+                            rc.attach_to_this(&mut args);
+                        }
+                        #callback_name
+                    },
+                }
+            }
+        })
+        .next()
+}
+
 /// Extracts named fields from a struct, returning an empty list for unit structs.
 /// Returns `Err` with a compile error for tuple structs or non-struct data.
 fn extract_named_fields(
@@ -634,6 +762,30 @@ pub fn jsg_static_constant(_attr: TokenStream, item: TokenStream) -> TokenStream
     item
 }

+/// Marks a static method as the JavaScript constructor for a `#[jsg_resource]`.
+///
+/// The method must be a static function (no `self` receiver) that returns `Self`.
+/// When JavaScript calls `new MyResource(args)`, V8 invokes this method,
+/// wraps the returned resource, and attaches it to the `this` object.
+///
+/// ```ignore
+/// #[jsg_resource]
+/// impl MyResource {
+///     #[jsg_constructor]
+///     fn constructor(name: String) -> Self {
+///         Self { name }
+///     }
+/// }
+/// // JS: let obj = new MyResource("hello");
+/// ```
+///
+/// Only one `#[jsg_constructor]` is allowed per impl block.
+#[proc_macro_attribute]
+pub fn jsg_constructor(_attr: TokenStream, item: TokenStream) -> TokenStream {
+    // Marker attribute — the actual registration is handled by #[jsg_resource] on the impl block.
+    item
+}
+
 /// Returns true if the type is `&mut Lock` or `&mut jsg::Lock`.
 ///
 /// When a method's first typed parameter matches this pattern, the macro passes the
diff --git a/src/rust/jsg-test/tests/resource_callback.rs b/src/rust/jsg-test/tests/resource_callback.rs
index d8dca56a66a..9e5c531886f 100644
--- a/src/rust/jsg-test/tests/resource_callback.rs
+++ b/src/rust/jsg-test/tests/resource_callback.rs
@@ -15,6 +15,7 @@ use std::rc::Rc;
 use jsg::ExceptionType;
 use jsg::Number;
 use jsg::ToJS;
+use jsg_macros::jsg_constructor;
 use jsg_macros::jsg_method;
 use jsg_macros::jsg_resource;
 use jsg_macros::jsg_static_constant;
@@ -413,3 +414,146 @@ fn static_constant_coexists_with_methods() {
         Ok(())
     });
 }
+
+// =============================================================================
+// Constructor tests
+// =============================================================================
+
+#[jsg_resource]
+struct Greeting {
+    message: String,
+}
+
+#[jsg_resource]
+impl Greeting {
+    #[jsg_constructor]
+    fn constructor(message: String) -> Self {
+        Self { message }
+    }
+
+    #[jsg_method]
+    fn get_message(&self) -> String {
+        self.message.clone()
+    }
+}
+
+/// Resources without `#[jsg_constructor]` should throw when called with `new`.
+#[test]
+fn resource_without_constructor_throws() {
+    let harness = crate::Harness::new();
+    harness.run_in_context(|lock, ctx| {
+        let constructor = jsg::resource::function_template_of::<EchoResource>(lock);
+        ctx.set_global("EchoResource", constructor.into());
+
+        let result: Result<Number, _> = ctx.eval(lock, "new EchoResource('hi')");
+        assert!(result.is_err(), "should throw illegal constructor");
+        Ok(())
+    });
+}
+
+/// A `#[jsg_constructor]` method is callable from JavaScript via `new`.
+#[test]
+fn constructor_creates_instance() {
+    let harness = crate::Harness::new();
+    harness.run_in_context(|lock, ctx| {
+        let constructor = jsg::resource::function_template_of::<Greeting>(lock);
+        ctx.set_global("Greeting", constructor.into());
+
+        let result: String = ctx
+            .eval(lock, "new Greeting('hello').getMessage()")
+            .unwrap();
+        assert_eq!(result, "hello");
+        Ok(())
+    });
+}
+
+/// Constructor arguments are converted from JS types via `FromJS`.
+#[test]
+fn constructor_converts_arguments() {
+    let harness = crate::Harness::new();
+    harness.run_in_context(|lock, ctx| {
+        let constructor = jsg::resource::function_template_of::<Greeting>(lock);
+        ctx.set_global("Greeting", constructor.into());
+
+        // Number is coerced to string by V8
+        let result: String = ctx
+            .eval(lock, "new Greeting(String(42)).getMessage()")
+            .unwrap();
+        assert_eq!(result, "42");
+        Ok(())
+    });
+}
+
+/// Multiple `new` calls create distinct JS objects.
+#[test]
+fn constructor_creates_distinct_objects() {
+    let harness = crate::Harness::new();
+    harness.run_in_context(|lock, ctx| {
+        let constructor = jsg::resource::function_template_of::<Greeting>(lock);
+        ctx.set_global("Greeting", constructor.into());
+
+        let result: String = ctx
+            .eval(
+                lock,
+                "let a = new Greeting('one'); let b = new Greeting('two'); \
+                 a.getMessage() + ',' + b.getMessage()",
+            )
+            .unwrap();
+        assert_eq!(result, "one,two");
+        Ok(())
+    });
+}
+
+/// `instanceof` works correctly for constructor-created instances.
+#[test]
+fn constructor_instanceof_works() {
+    let harness = crate::Harness::new();
+    harness.run_in_context(|lock, ctx| {
+        let constructor = jsg::resource::function_template_of::<Greeting>(lock);
+        ctx.set_global("Greeting", constructor.into());
+
+        let result: String = ctx
+            .eval(
+                lock,
+                "let g = new Greeting('test'); \
+                 String(g instanceof Greeting)",
+            )
+            .unwrap();
+        assert_eq!(result, "true");
+        Ok(())
+    });
+}
+
+// Constructor with Lock parameter
+
+#[jsg_resource]
+struct Counter {
+    value: Number,
+}
+
+#[jsg_resource]
+impl Counter {
+    #[jsg_constructor]
+    fn constructor(_lock: &mut jsg::Lock, value: Number) -> Self {
+        Self { value }
+    }
+
+    #[jsg_method]
+    fn get_value(&self) -> Number {
+        self.value
+    }
+}
+
+/// `#[jsg_constructor]` with a `Lock` parameter works.
+#[test]
+fn constructor_with_lock_parameter() {
+    let harness = crate::Harness::new();
+    harness.run_in_context(|lock, ctx| {
+        let constructor = jsg::resource::function_template_of::<Counter>(lock);
+        ctx.set_global("Counter", constructor.into());
+
+        let result: Number = ctx.eval(lock, "new Counter(99).getValue()").unwrap();
+        assert!((result.value() - 99.0).abs() < f64::EPSILON);
+        Ok(())
+    });
+}
diff --git a/src/rust/jsg/README.md b/src/rust/jsg/README.md
index 9e2e1939217..54a82e25445 100644
--- a/src/rust/jsg/README.md
+++ b/src/rust/jsg/README.md
@@ -48,15 +48,14 @@ impl MyResource {
 ### Lifecycle

 ```rust
-// Allocate on the KJ heap
+// Create a resource
 let resource = jsg::Rc::new(MyResource { ... });

-// Wrap as a JS object (uses cached FunctionTemplate)
-let js_obj = MyResource::wrap(resource.clone(), &mut lock);
+// Convert to a JS object (uses cached FunctionTemplate)
+let js_obj = resource.to_js(&mut lock);

-// Unwrap from JS back to Rust
-let r: &mut MyResource = MyResource::unwrap(&mut lock, js_val)
-    .expect("not a Rust-wrapped resource");
+// Convert from JS back to a Ref
+let r: jsg::Rc<MyResource> = jsg::Rc::from_js(&mut lock, js_val)?;
 ```

 ### GC Behavior
@@ -138,6 +137,39 @@ if lock.feature_flags().get_node_js_compat() {
 | Generated Rust bindings | `//src/workerd/io:compatibility-date_capnp_rust` (Bazel target) |


+## Constructors
+
+To allow JavaScript to create instances of a resource via `new MyResource(args)`, mark a static method with `#[jsg_constructor]`:
+
+```rust
+use jsg_macros::{jsg_resource, jsg_method, jsg_constructor};
+
+#[jsg_resource]
+struct Greeting {
+    message: String,
+}
+
+#[jsg_resource]
+impl Greeting {
+    #[jsg_constructor]
+    fn constructor(message: String) -> Self {
+        Self { message }
+    }
+
+    #[jsg_method]
+    fn get_message(&self) -> String {
+        self.message.clone()
+    }
+}
+// JS: let g = new Greeting("hello"); g.getMessage() === "hello"
+```
+
+**Rules:**
+- The method must be static (no `self` receiver) and must return `Self`.
+- Only one `#[jsg_constructor]` is allowed per impl block.
+- The first parameter may be `&mut Lock` (or `&mut jsg::Lock`) if the constructor needs isolate access; it is not exposed as a JS argument.
+- If no `#[jsg_constructor]` is present, `new MyResource()` throws an `Illegal constructor` error, matching C++ JSG behavior.
+
 ## Static Constants

 To expose numeric constants on a resource class (equivalent to `JSG_STATIC_CONSTANT` in C++), use `#[jsg_static_constant]` on `const` items inside a `#[jsg_resource]` impl block:
diff --git a/src/rust/jsg/ffi.c++ b/src/rust/jsg/ffi.c++
index cd537724844..80023dc280e 100644
--- a/src/rust/jsg/ffi.c++
+++ b/src/rust/jsg/ffi.c++
@@ -333,6 +333,20 @@ Local wrap_resource(Isolate* isolate, kj::Rc<Wrappable> wrappable, const Global&
   return to_ffi(v8::Local<v8::Value>::Cast(object));
 }

+void wrappable_attach_wrapper(kj::Rc<Wrappable> wrappable, FunctionCallbackInfo& args) {
+  auto* isolate = args.GetIsolate();
+  auto object = args.This();
+
+  // attachWrapper sets up CppgcShim, TracedReference, internal fields, etc.
+  wrappable->attachWrapper(isolate, object, true);
+
+  // Override tag to identify as Rust object for unwrapping
+  auto tagAddress = const_cast<uint16_t*>(&::workerd::jsg::Wrappable::WORKERD_RUST_WRAPPABLE_TAG);
+  object->SetAlignedPointerInInternalField(::workerd::jsg::Wrappable::WRAPPABLE_TAG_FIELD_INDEX,
+      tagAddress,
+      static_cast<v8::EmbedderDataTypeTag>(::workerd::jsg::Wrappable::WRAPPABLE_TAG_FIELD_INDEX));
+}
+
 // Unwrappers
 ::rust::String unwrap_string(Isolate* isolate, Local value) {
   v8::Local<v8::String> v8Str = ::workerd::jsg::check(
diff --git a/src/rust/jsg/ffi.h b/src/rust/jsg/ffi.h
index 55a1f9f4fcf..bf58b625a82 100644
--- a/src/rust/jsg/ffi.h
+++ b/src/rust/jsg/ffi.h
@@ -173,6 +173,7 @@ kj::uint wrappable_strong_refcount(const Wrappable& wrappable);

 // Wrappers
 Local wrap_resource(Isolate* isolate, kj::Rc<Wrappable> wrappable, const Global& tmpl);
+void wrappable_attach_wrapper(kj::Rc<Wrappable> wrappable, FunctionCallbackInfo& args);

 // Unwrappers
 ::rust::String unwrap_string(Isolate* isolate, Local value);
diff --git a/src/rust/jsg/resource.rs b/src/rust/jsg/resource.rs
index cc1d6fef3ac..b32e73f6bf4 100644
--- a/src/rust/jsg/resource.rs
+++ b/src/rust/jsg/resource.rs
@@ -113,6 +113,16 @@ impl<R: Resource> Rc<R> {
         Weak::from(self)
     }

+    /// Attaches this resource to the `this` object in a V8 constructor callback.
+    ///
+    /// Called from `#[jsg_constructor]`-generated code. V8 has already created
+    /// the `this` object from the `FunctionTemplate`'s `InstanceTemplate`;
+    /// this method attaches the `Wrappable` to it so that instance methods
+    /// can resolve the resource via `resolve_resource`.
+    pub fn attach_to_this(&self, info: &mut v8::FunctionCallbackInfo) {
+        self.wrappable.attach_to_this(info);
+    }
+
     /// Returns the C++ Wrappable's strong reference count.
     #[cfg(debug_assertions)]
     pub fn strong_refcount(&self) -> u32 {
diff --git a/src/rust/jsg/v8.rs b/src/rust/jsg/v8.rs
index 2cf9362d761..aca630e09e9 100644
--- a/src/rust/jsg/v8.rs
+++ b/src/rust/jsg/v8.rs
@@ -388,6 +388,11 @@ pub mod ffi {
             constructor: &Global, /* v8::Global<FunctionTemplate> */
         ) -> Local /* v8::Local<Value> */;

+        pub unsafe fn wrappable_attach_wrapper(
+            wrappable: KjRc<Wrappable>,
+            args: Pin<&mut FunctionCallbackInfo>,
+        );
+
         pub unsafe fn unwrap_resource(
             isolate: *mut Isolate,
             value: Local, /* v8::LocalValue */
@@ -1757,6 +1762,19 @@ impl WrappableRc {
         }
     }

+    /// Attaches this Wrappable to the `this` object in a V8 constructor callback.
+    ///
+    /// V8 has already created the `this` object from the `FunctionTemplate`'s
+    /// `InstanceTemplate`; this method attaches the Wrappable to it via
+    /// `CppgcShim` so that instance methods can resolve the resource.
+    pub fn attach_to_this(&self, info: &mut FunctionCallbackInfo) {
+        // SAFETY: info is valid for the duration of the callback.
+        let pin = unsafe { std::pin::Pin::new_unchecked(&mut *info.0) };
+        // SAFETY: The Pin guarantees info is valid. wrap_constructor attaches
+        // the Wrappable to args.This() and sets the Rust tag.
+        unsafe { ffi::wrappable_attach_wrapper(self.handle.clone(), pin) };
+    }
+
     /// Creates an owning `WrappableRc` from a raw `*const ffi::Wrappable` pointer.
     ///
     /// Increments the `kj::Rc` refcount via `addRefToThis()`.

PATCH

echo "Patch applied successfully."
