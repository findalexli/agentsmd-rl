#!/usr/bin/env bash
set -euo pipefail

cd /workspace/workerd

# Idempotent: skip if already applied
if grep -q 'pub fn jsg_oneof' src/rust/jsg-macros/lib.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/rust/jsg-macros/README.md b/src/rust/jsg-macros/README.md
index ba0cef92508..a5880c92199 100644
--- a/src/rust/jsg-macros/README.md
+++ b/src/rust/jsg-macros/README.md
@@ -76,3 +76,32 @@ impl DnsUtil {
 ```

 On struct definitions, generates `jsg::Type`, wrapper struct, and `ResourceTemplate` implementations. On impl blocks, scans for `#[jsg_method]` attributes and generates the `Resource` trait implementation.
+
+## `#[jsg_oneof]`
+
+Generates `jsg::Type` and `jsg::FromJS` implementations for union types. Use this to accept parameters that can be one of several JavaScript types.
+
+Each enum variant should be a single-field tuple variant where the field type implements `jsg::Type` and `jsg::FromJS` (e.g., `String`, `f64`, `bool`).
+
+```rust
+use jsg_macros::jsg_oneof;
+
+#[jsg_oneof]
+#[derive(Debug, Clone)]
+enum StringOrNumber {
+    String(String),
+    Number(f64),
+}
+
+impl MyResource {
+    #[jsg_method]
+    pub fn process(&self, value: StringOrNumber) -> Result<String, jsg::Error> {
+        match value {
+            StringOrNumber::String(s) => Ok(format!("string: {}", s)),
+            StringOrNumber::Number(n) => Ok(format!("number: {}", n)),
+        }
+    }
+}
+```
+
+The macro generates type-checking code that matches JavaScript values to enum variants without coercion. If no variant matches, a `TypeError` is thrown listing all expected types.
diff --git a/src/rust/jsg-macros/lib.rs b/src/rust/jsg-macros/lib.rs
index 46b486d43bb..4754c206560 100644
--- a/src/rust/jsg-macros/lib.rs
+++ b/src/rust/jsg-macros/lib.rs
@@ -346,3 +346,121 @@ fn is_result_type(ty: &syn::Type) -> bool {
     }
     false
 }
