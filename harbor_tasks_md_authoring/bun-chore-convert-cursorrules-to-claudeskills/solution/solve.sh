#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotency guard
if grep -qF "{ \"property\"_s, static_cast<unsigned>(PropertyAttribute::ReadOnly | PropertyAttr" ".claude/skills/implementing-jsc-classes-cpp/SKILL.md" && grep -qF "description: Creates JavaScript classes using Bun's Zig bindings generator (.cla" ".claude/skills/implementing-jsc-classes-zig/SKILL.md" && grep -qF "description: Guides writing bundler tests using itBundled/expectBundled in test/" ".claude/skills/writing-bundler-tests/SKILL.md" && grep -qF "description: Guides writing HMR/Dev Server tests in test/bake/. Use when creatin" ".claude/skills/writing-dev-server-tests/SKILL.md" && grep -qF "description: Guides using bun.sys for system calls and file I/O in Zig. Use when" ".claude/skills/zig-system-calls/SKILL.md" && grep -qF ".cursor/rules/building-bun.mdc" ".cursor/rules/building-bun.mdc" && grep -qF ".cursor/rules/dev-server-tests.mdc" ".cursor/rules/dev-server-tests.mdc" && grep -qF ".cursor/rules/javascriptcore-class.mdc" ".cursor/rules/javascriptcore-class.mdc" && grep -qF ".cursor/rules/registering-bun-modules.mdc" ".cursor/rules/registering-bun-modules.mdc" && grep -qF ".cursor/rules/writing-tests.mdc" ".cursor/rules/writing-tests.mdc" && grep -qF ".cursor/rules/zig-javascriptcore-classes.mdc" ".cursor/rules/zig-javascriptcore-classes.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/implementing-jsc-classes-cpp/SKILL.md b/.claude/skills/implementing-jsc-classes-cpp/SKILL.md
@@ -0,0 +1,184 @@
+---
+name: implementing-jsc-classes-cpp
+description: Implements JavaScript classes in C++ using JavaScriptCore. Use when creating new JS classes with C++ bindings, prototypes, or constructors.
+---
+
+# Implementing JavaScript Classes in C++
+
+## Class Structure
+
+For publicly accessible Constructor and Prototype, create 3 classes:
+
+1. **`class Foo : public JSC::DestructibleObject`** - if C++ fields exist; otherwise use `JSC::constructEmptyObject` with `putDirectOffset`
+2. **`class FooPrototype : public JSC::JSNonFinalObject`**
+3. **`class FooConstructor : public JSC::InternalFunction`**
+
+No public constructor? Only Prototype and class needed.
+
+## Iso Subspaces
+
+Classes with C++ fields need subspaces in:
+
+- `src/bun.js/bindings/webcore/DOMClientIsoSubspaces.h`
+- `src/bun.js/bindings/webcore/DOMIsoSubspaces.h`
+
+```cpp
+template<typename MyClassT, JSC::SubspaceAccess mode>
+static JSC::GCClient::IsoSubspace* subspaceFor(JSC::VM& vm) {
+    if constexpr (mode == JSC::SubspaceAccess::Concurrently)
+        return nullptr;
+    return WebCore::subspaceForImpl<MyClassT, WebCore::UseCustomHeapCellType::No>(
+        vm,
+        [](auto& spaces) { return spaces.m_clientSubspaceForMyClassT.get(); },
+        [](auto& spaces, auto&& space) { spaces.m_clientSubspaceForMyClassT = std::forward<decltype(space)>(space); },
+        [](auto& spaces) { return spaces.m_subspaceForMyClassT.get(); },
+        [](auto& spaces, auto&& space) { spaces.m_subspaceForMyClassT = std::forward<decltype(space)>(space); });
+}
+```
+
+## Property Definitions
+
+```cpp
+static JSC_DECLARE_HOST_FUNCTION(jsFooProtoFuncMethod);
+static JSC_DECLARE_CUSTOM_GETTER(jsFooGetter_property);
+
+static const HashTableValue JSFooPrototypeTableValues[] = {
+    { "property"_s, static_cast<unsigned>(PropertyAttribute::ReadOnly | PropertyAttribute::CustomAccessor), NoIntrinsic, { HashTableValue::GetterSetterType, jsFooGetter_property, 0 } },
+    { "method"_s, static_cast<unsigned>(PropertyAttribute::Function), NoIntrinsic, { HashTableValue::NativeFunctionType, jsFooProtoFuncMethod, 1 } },
+};
+```
+
+## Prototype Class
+
+```cpp
+class JSFooPrototype final : public JSC::JSNonFinalObject {
+public:
+    using Base = JSC::JSNonFinalObject;
+    static constexpr unsigned StructureFlags = Base::StructureFlags;
+
+    static JSFooPrototype* create(JSC::VM& vm, JSC::JSGlobalObject* globalObject, JSC::Structure* structure) {
+        JSFooPrototype* prototype = new (NotNull, allocateCell<JSFooPrototype>(vm)) JSFooPrototype(vm, structure);
+        prototype->finishCreation(vm);
+        return prototype;
+    }
+
+    template<typename, JSC::SubspaceAccess>
+    static JSC::GCClient::IsoSubspace* subspaceFor(JSC::VM& vm) { return &vm.plainObjectSpace(); }
+
+    DECLARE_INFO;
+
+    static JSC::Structure* createStructure(JSC::VM& vm, JSC::JSGlobalObject* globalObject, JSC::JSValue prototype) {
+        auto* structure = JSC::Structure::create(vm, globalObject, prototype, JSC::TypeInfo(JSC::ObjectType, StructureFlags), info());
+        structure->setMayBePrototype(true);
+        return structure;
+    }
+
+private:
+    JSFooPrototype(JSC::VM& vm, JSC::Structure* structure) : Base(vm, structure) {}
+    void finishCreation(JSC::VM& vm);
+};
+
+void JSFooPrototype::finishCreation(VM& vm) {
+    Base::finishCreation(vm);
+    reifyStaticProperties(vm, JSFoo::info(), JSFooPrototypeTableValues, *this);
+    JSC_TO_STRING_TAG_WITHOUT_TRANSITION();
+}
+```
+
+## Getter/Setter/Function Definitions
+
+```cpp
+// Getter
+JSC_DEFINE_CUSTOM_GETTER(jsFooGetter_prop, (JSGlobalObject* globalObject, EncodedJSValue thisValue, PropertyName)) {
+    VM& vm = globalObject->vm();
+    auto scope = DECLARE_THROW_SCOPE(vm);
+    JSFoo* thisObject = jsDynamicCast<JSFoo*>(JSValue::decode(thisValue));
+    if (UNLIKELY(!thisObject)) {
+        Bun::throwThisTypeError(*globalObject, scope, "JSFoo"_s, "prop"_s);
+        return {};
+    }
+    return JSValue::encode(jsBoolean(thisObject->value()));
+}
+
+// Function
+JSC_DEFINE_HOST_FUNCTION(jsFooProtoFuncMethod, (JSGlobalObject* globalObject, CallFrame* callFrame)) {
+    VM& vm = globalObject->vm();
+    auto scope = DECLARE_THROW_SCOPE(vm);
+    auto* thisObject = jsDynamicCast<JSFoo*>(callFrame->thisValue());
+    if (UNLIKELY(!thisObject)) {
+        Bun::throwThisTypeError(*globalObject, scope, "Foo"_s, "method"_s);
+        return {};
+    }
+    return JSValue::encode(thisObject->doSomething(vm, globalObject));
+}
+```
+
+## Constructor Class
+
+```cpp
+class JSFooConstructor final : public JSC::InternalFunction {
+public:
+    using Base = JSC::InternalFunction;
+    static constexpr unsigned StructureFlags = Base::StructureFlags;
+
+    static JSFooConstructor* create(JSC::VM& vm, JSC::Structure* structure, JSC::JSObject* prototype) {
+        JSFooConstructor* constructor = new (NotNull, JSC::allocateCell<JSFooConstructor>(vm)) JSFooConstructor(vm, structure);
+        constructor->finishCreation(vm, prototype);
+        return constructor;
+    }
+
+    DECLARE_INFO;
+
+    template<typename CellType, JSC::SubspaceAccess>
+    static JSC::GCClient::IsoSubspace* subspaceFor(JSC::VM& vm) { return &vm.internalFunctionSpace(); }
+
+    static JSC::Structure* createStructure(JSC::VM& vm, JSC::JSGlobalObject* globalObject, JSC::JSValue prototype) {
+        return JSC::Structure::create(vm, globalObject, prototype, JSC::TypeInfo(JSC::InternalFunctionType, StructureFlags), info());
+    }
+
+private:
+    JSFooConstructor(JSC::VM& vm, JSC::Structure* structure) : Base(vm, structure, callFoo, constructFoo) {}
+
+    void finishCreation(JSC::VM& vm, JSC::JSObject* prototype) {
+        Base::finishCreation(vm, 0, "Foo"_s);
+        putDirectWithoutTransition(vm, vm.propertyNames->prototype, prototype, JSC::PropertyAttribute::DontEnum | JSC::PropertyAttribute::DontDelete | JSC::PropertyAttribute::ReadOnly);
+    }
+};
+```
+
+## Structure Caching
+
+Add to `ZigGlobalObject.h`:
+
+```cpp
+JSC::LazyClassStructure m_JSFooClassStructure;
+```
+
+Initialize in `ZigGlobalObject.cpp`:
+
+```cpp
+m_JSFooClassStructure.initLater([](LazyClassStructure::Initializer& init) {
+    Bun::initJSFooClassStructure(init);
+});
+```
+
+Visit in `visitChildrenImpl`:
+
+```cpp
+m_JSFooClassStructure.visit(visitor);
+```
+
+## Expose to Zig
+
+```cpp
+extern "C" JSC::EncodedJSValue Bun__JSFooConstructor(Zig::GlobalObject* globalObject) {
+    return JSValue::encode(globalObject->m_JSFooClassStructure.constructor(globalObject));
+}
+
+extern "C" EncodedJSValue Bun__Foo__toJS(Zig::GlobalObject* globalObject, Foo* foo) {
+    auto* structure = globalObject->m_JSFooClassStructure.get(globalObject);
+    return JSValue::encode(JSFoo::create(globalObject->vm(), structure, globalObject, WTFMove(foo)));
+}
+```
+
+Include `#include "root.h"` at the top of C++ files.
diff --git a/.claude/skills/implementing-jsc-classes-zig/SKILL.md b/.claude/skills/implementing-jsc-classes-zig/SKILL.md
@@ -0,0 +1,206 @@
+---
+name: implementing-jsc-classes-zig
+description: Creates JavaScript classes using Bun's Zig bindings generator (.classes.ts). Use when implementing new JS APIs in Zig with JSC integration.
+---
+
+# Bun's JavaScriptCore Class Bindings Generator
+
+Bridge JavaScript and Zig through `.classes.ts` definitions and Zig implementations.
+
+## Architecture
+
+1. **Zig Implementation** (.zig files)
+2. **JavaScript Interface Definition** (.classes.ts files)
+3. **Generated Code** (C++/Zig files connecting them)
+
+## Class Definition (.classes.ts)
+
+```typescript
+define({
+  name: "TextDecoder",
+  constructor: true,
+  JSType: "object",
+  finalize: true,
+  proto: {
+    decode: { args: 1 },
+    encoding: { getter: true, cache: true },
+    fatal: { getter: true },
+  },
+});
+```
+
+Options:
+
+- `name`: Class name
+- `constructor`: Has public constructor
+- `JSType`: "object", "function", etc.
+- `finalize`: Needs cleanup
+- `proto`: Properties/methods
+- `cache`: Cache property values via WriteBarrier
+
+## Zig Implementation
+
+```zig
+pub const TextDecoder = struct {
+    pub const js = JSC.Codegen.JSTextDecoder;
+    pub const toJS = js.toJS;
+    pub const fromJS = js.fromJS;
+    pub const fromJSDirect = js.fromJSDirect;
+
+    encoding: []const u8,
+    fatal: bool,
+
+    pub fn constructor(
+        globalObject: *JSGlobalObject,
+        callFrame: *JSC.CallFrame,
+    ) bun.JSError!*TextDecoder {
+        return bun.new(TextDecoder, .{ .encoding = "utf-8", .fatal = false });
+    }
+
+    pub fn decode(
+        this: *TextDecoder,
+        globalObject: *JSGlobalObject,
+        callFrame: *JSC.CallFrame,
+    ) bun.JSError!JSC.JSValue {
+        const args = callFrame.arguments();
+        if (args.len < 1 or args.ptr[0].isUndefinedOrNull()) {
+            return globalObject.throw("Input cannot be null", .{});
+        }
+        return JSC.JSValue.jsString(globalObject, "result");
+    }
+
+    pub fn getEncoding(this: *TextDecoder, globalObject: *JSGlobalObject) JSC.JSValue {
+        return JSC.JSValue.createStringFromUTF8(globalObject, this.encoding);
+    }
+
+    fn deinit(this: *TextDecoder) void {
+        // Release resources
+    }
+
+    pub fn finalize(this: *TextDecoder) void {
+        this.deinit();
+        bun.destroy(this);
+    }
+};
+```
+
+**Key patterns:**
+
+- Use `bun.JSError!JSValue` return type for error handling
+- Use `globalObject` not `ctx`
+- `deinit()` for cleanup, `finalize()` called by GC
+- Update `src/bun.js/bindings/generated_classes_list.zig`
+
+## CallFrame Access
+
+```zig
+const args = callFrame.arguments();
+const first_arg = args.ptr[0];  // Access as slice
+const argCount = args.len;
+const thisValue = callFrame.thisValue();
+```
+
+## Property Caching
+
+For `cache: true` properties, generated accessors:
+
+```zig
+// Get cached value
+pub fn encodingGetCached(thisValue: JSC.JSValue) ?JSC.JSValue {
+    const result = TextDecoderPrototype__encodingGetCachedValue(thisValue);
+    if (result == .zero) return null;
+    return result;
+}
+
+// Set cached value
+pub fn encodingSetCached(thisValue: JSC.JSValue, globalObject: *JSC.JSGlobalObject, value: JSC.JSValue) void {
+    TextDecoderPrototype__encodingSetCachedValue(thisValue, globalObject, value);
+}
+```
+
+## Error Handling
+
+```zig
+pub fn method(this: *MyClass, globalObject: *JSGlobalObject, callFrame: *JSC.CallFrame) bun.JSError!JSC.JSValue {
+    const args = callFrame.arguments();
+    if (args.len < 1) {
+        return globalObject.throw("Missing required argument", .{});
+    }
+    return JSC.JSValue.jsString(globalObject, "Success!");
+}
+```
+
+## Memory Management
+
+```zig
+pub fn deinit(this: *TextDecoder) void {
+    this._encoding.deref();
+    if (this.buffer) |buffer| {
+        bun.default_allocator.free(buffer);
+    }
+}
+
+pub fn finalize(this: *TextDecoder) void {
+    JSC.markBinding(@src());
+    this.deinit();
+    bun.default_allocator.destroy(this);
+}
+```
+
+## Creating a New Binding
+
+1. Define interface in `.classes.ts`:
+
+```typescript
+define({
+  name: "MyClass",
+  constructor: true,
+  finalize: true,
+  proto: {
+    myMethod: { args: 1 },
+    myProperty: { getter: true, cache: true },
+  },
+});
+```
+
+2. Implement in `.zig`:
+
+```zig
+pub const MyClass = struct {
+    pub const js = JSC.Codegen.JSMyClass;
+    pub const toJS = js.toJS;
+    pub const fromJS = js.fromJS;
+
+    value: []const u8,
+
+    pub const new = bun.TrivialNew(@This());
+
+    pub fn constructor(globalObject: *JSGlobalObject, callFrame: *JSC.CallFrame) bun.JSError!*MyClass {
+        return MyClass.new(.{ .value = "" });
+    }
+
+    pub fn myMethod(this: *MyClass, globalObject: *JSGlobalObject, callFrame: *JSC.CallFrame) bun.JSError!JSC.JSValue {
+        return JSC.JSValue.jsUndefined();
+    }
+
+    pub fn getMyProperty(this: *MyClass, globalObject: *JSGlobalObject) JSC.JSValue {
+        return JSC.JSValue.jsString(globalObject, this.value);
+    }
+
+    pub fn deinit(this: *MyClass) void {}
+
+    pub fn finalize(this: *MyClass) void {
+        this.deinit();
+        bun.destroy(this);
+    }
+};
+```
+
+3. Add to `src/bun.js/bindings/generated_classes_list.zig`
+
+## Generated Components
+
+- **C++ Classes**: `JSMyClass`, `JSMyClassPrototype`, `JSMyClassConstructor`
+- **Method Bindings**: `MyClassPrototype__myMethodCallback`
+- **Property Accessors**: `MyClassPrototype__myPropertyGetterWrap`
+- **Zig Bindings**: External function declarations, cached value accessors
diff --git a/.claude/skills/writing-bundler-tests/SKILL.md b/.claude/skills/writing-bundler-tests/SKILL.md
@@ -0,0 +1,222 @@
+---
+name: writing-bundler-tests
+description: Guides writing bundler tests using itBundled/expectBundled in test/bundler/. Use when creating or modifying bundler, transpiler, or code transformation tests.
+---
+
+# Writing Bundler Tests
+
+Bundler tests use `itBundled()` from `test/bundler/expectBundled.ts` to test Bun's bundler.
+
+## Basic Usage
+
+```typescript
+import { describe } from "bun:test";
+import { itBundled, dedent } from "./expectBundled";
+
+describe("bundler", () => {
+  itBundled("category/TestName", {
+    files: {
+      "index.js": `console.log("hello");`,
+    },
+    run: {
+      stdout: "hello",
+    },
+  });
+});
+```
+
+Test ID format: `category/TestName` (e.g., `banner/CommentBanner`, `minify/Empty`)
+
+## File Setup
+
+```typescript
+{
+  files: {
+    "index.js": `console.log("test");`,
+    "lib.ts": `export const foo = 123;`,
+    "nested/file.js": `export default {};`,
+  },
+  entryPoints: ["index.js"],  // defaults to first file
+  runtimeFiles: {             // written AFTER bundling
+    "extra.js": `console.log("added later");`,
+  },
+}
+```
+
+## Bundler Options
+
+```typescript
+{
+  outfile: "/out.js",
+  outdir: "/out",
+  format: "esm" | "cjs" | "iife",
+  target: "bun" | "browser" | "node",
+
+  // Minification
+  minifyWhitespace: true,
+  minifyIdentifiers: true,
+  minifySyntax: true,
+
+  // Code manipulation
+  banner: "// copyright",
+  footer: "// end",
+  define: { "PROD": "true" },
+  external: ["lodash"],
+
+  // Advanced
+  sourceMap: "inline" | "external",
+  splitting: true,
+  treeShaking: true,
+  drop: ["console"],
+}
+```
+
+## Runtime Verification
+
+```typescript
+{
+  run: {
+    stdout: "expected output",      // exact match
+    stdout: /regex/,                // pattern match
+    partialStdout: "contains this", // substring
+    stderr: "error output",
+    exitCode: 1,
+    env: { NODE_ENV: "production" },
+    runtime: "bun" | "node",
+
+    // Runtime errors
+    error: "ReferenceError: x is not defined",
+  },
+}
+```
+
+## Bundle Errors/Warnings
+
+```typescript
+{
+  bundleErrors: {
+    "/file.js": ["error message 1", "error message 2"],
+  },
+  bundleWarnings: {
+    "/file.js": ["warning message"],
+  },
+}
+```
+
+## Dead Code Elimination (DCE)
+
+Add markers in source code:
+
+```javascript
+// KEEP - this should survive
+const used = 1;
+
+// REMOVE - this should be eliminated
+const unused = 2;
+```
+
+```typescript
+{
+  dce: true,
+  dceKeepMarkerCount: 5,  // expected KEEP markers
+}
+```
+
+## Capture Pattern
+
+Verify exact transpilation with `capture()`:
+
+```typescript
+itBundled("string/Folding", {
+  files: {
+    "index.ts": `capture(\`\${1 + 1}\`);`,
+  },
+  capture: ['"2"'], // expected captured value
+  minifySyntax: true,
+});
+```
+
+## Post-Bundle Assertions
+
+```typescript
+{
+  onAfterBundle(api) {
+    api.expectFile("out.js").toContain("console.log");
+    api.assertFileExists("out.js");
+
+    const content = api.readFile("out.js");
+    expect(content).toMatchSnapshot();
+
+    const values = api.captureFile("out.js");
+    expect(values).toEqual(["2"]);
+  },
+}
+```
+
+## Common Patterns
+
+**Simple output verification:**
+
+```typescript
+itBundled("banner/Comment", {
+  banner: "// copyright",
+  files: { "a.js": `console.log("Hello")` },
+  onAfterBundle(api) {
+    api.expectFile("out.js").toContain("// copyright");
+  },
+});
+```
+
+**Multi-file CJS/ESM interop:**
+
+```typescript
+itBundled("cjs/ImportSyntax", {
+  files: {
+    "entry.js": `import lib from './lib.cjs'; console.log(lib);`,
+    "lib.cjs": `exports.foo = 'bar';`,
+  },
+  run: { stdout: '{"foo":"bar"}' },
+});
+```
+
+**Error handling:**
+
+```typescript
+itBundled("edgecase/InvalidLoader", {
+  files: { "index.js": `...` },
+  bundleErrors: {
+    "index.js": ["Unsupported loader type"],
+  },
+});
+```
+
+## Test Organization
+
+```text
+test/bundler/
+├── bundler_banner.test.ts
+├── bundler_string.test.ts
+├── bundler_minify.test.ts
+├── bundler_cjs.test.ts
+├── bundler_edgecase.test.ts
+├── bundler_splitting.test.ts
+├── css/
+├── transpiler/
+└── expectBundled.ts
+```
+
+## Running Tests
+
+```bash
+bun bd test test/bundler/bundler_banner.test.ts
+BUN_BUNDLER_TEST_FILTER="banner/Comment" bun bd test bundler_banner.test.ts
+BUN_BUNDLER_TEST_DEBUG=1 bun bd test bundler_minify.test.ts
+```
+
+## Key Points
+
+- Use `dedent` for readable multi-line code
+- File paths are relative (e.g., `/index.js`)
+- Use `capture()` to verify exact transpilation results
+- Use `.toMatchSnapshot()` for complex outputs
+- Pass array to `run` for multiple test scenarios
diff --git a/.claude/skills/writing-dev-server-tests/SKILL.md b/.claude/skills/writing-dev-server-tests/SKILL.md
@@ -0,0 +1,94 @@
+---
+name: writing-dev-server-tests
+description: Guides writing HMR/Dev Server tests in test/bake/. Use when creating or modifying dev server, hot reloading, or bundling tests.
+---
+
+# Writing HMR/Dev Server Tests
+
+Dev server tests validate hot-reloading robustness and reliability.
+
+## File Structure
+
+- `test/bake/bake-harness.ts` - shared utilities: `devTest`, `prodTest`, `devAndProductionTest`, `Dev` class, `Client` class
+- `test/bake/client-fixture.mjs` - subprocess for `Client` (page loading, IPC queries)
+- `test/bake/dev/*.test.ts` - dev server and hot reload tests
+- `test/bake/dev-and-prod.ts` - tests running on both dev and production mode
+
+## Test Categories
+
+- `bundle.test.ts` - DevServer-specific bundling bugs
+- `css.test.ts` - CSS bundling issues
+- `plugins.test.ts` - development mode plugins
+- `ecosystem.test.ts` - library compatibility (prefer concrete bugs over full package tests)
+- `esm.test.ts` - ESM features in development
+- `html.test.ts` - HTML file handling
+- `react-spa.test.ts` - React, react-refresh transform, server components
+- `sourcemap.test.ts` - source map correctness
+
+## devTest Basics
+
+```ts
+import { devTest, emptyHtmlFile } from "../bake-harness";
+
+devTest("html file is watched", {
+  files: {
+    "index.html": emptyHtmlFile({
+      scripts: ["/script.ts"],
+      body: "<h1>Hello</h1>",
+    }),
+    "script.ts": `console.log("hello");`,
+  },
+  async test(dev) {
+    await dev.fetch("/").expect.toInclude("<h1>Hello</h1>");
+    await dev.patch("index.html", { find: "Hello", replace: "World" });
+    await dev.fetch("/").expect.toInclude("<h1>World</h1>");
+
+    await using c = await dev.client("/");
+    await c.expectMessage("hello");
+
+    await c.expectReload(async () => {
+      await dev.patch("index.html", { find: "World", replace: "Bar" });
+    });
+    await c.expectMessage("hello");
+  },
+});
+```
+
+## Key APIs
+
+- **`files`**: Initial filesystem state
+- **`dev.fetch()`**: HTTP requests
+- **`dev.client()`**: Opens browser instance
+- **`dev.write/patch/delete`**: Filesystem mutations (wait for hot-reload automatically)
+- **`c.expectMessage()`**: Assert console.log output
+- **`c.expectReload()`**: Wrap code that causes hard reload
+
+**Important**: Use `dev.write/patch/delete` instead of `node:fs` - they wait for hot-reload.
+
+## Testing Errors
+
+```ts
+devTest("import then create", {
+  files: {
+    "index.html": `<!DOCTYPE html><html><head></head><body><script type="module" src="/script.ts"></script></body></html>`,
+    "script.ts": `import data from "./data"; console.log(data);`,
+  },
+  async test(dev) {
+    const c = await dev.client("/", {
+      errors: ['script.ts:1:18: error: Could not resolve: "./data"'],
+    });
+    await c.expectReload(async () => {
+      await dev.write("data.ts", "export default 'data';");
+    });
+    await c.expectMessage("data");
+  },
+});
+```
+
+Specify expected errors with the `errors` option:
+
+```ts
+await dev.delete("other.ts", {
+  errors: ['index.ts:1:16: error: Could not resolve: "./other"'],
+});
+```
diff --git a/.claude/skills/zig-system-calls/SKILL.md b/.claude/skills/zig-system-calls/SKILL.md
@@ -0,0 +1,268 @@
+---
+name: zig-system-calls
+description: Guides using bun.sys for system calls and file I/O in Zig. Use when implementing file operations instead of std.fs or std.posix.
+---
+
+# System Calls & File I/O in Zig
+
+Use `bun.sys` instead of `std.fs` or `std.posix` for cross-platform syscalls with proper error handling.
+
+## bun.sys.File (Preferred)
+
+For most file operations, use the `bun.sys.File` wrapper:
+
+```zig
+const File = bun.sys.File;
+
+const file = switch (File.open(path, bun.O.RDWR, 0o644)) {
+    .result => |f| f,
+    .err => |err| return .{ .err = err },
+};
+defer file.close();
+
+// Read/write
+_ = try file.read(buffer).unwrap();
+_ = try file.writeAll(data).unwrap();
+
+// Get file info
+const stat = try file.stat().unwrap();
+const size = try file.getEndPos().unwrap();
+
+// std.io compatible
+const reader = file.reader();
+const writer = file.writer();
+```
+
+### Complete Example
+
+```zig
+const File = bun.sys.File;
+
+pub fn writeFile(path: [:0]const u8, data: []const u8) File.WriteError!void {
+    const file = switch (File.open(path, bun.O.WRONLY | bun.O.CREAT | bun.O.TRUNC, 0o664)) {
+        .result => |f| f,
+        .err => |err| return err.toError(),
+    };
+    defer file.close();
+
+    _ = switch (file.writeAll(data)) {
+        .result => {},
+        .err => |err| return err.toError(),
+    };
+}
+```
+
+## Why bun.sys?
+
+| Aspect      | bun.sys                          | std.fs/std.posix    |
+| ----------- | -------------------------------- | ------------------- |
+| Return Type | `Maybe(T)` with detailed Error   | Generic error union |
+| Windows     | Full support with libuv fallback | Limited/POSIX-only  |
+| Error Info  | errno, syscall tag, path, fd     | errno only          |
+| EINTR       | Automatic retry                  | Manual handling     |
+
+## Error Handling with Maybe(T)
+
+`bun.sys` functions return `Maybe(T)` - a tagged union:
+
+```zig
+const sys = bun.sys;
+
+// Pattern 1: Switch on result/error
+switch (sys.read(fd, buffer)) {
+    .result => |bytes_read| {
+        // use bytes_read
+    },
+    .err => |err| {
+        // err.errno, err.syscall, err.fd, err.path
+        if (err.getErrno() == .AGAIN) {
+            // handle EAGAIN
+        }
+    },
+}
+
+// Pattern 2: Unwrap with try (converts to Zig error)
+const bytes = try sys.read(fd, buffer).unwrap();
+
+// Pattern 3: Unwrap with default
+const value = sys.stat(path).unwrapOr(default_stat);
+```
+
+## Low-Level File Operations
+
+Only use these when `bun.sys.File` doesn't meet your needs.
+
+### Opening Files
+
+```zig
+const sys = bun.sys;
+
+// Use bun.O flags (cross-platform normalized)
+const fd = switch (sys.open(path, bun.O.RDONLY, 0)) {
+    .result => |fd| fd,
+    .err => |err| return .{ .err = err },
+};
+defer fd.close();
+
+// Common flags
+bun.O.RDONLY, bun.O.WRONLY, bun.O.RDWR
+bun.O.CREAT, bun.O.TRUNC, bun.O.APPEND
+bun.O.NONBLOCK, bun.O.DIRECTORY
+```
+
+### Reading & Writing
+
+```zig
+// Single read (may return less than buffer size)
+switch (sys.read(fd, buffer)) {
+    .result => |n| { /* n bytes read */ },
+    .err => |err| { /* handle error */ },
+}
+
+// Read until EOF or buffer full
+const total = try sys.readAll(fd, buffer).unwrap();
+
+// Position-based read/write
+sys.pread(fd, buffer, offset)
+sys.pwrite(fd, data, offset)
+
+// Vector I/O
+sys.readv(fd, iovecs)
+sys.writev(fd, iovecs)
+```
+
+### File Info
+
+```zig
+sys.stat(path)      // Follow symlinks
+sys.lstat(path)     // Don't follow symlinks
+sys.fstat(fd)       // From file descriptor
+sys.fstatat(fd, path)
+
+// Linux-only: faster selective stat
+sys.statx(path, &.{ .size, .mtime })
+```
+
+### Path Operations
+
+```zig
+sys.unlink(path)
+sys.unlinkat(dir_fd, path)
+sys.rename(from, to)
+sys.renameat(from_dir, from, to_dir, to)
+sys.readlink(path, buf)
+sys.readlinkat(fd, path, buf)
+sys.link(T, src, dest)
+sys.linkat(src_fd, src, dest_fd, dest)
+sys.symlink(target, dest)
+sys.symlinkat(target, dirfd, dest)
+sys.mkdir(path, mode)
+sys.mkdirat(dir_fd, path, mode)
+sys.rmdir(path)
+```
+
+### Permissions
+
+```zig
+sys.chmod(path, mode)
+sys.fchmod(fd, mode)
+sys.fchmodat(fd, path, mode, flags)
+sys.chown(path, uid, gid)
+sys.fchown(fd, uid, gid)
+```
+
+### Closing File Descriptors
+
+Close is on `bun.FD`:
+
+```zig
+fd.close();  // Asserts on error (use in defer)
+
+// Or if you need error info:
+if (fd.closeAllowingBadFileDescriptor(null)) |err| {
+    // handle error
+}
+```
+
+## Directory Operations
+
+```zig
+var buf: bun.PathBuffer = undefined;
+const cwd = try sys.getcwd(&buf).unwrap();
+const cwdZ = try sys.getcwdZ(&buf).unwrap();  // Zero-terminated
+sys.chdir(path, destination)
+```
+
+### Directory Iteration
+
+Use `bun.DirIterator` instead of `std.fs.Dir.Iterator`:
+
+```zig
+var iter = bun.iterateDir(dir_fd);
+while (true) {
+    switch (iter.next()) {
+        .result => |entry| {
+            if (entry) |e| {
+                const name = e.name.slice();
+                const kind = e.kind;  // .file, .directory, .sym_link, etc.
+            } else {
+                break;  // End of directory
+            }
+        },
+        .err => |err| return .{ .err = err },
+    }
+}
+```
+
+## Socket Operations
+
+**Important**: `bun.sys` has limited socket support. For network I/O:
+
+- **Non-blocking sockets**: Use `uws.Socket` (libuwebsockets) exclusively
+- **Pipes/blocking I/O**: Use `PipeReader.zig` and `PipeWriter.zig`
+
+Available in bun.sys:
+
+```zig
+sys.setsockopt(fd, level, optname, value)
+sys.socketpair(domain, socktype, protocol, nonblocking_status)
+```
+
+Do NOT use `bun.sys` for socket read/write - use `uws.Socket` instead.
+
+## Other Operations
+
+```zig
+sys.ftruncate(fd, size)
+sys.lseek(fd, offset, whence)
+sys.dup(fd)
+sys.dupWithFlags(fd, flags)
+sys.fcntl(fd, cmd, arg)
+sys.pipe()
+sys.mmap(...)
+sys.munmap(memory)
+sys.access(path, mode)
+sys.futimens(fd, atime, mtime)
+sys.utimens(path, atime, mtime)
+```
+
+## Error Type
+
+```zig
+const err: bun.sys.Error = ...;
+err.errno      // Raw errno value
+err.getErrno() // As std.posix.E enum
+err.syscall    // Which syscall failed (Tag enum)
+err.fd         // Optional: file descriptor
+err.path       // Optional: path string
+```
+
+## Key Points
+
+- Prefer `bun.sys.File` wrapper for most file operations
+- Use low-level `bun.sys` functions only when needed
+- Use `bun.O.*` flags instead of `std.os.O.*`
+- Handle `Maybe(T)` with switch or `.unwrap()`
+- Use `defer fd.close()` for cleanup
+- EINTR is handled automatically in most functions
+- For sockets, use `uws.Socket` not `bun.sys`
diff --git a/.cursor/rules/building-bun.mdc b/.cursor/rules/building-bun.mdc
@@ -1,41 +0,0 @@
----
-description:
-globs: src/**/*.cpp,src/**/*.zig
-alwaysApply: false
----
-
-### Build Commands
-
-- **Build debug version**: `bun bd` or `bun run build:debug`
-  - Creates a debug build at `./build/debug/bun-debug`
-  - Compilation takes ~2.5 minutes
-- **Run tests with your debug build**: `bun bd test <test-file>`
-  - **CRITICAL**: Never use `bun test` directly - it won't include your changes
-- **Run any command with debug build**: `bun bd <command>`
-
-### Run a file
-
-To run a file, use:
-
-```sh
-bun bd <file> <...args>
-```
-
-**CRITICAL**: Never use `bun <file>` directly. It will not have your changes.
-
-### Logging
-
-`BUN_DEBUG_$(SCOPE)=1` enables debug logs for a specific debug log scope.
-
-Debug logs look like this:
-
-```zig
-const log = bun.Output.scoped(.${SCOPE}, .hidden);
-
-// ...later
-log("MY DEBUG LOG", .{})
-```
-
-### Code Generation
-
-Code generation happens automatically as part of the build process. There are no commands to run.
diff --git a/.cursor/rules/dev-server-tests.mdc b/.cursor/rules/dev-server-tests.mdc
@@ -1,139 +0,0 @@
----
-description: Writing HMR/Dev Server tests
-globs: test/bake/*
----
-
-# Writing HMR/Dev Server tests
-
-Dev server tests validate that hot-reloading is robust, correct, and reliable. Remember to write thorough, yet concise tests.
-
-## File Structure
-
-- `test/bake/bake-harness.ts` - shared utilities and test harness
-  - primary test functions `devTest` / `prodTest` / `devAndProductionTest`
-  - class `Dev` (controls subprocess for dev server)
-  - class `Client` (controls a happy-dom subprocess for having the page open)
-  - more helpers
-- `test/bake/client-fixture.mjs` - subprocess for what `Client` controls. it loads a page and uses IPC to query parts of the page, run javascript, and much more.
-- `test/bake/dev/*.test.ts` - these call `devTest` to test dev server and hot reloading
-- `test/bake/dev-and-prod.ts` - these use `devAndProductionTest` to run the same test on dev and production mode. these tests cannot really test hot reloading for obvious reasons.
-
-## Categories
-
-bundle.test.ts - Bundle tests are tests concerning bundling bugs that only occur in DevServer.
-css.test.ts - CSS tests concern bundling bugs with CSS files
-plugins.test.ts - Plugin tests concern plugins in development mode.
-ecosystem.test.ts - These tests involve ensuring certain libraries are correct. It is preferred to test more concrete bugs than testing entire packages.
-esm.test.ts - ESM tests are about various esm features in development mode.
-html.test.ts - HTML tests are tests relating to HTML files themselves.
-react-spa.test.ts - Tests relating to React, our react-refresh transform, and basic server component transforms.
-sourcemap.test.ts - Tests verifying source-maps are correct.
-
-## `devTest` Basics
-
-A test takes in two primary inputs: `files` and `async test(dev) {`
-
-```ts
-import { devTest, emptyHtmlFile } from "../bake-harness";
-
-devTest("html file is watched", {
-  files: {
-    "index.html": emptyHtmlFile({
-      scripts: ["/script.ts"],
-      body: "<h1>Hello</h1>",
-    }),
-    "script.ts": `
-      console.log("hello");
-    `,
-  },
-  async test(dev) {
-    await dev.fetch("/").expect.toInclude("<h1>Hello</h1>");
-    await dev.fetch("/").expect.toInclude("<h1>Hello</h1>");
-    await dev.patch("index.html", {
-      find: "Hello",
-      replace: "World",
-    });
-    await dev.fetch("/").expect.toInclude("<h1>World</h1>");
-
-    // Works
-    await using c = await dev.client("/");
-    await c.expectMessage("hello");
-
-    // Editing HTML reloads
-    await c.expectReload(async () => {
-      await dev.patch("index.html", {
-        find: "World",
-        replace: "Hello",
-      });
-      await dev.fetch("/").expect.toInclude("<h1>Hello</h1>");
-    });
-    await c.expectMessage("hello");
-
-    await c.expectReload(async () => {
-      await dev.patch("index.html", {
-        find: "Hello",
-        replace: "Bar",
-      });
-      await dev.fetch("/").expect.toInclude("<h1>Bar</h1>");
-    });
-    await c.expectMessage("hello");
-
-    await c.expectReload(async () => {
-      await dev.patch("script.ts", {
-        find: "hello",
-        replace: "world",
-      });
-    });
-    await c.expectMessage("world");
-  },
-});
-```
-
-`files` holds the initial state, and the callback runs with the server running. `dev.fetch()` runs HTTP requests, while `dev.client()` opens a browser instance to the code.
-
-Functions `dev.write` and `dev.patch` and `dev.delete` mutate the filesystem. Do not use `node:fs` APIs, as the dev server ones are hooked to wait for hot-reload, and all connected clients to receive changes.
-
-When a change performs a hard-reload, that must be explicitly annotated with `expectReload`. This tells `client-fixture.mjs` that the test is meant to reload the page once; All other hard reloads automatically fail the test.
-
-Client's have `console.log` instrumented, so that any unasserted logs fail the test. This makes it more obvious when an extra reload or re-evaluation. Messages are awaited via `c.expectMessage("log")` or with multiple arguments if there are multiple logs.
-
-## Testing for bundling errors
-
-By default, a client opening a page to an error will fail the test. This makes testing errors explicit.
-
-```ts
-devTest("import then create", {
-  files: {
-    "index.html": `
-      <!DOCTYPE html>
-      <html>
-      <head></head>
-      <body>
-        <script type="module" src="/script.ts"></script>
-      </body>
-      </html>
-    `,
-    "script.ts": `
-      import data from "./data";
-      console.log(data);
-    `,
-  },
-  async test(dev) {
-    const c = await dev.client("/", {
-      errors: ['script.ts:1:18: error: Could not resolve: "./data"'],
-    });
-    await c.expectReload(async () => {
-      await dev.write("data.ts", "export default 'data';");
-    });
-    await c.expectMessage("data");
-  },
-});
-```
-
-Many functions take an options value to allow specifying it will produce errors. For example, this delete is going to cause a resolution failure.
-
-```ts
-await dev.delete("other.ts", {
-  errors: ['index.ts:1:16: error: Could not resolve: "./other"'],
-});
-```
diff --git a/.cursor/rules/javascriptcore-class.mdc b/.cursor/rules/javascriptcore-class.mdc
@@ -1,413 +0,0 @@
----
-description: JavaScript class implemented in C++
-globs: *.cpp
-alwaysApply: false
----
-
-# Implementing JavaScript classes in C++
-
-If there is a publicly accessible Constructor and Prototype, then there are 3 classes:
-
-- IF there are C++ class members we need a destructor, so `class Foo : public JSC::DestructibleObject`, if no C++ class fields (only JS properties) then we don't need a class at all usually. We can instead use JSC::constructEmptyObject(vm, structure) and `putDirectOffset` like in [NodeFSStatBinding.cpp](mdc:src/bun.js/bindings/NodeFSStatBinding.cpp).
-- class FooPrototype : public JSC::JSNonFinalObject
-- class FooConstructor : public JSC::InternalFunction
-
-If there is no publicly accessible Constructor, just the Prototype and the class is necessary. In some cases, we can avoid the prototype entirely (but that's rare).
-
-If there are C++ fields on the Foo class, the Foo class will need an iso subspace added to [DOMClientIsoSubspaces.h](mdc:src/bun.js/bindings/webcore/DOMClientIsoSubspaces.h) and [DOMIsoSubspaces.h](mdc:src/bun.js/bindings/webcore/DOMIsoSubspaces.h). Prototype and Constructor do not need subspaces.
-
-Usually you'll need to #include "root.h" at the top of C++ files or you'll get lint errors.
-
-Generally, defining the subspace looks like this:
-
-```c++
-
-class Foo : public JSC::DestructibleObject {
-
-// ...
-
- template<typename MyClassT, JSC::SubspaceAccess mode>
-    static JSC::GCClient::IsoSubspace* subspaceFor(JSC::VM& vm)
-    {
-        if constexpr (mode == JSC::SubspaceAccess::Concurrently)
-            return nullptr;
-        return WebCore::subspaceForImpl<MyClassT, WebCore::UseCustomHeapCellType::No>(
-            vm,
-            [](auto& spaces) { return spaces.m_clientSubspaceFor${MyClassT}.get(); },
-            [](auto& spaces, auto&& space) { spaces.m_clientSubspaceFor${MyClassT} = std::forward<decltype(space)>(space); },
-            [](auto& spaces) { return spaces.m_subspaceFo${MyClassT}.get(); },
-            [](auto& spaces, auto&& space) { spaces.m_subspaceFor${MyClassT} = std::forward<decltype(space)>(space); });
-    }
-
-
-```
-
-It's better to put it in the .cpp file instead of the .h file, when possible.
-
-## Defining properties
-
-Define properties on the prototype. Use a const HashTableValues like this:
-
-```C++
-static JSC_DECLARE_HOST_FUNCTION(jsX509CertificateProtoFuncCheckEmail);
-static JSC_DECLARE_HOST_FUNCTION(jsX509CertificateProtoFuncCheckHost);
-static JSC_DECLARE_HOST_FUNCTION(jsX509CertificateProtoFuncCheckIP);
-static JSC_DECLARE_HOST_FUNCTION(jsX509CertificateProtoFuncCheckIssued);
-static JSC_DECLARE_HOST_FUNCTION(jsX509CertificateProtoFuncCheckPrivateKey);
-static JSC_DECLARE_HOST_FUNCTION(jsX509CertificateProtoFuncToJSON);
-static JSC_DECLARE_HOST_FUNCTION(jsX509CertificateProtoFuncToLegacyObject);
-static JSC_DECLARE_HOST_FUNCTION(jsX509CertificateProtoFuncToString);
-static JSC_DECLARE_HOST_FUNCTION(jsX509CertificateProtoFuncVerify);
-
-static JSC_DECLARE_CUSTOM_GETTER(jsX509CertificateGetter_ca);
-static JSC_DECLARE_CUSTOM_GETTER(jsX509CertificateGetter_fingerprint);
-static JSC_DECLARE_CUSTOM_GETTER(jsX509CertificateGetter_fingerprint256);
-static JSC_DECLARE_CUSTOM_GETTER(jsX509CertificateGetter_fingerprint512);
-static JSC_DECLARE_CUSTOM_GETTER(jsX509CertificateGetter_subject);
-static JSC_DECLARE_CUSTOM_GETTER(jsX509CertificateGetter_subjectAltName);
-static JSC_DECLARE_CUSTOM_GETTER(jsX509CertificateGetter_infoAccess);
-static JSC_DECLARE_CUSTOM_GETTER(jsX509CertificateGetter_keyUsage);
-static JSC_DECLARE_CUSTOM_GETTER(jsX509CertificateGetter_issuer);
-static JSC_DECLARE_CUSTOM_GETTER(jsX509CertificateGetter_issuerCertificate);
-static JSC_DECLARE_CUSTOM_GETTER(jsX509CertificateGetter_publicKey);
-static JSC_DECLARE_CUSTOM_GETTER(jsX509CertificateGetter_raw);
-static JSC_DECLARE_CUSTOM_GETTER(jsX509CertificateGetter_serialNumber);
-static JSC_DECLARE_CUSTOM_GETTER(jsX509CertificateGetter_validFrom);
-static JSC_DECLARE_CUSTOM_GETTER(jsX509CertificateGetter_validTo);
-static JSC_DECLARE_CUSTOM_GETTER(jsX509CertificateGetter_validFromDate);
-static JSC_DECLARE_CUSTOM_GETTER(jsX509CertificateGetter_validToDate);
-
-static const HashTableValue JSX509CertificatePrototypeTableValues[] = {
-    { "ca"_s, static_cast<unsigned>(PropertyAttribute::ReadOnly | PropertyAttribute::CustomAccessor), NoIntrinsic, { HashTableValue::GetterSetterType, jsX509CertificateGetter_ca, 0 } },
-    { "checkEmail"_s, static_cast<unsigned>(PropertyAttribute::Function), NoIntrinsic, { HashTableValue::NativeFunctionType, jsX509CertificateProtoFuncCheckEmail, 2 } },
-    { "checkHost"_s, static_cast<unsigned>(PropertyAttribute::Function), NoIntrinsic, { HashTableValue::NativeFunctionType, jsX509CertificateProtoFuncCheckHost, 2 } },
-    { "checkIP"_s, static_cast<unsigned>(PropertyAttribute::Function), NoIntrinsic, { HashTableValue::NativeFunctionType, jsX509CertificateProtoFuncCheckIP, 1 } },
-    { "checkIssued"_s, static_cast<unsigned>(PropertyAttribute::Function), NoIntrinsic, { HashTableValue::NativeFunctionType, jsX509CertificateProtoFuncCheckIssued, 1 } },
-    { "checkPrivateKey"_s, static_cast<unsigned>(PropertyAttribute::Function), NoIntrinsic, { HashTableValue::NativeFunctionType, jsX509CertificateProtoFuncCheckPrivateKey, 1 } },
-    { "fingerprint"_s, static_cast<unsigned>(PropertyAttribute::ReadOnly | PropertyAttribute::CustomAccessor), NoIntrinsic, { HashTableValue::GetterSetterType, jsX509CertificateGetter_fingerprint, 0 } },
-    { "fingerprint256"_s, static_cast<unsigned>(PropertyAttribute::ReadOnly | PropertyAttribute::CustomAccessor), NoIntrinsic, { HashTableValue::GetterSetterType, jsX509CertificateGetter_fingerprint256, 0 } },
-    { "fingerprint512"_s, static_cast<unsigned>(PropertyAttribute::ReadOnly | PropertyAttribute::CustomAccessor), NoIntrinsic, { HashTableValue::GetterSetterType, jsX509CertificateGetter_fingerprint512, 0 } },
-    { "infoAccess"_s, static_cast<unsigned>(PropertyAttribute::ReadOnly | PropertyAttribute::CustomAccessor), NoIntrinsic, { HashTableValue::GetterSetterType, jsX509CertificateGetter_infoAccess, 0 } },
-    { "issuer"_s, static_cast<unsigned>(PropertyAttribute::ReadOnly | PropertyAttribute::CustomAccessor), NoIntrinsic, { HashTableValue::GetterSetterType, jsX509CertificateGetter_issuer, 0 } },
-    { "issuerCertificate"_s, static_cast<unsigned>(PropertyAttribute::ReadOnly | PropertyAttribute::CustomAccessor), NoIntrinsic, { HashTableValue::GetterSetterType, jsX509CertificateGetter_issuerCertificate, 0 } },
-    { "keyUsage"_s, static_cast<unsigned>(PropertyAttribute::ReadOnly | PropertyAttribute::CustomAccessor), NoIntrinsic, { HashTableValue::GetterSetterType, jsX509CertificateGetter_keyUsage, 0 } },
-    { "publicKey"_s, static_cast<unsigned>(PropertyAttribute::ReadOnly | PropertyAttribute::CustomAccessor), NoIntrinsic, { HashTableValue::GetterSetterType, jsX509CertificateGetter_publicKey, 0 } },
-    { "raw"_s, static_cast<unsigned>(PropertyAttribute::ReadOnly | PropertyAttribute::CustomAccessor), NoIntrinsic, { HashTableValue::GetterSetterType, jsX509CertificateGetter_raw, 0 } },
-    { "serialNumber"_s, static_cast<unsigned>(PropertyAttribute::ReadOnly | PropertyAttribute::CustomAccessor), NoIntrinsic, { HashTableValue::GetterSetterType, jsX509CertificateGetter_serialNumber, 0 } },
-    { "subject"_s, static_cast<unsigned>(PropertyAttribute::ReadOnly | PropertyAttribute::CustomAccessor), NoIntrinsic, { HashTableValue::GetterSetterType, jsX509CertificateGetter_subject, 0 } },
-    { "subjectAltName"_s, static_cast<unsigned>(PropertyAttribute::ReadOnly | PropertyAttribute::CustomAccessor), NoIntrinsic, { HashTableValue::GetterSetterType, jsX509CertificateGetter_subjectAltName, 0 } },
-    { "toJSON"_s, static_cast<unsigned>(PropertyAttribute::Function), NoIntrinsic, { HashTableValue::NativeFunctionType, jsX509CertificateProtoFuncToJSON, 0 } },
-    { "toLegacyObject"_s, static_cast<unsigned>(PropertyAttribute::Function), NoIntrinsic, { HashTableValue::NativeFunctionType, jsX509CertificateProtoFuncToLegacyObject, 0 } },
-    { "toString"_s, static_cast<unsigned>(PropertyAttribute::Function), NoIntrinsic, { HashTableValue::NativeFunctionType, jsX509CertificateProtoFuncToString, 0 } },
-    { "validFrom"_s, static_cast<unsigned>(PropertyAttribute::ReadOnly | PropertyAttribute::CustomAccessor), NoIntrinsic, { HashTableValue::GetterSetterType, jsX509CertificateGetter_validFrom, 0 } },
-    { "validFromDate"_s, static_cast<unsigned>(PropertyAttribute::ReadOnly | PropertyAttribute::CustomAccessorOrValue), NoIntrinsic, { HashTableValue::GetterSetterType, jsX509CertificateGetter_validFromDate, 0 } },
-    { "validTo"_s, static_cast<unsigned>(PropertyAttribute::ReadOnly | PropertyAttribute::CustomAccessor), NoIntrinsic, { HashTableValue::GetterSetterType, jsX509CertificateGetter_validTo, 0 } },
-    { "validToDate"_s, static_cast<unsigned>(PropertyAttribute::ReadOnly | PropertyAttribute::CustomAccessorOrValue), NoIntrinsic, { HashTableValue::GetterSetterType, jsX509CertificateGetter_validToDate, 0 } },
-    { "verify"_s, static_cast<unsigned>(PropertyAttribute::Function), NoIntrinsic, { HashTableValue::NativeFunctionType, jsX509CertificateProtoFuncVerify, 1 } },
-};
-```
-
-### Creating a prototype class
-
-Follow a pattern like this:
-
-```c++
-class JSX509CertificatePrototype final : public JSC::JSNonFinalObject {
-public:
-    using Base = JSC::JSNonFinalObject;
-    static constexpr unsigned StructureFlags = Base::StructureFlags;
-
-    static JSX509CertificatePrototype* create(JSC::VM& vm, JSC::JSGlobalObject* globalObject, JSC::Structure* structure)
-    {
-        JSX509CertificatePrototype* prototype = new (NotNull, allocateCell<JSX509CertificatePrototype>(vm)) JSX509CertificatePrototype(vm, structure);
-        prototype->finishCreation(vm);
-        return prototype;
-    }
-
-    template<typename, JSC::SubspaceAccess>
-    static JSC::GCClient::IsoSubspace* subspaceFor(JSC::VM& vm)
-    {
-        return &vm.plainObjectSpace();
-    }
-
-    DECLARE_INFO;
-
-    static JSC::Structure* createStructure(JSC::VM& vm, JSC::JSGlobalObject* globalObject, JSC::JSValue prototype)
-    {
-        auto* structure = JSC::Structure::create(vm, globalObject, prototype, JSC::TypeInfo(JSC::ObjectType, StructureFlags), info());
-        structure->setMayBePrototype(true);
-        return structure;
-    }
-
-private:
-    JSX509CertificatePrototype(JSC::VM& vm, JSC::Structure* structure)
-        : Base(vm, structure)
-    {
-    }
-
-    void finishCreation(JSC::VM& vm);
-};
-
-const ClassInfo JSX509CertificatePrototype::s_info = { "X509Certificate"_s, &Base::s_info, nullptr, nullptr, CREATE_METHOD_TABLE(JSX509CertificatePrototype) };
-
-void JSX509CertificatePrototype::finishCreation(VM& vm)
-{
-    Base::finishCreation(vm);
-    reifyStaticProperties(vm, JSX509Certificate::info(), JSX509CertificatePrototypeTableValues, *this);
-    JSC_TO_STRING_TAG_WITHOUT_TRANSITION();
-}
-
-} // namespace Bun
-```
-
-### Getter definition:
-
-```C++
-
-JSC_DEFINE_CUSTOM_GETTER(jsX509CertificateGetter_ca, (JSGlobalObject * globalObject, EncodedJSValue thisValue, PropertyName))
-{
-    VM& vm = globalObject->vm();
-    auto scope = DECLARE_THROW_SCOPE(vm);
-
-    JSX509Certificate* thisObject = jsDynamicCast<JSX509Certificate*>(JSValue::decode(thisValue));
-    if (UNLIKELY(!thisObject)) {
-        Bun::throwThisTypeError(*globalObject, scope, "JSX509Certificate"_s, "ca"_s);
-        return {};
-    }
-
-    return JSValue::encode(jsBoolean(thisObject->view().isCA()));
-}
-```
-
-### Setter definition
-
-```C++
-JSC_DEFINE_CUSTOM_SETTER(jsImportMetaObjectSetter_require, (JSGlobalObject * jsGlobalObject, JSC::EncodedJSValue thisValue, JSC::EncodedJSValue encodedValue, PropertyName propertyName))
-{
-    ImportMetaObject* thisObject = jsDynamicCast<ImportMetaObject*>(JSValue::decode(thisValue));
-    if (UNLIKELY(!thisObject))
-        return false;
-
-    JSValue value = JSValue::decode(encodedValue);
-    if (!value.isCell()) {
-        // TODO:
-        return true;
-    }
-
-    thisObject->requireProperty.set(thisObject->vm(), thisObject, value.asCell());
-    return true;
-}
-```
-
-### Function definition
-
-```C++
-JSC_DEFINE_HOST_FUNCTION(jsX509CertificateProtoFuncToJSON, (JSGlobalObject * globalObject, CallFrame* callFrame))
-{
-    VM& vm = globalObject->vm();
-    auto scope = DECLARE_THROW_SCOPE(vm);
-    auto *thisObject = jsDynamicCast<MyClassT*>(callFrame->thisValue());
-     if (UNLIKELY(!thisObject)) {
-        Bun::throwThisTypeError(*globalObject, scope, "MyClass"_s, "myFunctionName"_s);
-        return {};
-    }
-
-    return JSValue::encode(functionThatReturnsJSValue(vm, globalObject, thisObject));
-}
-```
-
-### Constructor definition
-
-```C++
-
-JSC_DECLARE_HOST_FUNCTION(callStats);
-JSC_DECLARE_HOST_FUNCTION(constructStats);
-
-class JSStatsConstructor final : public JSC::InternalFunction {
-public:
-    using Base = JSC::InternalFunction;
-    static constexpr unsigned StructureFlags = Base::StructureFlags;
-
-    static JSStatsConstructor* create(JSC::VM& vm, JSC::Structure* structure, JSC::JSObject* prototype)
-    {
-        JSStatsConstructor* constructor = new (NotNull, JSC::allocateCell<JSStatsConstructor>(vm)) JSStatsConstructor(vm, structure);
-        constructor->finishCreation(vm, prototype);
-        return constructor;
-    }
-
-    DECLARE_INFO;
-
-    template<typename CellType, JSC::SubspaceAccess>
-    static JSC::GCClient::IsoSubspace* subspaceFor(JSC::VM& vm)
-    {
-        return &vm.internalFunctionSpace();
-    }
-
-    static JSC::Structure* createStructure(JSC::VM& vm, JSC::JSGlobalObject* globalObject, JSC::JSValue prototype)
-    {
-        return JSC::Structure::create(vm, globalObject, prototype, JSC::TypeInfo(JSC::InternalFunctionType, StructureFlags), info());
-    }
-
-private:
-    JSStatsConstructor(JSC::VM& vm, JSC::Structure* structure)
-        : Base(vm, structure, callStats, constructStats)
-    {
-    }
-
-    void finishCreation(JSC::VM& vm, JSC::JSObject* prototype)
-    {
-        Base::finishCreation(vm, 0, "Stats"_s);
-        putDirectWithoutTransition(vm, vm.propertyNames->prototype, prototype, JSC::PropertyAttribute::DontEnum | JSC::PropertyAttribute::DontDelete | JSC::PropertyAttribute::ReadOnly);
-    }
-};
-```
-
-### Structure caching
-
-If there's a class, prototype, and constructor:
-
-1. Add the `JSC::LazyClassStructure` to [ZigGlobalObject.h](mdc:src/bun.js/bindings/ZigGlobalObject.h)
-2. Initialize the class structure in [ZigGlobalObject.cpp](mdc:src/bun.js/bindings/ZigGlobalObject.cpp) in `void GlobalObject::finishCreation(VM& vm)`
-3. Visit the class structure in visitChildren in [ZigGlobalObject.cpp](mdc:src/bun.js/bindings/ZigGlobalObject.cpp) in `void GlobalObject::visitChildrenImpl`
-
-```c++#ZigGlobalObject.cpp
-void GlobalObject::finishCreation(VM& vm) {
-// ...
-    m_JSStatsBigIntClassStructure.initLater(
-        [](LazyClassStructure::Initializer& init) {
-            // Call the function to initialize our class structure.
-            Bun::initJSBigIntStatsClassStructure(init);
-        });
-```
-
-Then, implement the function that creates the structure:
-
-```c++
-void setupX509CertificateClassStructure(LazyClassStructure::Initializer& init)
-{
-    auto* prototypeStructure = JSX509CertificatePrototype::createStructure(init.vm, init.global, init.global->objectPrototype());
-    auto* prototype = JSX509CertificatePrototype::create(init.vm, init.global, prototypeStructure);
-
-    auto* constructorStructure = JSX509CertificateConstructor::createStructure(init.vm, init.global, init.global->functionPrototype());
-
-    auto* constructor = JSX509CertificateConstructor::create(init.vm, init.global, constructorStructure, prototype);
-
-    auto* structure = JSX509Certificate::createStructure(init.vm, init.global, prototype);
-    init.setPrototype(prototype);
-    init.setStructure(structure);
-    init.setConstructor(constructor);
-}
-```
-
-If there's only a class, use `JSC::LazyProperty<JSGlobalObject, Structure>` instead of `JSC::LazyClassStructure`:
-
-1. Add the `JSC::LazyProperty<JSGlobalObject, Structure>` to @ZigGlobalObject.h
-2. Initialize the class structure in @ZigGlobalObject.cpp in `void GlobalObject::finishCreation(VM& vm)`
-3. Visit the lazy property in visitChildren in @ZigGlobalObject.cpp in `void GlobalObject::visitChildrenImpl`
-   void GlobalObject::finishCreation(VM& vm) {
-   // ...
-   this.m_myLazyProperty.initLater([](const JSC::LazyProperty<JSC::JSGlobalObject, JSC::Structure>::Initializer& init) {
-   init.set(Bun::initMyStructure(init.vm, reinterpret_cast<Zig::GlobalObject\*>(init.owner)));
-   });
-
-```
-
-Then, implement the function that creates the structure:
-```c++
-Structure* setupX509CertificateStructure(JSC::VM &vm, Zig::GlobalObject* globalObject)
-{
-    // If there is a prototype:
-    auto* prototypeStructure = JSX509CertificatePrototype::createStructure(init.vm, init.global, init.global->objectPrototype());
-    auto* prototype = JSX509CertificatePrototype::create(init.vm, init.global, prototypeStructure);
-
-    // If there is no prototype or it only has
-
-    auto* structure = JSX509Certificate::createStructure(init.vm, init.global, prototype);
-    init.setPrototype(prototype);
-    init.setStructure(structure);
-    init.setConstructor(constructor);
-}
-```
-
-Then, use the structure by calling `globalObject.m_myStructureName.get(globalObject)`
-
-```C++
-JSC_DEFINE_HOST_FUNCTION(x509CertificateConstructorConstruct, (JSGlobalObject * globalObject, CallFrame* callFrame))
-{
-    VM& vm = globalObject->vm();
-    auto scope = DECLARE_THROW_SCOPE(vm);
-
-    if (!callFrame->argumentCount()) {
-        Bun::throwError(globalObject, scope, ErrorCode::ERR_MISSING_ARGS, "X509Certificate constructor requires at least one argument"_s);
-        return {};
-    }
-
-    JSValue arg = callFrame->uncheckedArgument(0);
-    if (!arg.isCell()) {
-        Bun::throwError(globalObject, scope, ErrorCode::ERR_INVALID_ARG_TYPE, "X509Certificate constructor argument must be a Buffer, TypedArray, or string"_s);
-        return {};
-    }
-
-    auto* zigGlobalObject = defaultGlobalObject(globalObject);
-    Structure* structure = zigGlobalObject->m_JSX509CertificateClassStructure.get(zigGlobalObject);
-    JSValue newTarget = callFrame->newTarget();
-    if (UNLIKELY(zigGlobalObject->m_JSX509CertificateClassStructure.constructor(zigGlobalObject) != newTarget)) {
-        auto scope = DECLARE_THROW_SCOPE(vm);
-        if (!newTarget) {
-            throwTypeError(globalObject, scope, "Class constructor X509Certificate cannot be invoked without 'new'"_s);
-            return {};
-        }
-
-        auto* functionGlobalObject = defaultGlobalObject(getFunctionRealm(globalObject, newTarget.getObject()));
-        RETURN_IF_EXCEPTION(scope, {});
-        structure = InternalFunction::createSubclassStructure(globalObject, newTarget.getObject(), functionGlobalObject->NodeVMScriptStructure());
-        RETURN_IF_EXCEPTION(scope, {});
-    }
-
-    return JSValue::encode(createX509Certificate(vm, globalObject, structure, arg));
-}
-```
-
-### Expose to Zig
-
-To expose the constructor to zig:
-
-```c++
-extern "C" JSC::EncodedJSValue Bun__JSBigIntStatsObjectConstructor(Zig::GlobalObject* globalobject)
-{
-    return JSValue::encode(globalobject->m_JSStatsBigIntClassStructure.constructor(globalobject));
-}
-```
-
-Zig:
-
-```zig
-extern "c" fn Bun__JSBigIntStatsObjectConstructor(*JSC.JSGlobalObject) JSC.JSValue;
-pub const getBigIntStatsConstructor =  Bun__JSBigIntStatsObjectConstructor;
-```
-
-To create an object (instance) of a JS class defined in C++ from Zig, follow the \_\_toJS convention like this:
-
-```c++
-// X509* is whatever we need to create the object
-extern "C" EncodedJSValue Bun__X509__toJS(Zig::GlobalObject* globalObject, X509* cert)
-{
-    // ... implementation details
-    auto* structure = globalObject->m_JSX509CertificateClassStructure.get(globalObject);
-    return JSValue::encode(JSX509Certificate::create(globalObject->vm(), structure, globalObject, WTFMove(cert)));
-}
-```
-
-And from Zig:
-
-```zig
-const X509 = opaque {
-    // ... class
-
-    extern fn Bun__X509__toJS(*JSC.JSGlobalObject, *X509) JSC.JSValue;
-
-    pub fn toJS(this: *X509, globalObject: *JSC.JSGlobalObject) JSC.JSValue {
-        return Bun__X509__toJS(globalObject, this);
-    }
-};
-```
diff --git a/.cursor/rules/registering-bun-modules.mdc b/.cursor/rules/registering-bun-modules.mdc
@@ -1,203 +0,0 @@
-# Registering Functions, Objects, and Modules in Bun
-
-This guide documents the process of adding new functionality to the Bun global object and runtime.
-
-## Overview
-
-Bun's architecture exposes functionality to JavaScript through a set of carefully registered functions, objects, and modules. Most core functionality is implemented in Zig, with JavaScript bindings that make these features accessible to users.
-
-There are several key ways to expose functionality in Bun:
-
-1. **Global Functions**: Direct methods on the `Bun` object (e.g., `Bun.serve()`)
-2. **Getter Properties**: Lazily initialized properties on the `Bun` object (e.g., `Bun.sqlite`)
-3. **Constructor Classes**: Classes available through the `Bun` object (e.g., `Bun.ValkeyClient`)
-4. **Global Modules**: Modules that can be imported directly (e.g., `import {X} from "bun:*"`)
-
-## The Registration Process
-
-Adding new functionality to Bun involves several coordinated steps across multiple files:
-
-### 1. Implement the Core Functionality in Zig
-
-First, implement your feature in Zig, typically in its own directory in `src/`. Examples:
-
-- `src/valkey/` for Redis/Valkey client
-- `src/semver/` for SemVer functionality
-- `src/smtp/` for SMTP client
-
-### 2. Create JavaScript Bindings
-
-Create bindings that expose your Zig functionality to JavaScript:
-
-- Create a class definition file (e.g., `js_bindings.classes.ts`) to define the JavaScript interface
-- Implement `JSYourFeature` struct in a file like `js_your_feature.zig`
-
-Example from a class definition file:
-
-```typescript
-// Example from a .classes.ts file
-import { define } from "../../codegen/class-definitions";
-
-export default [
-  define({
-    name: "YourFeature",
-    construct: true,
-    finalize: true,
-    hasPendingActivity: true,
-    memoryCost: true,
-    klass: {},
-    JSType: "0b11101110",
-    proto: {
-      yourMethod: {
-        fn: "yourZigMethod",
-        length: 1,
-      },
-      property: {
-        getter: "getProperty",
-      },
-    },
-    values: ["cachedValues"],
-  }),
-];
-```
-
-### 3. Register with BunObject in `src/bun.js/bindings/BunObject+exports.h`
-
-Add an entry to the `FOR_EACH_GETTER` macro:
-
-```c
-// In BunObject+exports.h
-#define FOR_EACH_GETTER(macro) \
-    macro(CSRF) \
-    macro(CryptoHasher) \
-    ... \
-    macro(YourFeature) \
-```
-
-### 4. Create a Getter Function in `src/bun.js/api/BunObject.zig`
-
-Implement a getter function in `BunObject.zig` that returns your feature:
-
-```zig
-// In BunObject.zig
-pub const YourFeature = toJSGetter(Bun.getYourFeatureConstructor);
-
-// In the exportAll() function:
-@export(&BunObject.YourFeature, .{ .name = getterName("YourFeature") });
-```
-
-### 5. Implement the Getter Function in a Relevant Zig File
-
-Implement the function that creates your object:
-
-```zig
-// In your main module file (e.g., src/your_feature/your_feature.zig)
-pub fn getYourFeatureConstructor(globalThis: *JSC.JSGlobalObject, _: *JSC.JSObject) JSC.JSValue {
-    return JSC.API.YourFeature.getConstructor(globalThis);
-}
-```
-
-### 6. Add to Build System
-
-Ensure your files are included in the build system by adding them to the appropriate targets.
-
-## Example: Adding a New Module
-
-Here's a comprehensive example of adding a hypothetical SMTP module:
-
-1. Create implementation files in `src/smtp/`:
-
-   - `index.zig`: Main entry point that exports everything
-   - `SmtpClient.zig`: Core SMTP client implementation
-   - `js_smtp.zig`: JavaScript bindings
-   - `js_bindings.classes.ts`: Class definition
-
-2. Define your JS class in `js_bindings.classes.ts`:
-
-```typescript
-import { define } from "../../codegen/class-definitions";
-
-export default [
-  define({
-    name: "EmailClient",
-    construct: true,
-    finalize: true,
-    hasPendingActivity: true,
-    configurable: false,
-    memoryCost: true,
-    klass: {},
-    JSType: "0b11101110",
-    proto: {
-      send: {
-        fn: "send",
-        length: 1,
-      },
-      verify: {
-        fn: "verify",
-        length: 0,
-      },
-      close: {
-        fn: "close",
-        length: 0,
-      },
-    },
-    values: ["connectionPromise"],
-  }),
-];
-```
-
-3. Add getter to `BunObject+exports.h`:
-
-```c
-#define FOR_EACH_GETTER(macro) \
-    macro(CSRF) \
-    ... \
-    macro(SMTP) \
-```
-
-4. Add getter function to `BunObject.zig`:
-
-```zig
-pub const SMTP = toJSGetter(Bun.getSmtpConstructor);
-
-// In exportAll:
-@export(&BunObject.SMTP, .{ .name = getterName("SMTP") });
-```
-
-5. Implement getter in your module:
-
-```zig
-pub fn getSmtpConstructor(globalThis: *JSC.JSGlobalObject, _: *JSC.JSObject) JSC.JSValue {
-    return JSC.API.JSEmailClient.getConstructor(globalThis);
-}
-```
-
-## Best Practices
-
-1. **Follow Naming Conventions**: Align your naming with existing patterns
-2. **Reference Existing Modules**: Study similar modules like Valkey or S3Client for guidance
-3. **Memory Management**: Be careful with memory management and reference counting
-4. **Error Handling**: Use `bun.JSError!JSValue` for proper error propagation
-5. **Documentation**: Add JSDoc comments to your JavaScript bindings
-6. **Testing**: Add tests for your new functionality
-
-## Common Gotchas
-
-- Be sure to handle reference counting properly with `ref()`/`deref()`
-- Always implement proper cleanup in `deinit()` and `finalize()`
-- For network operations, manage socket lifetimes correctly
-- Use `JSC.Codegen` correctly to generate necessary binding code
-
-## Related Files
-
-- `src/bun.js/bindings/BunObject+exports.h`: Registration of getters and functions
-- `src/bun.js/api/BunObject.zig`: Implementation of getters and object creation
-- `src/bun.js/api/BunObject.classes.ts`: Class definitions
-- `.cursor/rules/zig-javascriptcore-classes.mdc`: More details on class bindings
-
-## Additional Resources
-
-For more detailed information on specific topics:
-
-- See `zig-javascriptcore-classes.mdc` for details on creating JS class bindings
-- Review existing modules like `valkey`, `sqlite`, or `s3` for real-world examples
diff --git a/.cursor/rules/writing-tests.mdc b/.cursor/rules/writing-tests.mdc
@@ -1,91 +0,0 @@
----
-description: Writing tests for Bun
-globs: 
----
-# Writing tests for Bun
-
-## Where tests are found
-
-You'll find all of Bun's tests in the `test/` directory.
-
-* `test/`
-  * `cli/` - CLI command tests, like `bun install` or `bun init`
-  * `js/` - JavaScript & TypeScript tests
-    * `bun/` - `Bun` APIs tests, separated by category, for example: `glob/` for `Bun.Glob` tests
-    * `node/` - Node.js module tests, separated by module, for example: `assert/` for `node:assert` tests
-      * `test/` - Vendored Node.js tests, taken from the Node.js repository (does not conform to Bun's test style)
-    * `web/` - Web API tests, separated by category, for example: `fetch/` for `Request` and `Response` tests
-    * `third_party/` - npm package tests, to validate that basic usage works in Bun
-  * `napi/` - N-API tests
-  * `v8/` - V8 C++ API tests
-  * `bundler/` - Bundler, transpiler, CSS, and `bun build` tests
-  * `regression/issue/[number]` - Regression tests, always make one when fixing a particular issue
-
-## How tests are written
-
-Bun's tests are written as JavaScript and TypeScript files with the Jest-style APIs, like `test`, `describe`, and `expect`. They are tested using Bun's own test runner, `bun test`. 
-
-```js
-import { describe, test, expect } from "bun:test";
-import assert, { AssertionError } from "assert";
-
-describe("assert(expr)", () => {
-  test.each([true, 1, "foo"])(`assert(%p) does not throw`, expr => {
-    expect(() => assert(expr)).not.toThrow();
-  });
-
-  test.each([false, 0, "", null, undefined])(`assert(%p) throws`, expr => {
-    expect(() => assert(expr)).toThrow(AssertionError);
-  });
-});
-```
-
-## Testing conventions
-
-* See `test/harness.ts` for common test utilities and helpers
-* Be rigorous and test for edge-cases and unexpected inputs
-* Use data-driven tests, e.g. `test.each`, to reduce boilerplate when possible
-* When you need to test Bun as a CLI, use the following pattern:
-
-```js
-import { test, expect } from "bun:test";
-import { spawn } from "bun";
-import { bunExe, bunEnv } from "harness";
-
-test("bun --version", async () => {
-  const { exited, stdout: stdoutStream, stderr: stderrStream } = spawn({
-    cmd: [bunExe(), "--version"],
-    env: bunEnv,
-    stdout: "pipe",
-    stderr: "pipe",
-  });
-  const [ exitCode, stdout, stderr ] = await Promise.all([
-    exited,
-    new Response(stdoutStream).text(),
-    new Response(stderrStream).text(),
-  ]);
-  expect({ exitCode, stdout, stderr }).toMatchObject({
-    exitCode: 0,
-    stdout: expect.stringContaining(Bun.version),
-    stderr: "",
-  });
-});
-```
-
-## Before writing a test
-
-* If you are fixing a bug, write the test first and make sure it fails (as expected) with the canary version of Bun
-* If you are fixing a Node.js compatibility bug, create a throw-away snippet of code and test that it works as you expect in Node.js, then that it fails (as expected) with the canary version of Bun
-* When the expected behaviour is ambigious, defer to matching what happens in Node.js
-* Always attempt to find related tests in an existing test file before creating a new test file
-
-
-
-
-
-
-
-
-
-
-
diff --git a/.cursor/rules/zig-javascriptcore-classes.mdc b/.cursor/rules/zig-javascriptcore-classes.mdc
@@ -1,509 +0,0 @@
----
-description: How Zig works with JavaScriptCore bindings generator
-globs:
-alwaysApply: false
----
-
-# Bun's JavaScriptCore Class Bindings Generator
-
-This document explains how Bun's class bindings generator works to bridge Zig and JavaScript code through JavaScriptCore (JSC).
-
-## Architecture Overview
-
-Bun's binding system creates a seamless bridge between JavaScript and Zig, allowing Zig implementations to be exposed as JavaScript classes. The system has several key components:
-
-1. **Zig Implementation** (.zig files)
-2. **JavaScript Interface Definition** (.classes.ts files)
-3. **Generated Code** (C++/Zig files that connect everything)
-
-## Class Definition Files
-
-### JavaScript Interface (.classes.ts)
-
-The `.classes.ts` files define the JavaScript API using a declarative approach:
-
-```typescript
-// Example: encoding.classes.ts
-define({
-  name: "TextDecoder",
-  constructor: true,
-  JSType: "object",
-  finalize: true,
-  proto: {
-    decode: {
-      // Function definition
-      args: 1,
-    },
-    encoding: {
-      // Getter with caching
-      getter: true,
-      cache: true,
-    },
-    fatal: {
-      // Read-only property
-      getter: true,
-    },
-    ignoreBOM: {
-      // Read-only property
-      getter: true,
-    },
-  },
-});
-```
-
-Each class definition specifies:
-
-- The class name
-- Whether it has a constructor
-- JavaScript type (object, function, etc.)
-- Properties and methods in the `proto` field
-- Caching strategy for properties
-- Finalization requirements
-
-### Zig Implementation (.zig)
-
-The Zig files implement the native functionality:
-
-```zig
-// Example: TextDecoder.zig
-pub const TextDecoder = struct {
-    // Expose generated bindings as `js` namespace with trait conversion methods
-    pub const js = JSC.Codegen.JSTextDecoder;
-    pub const toJS = js.toJS;
-    pub const fromJS = js.fromJS;
-    pub const fromJSDirect = js.fromJSDirect;
-
-    // Internal state
-    encoding: []const u8,
-    fatal: bool,
-    ignoreBOM: bool,
-
-    // Constructor implementation - note use of globalObject
-    pub fn constructor(
-        globalObject: *JSGlobalObject,
-        callFrame: *JSC.CallFrame,
-    ) bun.JSError!*TextDecoder {
-        // Implementation
-
-        return bun.new(TextDecoder, .{
-            // Fields
-        });
-    }
-
-    // Prototype methods - note return type includes JSError
-    pub fn decode(
-        this: *TextDecoder,
-        globalObject: *JSGlobalObject,
-        callFrame: *JSC.CallFrame,
-    ) bun.JSError!JSC.JSValue {
-        // Implementation
-    }
-
-    // Getters
-    pub fn getEncoding(this: *TextDecoder, globalObject: *JSGlobalObject) JSC.JSValue {
-        return JSC.JSValue.createStringFromUTF8(globalObject, this.encoding);
-    }
-
-    pub fn getFatal(this: *TextDecoder, globalObject: *JSGlobalObject) JSC.JSValue {
-        return JSC.JSValue.jsBoolean(this.fatal);
-    }
-
-    // Cleanup - note standard pattern of using deinit/deref
-    fn deinit(this: *TextDecoder) void {
-        // Release any retained resources
-        // Free the pointer at the end.
-        bun.destroy(this);
-    }
-
-    // Finalize - called by JS garbage collector. This should call deinit, or deref if reference counted.
-    pub fn finalize(this: *TextDecoder) void {
-        this.deinit();
-    }
-};
-```
-
-Key components in the Zig file:
-
-- The struct containing native state
-- `pub const js = JSC.Codegen.JS<ClassName>` to include generated code
-- Constructor and methods using `bun.JSError!JSValue` return type for proper error handling
-- Consistent use of `globalObject` parameter name instead of `ctx`
-- Methods matching the JavaScript interface
-- Getters/setters for properties
-- Proper resource cleanup pattern with `deinit()` and `finalize()`
-- Update `src/bun.js/bindings/generated_classes_list.zig` to include the new class
-
-## Code Generation System
-
-The binding generator produces C++ code that connects JavaScript and Zig:
-
-1. **JSC Class Structure**: Creates C++ classes for the JS object, prototype, and constructor
-2. **Memory Management**: Handles GC integration through JSC's WriteBarrier
-3. **Method Binding**: Connects JS function calls to Zig implementations
-4. **Type Conversion**: Converts between JS values and Zig types
-5. **Property Caching**: Implements the caching system for properties
-
-The generated C++ code includes:
-
-- A JSC wrapper class (`JSTextDecoder`)
-- A prototype class (`JSTextDecoderPrototype`)
-- A constructor function (`JSTextDecoderConstructor`)
-- Function bindings (`TextDecoderPrototype__decodeCallback`)
-- Property getters/setters (`TextDecoderPrototype__encodingGetterWrap`)
-
-## CallFrame Access
-
-The `CallFrame` object provides access to JavaScript execution context:
-
-```zig
-pub fn decode(
-    this: *TextDecoder,
-    globalObject: *JSGlobalObject,
-    callFrame: *JSC.CallFrame
-) bun.JSError!JSC.JSValue {
-    // Get arguments
-    const input = callFrame.argument(0);
-    const options = callFrame.argument(1);
-
-    // Get this value
-    const thisValue = callFrame.thisValue();
-
-    // Implementation with error handling
-    if (input.isUndefinedOrNull()) {
-        return globalObject.throw("Input cannot be null or undefined", .{});
-    }
-
-    // Return value or throw error
-    return JSC.JSValue.jsString(globalObject, "result");
-}
-```
-
-CallFrame methods include:
-
-- `argument(i)`: Get the i-th argument
-- `argumentCount()`: Get the number of arguments
-- `thisValue()`: Get the `this` value
-- `callee()`: Get the function being called
-
-## Property Caching and GC-Owned Values
-
-The `cache: true` option in property definitions enables JSC's WriteBarrier to efficiently store values:
-
-```typescript
-encoding: {
-  getter: true,
-  cache: true, // Enable caching
-}
-```
-
-### C++ Implementation
-
-In the generated C++ code, caching uses JSC's WriteBarrier:
-
-```cpp
-JSC_DEFINE_CUSTOM_GETTER(TextDecoderPrototype__encodingGetterWrap, (...)) {
-    auto& vm = JSC::getVM(lexicalGlobalObject);
-    Zig::GlobalObject *globalObject = reinterpret_cast<Zig::GlobalObject*>(lexicalGlobalObject);
-    auto throwScope = DECLARE_THROW_SCOPE(vm);
-    JSTextDecoder* thisObject = jsCast<JSTextDecoder*>(JSValue::decode(encodedThisValue));
-    JSC::EnsureStillAliveScope thisArg = JSC::EnsureStillAliveScope(thisObject);
-
-    // Check for cached value and return if present
-    if (JSValue cachedValue = thisObject->m_encoding.get())
-        return JSValue::encode(cachedValue);
-
-    // Get value from Zig implementation
-    JSC::JSValue result = JSC::JSValue::decode(
-        TextDecoderPrototype__getEncoding(thisObject->wrapped(), globalObject)
-    );
-    RETURN_IF_EXCEPTION(throwScope, {});
-
-    // Store in cache for future access
-    thisObject->m_encoding.set(vm, thisObject, result);
-    RELEASE_AND_RETURN(throwScope, JSValue::encode(result));
-}
-```
-
-### Zig Accessor Functions
-
-For each cached property, the generator creates Zig accessor functions that allow Zig code to work with these GC-owned values:
-
-```zig
-// External function declarations
-extern fn TextDecoderPrototype__encodingSetCachedValue(JSC.JSValue, *JSC.JSGlobalObject, JSC.JSValue) callconv(JSC.conv) void;
-extern fn TextDecoderPrototype__encodingGetCachedValue(JSC.JSValue) callconv(JSC.conv) JSC.JSValue;
-
-/// `TextDecoder.encoding` setter
-/// This value will be visited by the garbage collector.
-pub fn encodingSetCached(thisValue: JSC.JSValue, globalObject: *JSC.JSGlobalObject, value: JSC.JSValue) void {
-    JSC.markBinding(@src());
-    TextDecoderPrototype__encodingSetCachedValue(thisValue, globalObject, value);
-}
-
-/// `TextDecoder.encoding` getter
-/// This value will be visited by the garbage collector.
-pub fn encodingGetCached(thisValue: JSC.JSValue) ?JSC.JSValue {
-    JSC.markBinding(@src());
-    const result = TextDecoderPrototype__encodingGetCachedValue(thisValue);
-    if (result == .zero)
-        return null;
-
-    return result;
-}
-```
-
-### Benefits of GC-Owned Values
-
-This system provides several key benefits:
-
-1. **Automatic Memory Management**: The JavaScriptCore GC tracks and manages these values
-2. **Proper Garbage Collection**: The WriteBarrier ensures values are properly visited during GC
-3. **Consistent Access**: Zig code can easily get/set these cached JS values
-4. **Performance**: Cached values avoid repeated computation or serialization
-
-### Use Cases
-
-GC-owned cached values are particularly useful for:
-
-1. **Computed Properties**: Store expensive computation results
-2. **Lazily Created Objects**: Create objects only when needed, then cache them
-3. **References to Other Objects**: Store references to other JS objects that need GC tracking
-4. **Memoization**: Cache results based on input parameters
-
-The WriteBarrier mechanism ensures that any JS values stored in this way are properly tracked by the garbage collector.
-
-## Memory Management and Finalization
-
-The binding system handles memory management across the JavaScript/Zig boundary:
-
-1. **Object Creation**: JavaScript `new TextDecoder()` creates both a JS wrapper and a Zig struct
-2. **Reference Tracking**: JSC's GC tracks all JS references to the object
-3. **Finalization**: When the JS object is collected, the finalizer releases Zig resources
-
-Bun uses a consistent pattern for resource cleanup:
-
-```zig
-// Resource cleanup method - separate from finalization
-pub fn deinit(this: *TextDecoder) void {
-    // Release resources like strings
-    this._encoding.deref(); // String deref pattern
-
-    // Free any buffers
-    if (this.buffer) |buffer| {
-        bun.default_allocator.free(buffer);
-    }
-}
-
-// Called by the GC when object is collected
-pub fn finalize(this: *TextDecoder) void {
-    JSC.markBinding(@src()); // For debugging
-    this.deinit(); // Clean up resources
-    bun.default_allocator.destroy(this); // Free the object itself
-}
-```
-
-Some objects that hold references to other JS objects use `.deref()` instead:
-
-```zig
-pub fn finalize(this: *SocketAddress) void {
-    JSC.markBinding(@src());
-    this._presentation.deref(); // Release references
-    this.destroy();
-}
-```
-
-## Error Handling with JSError
-
-Bun uses `bun.JSError!JSValue` return type for proper error handling:
-
-```zig
-pub fn decode(
-    this: *TextDecoder,
-    globalObject: *JSGlobalObject,
-    callFrame: *JSC.CallFrame
-) bun.JSError!JSC.JSValue {
-    // Throwing an error
-    if (callFrame.argumentCount() < 1) {
-        return globalObject.throw("Missing required argument", .{});
-    }
-
-    // Or returning a success value
-    return JSC.JSValue.jsString(globalObject, "Success!");
-}
-```
-
-This pattern allows Zig functions to:
-
-1. Return JavaScript values on success
-2. Throw JavaScript exceptions on error
-3. Propagate errors automatically through the call stack
-
-## Type Safety and Error Handling
-
-The binding system includes robust error handling:
-
-```cpp
-// Example of type checking in generated code
-JSTextDecoder* thisObject = jsDynamicCast<JSTextDecoder*>(callFrame->thisValue());
-if (UNLIKELY(!thisObject)) {
-    scope.throwException(lexicalGlobalObject,
-        Bun::createInvalidThisError(lexicalGlobalObject, callFrame->thisValue(), "TextDecoder"_s));
-    return {};
-}
-```
-
-## Prototypal Inheritance
-
-The binding system creates proper JavaScript prototype chains:
-
-1. **Constructor**: JSTextDecoderConstructor with standard .prototype property
-2. **Prototype**: JSTextDecoderPrototype with methods and properties
-3. **Instances**: Each JSTextDecoder instance with **proto** pointing to prototype
-
-This ensures JavaScript inheritance works as expected:
-
-```cpp
-// From generated code
-void JSTextDecoderConstructor::finishCreation(VM& vm, JSC::JSGlobalObject* globalObject, JSTextDecoderPrototype* prototype)
-{
-    Base::finishCreation(vm, 0, "TextDecoder"_s, PropertyAdditionMode::WithoutStructureTransition);
-
-    // Set up the prototype chain
-    putDirectWithoutTransition(vm, vm.propertyNames->prototype, prototype, PropertyAttribute::DontEnum | PropertyAttribute::DontDelete | PropertyAttribute::ReadOnly);
-    ASSERT(inherits(info()));
-}
-```
-
-## Performance Considerations
-
-The binding system is optimized for performance:
-
-1. **Direct Pointer Access**: JavaScript objects maintain a direct pointer to Zig objects
-2. **Property Caching**: WriteBarrier caching avoids repeated native calls for stable properties
-3. **Memory Management**: JSC garbage collection integrated with Zig memory management
-4. **Type Conversion**: Fast paths for common JavaScript/Zig type conversions
-
-## Creating a New Class Binding
-
-To create a new class binding in Bun:
-
-1. **Define the class interface** in a `.classes.ts` file:
-
-   ```typescript
-   define({
-     name: "MyClass",
-     constructor: true,
-     finalize: true,
-     proto: {
-       myMethod: {
-         args: 1,
-       },
-       myProperty: {
-         getter: true,
-         cache: true,
-       },
-     },
-   });
-   ```
-
-2. **Implement the native functionality** in a `.zig` file:
-
-   ```zig
-   pub const MyClass = struct {
-       // Generated bindings
-       pub const js = JSC.Codegen.JSMyClass;
-       pub const toJS = js.toJS;
-       pub const fromJS = js.fromJS;
-       pub const fromJSDirect = js.fromJSDirect;
-
-       // State
-       value: []const u8,
-
-       pub const new = bun.TrivialNew(@This());
-
-       // Constructor
-       pub fn constructor(
-           globalObject: *JSGlobalObject,
-           callFrame: *JSC.CallFrame,
-       ) bun.JSError!*MyClass {
-           const arg = callFrame.argument(0);
-           // Implementation
-       }
-
-       // Method
-       pub fn myMethod(
-           this: *MyClass,
-           globalObject: *JSGlobalObject,
-           callFrame: *JSC.CallFrame,
-       ) bun.JSError!JSC.JSValue {
-           // Implementation
-       }
-
-       // Getter
-       pub fn getMyProperty(this: *MyClass, globalObject: *JSGlobalObject) JSC.JSValue {
-           return JSC.JSValue.jsString(globalObject, this.value);
-       }
-
-       // Resource cleanup
-       pub fn deinit(this: *MyClass) void {
-           // Clean up resources
-       }
-
-       pub fn finalize(this: *MyClass) void {
-           this.deinit();
-           bun.destroy(this);
-       }
-   };
-   ```
-
-3. **The binding generator** creates all necessary C++ and Zig glue code to connect JavaScript and Zig, including:
-   - C++ class definitions
-   - Method and property bindings
-   - Memory management utilities
-   - GC integration code
-
-## Generated Code Structure
-
-The binding generator produces several components:
-
-### 1. C++ Classes
-
-For each Zig class, the system generates:
-
-- **JS<Class>**: Main wrapper that holds a pointer to the Zig object (`JSTextDecoder`)
-- **JS<Class>Prototype**: Contains methods and properties (`JSTextDecoderPrototype`)
-- **JS<Class>Constructor**: Implementation of the JavaScript constructor (`JSTextDecoderConstructor`)
-
-### 2. C++ Methods and Properties
-
-- **Method Callbacks**: `TextDecoderPrototype__decodeCallback`
-- **Property Getters/Setters**: `TextDecoderPrototype__encodingGetterWrap`
-- **Initialization Functions**: `finishCreation` methods for setting up the class
-
-### 3. Zig Bindings
-
-- **External Function Declarations**:
-
-  ```zig
-  extern fn TextDecoderPrototype__decode(*TextDecoder, *JSC.JSGlobalObject, *JSC.CallFrame) callconv(JSC.conv) JSC.EncodedJSValue;
-  ```
-
-- **Cached Value Accessors**:
-
-  ```zig
-  pub fn encodingGetCached(thisValue: JSC.JSValue) ?JSC.JSValue { ... }
-  pub fn encodingSetCached(thisValue: JSC.JSValue, globalObject: *JSC.JSGlobalObject, value: JSC.JSValue) void { ... }
-  ```
-
-- **Constructor Helpers**:
-  ```zig
-  pub fn create(globalObject: *JSC.JSGlobalObject) bun.JSError!JSC.JSValue { ... }
-  ```
-
-### 4. GC Integration
-
-- **Memory Cost Calculation**: `estimatedSize` method
-- **Child Visitor Methods**: `visitChildrenImpl` and `visitAdditionalChildren`
-- **Heap Analysis**: `analyzeHeap` for debugging memory issues
-
-This architecture makes it possible to implement high-performance native functionality in Zig while exposing a clean, idiomatic JavaScript API to users.
PATCH

echo "Gold patch applied."
