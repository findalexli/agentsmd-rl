# Add `#[jsg_constructor]` support to Rust JSG macros

## Problem

The Rust JSG (JavaScript Glue) macro system supports `#[jsg_method]`, `#[jsg_static_constant]`, and `#[jsg_resource]` for exposing Rust types to JavaScript. However, there is no way to define a JavaScript constructor — calling `new MyResource(args)` from JavaScript always throws an "Illegal constructor" error, even when you want to allow JavaScript code to create instances directly.

In the C++ JSG layer, constructors are supported via `JSG_RESOURCE_TYPE` macros. The Rust side needs equivalent functionality.

## Expected Behavior

A new `#[jsg_constructor]` attribute macro should allow marking a static method as the JavaScript constructor for a `#[jsg_resource]`. When JavaScript calls `new MyResource(args)`, V8 should invoke the marked method, create a `jsg::Rc<Self>`, and attach it to the `this` object.

The constructor method must be static (no `self` receiver) and must return `Self`. Only one constructor should be allowed per impl block. The first parameter may optionally be `&mut Lock` for isolate access (not exposed as a JS argument). Without `#[jsg_constructor]`, `new MyResource()` should continue to throw an "Illegal constructor" error.

## Files to Look At

- `src/rust/jsg-macros/lib.rs` — Proc macro definitions. This is where existing macros like `jsg_method` and `jsg_resource` are defined. The new `jsg_constructor` attribute and its code generation logic go here.
- `src/rust/jsg/resource.rs` — `Rc<R>` implementation. Needs a method to attach a resource to the constructor's `this` object.
- `src/rust/jsg/v8.rs` — V8 FFI bindings and `WrappableRc`. Needs FFI declaration and implementation for attaching wrappable in constructor context.
- `src/rust/jsg/ffi.c++` and `src/rust/jsg/ffi.h` — C++ FFI layer. Needs a new function to attach a `Wrappable` to the constructor callback's `this` object (similar to how `wrap_resource` works but using `FunctionCallbackInfo`).
- `src/rust/jsg-test/tests/resource_callback.rs` — Existing test file for resource callbacks. Add constructor tests here.

After implementing the feature, update the relevant documentation files (`src/rust/jsg-macros/README.md` and `src/rust/jsg/README.md`) to document the new `#[jsg_constructor]` attribute, its usage, rules, and behavior. Follow the existing documentation style for other macros like `#[jsg_method]` and `#[jsg_static_constant]`.