+
+/// Generates `jsg::Type` and `jsg::FromJS` implementations for union types.
+///
+/// This macro automatically implements the traits needed for enums with
+/// single-field tuple variants to be used directly as `jsg_method` parameters.
+/// Each variant should contain a type that implements `jsg::Type` and `jsg::FromJS`.
+///
+/// # Example
+///
+/// ```ignore
+/// use jsg_macros::jsg_oneof;
+///
+/// #[jsg_oneof]
+/// #[derive(Debug, Clone)]
+/// enum StringOrNumber {
+///     String(String),
+///     Number(f64),
+/// }
+///
+/// // Use directly as a parameter type:
+/// #[jsg_method]
+/// fn process(&self, value: StringOrNumber) -> Result<String, jsg::Error> {
+///     match value {
+///         StringOrNumber::String(s) => Ok(format!("string: {}", s)),
+///         StringOrNumber::Number(n) => Ok(format!("number: {}", n)),
+///     }
+/// }
+/// ```
+#[proc_macro_attribute]
+pub fn jsg_oneof(_attr: TokenStream, item: TokenStream) -> TokenStream {
+    let input = parse_macro_input!(item as DeriveInput);
+    let name = &input.ident;
+
+    let Data::Enum(data) = &input.data else {
+        return error(&input, "#[jsg_oneof] can only be applied to enums");
+    };
+
+    let mut variants = Vec::new();
+    for variant in &data.variants {
+        let variant_name = &variant.ident;
+        let Fields::Unnamed(fields) = &variant.fields else {
+            return error(
+                variant,
+                "#[jsg_oneof] variants must be tuple variants (e.g., `Variant(Type)`)",
+            );
+        };
+        if fields.unnamed.len() != 1 {
+            return error(variant, "#[jsg_oneof] variants must have exactly one field");
+        }
+        let inner_type = &fields.unnamed[0].ty;
+        variants.push((variant_name, inner_type));
+    }
+
+    if variants.is_empty() {
+        return error(&input, "#[jsg_oneof] requires at least one variant");
+    }
+
+    let type_checks: Vec<_> = variants
+        .iter()
+        .map(|(variant_name, inner_type)| {
+            quote! {
+                if let Some(result) = <#inner_type as jsg::FromJS>::try_from_js_exact(lock, &value) {
+                    return result.map(Self::#variant_name);
+                }
+            }
+        })
+        .collect();
+
+    let type_names: Vec<_> = variants
+        .iter()
+        .map(|(_, inner_type)| {
+            quote! { <#inner_type as jsg::Type>::class_name() }
+        })
+        .collect();
+
+    let is_exact_checks: Vec<_> = variants
+        .iter()
+        .map(|(_, inner_type)| {
+            quote! { <#inner_type as jsg::Type>::is_exact(value) }
+        })
+        .collect();
+
+    let error_msg = quote! {
+        let expected: Vec<&str> = vec![#(#type_names),*];
+        let msg = format!(
+            "Expected one of [{}] but got {}",
+            expected.join(", "),
+            value.type_of()
+        );
+        Err(jsg::Error::new_type_error(msg))
+    };
+
+    quote! {
+        #input
+
+        #[automatically_derived]
+        impl jsg::Type for #name {
+            fn class_name() -> &'static str {
+                stringify!(#name)
+            }
+
+            fn is_exact(value: &jsg::v8::Local<jsg::v8::Value>) -> bool {
+                #(#is_exact_checks)||*
+            }
+        }
+
+        #[automatically_derived]
+        impl jsg::FromJS for #name {
+            type ResultType = Self;
+
+            fn from_js(lock: &mut jsg::Lock, value: jsg::v8::Local<jsg::v8::Value>) -> Result<Self::ResultType, jsg::Error> {
+                #(#type_checks)*
+                #error_msg
+            }
+        }
+    }
+    .into()
+}
diff --git a/src/rust/jsg-test/tests/jsg_oneof.rs b/src/rust/jsg-test/tests/jsg_oneof.rs
new file mode 100644
index 00000000000..1a56e0c6ebb
--- /dev/null
+++ b/src/rust/jsg-test/tests/jsg_oneof.rs
@@ -0,0 +1,271 @@
+use jsg::ExceptionType;
+use jsg::ResourceState;
+use jsg::ResourceTemplate;
+use jsg_macros::jsg_method;
+use jsg_macros::jsg_oneof;
+use jsg_macros::jsg_resource;
+
+#[jsg_oneof]
+#[derive(Debug, Clone, PartialEq)]
+enum StringOrNumber {
+    String(String),
+    Number(f64),
+}
+
+#[jsg_oneof]
+#[derive(Debug, Clone, PartialEq)]
+enum NumberOrString {
+    Number(f64),
+    String(String),
+}
+
+#[jsg_oneof]
+#[derive(Debug, Clone, PartialEq)]
+enum StringOrBool {
+    String(String),
+    Bool(bool),
+}
+
+#[jsg_oneof]
+#[derive(Debug, Clone, PartialEq)]
+enum ThreeTypes {
+    String(String),
+    Number(f64),
+    Bool(bool),
+}
+
+#[jsg_resource]
+struct EnumTestResource {
+    _state: ResourceState,
+}
+
+#[jsg_resource]
+#[expect(clippy::unnecessary_wraps)]
+impl EnumTestResource {
+    #[jsg_method]
+    pub fn string_or_number(&self, value: StringOrNumber) -> Result<String, jsg::Error> {
+        match value {
+            StringOrNumber::String(s) => Ok(format!("string:{s}")),
+            StringOrNumber::Number(n) => Ok(format!("number:{n}")),
+        }
+    }
+
+    #[jsg_method]
+    pub fn string_or_number_ref(&self, value: &StringOrNumber) -> Result<String, jsg::Error> {
+        match value {
+            StringOrNumber::String(s) => Ok(format!("ref_string:{s}")),
+            StringOrNumber::Number(n) => Ok(format!("ref_number:{n}")),
+        }
+    }
+
+    #[jsg_method]
+    pub fn string_or_bool(&self, value: StringOrBool) -> Result<String, jsg::Error> {
+        match value {
+            StringOrBool::String(s) => Ok(format!("string:{s}")),
+            StringOrBool::Bool(b) => Ok(format!("bool:{b}")),
+        }
+    }
+
+    #[jsg_method]
+    pub fn three_types(&self, value: ThreeTypes) -> Result<String, jsg::Error> {
+        match value {
+            ThreeTypes::String(s) => Ok(format!("string:{s}")),
+            ThreeTypes::Number(n) => Ok(format!("number:{n}")),
+            ThreeTypes::Bool(b) => Ok(format!("bool:{b}")),
+        }
+    }
+
+    #[jsg_method]
+    pub fn number_or_string(&self, value: NumberOrString) -> Result<String, jsg::Error> {
+        match value {
+            NumberOrString::Number(n) => Ok(format!("number:{n}")),
+            NumberOrString::String(s) => Ok(format!("string:{s}")),
+        }
+    }
+}
+
+#[test]
+fn jsg_oneof_derives_debug_and_clone() {
+    let s = StringOrNumber::String("test".to_owned());
+    let cloned = s.clone();
+    assert_eq!(s, cloned);
+
+    let debug_str = format!("{s:?}");
+    assert!(debug_str.contains("String"));
+    assert!(debug_str.contains("test"));
+}
+
+#[test]
+fn jsg_oneof_string_or_number_accepts_string() {
+    let harness = crate::Harness::new();
+    harness.run_in_context(|lock, ctx| {
+        let resource = jsg::Ref::new(EnumTestResource {
+            _state: ResourceState::default(),
+        });
+        let mut template = EnumTestResourceTemplate::new(lock);
+        let wrapped = unsafe { jsg::wrap_resource(lock, resource, &mut template) };
+        ctx.set_global("resource", wrapped);
+
+        let result: String = ctx.eval(lock, "resource.stringOrNumber('hello')").unwrap();
+        assert_eq!(result, "string:hello");
+        Ok(())
+    });
+}
+
+#[test]
+fn jsg_oneof_string_or_number_accepts_number() {
+    let harness = crate::Harness::new();
+    harness.run_in_context(|lock, ctx| {
+        let resource = jsg::Ref::new(EnumTestResource {
+            _state: ResourceState::default(),
+        });
+        let mut template = EnumTestResourceTemplate::new(lock);
+        let wrapped = unsafe { jsg::wrap_resource(lock, resource, &mut template) };
+        ctx.set_global("resource", wrapped);
+
+        let result: String = ctx.eval(lock, "resource.stringOrNumber(42)").unwrap();
+        assert_eq!(result, "number:42");
+        Ok(())
+    });
+}
+
+#[test]
+fn jsg_oneof_string_or_number_rejects_boolean() {
+    let harness = crate::Harness::new();
+    harness.run_in_context(|lock, ctx| {
+        let resource = jsg::Ref::new(EnumTestResource {
+            _state: ResourceState::default(),
+        });
+        let mut template = EnumTestResourceTemplate::new(lock);
+        let wrapped = unsafe { jsg::wrap_resource(lock, resource, &mut template) };
+        ctx.set_global("resource", wrapped);
+
+        let err = ctx
+            .eval::<String>(lock, "resource.stringOrNumber(true)")
+            .unwrap_err()
+            .unwrap_jsg_err(lock);
+        assert_eq!(err.name, ExceptionType::TypeError);
+        assert!(err.message.contains("string"));
+        assert!(err.message.contains("number"));
+        Ok(())
+    });
+}
+
+#[test]
+fn jsg_oneof_string_or_bool_accepts_both() {
+    let harness = crate::Harness::new();
+    harness.run_in_context(|lock, ctx| {
+        let resource = jsg::Ref::new(EnumTestResource {
+            _state: ResourceState::default(),
+        });
+        let mut template = EnumTestResourceTemplate::new(lock);
+        let wrapped = unsafe { jsg::wrap_resource(lock, resource, &mut template) };
+        ctx.set_global("resource", wrapped);
+
+        let result: String = ctx.eval(lock, "resource.stringOrBool('test')").unwrap();
+        assert_eq!(result, "string:test");
+
+        let result: String = ctx.eval(lock, "resource.stringOrBool(true)").unwrap();
+        assert_eq!(result, "bool:true");
+        Ok(())
+    });
+}
+
+#[test]
+fn jsg_oneof_three_types_accepts_all() {
+    let harness = crate::Harness::new();
+    harness.run_in_context(|lock, ctx| {
+        let resource = jsg::Ref::new(EnumTestResource {
+            _state: ResourceState::default(),
+        });
+        let mut template = EnumTestResourceTemplate::new(lock);
+        let wrapped = unsafe { jsg::wrap_resource(lock, resource, &mut template) };
+        ctx.set_global("resource", wrapped);
+
+        let result: String = ctx.eval(lock, "resource.threeTypes('hello')").unwrap();
+        assert_eq!(result, "string:hello");
+
+        let result: String = ctx.eval(lock, "resource.threeTypes(123.5)").unwrap();
+        assert_eq!(result, "number:123.5");
+
+        let result: String = ctx.eval(lock, "resource.threeTypes(false)").unwrap();
+        assert_eq!(result, "bool:false");
+        Ok(())
+    });
+}
+
+#[test]
+fn jsg_oneof_three_types_rejects_null_and_undefined() {
+    let harness = crate::Harness::new();
+    harness.run_in_context(|lock, ctx| {
+        let resource = jsg::Ref::new(EnumTestResource {
+            _state: ResourceState::default(),
+        });
+        let mut template = EnumTestResourceTemplate::new(lock);
+        let wrapped = unsafe { jsg::wrap_resource(lock, resource, &mut template) };
+        ctx.set_global("resource", wrapped);
+
+        let err = ctx
+            .eval::<String>(lock, "resource.threeTypes(null)")
+            .unwrap_err()
+            .unwrap_jsg_err(lock);
+        assert_eq!(err.name, ExceptionType::TypeError);
+
+        let err = ctx
+            .eval::<String>(lock, "resource.threeTypes(undefined)")
+            .unwrap_err()
+            .unwrap_jsg_err(lock);
+        assert_eq!(err.name, ExceptionType::TypeError);
+        Ok(())
+    });
+}
+
+#[test]
+fn jsg_oneof_variant_order_matches_declaration() {
+    let harness = crate::Harness::new();
+    harness.run_in_context(|lock, ctx| {
+        let resource = jsg::Ref::new(EnumTestResource {
+            _state: ResourceState::default(),
+        });
+        let mut template = EnumTestResourceTemplate::new(lock);
+        let wrapped = unsafe { jsg::wrap_resource(lock, resource, &mut template) };
+        ctx.set_global("resource", wrapped);
+
+        // StringOrNumber has String first, Number second
+        let result: String = ctx.eval(lock, "resource.stringOrNumber('42')").unwrap();
+        assert_eq!(result, "string:42");
+
+        let result: String = ctx.eval(lock, "resource.stringOrNumber(42)").unwrap();
+        assert_eq!(result, "number:42");
+
+        // NumberOrString has Number first, String second
+        let result: String = ctx.eval(lock, "resource.numberOrString(42)").unwrap();
+        assert_eq!(result, "number:42");
+
+        let result: String = ctx.eval(lock, "resource.numberOrString('42')").unwrap();
+        assert_eq!(result, "string:42");
+        Ok(())
+    });
+}
+
+#[test]
+fn jsg_oneof_reference_parameter() {
+    let harness = crate::Harness::new();
+    harness.run_in_context(|lock, ctx| {
+        let resource = jsg::Ref::new(EnumTestResource {
+            _state: ResourceState::default(),
+        });
+        let mut template = EnumTestResourceTemplate::new(lock);
+        let wrapped = unsafe { jsg::wrap_resource(lock, resource, &mut template) };
+        ctx.set_global("resource", wrapped);
+
+        let result: String = ctx
+            .eval(lock, "resource.stringOrNumberRef('hello')")
+            .unwrap();
+        assert_eq!(result, "ref_string:hello");
+
+        let result: String = ctx.eval(lock, "resource.stringOrNumberRef(42)").unwrap();
+        assert_eq!(result, "ref_number:42");
+        Ok(())
+    });
+}
diff --git a/src/rust/jsg-test/tests/mod.rs b/src/rust/jsg-test/tests/mod.rs
index 75e712e92ef..e4154031292 100644
--- a/src/rust/jsg-test/tests/mod.rs
+++ b/src/rust/jsg-test/tests/mod.rs
@@ -1,4 +1,5 @@
 mod eval;
+mod jsg_oneof;
 mod jsg_struct;
 mod non_coercible;
 mod resource_callback;
diff --git a/src/rust/jsg/README.md b/src/rust/jsg/README.md
index 98f787b4b52..0b67a13e8b5 100644
--- a/src/rust/jsg/README.md
+++ b/src/rust/jsg/README.md
@@ -13,3 +13,28 @@ pub unsafe fn realm_create(isolate: *mut v8::ffi::Isolate) -> Box<Realm> {
 ```

 For more information on unsafe Rust and raw pointers, see the [Rust Book: Unsafe Superpowers](https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html#unsafe-superpowers).
+
+## Union Types
+
+To accept JavaScript values that can be one of several types, define an enum with the `#[jsg_oneof]` macro:
+
+```rust
+use jsg_macros::jsg_oneof;
+
+#[jsg_oneof]
+#[derive(Debug, Clone)]
+enum StringOrNumber {
+    String(String),
+    Number(f64),
+}
+
+// In a jsg_method:
+pub fn process(&self, value: StringOrNumber) -> Result<String, jsg::Error> {
+    match value {
+        StringOrNumber::String(s) => Ok(format!("string: {}", s)),
+        StringOrNumber::Number(n) => Ok(format!("number: {}", n)),
+    }
+}
+```
+
+This is similar to `kj::OneOf<>` in C++ JSG.
diff --git a/src/rust/jsg/wrappable.rs b/src/rust/jsg/wrappable.rs
index c2e271e18b6..de2c2217eea 100644
--- a/src/rust/jsg/wrappable.rs
+++ b/src/rust/jsg/wrappable.rs
@@ -54,6 +54,23 @@ pub trait FromJS: Sized {

     /// Converts a JavaScript value into this Rust type.
     fn from_js(lock: &mut Lock, value: v8::Local<v8::Value>) -> Result<Self::ResultType, Error>;
+
+    /// Tries to convert only if the JavaScript type matches exactly.
+    /// Returns `None` if the type doesn't match, `Some(result)` if conversion was attempted.
+    /// Used by `#[jsg_oneof]` macro to try each variant without coercion.
+    fn try_from_js_exact(
+        lock: &mut Lock,
+        value: &v8::Local<v8::Value>,
+    ) -> Option<Result<Self::ResultType, Error>>
+    where
+        Self: Type,
+    {
+        if Self::is_exact(value) {
+            Some(Self::from_js(lock, value.clone()))
+        } else {
+            None
+        }
+    }
 }

 // =============================================================================
@@ -117,6 +134,14 @@ impl FromJS for &str {
     }
 }

+impl<T: FromJS<ResultType = T>> FromJS for &T {
+    type ResultType = T;
+
+    fn from_js(lock: &mut Lock, value: v8::Local<v8::Value>) -> Result<Self::ResultType, Error> {
+        T::from_js(lock, value)
+    }
+}
+
 // =============================================================================
 // Wrapper type implementations
 // =============================================================================

PATCH

echo "Patch applied successfully."
