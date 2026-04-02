# Agent Config Files for bun-fd-float-overflow-panic

Repo: oven-sh/bun
Commit: 8f0fd0cf1da17fff23df7133e414cdd1f5ed917e
Files found: 39


---
## .claude/commands/dedupe.md

```
   1 | ---
   2 | allowed-tools: Bash(gh issue view:*), Bash(gh search:*), Bash(gh issue list:*), Bash(gh api:*), Bash(gh issue comment:*)
   3 | description: Find duplicate GitHub issues
   4 | ---
   5 | 
   6 | # Issue deduplication command
   7 | 
   8 | Find up to 3 likely duplicate issues for a given GitHub issue.
   9 | 
  10 | To do this, follow these steps precisely:
  11 | 
  12 | 1. Use an agent to check if the GitHub issue (a) is closed, (b) does not need to be deduped (eg. because it is broad product feedback without a specific solution, or positive feedback), or (c) already has a duplicate detection comment (check for the exact HTML marker `<!-- dedupe-bot:marker -->` in the issue comments - ignore other bot comments). If so, do not proceed.
  13 | 2. Use an agent to view a GitHub issue, and ask the agent to return a summary of the issue
  14 | 3. Then, launch 5 parallel agents to search GitHub for duplicates of this issue, using diverse keywords and search approaches, using the summary from Step 2. **IMPORTANT**: Always scope searches with `repo:owner/repo` to constrain results to the current repository only.
  15 | 4. Next, feed the results from Steps 2 and 3 into another agent, so that it can filter out false positives, that are likely not actually duplicates of the original issue. If there are no duplicates remaining, do not proceed.
  16 | 5. Finally, comment back on the issue with a list of up to three duplicate issues (or zero, if there are no likely duplicates)
  17 | 
  18 | Notes (be sure to tell this to your agents, too):
  19 | 
  20 | - Use `gh` to interact with GitHub, rather than web fetch
  21 | - Do not use other tools, beyond `gh` (eg. don't use other MCP servers, file edit, etc.)
  22 | - Make a todo list first
  23 | - Always scope searches with `repo:owner/repo` to prevent cross-repo false positives
  24 | - For your comment, follow the following format precisely (assuming for this example that you found 3 suspected duplicates):
  25 | 
  26 | ---
  27 | 
  28 | Found 3 possible duplicate issues:
  29 | 
  30 | 1. <link to issue>
  31 | 2. <link to issue>
  32 | 3. <link to issue>
  33 | 
  34 | This issue will be automatically closed as a duplicate in 3 days.
  35 | 
  36 | - If your issue is a duplicate, please close it and 👍 the existing issue instead
  37 | - To prevent auto-closure, add a comment or 👎 this comment
  38 | 
  39 | 🤖 Generated with [Claude Code](https://claude.ai/code)
  40 | 
  41 | <!-- dedupe-bot:marker -->
  42 | 
  43 | ---
```


---
## .claude/commands/find-issues.md

```
   1 | ---
   2 | allowed-tools: Bash(gh pr view:*), Bash(gh pr diff:*), Bash(gh search:*), Bash(gh issue list:*), Bash(gh issue view:*), Bash(gh api:*), Bash(gh pr comment:*)
   3 | description: Find GitHub issues that a PR might fix
   4 | ---
   5 | 
   6 | # Find issues for PR command
   7 | 
   8 | Find open GitHub issues that a pull request might fix. Include all likely matches — do not artificially limit the number of results.
   9 | 
  10 | To do this, follow these steps precisely:
  11 | 
  12 | 1. Use an agent to check if the PR (a) is closed/merged, or (b) already has a related-issues comment (check for the exact HTML marker `<!-- find-issues-bot:marker -->` in the PR comments - ignore other bot comments). If so, do not proceed.
  13 | 2. Use an agent to view the PR title, body, and diff (`gh pr view` and `gh pr diff`), and ask the agent to return a summary of:
  14 |    - What the PR changes (files modified, functions changed, features added/fixed)
  15 |    - Key technical terms, error messages, API names, or module names involved
  16 |    - Any issue numbers already referenced in the PR body or commit messages
  17 | 3. Then, launch 5 parallel agents to search GitHub for open issues that this PR might fix, using diverse keywords and search approaches derived from the summary in Step 2. **IMPORTANT**: Always scope searches with `repo:owner/repo` to constrain results to the current repository only. Each agent should try a different search strategy:
  18 |    - Agent 1: Search using error messages or symptoms described in the diff
  19 |    - Agent 2: Search using feature/module names from the changed files
  20 |    - Agent 3: Search using API names or function names that were modified
  21 |    - Agent 4: Search using keywords from the PR title and description
  22 |    - Agent 5: Search using broader terms related to the area of code changed
  23 | 4. Next, feed the results from Steps 2 and 3 into another agent, so that it can filter out false positives that are likely not actually related to the PR's changes. Exclude issues already referenced in the PR body (e.g. "fixes #123", "closes #456", "resolves #789"). Only keep issues where the PR changes are clearly relevant to the issue. If there are no related issues remaining, do not proceed.
  24 | 5. Finally, comment on the PR with all related open issues found (or zero, if there are no likely matches). Do not cap the number — list every issue that is a likely match.
  25 | 
  26 | Notes (be sure to tell this to your agents, too):
  27 | 
  28 | - Use `gh` to interact with GitHub, rather than web fetch
  29 | - Do not use other tools, beyond `gh` (eg. don't use other MCP servers, file edit, etc.)
  30 | - Make a todo list first
  31 | - Always scope searches with `repo:owner/repo` to prevent cross-repo false positives
  32 | - Only match against **open** issues - do not suggest closed issues
  33 | - Exclude issues that are already linked in the PR description
  34 | - For your comment, follow the following format precisely (assuming for this example that you found 3 related issues):
  35 | 
  36 | ---
  37 | 
  38 | Found 3 issues this PR may fix:
  39 | 
  40 | 1. <link to issue> - <one-line summary of why this PR is relevant>
  41 | 2. <link to issue> - <one-line summary of why this PR is relevant>
  42 | 3. <link to issue> - <one-line summary of why this PR is relevant>
  43 | 
  44 | > If this is helpful, consider adding `Fixes #<number>` to the PR description to auto-close the issue on merge.
  45 | 
  46 | 🤖 Generated with [Claude Code](https://claude.ai/code)
  47 | 
  48 | <!-- find-issues-bot:marker -->
  49 | 
  50 | ---
```


---
## .claude/commands/upgrade-nodejs.md

```
   1 | # Upgrading Bun's Self-Reported Node.js Version
   2 | 
   3 | This guide explains how to upgrade the Node.js version that Bun reports for compatibility with Node.js packages and native addons.
   4 | 
   5 | ## Overview
   6 | 
   7 | Bun reports a Node.js version for compatibility with the Node.js ecosystem. This affects:
   8 | - `process.version` output
   9 | - Node-API (N-API) compatibility
  10 | - Native addon ABI compatibility
  11 | - V8 API compatibility for addons using V8 directly
  12 | 
  13 | ## Files That Always Need Updates
  14 | 
  15 | ### 1. Bootstrap Scripts
  16 | - `scripts/bootstrap.sh` - Update `NODEJS_VERSION=`
  17 | - `scripts/bootstrap.ps1` - Update `$NODEJS_VERSION =`
  18 | 
  19 | ### 2. CMake Configuration
  20 | - `cmake/Options.cmake`
  21 |   - `NODEJS_VERSION` - The Node.js version string (e.g., "24.3.0")
  22 |   - `NODEJS_ABI_VERSION` - The ABI version number (find using command below)
  23 | 
  24 | ### 3. Version Strings
  25 | - `src/bun.js/bindings/BunProcess.cpp`
  26 |   - Update `Bun__versions_node` with the Node.js version
  27 |   - Update `Bun__versions_v8` with the V8 version (find using command below)
  28 | 
  29 | ### 4. N-API Version
  30 | - `src/napi/js_native_api.h`
  31 |   - Update `NAPI_VERSION` define (check Node.js release notes)
  32 | 
  33 | ## Files That May Need Updates
  34 | 
  35 | Only check these if the build fails or tests crash after updating version numbers:
  36 | - V8 compatibility files in `src/bun.js/bindings/v8/` (if V8 API changed)
  37 | - Test files (if Node.js requires newer C++ standard)
  38 | 
  39 | ## Quick Commands to Find Version Info
  40 | 
  41 | ```bash
  42 | # Get latest Node.js version info
  43 | curl -s https://nodejs.org/dist/index.json | jq '.[0]'
  44 | 
  45 | # Get V8 version for a specific Node.js version (replace v24.3.0)
  46 | curl -s https://nodejs.org/dist/v24.3.0/node-v24.3.0-headers.tar.gz | tar -xzO node-v24.3.0/include/node/node_version.h | grep V8_VERSION
  47 | 
  48 | # Get ABI version for a specific Node.js version
  49 | curl -s https://nodejs.org/dist/v24.3.0/node-v24.3.0-headers.tar.gz | tar -xzO node-v24.3.0/include/node/node_version.h | grep NODE_MODULE_VERSION
  50 | 
  51 | # Or use the ABI registry
  52 | curl -s https://raw.githubusercontent.com/nodejs/node/main/doc/abi_version_registry.json | jq '.NODE_MODULE_VERSION."<version>"'
  53 | ```
  54 | 
  55 | ## Update Process
  56 | 
  57 | 1. **Gather version info** using the commands above
  58 | 2. **Update the required files** listed in the sections above
  59 | 3. **Build and test**:
  60 |    ```bash
  61 |    bun bd
  62 |    bun bd -e "console.log(process.version)"
  63 |    bun bd -e "console.log(process.versions.v8)"
  64 |    bun bd test test/v8/v8.test.ts
  65 |    bun bd test test/napi/napi.test.ts
  66 |    ```
  67 | 
  68 | 4. **Check for V8 API changes** only if build fails or tests crash:
  69 |    - Compare v8-function-callback.h between versions
  70 |    - Check v8-internal.h for Isolate size changes
  71 |    - Look for new required APIs in build errors
  72 | 
  73 | ## If Build Fails or Tests Crash
  74 | 
  75 | The V8 API rarely has breaking changes between minor Node.js versions. If you encounter issues:
  76 | 1. Check build errors for missing symbols or type mismatches
  77 | 2. Compare V8 headers between old and new Node.js versions
  78 | 3. Most issues can be resolved by implementing missing functions or adjusting structures
  79 | 
  80 | ## Testing Checklist
  81 | 
  82 | - [ ] `process.version` returns correct version
  83 | - [ ] `process.versions.v8` returns correct V8 version  
  84 | - [ ] `process.config.variables.node_module_version` returns correct ABI
  85 | - [ ] V8 tests pass
  86 | - [ ] N-API tests pass
  87 | 
  88 | ## Notes
  89 | 
  90 | - Most upgrades only require updating version numbers
  91 | - Major V8 version changes (rare) may require API updates
  92 | - The V8 shim implements only APIs used by common native addons
```


---
## .claude/commands/upgrade-webkit.md

```
   1 | Upgrade Bun's Webkit fork to the latest upstream version of Webkit.
   2 | 
   3 | To do that:
   4 | 
   5 | - cd vendor/WebKit
   6 | - git fetch upstream
   7 | - git merge upstream main
   8 | - Fix the merge conflicts
   9 | - bun build.ts debug
  10 | - While it compiles, in another task review the JSC commits between the last version of Webkit and the new version. Write up a summary of the webkit changes in a file called "webkit-changes.md"
  11 | - bun run build:local (build a build of Bun with the new Webkit, make sure it compiles)
  12 | - After making sure it compiles, run some code to make sure things work. something like ./build/debug-local/bun-debug --print '42' should be all you need
  13 | - cd vendor/WebKit
  14 | - git commit -am "Upgrade Webkit to the latest version"
  15 | - git push
  16 | - get the commit SHA in the vendor/WebKit directory of your new commit
  17 | - cd ../../ (back to bun)
  18 | - Update WEBKIT_VERSION in cmake/tools/SetupWebKit.cmake to the commit SHA of your new commit
  19 | - git checkout -b bun/webkit-upgrade-<commit-sha>
  20 | - commit + push (without adding the webkit-changes.md file)
  21 | - create PR titled "Upgrade Webkit to the <commit-sha>", paste your webkit-changes.md into the PR description
  22 | - delete the webkit-changes.md file
  23 | 
  24 | Things to check for a successful upgrade:
  25 | - Did JSType in vendor/WebKit/Source/JavaScriptCore have any recent changes? Does the enum values align with whats present in src/bun.js/bindings/JSType.zig?
  26 | - Were there any changes to the webcore code generator? If there are C++ compilation errors, check for differences in some of the generated code in like vendor/WebKit/source/WebCore/bindings/scripts/test/JS/
```


---
## .claude/skills/implementing-jsc-classes-cpp/SKILL.md

```
   1 | ---
   2 | name: implementing-jsc-classes-cpp
   3 | description: Implements JavaScript classes in C++ using JavaScriptCore. Use when creating new JS classes with C++ bindings, prototypes, or constructors.
   4 | ---
   5 | 
   6 | # Implementing JavaScript Classes in C++
   7 | 
   8 | ## Class Structure
   9 | 
  10 | For publicly accessible Constructor and Prototype, create 3 classes:
  11 | 
  12 | 1. **`class Foo : public JSC::DestructibleObject`** - if C++ fields exist; otherwise use `JSC::constructEmptyObject` with `putDirectOffset`
  13 | 2. **`class FooPrototype : public JSC::JSNonFinalObject`**
  14 | 3. **`class FooConstructor : public JSC::InternalFunction`**
  15 | 
  16 | No public constructor? Only Prototype and class needed.
  17 | 
  18 | ## Iso Subspaces
  19 | 
  20 | Classes with C++ fields need subspaces in:
  21 | 
  22 | - `src/bun.js/bindings/webcore/DOMClientIsoSubspaces.h`
  23 | - `src/bun.js/bindings/webcore/DOMIsoSubspaces.h`
  24 | 
  25 | ```cpp
  26 | template<typename MyClassT, JSC::SubspaceAccess mode>
  27 | static JSC::GCClient::IsoSubspace* subspaceFor(JSC::VM& vm) {
  28 |     if constexpr (mode == JSC::SubspaceAccess::Concurrently)
  29 |         return nullptr;
  30 |     return WebCore::subspaceForImpl<MyClassT, WebCore::UseCustomHeapCellType::No>(
  31 |         vm,
  32 |         [](auto& spaces) { return spaces.m_clientSubspaceForMyClassT.get(); },
  33 |         [](auto& spaces, auto&& space) { spaces.m_clientSubspaceForMyClassT = std::forward<decltype(space)>(space); },
  34 |         [](auto& spaces) { return spaces.m_subspaceForMyClassT.get(); },
  35 |         [](auto& spaces, auto&& space) { spaces.m_subspaceForMyClassT = std::forward<decltype(space)>(space); });
  36 | }
  37 | ```
  38 | 
  39 | ## Property Definitions
  40 | 
  41 | ```cpp
  42 | static JSC_DECLARE_HOST_FUNCTION(jsFooProtoFuncMethod);
  43 | static JSC_DECLARE_CUSTOM_GETTER(jsFooGetter_property);
  44 | 
  45 | static const HashTableValue JSFooPrototypeTableValues[] = {
  46 |     { "property"_s, static_cast<unsigned>(PropertyAttribute::ReadOnly | PropertyAttribute::CustomAccessor), NoIntrinsic, { HashTableValue::GetterSetterType, jsFooGetter_property, 0 } },
  47 |     { "method"_s, static_cast<unsigned>(PropertyAttribute::Function), NoIntrinsic, { HashTableValue::NativeFunctionType, jsFooProtoFuncMethod, 1 } },
  48 | };
  49 | ```
  50 | 
  51 | ## Prototype Class
  52 | 
  53 | ```cpp
  54 | class JSFooPrototype final : public JSC::JSNonFinalObject {
  55 | public:
  56 |     using Base = JSC::JSNonFinalObject;
  57 |     static constexpr unsigned StructureFlags = Base::StructureFlags;
  58 | 
  59 |     static JSFooPrototype* create(JSC::VM& vm, JSC::JSGlobalObject* globalObject, JSC::Structure* structure) {
  60 |         JSFooPrototype* prototype = new (NotNull, allocateCell<JSFooPrototype>(vm)) JSFooPrototype(vm, structure);
  61 |         prototype->finishCreation(vm);
  62 |         return prototype;
  63 |     }
  64 | 
  65 |     template<typename, JSC::SubspaceAccess>
  66 |     static JSC::GCClient::IsoSubspace* subspaceFor(JSC::VM& vm) { return &vm.plainObjectSpace(); }
  67 | 
  68 |     DECLARE_INFO;
  69 | 
  70 |     static JSC::Structure* createStructure(JSC::VM& vm, JSC::JSGlobalObject* globalObject, JSC::JSValue prototype) {
  71 |         auto* structure = JSC::Structure::create(vm, globalObject, prototype, JSC::TypeInfo(JSC::ObjectType, StructureFlags), info());
  72 |         structure->setMayBePrototype(true);
  73 |         return structure;
  74 |     }
  75 | 
  76 | private:
  77 |     JSFooPrototype(JSC::VM& vm, JSC::Structure* structure) : Base(vm, structure) {}
  78 |     void finishCreation(JSC::VM& vm);
  79 | };
  80 | 
  81 | void JSFooPrototype::finishCreation(VM& vm) {
  82 |     Base::finishCreation(vm);
  83 |     reifyStaticProperties(vm, JSFoo::info(), JSFooPrototypeTableValues, *this);
  84 |     JSC_TO_STRING_TAG_WITHOUT_TRANSITION();
  85 | }
  86 | ```
  87 | 
  88 | ## Getter/Setter/Function Definitions
  89 | 
  90 | ```cpp
  91 | // Getter
  92 | JSC_DEFINE_CUSTOM_GETTER(jsFooGetter_prop, (JSGlobalObject* globalObject, EncodedJSValue thisValue, PropertyName)) {
  93 |     VM& vm = globalObject->vm();
  94 |     auto scope = DECLARE_THROW_SCOPE(vm);
  95 |     JSFoo* thisObject = jsDynamicCast<JSFoo*>(JSValue::decode(thisValue));
  96 |     if (UNLIKELY(!thisObject)) {
  97 |         Bun::throwThisTypeError(*globalObject, scope, "JSFoo"_s, "prop"_s);
  98 |         return {};
  99 |     }
 100 |     return JSValue::encode(jsBoolean(thisObject->value()));
 101 | }
 102 | 
 103 | // Function
 104 | JSC_DEFINE_HOST_FUNCTION(jsFooProtoFuncMethod, (JSGlobalObject* globalObject, CallFrame* callFrame)) {
 105 |     VM& vm = globalObject->vm();
 106 |     auto scope = DECLARE_THROW_SCOPE(vm);
 107 |     auto* thisObject = jsDynamicCast<JSFoo*>(callFrame->thisValue());
 108 |     if (UNLIKELY(!thisObject)) {
 109 |         Bun::throwThisTypeError(*globalObject, scope, "Foo"_s, "method"_s);
 110 |         return {};
 111 |     }
 112 |     return JSValue::encode(thisObject->doSomething(vm, globalObject));
 113 | }
 114 | ```
 115 | 
 116 | ## Constructor Class
 117 | 
 118 | ```cpp
 119 | class JSFooConstructor final : public JSC::InternalFunction {
 120 | public:
 121 |     using Base = JSC::InternalFunction;
 122 |     static constexpr unsigned StructureFlags = Base::StructureFlags;
 123 | 
 124 |     static JSFooConstructor* create(JSC::VM& vm, JSC::Structure* structure, JSC::JSObject* prototype) {
 125 |         JSFooConstructor* constructor = new (NotNull, JSC::allocateCell<JSFooConstructor>(vm)) JSFooConstructor(vm, structure);
 126 |         constructor->finishCreation(vm, prototype);
 127 |         return constructor;
 128 |     }
 129 | 
 130 |     DECLARE_INFO;
 131 | 
 132 |     template<typename CellType, JSC::SubspaceAccess>
 133 |     static JSC::GCClient::IsoSubspace* subspaceFor(JSC::VM& vm) { return &vm.internalFunctionSpace(); }
 134 | 
 135 |     static JSC::Structure* createStructure(JSC::VM& vm, JSC::JSGlobalObject* globalObject, JSC::JSValue prototype) {
 136 |         return JSC::Structure::create(vm, globalObject, prototype, JSC::TypeInfo(JSC::InternalFunctionType, StructureFlags), info());
 137 |     }
 138 | 
 139 | private:
 140 |     JSFooConstructor(JSC::VM& vm, JSC::Structure* structure) : Base(vm, structure, callFoo, constructFoo) {}
 141 | 
 142 |     void finishCreation(JSC::VM& vm, JSC::JSObject* prototype) {
 143 |         Base::finishCreation(vm, 0, "Foo"_s);
 144 |         putDirectWithoutTransition(vm, vm.propertyNames->prototype, prototype, JSC::PropertyAttribute::DontEnum | JSC::PropertyAttribute::DontDelete | JSC::PropertyAttribute::ReadOnly);
 145 |     }
 146 | };
 147 | ```
 148 | 
 149 | ## Structure Caching
 150 | 
 151 | Add to `ZigGlobalObject.h`:
 152 | 
 153 | ```cpp
 154 | JSC::LazyClassStructure m_JSFooClassStructure;
 155 | ```
 156 | 
 157 | Initialize in `ZigGlobalObject.cpp`:
 158 | 
 159 | ```cpp
 160 | m_JSFooClassStructure.initLater([](LazyClassStructure::Initializer& init) {
 161 |     Bun::initJSFooClassStructure(init);
 162 | });
 163 | ```
 164 | 
 165 | Visit in `visitChildrenImpl`:
 166 | 
 167 | ```cpp
 168 | m_JSFooClassStructure.visit(visitor);
 169 | ```
 170 | 
 171 | ## Expose to Zig
 172 | 
 173 | ```cpp
 174 | extern "C" JSC::EncodedJSValue Bun__JSFooConstructor(Zig::GlobalObject* globalObject) {
 175 |     return JSValue::encode(globalObject->m_JSFooClassStructure.constructor(globalObject));
 176 | }
 177 | 
 178 | extern "C" EncodedJSValue Bun__Foo__toJS(Zig::GlobalObject* globalObject, Foo* foo) {
 179 |     auto* structure = globalObject->m_JSFooClassStructure.get(globalObject);
 180 |     return JSValue::encode(JSFoo::create(globalObject->vm(), structure, globalObject, WTFMove(foo)));
 181 | }
 182 | ```
 183 | 
 184 | Include `#include "root.h"` at the top of C++ files.
```


---
## .claude/skills/implementing-jsc-classes-zig/SKILL.md

```
   1 | ---
   2 | name: implementing-jsc-classes-zig
   3 | description: Creates JavaScript classes using Bun's Zig bindings generator (.classes.ts). Use when implementing new JS APIs in Zig with JSC integration.
   4 | ---
   5 | 
   6 | # Bun's JavaScriptCore Class Bindings Generator
   7 | 
   8 | Bridge JavaScript and Zig through `.classes.ts` definitions and Zig implementations.
   9 | 
  10 | ## Architecture
  11 | 
  12 | 1. **Zig Implementation** (.zig files)
  13 | 2. **JavaScript Interface Definition** (.classes.ts files)
  14 | 3. **Generated Code** (C++/Zig files connecting them)
  15 | 
  16 | ## Class Definition (.classes.ts)
  17 | 
  18 | ```typescript
  19 | define({
  20 |   name: "TextDecoder",
  21 |   constructor: true,
  22 |   JSType: "object",
  23 |   finalize: true,
  24 |   proto: {
  25 |     decode: { args: 1 },
  26 |     encoding: { getter: true, cache: true },
  27 |     fatal: { getter: true },
  28 |   },
  29 | });
  30 | ```
  31 | 
  32 | Options:
  33 | 
  34 | - `name`: Class name
  35 | - `constructor`: Has public constructor
  36 | - `JSType`: "object", "function", etc.
  37 | - `finalize`: Needs cleanup
  38 | - `proto`: Properties/methods
  39 | - `cache`: Cache property values via WriteBarrier
  40 | 
  41 | ## Zig Implementation
  42 | 
  43 | ```zig
  44 | pub const TextDecoder = struct {
  45 |     pub const js = JSC.Codegen.JSTextDecoder;
  46 |     pub const toJS = js.toJS;
  47 |     pub const fromJS = js.fromJS;
  48 |     pub const fromJSDirect = js.fromJSDirect;
  49 | 
  50 |     encoding: []const u8,
  51 |     fatal: bool,
  52 | 
  53 |     pub fn constructor(
  54 |         globalObject: *JSGlobalObject,
  55 |         callFrame: *JSC.CallFrame,
  56 |     ) bun.JSError!*TextDecoder {
  57 |         return bun.new(TextDecoder, .{ .encoding = "utf-8", .fatal = false });
  58 |     }
  59 | 
  60 |     pub fn decode(
  61 |         this: *TextDecoder,
  62 |         globalObject: *JSGlobalObject,
  63 |         callFrame: *JSC.CallFrame,
  64 |     ) bun.JSError!JSC.JSValue {
  65 |         const args = callFrame.arguments();
  66 |         if (args.len < 1 or args.ptr[0].isUndefinedOrNull()) {
  67 |             return globalObject.throw("Input cannot be null", .{});
  68 |         }
  69 |         return JSC.JSValue.jsString(globalObject, "result");
  70 |     }
  71 | 
  72 |     pub fn getEncoding(this: *TextDecoder, globalObject: *JSGlobalObject) JSC.JSValue {
  73 |         return JSC.JSValue.createStringFromUTF8(globalObject, this.encoding);
  74 |     }
  75 | 
  76 |     fn deinit(this: *TextDecoder) void {
  77 |         // Release resources
  78 |     }
  79 | 
  80 |     pub fn finalize(this: *TextDecoder) void {
  81 |         this.deinit();
  82 |         bun.destroy(this);
  83 |     }
  84 | };
  85 | ```
  86 | 
  87 | **Key patterns:**
  88 | 
  89 | - Use `bun.JSError!JSValue` return type for error handling
  90 | - Use `globalObject` not `ctx`
  91 | - `deinit()` for cleanup, `finalize()` called by GC
  92 | - Update `src/bun.js/bindings/generated_classes_list.zig`
  93 | 
  94 | ## CallFrame Access
  95 | 
  96 | ```zig
  97 | const args = callFrame.arguments();
  98 | const first_arg = args.ptr[0];  // Access as slice
  99 | const argCount = args.len;
 100 | const thisValue = callFrame.thisValue();
 101 | ```
 102 | 
 103 | ## Property Caching
 104 | 
 105 | For `cache: true` properties, generated accessors:
 106 | 
 107 | ```zig
 108 | // Get cached value
 109 | pub fn encodingGetCached(thisValue: JSC.JSValue) ?JSC.JSValue {
 110 |     const result = TextDecoderPrototype__encodingGetCachedValue(thisValue);
 111 |     if (result == .zero) return null;
 112 |     return result;
 113 | }
 114 | 
 115 | // Set cached value
 116 | pub fn encodingSetCached(thisValue: JSC.JSValue, globalObject: *JSC.JSGlobalObject, value: JSC.JSValue) void {
 117 |     TextDecoderPrototype__encodingSetCachedValue(thisValue, globalObject, value);
 118 | }
 119 | ```
 120 | 
 121 | ## Error Handling
 122 | 
 123 | ```zig
 124 | pub fn method(this: *MyClass, globalObject: *JSGlobalObject, callFrame: *JSC.CallFrame) bun.JSError!JSC.JSValue {
 125 |     const args = callFrame.arguments();
 126 |     if (args.len < 1) {
 127 |         return globalObject.throw("Missing required argument", .{});
 128 |     }
 129 |     return JSC.JSValue.jsString(globalObject, "Success!");
 130 | }
 131 | ```
 132 | 
 133 | ## Memory Management
 134 | 
 135 | ```zig
 136 | pub fn deinit(this: *TextDecoder) void {
 137 |     this._encoding.deref();
 138 |     if (this.buffer) |buffer| {
 139 |         bun.default_allocator.free(buffer);
 140 |     }
 141 | }
 142 | 
 143 | pub fn finalize(this: *TextDecoder) void {
 144 |     JSC.markBinding(@src());
 145 |     this.deinit();
 146 |     bun.default_allocator.destroy(this);
 147 | }
 148 | ```
 149 | 
 150 | ## Creating a New Binding
 151 | 
 152 | 1. Define interface in `.classes.ts`:
 153 | 
 154 | ```typescript
 155 | define({
 156 |   name: "MyClass",
 157 |   constructor: true,
 158 |   finalize: true,
 159 |   proto: {
 160 |     myMethod: { args: 1 },
 161 |     myProperty: { getter: true, cache: true },
 162 |   },
 163 | });
 164 | ```
 165 | 
 166 | 2. Implement in `.zig`:
 167 | 
 168 | ```zig
 169 | pub const MyClass = struct {
 170 |     pub const js = JSC.Codegen.JSMyClass;
 171 |     pub const toJS = js.toJS;
 172 |     pub const fromJS = js.fromJS;
 173 | 
 174 |     value: []const u8,
 175 | 
 176 |     pub const new = bun.TrivialNew(@This());
 177 | 
 178 |     pub fn constructor(globalObject: *JSGlobalObject, callFrame: *JSC.CallFrame) bun.JSError!*MyClass {
 179 |         return MyClass.new(.{ .value = "" });
 180 |     }
 181 | 
 182 |     pub fn myMethod(this: *MyClass, globalObject: *JSGlobalObject, callFrame: *JSC.CallFrame) bun.JSError!JSC.JSValue {
 183 |         return JSC.JSValue.jsUndefined();
 184 |     }
 185 | 
 186 |     pub fn getMyProperty(this: *MyClass, globalObject: *JSGlobalObject) JSC.JSValue {
 187 |         return JSC.JSValue.jsString(globalObject, this.value);
 188 |     }
 189 | 
 190 |     pub fn deinit(this: *MyClass) void {}
 191 | 
 192 |     pub fn finalize(this: *MyClass) void {
 193 |         this.deinit();
 194 |         bun.destroy(this);
 195 |     }
 196 | };
 197 | ```
 198 | 
 199 | 3. Add to `src/bun.js/bindings/generated_classes_list.zig`
 200 | 
 201 | ## Generated Components
 202 | 
 203 | - **C++ Classes**: `JSMyClass`, `JSMyClassPrototype`, `JSMyClassConstructor`
 204 | - **Method Bindings**: `MyClassPrototype__myMethodCallback`
 205 | - **Property Accessors**: `MyClassPrototype__myPropertyGetterWrap`
 206 | - **Zig Bindings**: External function declarations, cached value accessors
```


---
## .claude/skills/writing-bundler-tests/SKILL.md

```
   1 | ---
   2 | name: writing-bundler-tests
   3 | description: Guides writing bundler tests using itBundled/expectBundled in test/bundler/. Use when creating or modifying bundler, transpiler, or code transformation tests.
   4 | ---
   5 | 
   6 | # Writing Bundler Tests
   7 | 
   8 | Bundler tests use `itBundled()` from `test/bundler/expectBundled.ts` to test Bun's bundler.
   9 | 
  10 | ## Basic Usage
  11 | 
  12 | ```typescript
  13 | import { describe } from "bun:test";
  14 | import { itBundled, dedent } from "./expectBundled";
  15 | 
  16 | describe("bundler", () => {
  17 |   itBundled("category/TestName", {
  18 |     files: {
  19 |       "index.js": `console.log("hello");`,
  20 |     },
  21 |     run: {
  22 |       stdout: "hello",
  23 |     },
  24 |   });
  25 | });
  26 | ```
  27 | 
  28 | Test ID format: `category/TestName` (e.g., `banner/CommentBanner`, `minify/Empty`)
  29 | 
  30 | ## File Setup
  31 | 
  32 | ```typescript
  33 | {
  34 |   files: {
  35 |     "index.js": `console.log("test");`,
  36 |     "lib.ts": `export const foo = 123;`,
  37 |     "nested/file.js": `export default {};`,
  38 |   },
  39 |   entryPoints: ["index.js"],  // defaults to first file
  40 |   runtimeFiles: {             // written AFTER bundling
  41 |     "extra.js": `console.log("added later");`,
  42 |   },
  43 | }
  44 | ```
  45 | 
  46 | ## Bundler Options
  47 | 
  48 | ```typescript
  49 | {
  50 |   outfile: "/out.js",
  51 |   outdir: "/out",
  52 |   format: "esm" | "cjs" | "iife",
  53 |   target: "bun" | "browser" | "node",
  54 | 
  55 |   // Minification
  56 |   minifyWhitespace: true,
  57 |   minifyIdentifiers: true,
  58 |   minifySyntax: true,
  59 | 
  60 |   // Code manipulation
  61 |   banner: "// copyright",
  62 |   footer: "// end",
  63 |   define: { "PROD": "true" },
  64 |   external: ["lodash"],
  65 | 
  66 |   // Advanced
  67 |   sourceMap: "inline" | "external",
  68 |   splitting: true,
  69 |   treeShaking: true,
  70 |   drop: ["console"],
  71 | }
  72 | ```
  73 | 
  74 | ## Runtime Verification
  75 | 
  76 | ```typescript
  77 | {
  78 |   run: {
  79 |     stdout: "expected output",      // exact match
  80 |     stdout: /regex/,                // pattern match
  81 |     partialStdout: "contains this", // substring
  82 |     stderr: "error output",
  83 |     exitCode: 1,
  84 |     env: { NODE_ENV: "production" },
  85 |     runtime: "bun" | "node",
  86 | 
  87 |     // Runtime errors
  88 |     error: "ReferenceError: x is not defined",
  89 |   },
  90 | }
  91 | ```
  92 | 
  93 | ## Bundle Errors/Warnings
  94 | 
  95 | ```typescript
  96 | {
  97 |   bundleErrors: {
  98 |     "/file.js": ["error message 1", "error message 2"],
  99 |   },
 100 |   bundleWarnings: {
 101 |     "/file.js": ["warning message"],
 102 |   },
 103 | }
 104 | ```
 105 | 
 106 | ## Dead Code Elimination (DCE)
 107 | 
 108 | Add markers in source code:
 109 | 
 110 | ```javascript
 111 | // KEEP - this should survive
 112 | const used = 1;
 113 | 
 114 | // REMOVE - this should be eliminated
 115 | const unused = 2;
 116 | ```
 117 | 
 118 | ```typescript
 119 | {
 120 |   dce: true,
 121 |   dceKeepMarkerCount: 5,  // expected KEEP markers
 122 | }
 123 | ```
 124 | 
 125 | ## Capture Pattern
 126 | 
 127 | Verify exact transpilation with `capture()`:
 128 | 
 129 | ```typescript
 130 | itBundled("string/Folding", {
 131 |   files: {
 132 |     "index.ts": `capture(\`\${1 + 1}\`);`,
 133 |   },
 134 |   capture: ['"2"'], // expected captured value
 135 |   minifySyntax: true,
 136 | });
 137 | ```
 138 | 
 139 | ## Post-Bundle Assertions
 140 | 
 141 | ```typescript
 142 | {
 143 |   onAfterBundle(api) {
 144 |     api.expectFile("out.js").toContain("console.log");
 145 |     api.assertFileExists("out.js");
 146 | 
 147 |     const content = api.readFile("out.js");
 148 |     expect(content).toMatchSnapshot();
 149 | 
 150 |     const values = api.captureFile("out.js");
 151 |     expect(values).toEqual(["2"]);
 152 |   },
 153 | }
 154 | ```
 155 | 
 156 | ## Common Patterns
 157 | 
 158 | **Simple output verification:**
 159 | 
 160 | ```typescript
 161 | itBundled("banner/Comment", {
 162 |   banner: "// copyright",
 163 |   files: { "a.js": `console.log("Hello")` },
 164 |   onAfterBundle(api) {
 165 |     api.expectFile("out.js").toContain("// copyright");
 166 |   },
 167 | });
 168 | ```
 169 | 
 170 | **Multi-file CJS/ESM interop:**
 171 | 
 172 | ```typescript
 173 | itBundled("cjs/ImportSyntax", {
 174 |   files: {
 175 |     "entry.js": `import lib from './lib.cjs'; console.log(lib);`,
 176 |     "lib.cjs": `exports.foo = 'bar';`,
 177 |   },
 178 |   run: { stdout: '{"foo":"bar"}' },
 179 | });
 180 | ```
 181 | 
 182 | **Error handling:**
 183 | 
 184 | ```typescript
 185 | itBundled("edgecase/InvalidLoader", {
 186 |   files: { "index.js": `...` },
 187 |   bundleErrors: {
 188 |     "index.js": ["Unsupported loader type"],
 189 |   },
 190 | });
 191 | ```
 192 | 
 193 | ## Test Organization
 194 | 
 195 | ```text
 196 | test/bundler/
 197 | ├── bundler_banner.test.ts
 198 | ├── bundler_string.test.ts
 199 | ├── bundler_minify.test.ts
 200 | ├── bundler_cjs.test.ts
 201 | ├── bundler_edgecase.test.ts
 202 | ├── bundler_splitting.test.ts
 203 | ├── css/
 204 | ├── transpiler/
 205 | └── expectBundled.ts
 206 | ```
 207 | 
 208 | ## Running Tests
 209 | 
 210 | ```bash
 211 | bun bd test test/bundler/bundler_banner.test.ts
 212 | BUN_BUNDLER_TEST_FILTER="banner/Comment" bun bd test bundler_banner.test.ts
 213 | BUN_BUNDLER_TEST_DEBUG=1 bun bd test bundler_minify.test.ts
 214 | ```
 215 | 
 216 | ## Key Points
 217 | 
 218 | - Use `dedent` for readable multi-line code
 219 | - File paths are relative (e.g., `/index.js`)
 220 | - Use `capture()` to verify exact transpilation results
 221 | - Use `.toMatchSnapshot()` for complex outputs
 222 | - Pass array to `run` for multiple test scenarios
```


---
## .claude/skills/writing-dev-server-tests/SKILL.md

```
   1 | ---
   2 | name: writing-dev-server-tests
   3 | description: Guides writing HMR/Dev Server tests in test/bake/. Use when creating or modifying dev server, hot reloading, or bundling tests.
   4 | ---
   5 | 
   6 | # Writing HMR/Dev Server Tests
   7 | 
   8 | Dev server tests validate hot-reloading robustness and reliability.
   9 | 
  10 | ## File Structure
  11 | 
  12 | - `test/bake/bake-harness.ts` - shared utilities: `devTest`, `prodTest`, `devAndProductionTest`, `Dev` class, `Client` class
  13 | - `test/bake/client-fixture.mjs` - subprocess for `Client` (page loading, IPC queries)
  14 | - `test/bake/dev/*.test.ts` - dev server and hot reload tests
  15 | - `test/bake/dev-and-prod.ts` - tests running on both dev and production mode
  16 | 
  17 | ## Test Categories
  18 | 
  19 | - `bundle.test.ts` - DevServer-specific bundling bugs
  20 | - `css.test.ts` - CSS bundling issues
  21 | - `plugins.test.ts` - development mode plugins
  22 | - `ecosystem.test.ts` - library compatibility (prefer concrete bugs over full package tests)
  23 | - `esm.test.ts` - ESM features in development
  24 | - `html.test.ts` - HTML file handling
  25 | - `react-spa.test.ts` - React, react-refresh transform, server components
  26 | - `sourcemap.test.ts` - source map correctness
  27 | 
  28 | ## devTest Basics
  29 | 
  30 | ```ts
  31 | import { devTest, emptyHtmlFile } from "../bake-harness";
  32 | 
  33 | devTest("html file is watched", {
  34 |   files: {
  35 |     "index.html": emptyHtmlFile({
  36 |       scripts: ["/script.ts"],
  37 |       body: "<h1>Hello</h1>",
  38 |     }),
  39 |     "script.ts": `console.log("hello");`,
  40 |   },
  41 |   async test(dev) {
  42 |     await dev.fetch("/").expect.toInclude("<h1>Hello</h1>");
  43 |     await dev.patch("index.html", { find: "Hello", replace: "World" });
  44 |     await dev.fetch("/").expect.toInclude("<h1>World</h1>");
  45 | 
  46 |     await using c = await dev.client("/");
  47 |     await c.expectMessage("hello");
  48 | 
  49 |     await c.expectReload(async () => {
  50 |       await dev.patch("index.html", { find: "World", replace: "Bar" });
  51 |     });
  52 |     await c.expectMessage("hello");
  53 |   },
  54 | });
  55 | ```
  56 | 
  57 | ## Key APIs
  58 | 
  59 | - **`files`**: Initial filesystem state
  60 | - **`dev.fetch()`**: HTTP requests
  61 | - **`dev.client()`**: Opens browser instance
  62 | - **`dev.write/patch/delete`**: Filesystem mutations (wait for hot-reload automatically)
  63 | - **`c.expectMessage()`**: Assert console.log output
  64 | - **`c.expectReload()`**: Wrap code that causes hard reload
  65 | 
  66 | **Important**: Use `dev.write/patch/delete` instead of `node:fs` - they wait for hot-reload.
  67 | 
  68 | ## Testing Errors
  69 | 
  70 | ```ts
  71 | devTest("import then create", {
  72 |   files: {
  73 |     "index.html": `<!DOCTYPE html><html><head></head><body><script type="module" src="/script.ts"></script></body></html>`,
  74 |     "script.ts": `import data from "./data"; console.log(data);`,
  75 |   },
  76 |   async test(dev) {
  77 |     const c = await dev.client("/", {
  78 |       errors: ['script.ts:1:18: error: Could not resolve: "./data"'],
  79 |     });
  80 |     await c.expectReload(async () => {
  81 |       await dev.write("data.ts", "export default 'data';");
  82 |     });
  83 |     await c.expectMessage("data");
  84 |   },
  85 | });
  86 | ```
  87 | 
  88 | Specify expected errors with the `errors` option:
  89 | 
  90 | ```ts
  91 | await dev.delete("other.ts", {
  92 |   errors: ['index.ts:1:16: error: Could not resolve: "./other"'],
  93 | });
  94 | ```
```


---
## .claude/skills/zig-system-calls/SKILL.md

```
   1 | ---
   2 | name: zig-system-calls
   3 | description: Guides using bun.sys for system calls and file I/O in Zig. Use when implementing file operations instead of std.fs or std.posix.
   4 | ---
   5 | 
   6 | # System Calls & File I/O in Zig
   7 | 
   8 | Use `bun.sys` instead of `std.fs` or `std.posix` for cross-platform syscalls with proper error handling.
   9 | 
  10 | ## bun.sys.File (Preferred)
  11 | 
  12 | For most file operations, use the `bun.sys.File` wrapper:
  13 | 
  14 | ```zig
  15 | const File = bun.sys.File;
  16 | 
  17 | const file = switch (File.open(path, bun.O.RDWR, 0o644)) {
  18 |     .result => |f| f,
  19 |     .err => |err| return .{ .err = err },
  20 | };
  21 | defer file.close();
  22 | 
  23 | // Read/write
  24 | _ = try file.read(buffer).unwrap();
  25 | _ = try file.writeAll(data).unwrap();
  26 | 
  27 | // Get file info
  28 | const stat = try file.stat().unwrap();
  29 | const size = try file.getEndPos().unwrap();
  30 | 
  31 | // std.io compatible
  32 | const reader = file.reader();
  33 | const writer = file.writer();
  34 | ```
  35 | 
  36 | ### Complete Example
  37 | 
  38 | ```zig
  39 | const File = bun.sys.File;
  40 | 
  41 | pub fn writeFile(path: [:0]const u8, data: []const u8) File.WriteError!void {
  42 |     const file = switch (File.open(path, bun.O.WRONLY | bun.O.CREAT | bun.O.TRUNC, 0o664)) {
  43 |         .result => |f| f,
  44 |         .err => |err| return err.toError(),
  45 |     };
  46 |     defer file.close();
  47 | 
  48 |     _ = switch (file.writeAll(data)) {
  49 |         .result => {},
  50 |         .err => |err| return err.toError(),
  51 |     };
  52 | }
  53 | ```
  54 | 
  55 | ## Why bun.sys?
  56 | 
  57 | | Aspect      | bun.sys                          | std.fs/std.posix    |
  58 | | ----------- | -------------------------------- | ------------------- |
  59 | | Return Type | `Maybe(T)` with detailed Error   | Generic error union |
  60 | | Windows     | Full support with libuv fallback | Limited/POSIX-only  |
  61 | | Error Info  | errno, syscall tag, path, fd     | errno only          |
  62 | | EINTR       | Automatic retry                  | Manual handling     |
  63 | 
  64 | ## Error Handling with Maybe(T)
  65 | 
  66 | `bun.sys` functions return `Maybe(T)` - a tagged union:
  67 | 
  68 | ```zig
  69 | const sys = bun.sys;
  70 | 
  71 | // Pattern 1: Switch on result/error
  72 | switch (sys.read(fd, buffer)) {
  73 |     .result => |bytes_read| {
  74 |         // use bytes_read
  75 |     },
  76 |     .err => |err| {
  77 |         // err.errno, err.syscall, err.fd, err.path
  78 |         if (err.getErrno() == .AGAIN) {
  79 |             // handle EAGAIN
  80 |         }
  81 |     },
  82 | }
  83 | 
  84 | // Pattern 2: Unwrap with try (converts to Zig error)
  85 | const bytes = try sys.read(fd, buffer).unwrap();
  86 | 
  87 | // Pattern 3: Unwrap with default
  88 | const value = sys.stat(path).unwrapOr(default_stat);
  89 | ```
  90 | 
  91 | ## Low-Level File Operations
  92 | 
  93 | Only use these when `bun.sys.File` doesn't meet your needs.
  94 | 
  95 | ### Opening Files
  96 | 
  97 | ```zig
  98 | const sys = bun.sys;
  99 | 
 100 | // Use bun.O flags (cross-platform normalized)
 101 | const fd = switch (sys.open(path, bun.O.RDONLY, 0)) {
 102 |     .result => |fd| fd,
 103 |     .err => |err| return .{ .err = err },
 104 | };
 105 | defer fd.close();
 106 | 
 107 | // Common flags
 108 | bun.O.RDONLY, bun.O.WRONLY, bun.O.RDWR
 109 | bun.O.CREAT, bun.O.TRUNC, bun.O.APPEND
 110 | bun.O.NONBLOCK, bun.O.DIRECTORY
 111 | ```
 112 | 
 113 | ### Reading & Writing
 114 | 
 115 | ```zig
 116 | // Single read (may return less than buffer size)
 117 | switch (sys.read(fd, buffer)) {
 118 |     .result => |n| { /* n bytes read */ },
 119 |     .err => |err| { /* handle error */ },
 120 | }
 121 | 
 122 | // Read until EOF or buffer full
 123 | const total = try sys.readAll(fd, buffer).unwrap();
 124 | 
 125 | // Position-based read/write
 126 | sys.pread(fd, buffer, offset)
 127 | sys.pwrite(fd, data, offset)
 128 | 
 129 | // Vector I/O
 130 | sys.readv(fd, iovecs)
 131 | sys.writev(fd, iovecs)
 132 | ```
 133 | 
 134 | ### File Info
 135 | 
 136 | ```zig
 137 | sys.stat(path)      // Follow symlinks
 138 | sys.lstat(path)     // Don't follow symlinks
 139 | sys.fstat(fd)       // From file descriptor
 140 | sys.fstatat(fd, path)
 141 | 
 142 | // Linux-only: faster selective stat
 143 | sys.statx(path, &.{ .size, .mtime })
 144 | ```
 145 | 
 146 | ### Path Operations
 147 | 
 148 | ```zig
 149 | sys.unlink(path)
 150 | sys.unlinkat(dir_fd, path)
 151 | sys.rename(from, to)
 152 | sys.renameat(from_dir, from, to_dir, to)
 153 | sys.readlink(path, buf)
 154 | sys.readlinkat(fd, path, buf)
 155 | sys.link(T, src, dest)
 156 | sys.linkat(src_fd, src, dest_fd, dest)
 157 | sys.symlink(target, dest)
 158 | sys.symlinkat(target, dirfd, dest)
 159 | sys.mkdir(path, mode)
 160 | sys.mkdirat(dir_fd, path, mode)
 161 | sys.rmdir(path)
 162 | ```
 163 | 
 164 | ### Permissions
 165 | 
 166 | ```zig
 167 | sys.chmod(path, mode)
 168 | sys.fchmod(fd, mode)
 169 | sys.fchmodat(fd, path, mode, flags)
 170 | sys.chown(path, uid, gid)
 171 | sys.fchown(fd, uid, gid)
 172 | ```
 173 | 
 174 | ### Closing File Descriptors
 175 | 
 176 | Close is on `bun.FD`:
 177 | 
 178 | ```zig
 179 | fd.close();  // Asserts on error (use in defer)
 180 | 
 181 | // Or if you need error info:
 182 | if (fd.closeAllowingBadFileDescriptor(null)) |err| {
 183 |     // handle error
 184 | }
 185 | ```
 186 | 
 187 | ## Directory Operations
 188 | 
 189 | ```zig
 190 | var buf: bun.PathBuffer = undefined;
 191 | const cwd = try sys.getcwd(&buf).unwrap();
 192 | const cwdZ = try sys.getcwdZ(&buf).unwrap();  // Zero-terminated
 193 | sys.chdir(path, destination)
 194 | ```
 195 | 
 196 | ### Directory Iteration
 197 | 
 198 | Use `bun.DirIterator` instead of `std.fs.Dir.Iterator`:
 199 | 
 200 | ```zig
 201 | var iter = bun.iterateDir(dir_fd);
 202 | while (true) {
 203 |     switch (iter.next()) {
 204 |         .result => |entry| {
 205 |             if (entry) |e| {
 206 |                 const name = e.name.slice();
 207 |                 const kind = e.kind;  // .file, .directory, .sym_link, etc.
 208 |             } else {
 209 |                 break;  // End of directory
 210 |             }
 211 |         },
 212 |         .err => |err| return .{ .err = err },
 213 |     }
 214 | }
 215 | ```
 216 | 
 217 | ## Socket Operations
 218 | 
 219 | **Important**: `bun.sys` has limited socket support. For network I/O:
 220 | 
 221 | - **Non-blocking sockets**: Use `uws.Socket` (libuwebsockets) exclusively
 222 | - **Pipes/blocking I/O**: Use `PipeReader.zig` and `PipeWriter.zig`
 223 | 
 224 | Available in bun.sys:
 225 | 
 226 | ```zig
 227 | sys.setsockopt(fd, level, optname, value)
 228 | sys.socketpair(domain, socktype, protocol, nonblocking_status)
 229 | ```
 230 | 
 231 | Do NOT use `bun.sys` for socket read/write - use `uws.Socket` instead.
 232 | 
 233 | ## Other Operations
 234 | 
 235 | ```zig
 236 | sys.ftruncate(fd, size)
 237 | sys.lseek(fd, offset, whence)
 238 | sys.dup(fd)
 239 | sys.dupWithFlags(fd, flags)
 240 | sys.fcntl(fd, cmd, arg)
 241 | sys.pipe()
 242 | sys.mmap(...)
 243 | sys.munmap(memory)
 244 | sys.access(path, mode)
 245 | sys.futimens(fd, atime, mtime)
 246 | sys.utimens(path, atime, mtime)
 247 | ```
 248 | 
 249 | ## Error Type
 250 | 
 251 | ```zig
 252 | const err: bun.sys.Error = ...;
 253 | err.errno      // Raw errno value
 254 | err.getErrno() // As std.posix.E enum
 255 | err.syscall    // Which syscall failed (Tag enum)
 256 | err.fd         // Optional: file descriptor
 257 | err.path       // Optional: path string
 258 | ```
 259 | 
 260 | ## Key Points
 261 | 
 262 | - Prefer `bun.sys.File` wrapper for most file operations
 263 | - Use low-level `bun.sys` functions only when needed
 264 | - Use `bun.O.*` flags instead of `std.os.O.*`
 265 | - Handle `Maybe(T)` with switch or `.unwrap()`
 266 | - Use `defer fd.close()` for cleanup
 267 | - EINTR is handled automatically in most functions
 268 | - For sockets, use `uws.Socket` not `bun.sys`
```


---
## .github/workflows/CLAUDE.md

```
   1 | # GitHub Actions Workflow Maintenance Guide
   2 | 
   3 | This document provides guidance for maintaining the GitHub Actions workflows in this repository.
   4 | 
   5 | ## format.yml Workflow
   6 | 
   7 | ### Overview
   8 | The `format.yml` workflow runs code formatters (Prettier, clang-format, and Zig fmt) on pull requests and pushes to main. It's optimized for speed by running all formatters in parallel.
   9 | 
  10 | ### Key Components
  11 | 
  12 | #### 1. Clang-format Script (`scripts/run-clang-format.sh`)
  13 | - **Purpose**: Formats C++ source and header files
  14 | - **What it does**:
  15 |   - Reads C++ files from `cmake/sources/CxxSources.txt`
  16 |   - Finds all header files in `src/` and `packages/`
  17 |   - Excludes third-party directories (libuv, napi, deps, vendor, sqlite, etc.)
  18 |   - Requires specific clang-format version (no fallbacks)
  19 | 
  20 | **Important exclusions**:
  21 | - `src/napi/` - Node API headers (third-party)
  22 | - `src/bun.js/bindings/libuv/` - libuv headers (third-party)
  23 | - `src/bun.js/bindings/sqlite/` - SQLite headers (third-party)
  24 | - `src/bun.js/api/ffi-*.h` - FFI headers (generated/third-party)
  25 | - `src/deps/` - Dependencies (third-party)
  26 | - Files in `vendor/`, `third_party/`, `generated/` directories
  27 | 
  28 | #### 2. Parallel Execution
  29 | The workflow runs all three formatters simultaneously:
  30 | - Each formatter outputs with a prefix (`[prettier]`, `[clang-format]`, `[zig]`)
  31 | - Output is streamed in real-time without blocking
  32 | - Uses GitHub Actions groups (`::group::`) for collapsible sections
  33 | 
  34 | #### 3. Tool Installation
  35 | 
  36 | ##### Clang-format-21
  37 | - Installs ONLY `clang-format-21` package (not the entire LLVM toolchain)
  38 | - Uses `--no-install-recommends --no-install-suggests` to skip unnecessary packages
  39 | - Quiet installation with `-qq` and `-o=Dpkg::Use-Pty=0`
  40 | 
  41 | ##### Zig
  42 | - Downloads from `oven-sh/zig` releases (musl build for static linking)
  43 | - URL: `https://github.com/oven-sh/zig/releases/download/autobuild-{COMMIT}/bootstrap-x86_64-linux-musl.zip`
  44 | - Extracts to temp directory to avoid polluting the repository
  45 | - Directory structure: `bootstrap-x86_64-linux-musl/zig`
  46 | 
  47 | ### Updating the Workflow
  48 | 
  49 | #### To update Zig version:
  50 | 1. Find the new commit hash from https://github.com/oven-sh/zig/releases
  51 | 2. Replace the hash in the wget URL (line 65 of format.yml)
  52 | 3. Test that the URL is valid and the binary works
  53 | 
  54 | #### To update clang-format version:
  55 | 1. Update `LLVM_VERSION_MAJOR` environment variable at the top of format.yml
  56 | 2. Update the version check in `scripts/run-clang-format.sh`
  57 | 
  58 | #### To add/remove file exclusions:
  59 | 1. Edit the exclusion patterns in `scripts/run-clang-format.sh` (lines 34-39)
  60 | 2. Test locally to ensure the right files are being formatted
  61 | 
  62 | ### Performance Optimizations
  63 | 1. **Parallel execution**: All formatters run simultaneously
  64 | 2. **Minimal installations**: Only required packages, no extras
  65 | 3. **Temp directories**: Tools downloaded to temp dirs, cleaned up after use
  66 | 4. **Streaming output**: Real-time feedback without buffering
  67 | 5. **Early start**: Formatting begins immediately after each tool is ready
  68 | 
  69 | ### Troubleshooting
  70 | 
  71 | **If formatters appear to run sequentially:**
  72 | - Check if output is being buffered (should use `sed` for line prefixing)
  73 | - Ensure background processes use `&` and proper wait commands
  74 | 
  75 | **If third-party files are being formatted:**
  76 | - Review exclusion patterns in `scripts/run-clang-format.sh`
  77 | - Check if new third-party directories were added that need exclusion
  78 | 
  79 | **If clang-format installation is slow:**
  80 | - Ensure using minimal package installation flags
  81 | - Check if apt cache needs updating
  82 | - Consider caching the clang-format binary between runs
  83 | 
  84 | ### Testing Changes Locally
  85 | 
  86 | ```bash
  87 | # Test the clang-format script
  88 | export LLVM_VERSION_MAJOR=19
  89 | ./scripts/run-clang-format.sh format
  90 | 
  91 | # Test with check mode (no modifications)
  92 | ./scripts/run-clang-format.sh check
  93 | 
  94 | # Test specific file exclusions
  95 | ./scripts/run-clang-format.sh format 2>&1 | grep -E "(libuv|napi|deps)"
  96 | # Should return nothing if exclusions work correctly
  97 | ```
  98 | 
  99 | ### Important Notes
 100 | - The script defaults to **format** mode (modifies files)
 101 | - Always test locally before pushing workflow changes
 102 | - The musl Zig build works on glibc systems due to static linking
 103 | - Keep the exclusion list updated as new third-party code is added
```


---
## AGENTS.md

```
   1 | This is the Bun repository - an all-in-one JavaScript runtime & toolkit designed for speed, with a bundler, test runner, and Node.js-compatible package manager. It's written primarily in Zig with C++ for JavaScriptCore integration, powered by WebKit's JavaScriptCore engine.
   2 | 
   3 | ## Building and Running Bun
   4 | 
   5 | ### Build Commands
   6 | 
   7 | - **Build Bun**: `bun bd`
   8 |   - Creates a debug build at `./build/debug/bun-debug`
   9 |   - **CRITICAL**: do not set a timeout when running `bun bd`
  10 | - **Run tests with your debug build**: `bun bd test <test-file>`
  11 |   - **CRITICAL**: Never use `bun test` directly - it won't include your changes
  12 | - **Run any command with debug build**: `bun bd <command>`
  13 | - **Run with JavaScript exception scope verification**: `BUN_JSC_validateExceptionChecks=1
  14 | BUN_JSC_dumpSimulatedThrows=1 bun bd <command>`
  15 | 
  16 | Tip: Bun is already installed and in $PATH. The `bd` subcommand is a package.json script.
  17 | 
  18 | ## Testing
  19 | 
  20 | ### Running Tests
  21 | 
  22 | - **Single test file**: `bun bd test test/js/bun/http/serve.test.ts`
  23 | - **Fuzzy match test file**: `bun bd test http/serve.test.ts`
  24 | - **With filter**: `bun bd test test/js/bun/http/serve.test.ts -t "should handle"`
  25 | 
  26 | ### Test Organization
  27 | 
  28 | If a test is for a specific numbered GitHub Issue, it should be placed in `test/regression/issue/${issueNumber}.test.ts`. Ensure the issue number is **REAL** and not a placeholder!
  29 | 
  30 | If no valid issue number is provided, find the best existing file to modify instead, such as;
  31 | 
  32 | - `test/js/bun/` - Bun-specific API tests (http, crypto, ffi, shell, etc.)
  33 | - `test/js/node/` - Node.js compatibility tests
  34 | - `test/js/web/` - Web API tests (fetch, WebSocket, streams, etc.)
  35 | - `test/cli/` - CLI command tests (install, run, test, etc.)
  36 | - `test/bundler/` - Bundler and transpiler tests. Use `itBundled` helper.
  37 | - `test/integration/` - End-to-end integration tests
  38 | - `test/napi/` - N-API compatibility tests
  39 | - `test/v8/` - V8 C++ API compatibility tests
  40 | 
  41 | ### Writing Tests
  42 | 
  43 | Tests use Bun's Jest-compatible test runner with proper test fixtures.
  44 | 
  45 | - For **single-file tests**, prefer `-e` over `tempDir`.
  46 | - For **multi-file tests**, prefer `tempDir` and `Bun.spawn`.
  47 | 
  48 | ```typescript
  49 | import { test, expect } from "bun:test";
  50 | import { bunEnv, bunExe, normalizeBunSnapshot, tempDir } from "harness";
  51 | 
  52 | test("(single-file test) my feature", async () => {
  53 |   await using proc = Bun.spawn({
  54 |     cmd: [bunExe(), "-e", "console.log('Hello, world!')"],
  55 |     env: bunEnv,
  56 |   });
  57 | 
  58 |   const [stdout, stderr, exitCode] = await Promise.all([
  59 |     proc.stdout.text(),
  60 |     proc.stderr.text(),
  61 |     proc.exited,
  62 |   ]);
  63 | 
  64 |   expect(normalizeBunSnapshot(stdout)).toMatchInlineSnapshot(`"Hello, world!"`);
  65 |   expect(exitCode).toBe(0);
  66 | });
  67 | 
  68 | test("(multi-file test) my feature", async () => {
  69 |   // Create temp directory with test files
  70 |   using dir = tempDir("test-prefix", {
  71 |     "index.js": `import { foo } from "./foo.ts"; foo();`,
  72 |     "foo.ts": `export function foo() { console.log("foo"); }`,
  73 |   });
  74 | 
  75 |   // Spawn Bun process
  76 |   await using proc = Bun.spawn({
  77 |     cmd: [bunExe(), "index.js"],
  78 |     env: bunEnv,
  79 |     cwd: String(dir),
  80 |     stderr: "pipe",
  81 |   });
  82 | 
  83 |   const [stdout, stderr, exitCode] = await Promise.all([
  84 |     proc.stdout.text(),
  85 |     proc.stderr.text(),
  86 |     proc.exited,
  87 |   ]);
  88 | 
  89 |   // Prefer snapshot tests over expect(stdout).toBe("hello\n");
  90 |   expect(normalizeBunSnapshot(stdout, dir)).toMatchInlineSnapshot(`"hello"`);
  91 | 
  92 |   // Assert the exit code last. This gives you a more useful error message on test failure.
  93 |   expect(exitCode).toBe(0);
  94 | });
  95 | ```
  96 | 
  97 | - Always use `port: 0`. Do not hardcode ports. Do not use your own random port number function.
  98 | - Use `normalizeBunSnapshot` to normalize snapshot output of the test.
  99 | - NEVER write tests that check for no "panic" or "uncaught exception" or similar in the test output. These tests will never fail in CI.
 100 | - Use `tempDir` from `"harness"` to create a temporary directory. **Do not** use `tmpdirSync` or `fs.mkdtempSync` to create temporary directories.
 101 | - When spawning processes, tests should expect(stdout).toBe(...) BEFORE expect(exitCode).toBe(0). This gives you a more useful error message on test failure.
 102 | - **CRITICAL**: Do not write flaky tests. Do not use `setTimeout` in tests. Instead, `await` the condition to be met. You are not testing the TIME PASSING, you are testing the CONDITION.
 103 | - **CRITICAL**: Verify your test fails with `USE_SYSTEM_BUN=1 bun test <file>` and passes with `bun bd test <file>`. Your test is NOT VALID if it passes with `USE_SYSTEM_BUN=1`.
 104 | 
 105 | ## Code Architecture
 106 | 
 107 | ### Language Structure
 108 | 
 109 | - **Zig code** (`src/*.zig`): Core runtime, JavaScript bindings, package manager
 110 | - **C++ code** (`src/bun.js/bindings/*.cpp`): JavaScriptCore bindings, Web APIs
 111 | - **TypeScript** (`src/js/`): Built-in JavaScript modules with special syntax (see JavaScript Modules section)
 112 | - **Generated code**: Many files are auto-generated from `.classes.ts` and other sources. Bun will automatically rebuild these files when you make changes to them.
 113 | 
 114 | ### Core Source Organization
 115 | 
 116 | #### Runtime Core (`src/`)
 117 | 
 118 | - `bun.zig` - Main entry point
 119 | - `cli.zig` - CLI command orchestration
 120 | - `js_parser.zig`, `js_lexer.zig`, `js_printer.zig` - JavaScript parsing/printing
 121 | - `transpiler.zig` - Wrapper around js_parser with sourcemap support
 122 | - `resolver/` - Module resolution system
 123 | - `allocators/` - Custom memory allocators for performance
 124 | 
 125 | #### JavaScript Runtime (`src/bun.js/`)
 126 | 
 127 | - `bindings/` - C++ JavaScriptCore bindings
 128 |   - Generated classes from `.classes.ts` files
 129 |   - Manual bindings for complex APIs
 130 | - `api/` - Bun-specific APIs
 131 |   - `server.zig` - HTTP server implementation
 132 |   - `FFI.zig` - Foreign Function Interface
 133 |   - `crypto.zig` - Cryptographic operations
 134 |   - `glob.zig` - File pattern matching
 135 | - `node/` - Node.js compatibility layer
 136 |   - Module implementations (fs, path, crypto, etc.)
 137 |   - Process and Buffer APIs
 138 | - `webcore/` - Web API implementations
 139 |   - `fetch.zig` - Fetch API
 140 |   - `streams.zig` - Web Streams
 141 |   - `Blob.zig`, `Response.zig`, `Request.zig`
 142 | - `event_loop/` - Event loop and task management
 143 | 
 144 | #### Build Tools & Package Manager
 145 | 
 146 | - `src/bundler/` - JavaScript bundler
 147 |   - Advanced tree-shaking
 148 |   - CSS processing
 149 |   - HTML handling
 150 | - `src/install/` - Package manager
 151 |   - `lockfile/` - Lockfile handling
 152 |   - `npm.zig` - npm registry client
 153 |   - `lifecycle_script_runner.zig` - Package scripts
 154 | 
 155 | #### Other Key Components
 156 | 
 157 | - `src/shell/` - Cross-platform shell implementation
 158 | - `src/css/` - CSS parser and processor
 159 | - `src/http/` - HTTP client implementation
 160 |   - `websocket_client/` - WebSocket client (including deflate support)
 161 | - `src/sql/` - SQL database integrations
 162 | - `src/bake/` - Server-side rendering framework
 163 | 
 164 | #### Vendored Dependencies (`vendor/`)
 165 | 
 166 | Third-party C/C++ libraries are vendored locally and can be read from disk (these are not git submodules):
 167 | 
 168 | - `vendor/boringssl/` - BoringSSL (TLS/crypto)
 169 | - `vendor/brotli/` - Brotli compression
 170 | - `vendor/cares/` - c-ares (async DNS)
 171 | - `vendor/hdrhistogram/` - HdrHistogram (latency tracking)
 172 | - `vendor/highway/` - Google Highway (SIMD)
 173 | - `vendor/libarchive/` - libarchive (tar/zip)
 174 | - `vendor/libdeflate/` - libdeflate (fast deflate)
 175 | - `vendor/libuv/` - libuv (Windows event loop)
 176 | - `vendor/lolhtml/` - lol-html (HTML rewriter)
 177 | - `vendor/lshpack/` - ls-hpack (HTTP/2 HPACK)
 178 | - `vendor/mimalloc/` - mimalloc (memory allocator)
 179 | - `vendor/nodejs/` - Node.js headers (compatibility)
 180 | - `vendor/picohttpparser/` - PicoHTTPParser (HTTP parsing)
 181 | - `vendor/tinycc/` - TinyCC (FFI JIT compiler, fork: oven-sh/tinycc)
 182 | - `vendor/WebKit/` - WebKit/JavaScriptCore (JS engine)
 183 | - `vendor/zig/` - Zig compiler/stdlib
 184 | - `vendor/zlib/` - zlib (compression, cloudflare fork)
 185 | - `vendor/zstd/` - Zstandard (compression)
 186 | 
 187 | Build configuration for these is in `cmake/targets/Build*.cmake`.
 188 | 
 189 | ### JavaScript Class Implementation (C++)
 190 | 
 191 | When implementing JavaScript classes in C++:
 192 | 
 193 | 1. Create three classes if there's a public constructor:
 194 |    - `class Foo : public JSC::JSDestructibleObject` (if has C++ fields)
 195 |    - `class FooPrototype : public JSC::JSNonFinalObject`
 196 |    - `class FooConstructor : public JSC::InternalFunction`
 197 | 
 198 | 2. Define properties using HashTableValue arrays
 199 | 3. Add iso subspaces for classes with C++ fields
 200 | 4. Cache structures in ZigGlobalObject
 201 | 
 202 | ### Code Generation
 203 | 
 204 | Code generation happens automatically as part of the build process. The main scripts are:
 205 | 
 206 | - `src/codegen/generate-classes.ts` - Generates Zig & C++ bindings from `*.classes.ts` files
 207 | - `src/codegen/generate-jssink.ts` - Generates stream-related classes
 208 | - `src/codegen/bundle-modules.ts` - Bundles built-in modules like `node:fs`
 209 | - `src/codegen/bundle-functions.ts` - Bundles global functions like `ReadableStream`
 210 | 
 211 | In development, bundled modules can be reloaded without rebuilding Zig by running `bun run build`.
 212 | 
 213 | ## JavaScript Modules (`src/js/`)
 214 | 
 215 | Built-in JavaScript modules use special syntax and are organized as:
 216 | 
 217 | - `node/` - Node.js compatibility modules (`node:fs`, `node:path`, etc.)
 218 | - `bun/` - Bun-specific modules (`bun:ffi`, `bun:sqlite`, etc.)
 219 | - `thirdparty/` - NPM modules we replace (like `ws`)
 220 | - `internal/` - Internal modules not exposed to users
 221 | - `builtins/` - Core JavaScript builtins (streams, console, etc.)
 222 | 
 223 | ## Important Development Notes
 224 | 
 225 | 1. **Never use `bun test` or `bun <file>` directly** - always use `bun bd test` or `bun bd <command>`. `bun bd` compiles & runs the debug build.
 226 | 2. **All changes must be tested** - if you're not testing your changes, you're not done.
 227 | 3. **Get your tests to pass**. If you didn't run the tests, your code does not work.
 228 | 4. **Follow existing code style** - check neighboring files for patterns
 229 | 5. **Create tests in the right folder** in `test/` and the test must end in `.test.ts` or `.test.tsx`
 230 | 6. **Use absolute paths** - Always use absolute paths in file operations
 231 | 7. **Avoid shell commands** - Don't use `find` or `grep` in tests; use Bun's Glob and built-in tools
 232 | 8. **Memory management** - In Zig code, be careful with allocators and use defer for cleanup
 233 | 9. **Cross-platform** - Run `bun run zig:check-all` to compile the Zig code on all platforms when making platform-specific changes
 234 | 10. **Debug builds** - Use `BUN_DEBUG_QUIET_LOGS=1` to disable debug logging, or `BUN_DEBUG_<scopeName>=1` to enable specific `Output.scoped(.${scopeName}, .visible)`s
 235 | 11. **Be humble & honest** - NEVER overstate what you got done or what actually works in commits, PRs or in messages to the user.
 236 | 12. **Branch names must start with `claude/`** - This is a requirement for the CI to work.
 237 | 
 238 | **ONLY** push up changes after running `bun bd test <file>` and ensuring your tests pass.
 239 | 
 240 | ## Debugging CI Failures
 241 | 
 242 | Use `scripts/buildkite-failures.ts` to fetch and analyze CI build failures:
 243 | 
 244 | ```bash
 245 | # View failures for current branch
 246 | bun run scripts/buildkite-failures.ts
 247 | 
 248 | # View failures for a specific build number
 249 | bun run scripts/buildkite-failures.ts 35051
 250 | 
 251 | # View failures for a GitHub PR
 252 | bun run scripts/buildkite-failures.ts #26173
 253 | bun run scripts/buildkite-failures.ts https://github.com/oven-sh/bun/pull/26173
 254 | 
 255 | # Wait for build to complete (polls every 10s until pass/fail)
 256 | bun run scripts/buildkite-failures.ts --wait
 257 | ```
 258 | 
 259 | The script fetches logs from BuildKite's public API and saves complete logs to `/tmp/bun-build-{number}-{platform}-{step}.log`. It displays a summary of errors and the file path for each failed job. Use `--wait` to poll continuously until the build completes or fails.
```


---
## CLAUDE.md

```
   1 | This is the Bun repository - an all-in-one JavaScript runtime & toolkit designed for speed, with a bundler, test runner, and Node.js-compatible package manager. It's written primarily in Zig with C++ for JavaScriptCore integration, powered by WebKit's JavaScriptCore engine.
   2 | 
   3 | ## Building and Running Bun
   4 | 
   5 | ### Build Commands
   6 | 
   7 | - **Build Bun**: `bun bd`
   8 |   - Creates a debug build at `./build/debug/bun-debug`
   9 |   - **CRITICAL**: do not set a timeout when running `bun bd`
  10 | - **Run tests with your debug build**: `bun bd test <test-file>`
  11 |   - **CRITICAL**: Never use `bun test` directly - it won't include your changes
  12 | - **Run any command with debug build**: `bun bd <command>`
  13 | - **Run with JavaScript exception scope verification**: `BUN_JSC_validateExceptionChecks=1
  14 | BUN_JSC_dumpSimulatedThrows=1 bun bd <command>`
  15 | 
  16 | Tip: Bun is already installed and in $PATH. The `bd` subcommand is a package.json script.
  17 | 
  18 | ## Testing
  19 | 
  20 | ### Running Tests
  21 | 
  22 | - **Single test file**: `bun bd test test/js/bun/http/serve.test.ts`
  23 | - **Fuzzy match test file**: `bun bd test http/serve.test.ts`
  24 | - **With filter**: `bun bd test test/js/bun/http/serve.test.ts -t "should handle"`
  25 | 
  26 | ### Test Organization
  27 | 
  28 | If a test is for a specific numbered GitHub Issue, it should be placed in `test/regression/issue/${issueNumber}.test.ts`. Ensure the issue number is **REAL** and not a placeholder!
  29 | 
  30 | If no valid issue number is provided, find the best existing file to modify instead, such as;
  31 | 
  32 | - `test/js/bun/` - Bun-specific API tests (http, crypto, ffi, shell, etc.)
  33 | - `test/js/node/` - Node.js compatibility tests
  34 | - `test/js/web/` - Web API tests (fetch, WebSocket, streams, etc.)
  35 | - `test/cli/` - CLI command tests (install, run, test, etc.)
  36 | - `test/bundler/` - Bundler and transpiler tests. Use `itBundled` helper.
  37 | - `test/integration/` - End-to-end integration tests
  38 | - `test/napi/` - N-API compatibility tests
  39 | - `test/v8/` - V8 C++ API compatibility tests
  40 | 
  41 | ### Writing Tests
  42 | 
  43 | Tests use Bun's Jest-compatible test runner with proper test fixtures.
  44 | 
  45 | - For **single-file tests**, prefer `-e` over `tempDir`.
  46 | - For **multi-file tests**, prefer `tempDir` and `Bun.spawn`.
  47 | 
  48 | ```typescript
  49 | import { test, expect } from "bun:test";
  50 | import { bunEnv, bunExe, normalizeBunSnapshot, tempDir } from "harness";
  51 | 
  52 | test("(single-file test) my feature", async () => {
  53 |   await using proc = Bun.spawn({
  54 |     cmd: [bunExe(), "-e", "console.log('Hello, world!')"],
  55 |     env: bunEnv,
  56 |   });
  57 | 
  58 |   const [stdout, stderr, exitCode] = await Promise.all([
  59 |     proc.stdout.text(),
  60 |     proc.stderr.text(),
  61 |     proc.exited,
  62 |   ]);
  63 | 
  64 |   expect(normalizeBunSnapshot(stdout)).toMatchInlineSnapshot(`"Hello, world!"`);
  65 |   expect(exitCode).toBe(0);
  66 | });
  67 | 
  68 | test("(multi-file test) my feature", async () => {
  69 |   // Create temp directory with test files
  70 |   using dir = tempDir("test-prefix", {
  71 |     "index.js": `import { foo } from "./foo.ts"; foo();`,
  72 |     "foo.ts": `export function foo() { console.log("foo"); }`,
  73 |   });
  74 | 
  75 |   // Spawn Bun process
  76 |   await using proc = Bun.spawn({
  77 |     cmd: [bunExe(), "index.js"],
  78 |     env: bunEnv,
  79 |     cwd: String(dir),
  80 |     stderr: "pipe",
  81 |   });
  82 | 
  83 |   const [stdout, stderr, exitCode] = await Promise.all([
  84 |     proc.stdout.text(),
  85 |     proc.stderr.text(),
  86 |     proc.exited,
  87 |   ]);
  88 | 
  89 |   // Prefer snapshot tests over expect(stdout).toBe("hello\n");
  90 |   expect(normalizeBunSnapshot(stdout, dir)).toMatchInlineSnapshot(`"hello"`);
  91 | 
  92 |   // Assert the exit code last. This gives you a more useful error message on test failure.
  93 |   expect(exitCode).toBe(0);
  94 | });
  95 | ```
  96 | 
  97 | - Always use `port: 0`. Do not hardcode ports. Do not use your own random port number function.
  98 | - Use `normalizeBunSnapshot` to normalize snapshot output of the test.
  99 | - NEVER write tests that check for no "panic" or "uncaught exception" or similar in the test output. These tests will never fail in CI.
 100 | - Use `tempDir` from `"harness"` to create a temporary directory. **Do not** use `tmpdirSync` or `fs.mkdtempSync` to create temporary directories.
 101 | - When spawning processes, tests should expect(stdout).toBe(...) BEFORE expect(exitCode).toBe(0). This gives you a more useful error message on test failure.
 102 | - **CRITICAL**: Do not write flaky tests. Do not use `setTimeout` in tests. Instead, `await` the condition to be met. You are not testing the TIME PASSING, you are testing the CONDITION.
 103 | - **CRITICAL**: Verify your test fails with `USE_SYSTEM_BUN=1 bun test <file>` and passes with `bun bd test <file>`. Your test is NOT VALID if it passes with `USE_SYSTEM_BUN=1`.
 104 | 
 105 | ## Code Architecture
 106 | 
 107 | ### Language Structure
 108 | 
 109 | - **Zig code** (`src/*.zig`): Core runtime, JavaScript bindings, package manager
 110 | - **C++ code** (`src/bun.js/bindings/*.cpp`): JavaScriptCore bindings, Web APIs
 111 | - **TypeScript** (`src/js/`): Built-in JavaScript modules with special syntax (see JavaScript Modules section)
 112 | - **Generated code**: Many files are auto-generated from `.classes.ts` and other sources. Bun will automatically rebuild these files when you make changes to them.
 113 | 
 114 | ### Core Source Organization
 115 | 
 116 | #### Runtime Core (`src/`)
 117 | 
 118 | - `bun.zig` - Main entry point
 119 | - `cli.zig` - CLI command orchestration
 120 | - `js_parser.zig`, `js_lexer.zig`, `js_printer.zig` - JavaScript parsing/printing
 121 | - `transpiler.zig` - Wrapper around js_parser with sourcemap support
 122 | - `resolver/` - Module resolution system
 123 | - `allocators/` - Custom memory allocators for performance
 124 | 
 125 | #### JavaScript Runtime (`src/bun.js/`)
 126 | 
 127 | - `bindings/` - C++ JavaScriptCore bindings
 128 |   - Generated classes from `.classes.ts` files
 129 |   - Manual bindings for complex APIs
 130 | - `api/` - Bun-specific APIs
 131 |   - `server.zig` - HTTP server implementation
 132 |   - `FFI.zig` - Foreign Function Interface
 133 |   - `crypto.zig` - Cryptographic operations
 134 |   - `glob.zig` - File pattern matching
 135 | - `node/` - Node.js compatibility layer
 136 |   - Module implementations (fs, path, crypto, etc.)
 137 |   - Process and Buffer APIs
 138 | - `webcore/` - Web API implementations
 139 |   - `fetch.zig` - Fetch API
 140 |   - `streams.zig` - Web Streams
 141 |   - `Blob.zig`, `Response.zig`, `Request.zig`
 142 | - `event_loop/` - Event loop and task management
 143 | 
 144 | #### Build Tools & Package Manager
 145 | 
 146 | - `src/bundler/` - JavaScript bundler
 147 |   - Advanced tree-shaking
 148 |   - CSS processing
 149 |   - HTML handling
 150 | - `src/install/` - Package manager
 151 |   - `lockfile/` - Lockfile handling
 152 |   - `npm.zig` - npm registry client
 153 |   - `lifecycle_script_runner.zig` - Package scripts
 154 | 
 155 | #### Other Key Components
 156 | 
 157 | - `src/shell/` - Cross-platform shell implementation
 158 | - `src/css/` - CSS parser and processor
 159 | - `src/http/` - HTTP client implementation
 160 |   - `websocket_client/` - WebSocket client (including deflate support)
 161 | - `src/sql/` - SQL database integrations
 162 | - `src/bake/` - Server-side rendering framework
 163 | 
 164 | #### Vendored Dependencies (`vendor/`)
 165 | 
 166 | Third-party C/C++ libraries are vendored locally and can be read from disk (these are not git submodules):
 167 | 
 168 | - `vendor/boringssl/` - BoringSSL (TLS/crypto)
 169 | - `vendor/brotli/` - Brotli compression
 170 | - `vendor/cares/` - c-ares (async DNS)
 171 | - `vendor/hdrhistogram/` - HdrHistogram (latency tracking)
 172 | - `vendor/highway/` - Google Highway (SIMD)
 173 | - `vendor/libarchive/` - libarchive (tar/zip)
 174 | - `vendor/libdeflate/` - libdeflate (fast deflate)
 175 | - `vendor/libuv/` - libuv (Windows event loop)
 176 | - `vendor/lolhtml/` - lol-html (HTML rewriter)
 177 | - `vendor/lshpack/` - ls-hpack (HTTP/2 HPACK)
 178 | - `vendor/mimalloc/` - mimalloc (memory allocator)
 179 | - `vendor/nodejs/` - Node.js headers (compatibility)
 180 | - `vendor/picohttpparser/` - PicoHTTPParser (HTTP parsing)
 181 | - `vendor/tinycc/` - TinyCC (FFI JIT compiler, fork: oven-sh/tinycc)
 182 | - `vendor/WebKit/` - WebKit/JavaScriptCore (JS engine)
 183 | - `vendor/zig/` - Zig compiler/stdlib
 184 | - `vendor/zlib/` - zlib (compression, cloudflare fork)
 185 | - `vendor/zstd/` - Zstandard (compression)
 186 | 
 187 | Build configuration for these is in `cmake/targets/Build*.cmake`.
 188 | 
 189 | ### JavaScript Class Implementation (C++)
 190 | 
 191 | When implementing JavaScript classes in C++:
 192 | 
 193 | 1. Create three classes if there's a public constructor:
 194 |    - `class Foo : public JSC::JSDestructibleObject` (if has C++ fields)
 195 |    - `class FooPrototype : public JSC::JSNonFinalObject`
 196 |    - `class FooConstructor : public JSC::InternalFunction`
 197 | 
 198 | 2. Define properties using HashTableValue arrays
 199 | 3. Add iso subspaces for classes with C++ fields
 200 | 4. Cache structures in ZigGlobalObject
 201 | 
 202 | ### Code Generation
 203 | 
 204 | Code generation happens automatically as part of the build process. The main scripts are:
 205 | 
 206 | - `src/codegen/generate-classes.ts` - Generates Zig & C++ bindings from `*.classes.ts` files
 207 | - `src/codegen/generate-jssink.ts` - Generates stream-related classes
 208 | - `src/codegen/bundle-modules.ts` - Bundles built-in modules like `node:fs`
 209 | - `src/codegen/bundle-functions.ts` - Bundles global functions like `ReadableStream`
 210 | 
 211 | In development, bundled modules can be reloaded without rebuilding Zig by running `bun run build`.
 212 | 
 213 | ## JavaScript Modules (`src/js/`)
 214 | 
 215 | Built-in JavaScript modules use special syntax and are organized as:
 216 | 
 217 | - `node/` - Node.js compatibility modules (`node:fs`, `node:path`, etc.)
 218 | - `bun/` - Bun-specific modules (`bun:ffi`, `bun:sqlite`, etc.)
 219 | - `thirdparty/` - NPM modules we replace (like `ws`)
 220 | - `internal/` - Internal modules not exposed to users
 221 | - `builtins/` - Core JavaScript builtins (streams, console, etc.)
 222 | 
 223 | ## Important Development Notes
 224 | 
 225 | 1. **Never use `bun test` or `bun <file>` directly** - always use `bun bd test` or `bun bd <command>`. `bun bd` compiles & runs the debug build.
 226 | 2. **All changes must be tested** - if you're not testing your changes, you're not done.
 227 | 3. **Get your tests to pass**. If you didn't run the tests, your code does not work.
 228 | 4. **Follow existing code style** - check neighboring files for patterns
 229 | 5. **Create tests in the right folder** in `test/` and the test must end in `.test.ts` or `.test.tsx`
 230 | 6. **Use absolute paths** - Always use absolute paths in file operations
 231 | 7. **Avoid shell commands** - Don't use `find` or `grep` in tests; use Bun's Glob and built-in tools
 232 | 8. **Memory management** - In Zig code, be careful with allocators and use defer for cleanup
 233 | 9. **Cross-platform** - Run `bun run zig:check-all` to compile the Zig code on all platforms when making platform-specific changes
 234 | 10. **Debug builds** - Use `BUN_DEBUG_QUIET_LOGS=1` to disable debug logging, or `BUN_DEBUG_<scopeName>=1` to enable specific `Output.scoped(.${scopeName}, .visible)`s
 235 | 11. **Be humble & honest** - NEVER overstate what you got done or what actually works in commits, PRs or in messages to the user.
 236 | 12. **Branch names must start with `claude/`** - This is a requirement for the CI to work.
 237 | 
 238 | **ONLY** push up changes after running `bun bd test <file>` and ensuring your tests pass.
 239 | 
 240 | ## Debugging CI Failures
 241 | 
 242 | Use `scripts/buildkite-failures.ts` to fetch and analyze CI build failures:
 243 | 
 244 | ```bash
 245 | # View failures for current branch
 246 | bun run scripts/buildkite-failures.ts
 247 | 
 248 | # View failures for a specific build number
 249 | bun run scripts/buildkite-failures.ts 35051
 250 | 
 251 | # View failures for a GitHub PR
 252 | bun run scripts/buildkite-failures.ts #26173
 253 | bun run scripts/buildkite-failures.ts https://github.com/oven-sh/bun/pull/26173
 254 | 
 255 | # Wait for build to complete (polls every 10s until pass/fail)
 256 | bun run scripts/buildkite-failures.ts --wait
 257 | ```
 258 | 
 259 | The script fetches logs from BuildKite's public API and saves complete logs to `/tmp/bun-build-{number}-{platform}-{step}.log`. It displays a summary of errors and the file path for each failed job. Use `--wait` to poll continuously until the build completes or fails.
```


---
## README.md

```
   1 | <p align="center">
   2 |   <a href="https://bun.com"><img src="https://github.com/user-attachments/assets/50282090-adfd-4ddb-9e27-c30753c6b161" alt="Logo" height=170></a>
   3 | </p>
   4 | <h1 align="center">Bun</h1>
   5 | 
   6 | <p align="center">
   7 | <a href="https://bun.com/discord" target="_blank"><img height=20 src="https://img.shields.io/discord/876711213126520882" /></a>
   8 | <img src="https://img.shields.io/github/stars/oven-sh/bun" alt="stars">
   9 | <a href="https://twitter.com/jarredsumner/status/1542824445810642946"><img src="https://img.shields.io/static/v1?label=speed&message=fast&color=success" alt="Bun speed" /></a>
  10 | </p>
  11 | 
  12 | <div align="center">
  13 |   <a href="https://bun.com/docs">Documentation</a>
  14 |   <span>&nbsp;&nbsp;•&nbsp;&nbsp;</span>
  15 |   <a href="https://discord.com/invite/CXdq2DP29u">Discord</a>
  16 |   <span>&nbsp;&nbsp;•&nbsp;&nbsp;</span>
  17 |   <a href="https://github.com/oven-sh/bun/issues/new">Issues</a>
  18 |   <span>&nbsp;&nbsp;•&nbsp;&nbsp;</span>
  19 |   <a href="https://github.com/oven-sh/bun/issues/159">Roadmap</a>
  20 |   <br />
  21 | </div>
  22 | 
  23 | ### [Read the docs →](https://bun.com/docs)
  24 | 
  25 | ## What is Bun?
  26 | 
  27 | Bun is an all-in-one toolkit for JavaScript and TypeScript apps. It ships as a single executable called `bun`.
  28 | 
  29 | At its core is the _Bun runtime_, a fast JavaScript runtime designed as **a drop-in replacement for Node.js**. It's written in Zig and powered by JavaScriptCore under the hood, dramatically reducing startup times and memory usage.
  30 | 
  31 | ```bash
  32 | bun run index.tsx             # TS and JSX supported out-of-the-box
  33 | ```
  34 | 
  35 | The `bun` command-line tool also implements a test runner, script runner, and Node.js-compatible package manager. Instead of 1,000 node_modules for development, you only need `bun`. Bun's built-in tools are significantly faster than existing options and usable in existing Node.js projects with little to no changes.
  36 | 
  37 | ```bash
  38 | bun test                      # run tests
  39 | bun run start                 # run the `start` script in `package.json`
  40 | bun install <pkg>             # install a package
  41 | bunx cowsay 'Hello, world!'   # execute a package
  42 | ```
  43 | 
  44 | ## Install
  45 | 
  46 | Bun supports Linux (x64 & arm64), macOS (x64 & Apple Silicon), and Windows (x64 & arm64).
  47 | 
  48 | > **Linux users** — Kernel version 5.6 or higher is strongly recommended, but the minimum is 5.1.
  49 | 
  50 | > **x64 users** — if you see "illegal instruction" or similar errors, check our [CPU requirements](https://bun.com/docs/installation#cpu-requirements-and-baseline-builds)
  51 | 
  52 | ```sh
  53 | # with install script (recommended)
  54 | curl -fsSL https://bun.com/install | bash
  55 | 
  56 | # on windows
  57 | powershell -c "irm bun.sh/install.ps1 | iex"
  58 | 
  59 | # with npm
  60 | npm install -g bun
  61 | 
  62 | # with Homebrew
  63 | brew tap oven-sh/bun
  64 | brew install bun
  65 | 
  66 | # with Docker
  67 | docker pull oven/bun
  68 | docker run --rm --init --ulimit memlock=-1:-1 oven/bun
  69 | ```
  70 | 
  71 | ### Upgrade
  72 | 
  73 | To upgrade to the latest version of Bun, run:
  74 | 
  75 | ```sh
  76 | bun upgrade
  77 | ```
  78 | 
  79 | Bun automatically releases a canary build on every commit to `main`. To upgrade to the latest canary build, run:
  80 | 
  81 | ```sh
  82 | bun upgrade --canary
  83 | ```
  84 | 
  85 | [View canary build](https://github.com/oven-sh/bun/releases/tag/canary)
  86 | 
  87 | ## Quick links
  88 | 
  89 | - Intro
  90 |   - [What is Bun?](https://bun.com/docs/index)
  91 |   - [Installation](https://bun.com/docs/installation)
  92 |   - [Quickstart](https://bun.com/docs/quickstart)
  93 |   - [TypeScript](https://bun.com/docs/typescript)
  94 | 
  95 | - Templating
  96 |   - [`bun init`](https://bun.com/docs/cli/init)
  97 |   - [`bun create`](https://bun.com/docs/cli/bun-create)
  98 | 
  99 | - CLI
 100 |   - [`bun upgrade`](https://bun.com/docs/cli/bun-upgrade)
 101 | 
 102 | - Runtime
 103 |   - [`bun run`](https://bun.com/docs/cli/run)
 104 |   - [File types (Loaders)](https://bun.com/docs/runtime/loaders)
 105 |   - [TypeScript](https://bun.com/docs/runtime/typescript)
 106 |   - [JSX](https://bun.com/docs/runtime/jsx)
 107 |   - [Environment variables](https://bun.com/docs/runtime/environment-variables)
 108 |   - [Bun APIs](https://bun.com/docs/runtime/bun-apis)
 109 |   - [Web APIs](https://bun.com/docs/runtime/web-apis)
 110 |   - [Node.js compatibility](https://bun.com/docs/runtime/nodejs-compat)
 111 |   - [Single-file executable](https://bun.com/docs/bundler/executables)
 112 |   - [Plugins](https://bun.com/docs/runtime/plugins)
 113 |   - [Watch mode / Hot Reloading](https://bun.com/docs/runtime/watch-mode)
 114 |   - [Module resolution](https://bun.com/docs/runtime/modules)
 115 |   - [Auto-install](https://bun.com/docs/runtime/autoimport)
 116 |   - [bunfig.toml](https://bun.com/docs/runtime/bunfig)
 117 |   - [Debugger](https://bun.com/docs/runtime/debugger)
 118 |   - [$ Shell](https://bun.com/docs/runtime/shell)
 119 | 
 120 | - Package manager
 121 |   - [`bun install`](https://bun.com/docs/cli/install)
 122 |   - [`bun add`](https://bun.com/docs/cli/add)
 123 |   - [`bun remove`](https://bun.com/docs/cli/remove)
 124 |   - [`bun update`](https://bun.com/docs/cli/update)
 125 |   - [`bun link`](https://bun.com/docs/cli/link)
 126 |   - [`bun unlink`](https://bun.com/docs/cli/unlink)
 127 |   - [`bun pm`](https://bun.com/docs/cli/pm)
 128 |   - [`bun outdated`](https://bun.com/docs/cli/outdated)
 129 |   - [`bun publish`](https://bun.com/docs/cli/publish)
 130 |   - [`bun patch`](https://bun.com/docs/install/patch)
 131 |   - [`bun patch-commit`](https://bun.com/docs/cli/patch-commit)
 132 |   - [Global cache](https://bun.com/docs/install/cache)
 133 |   - [Workspaces](https://bun.com/docs/install/workspaces)
 134 |   - [Lifecycle scripts](https://bun.com/docs/install/lifecycle)
 135 |   - [Filter](https://bun.com/docs/cli/filter)
 136 |   - [Lockfile](https://bun.com/docs/install/lockfile)
 137 |   - [Scopes and registries](https://bun.com/docs/install/registries)
 138 |   - [Overrides and resolutions](https://bun.com/docs/install/overrides)
 139 |   - [`.npmrc`](https://bun.com/docs/install/npmrc)
 140 | 
 141 | - Bundler
 142 |   - [`Bun.build`](https://bun.com/docs/bundler)
 143 |   - [Loaders](https://bun.com/docs/bundler/loaders)
 144 |   - [Plugins](https://bun.com/docs/bundler/plugins)
 145 |   - [Macros](https://bun.com/docs/bundler/macros)
 146 |   - [vs esbuild](https://bun.com/docs/bundler/vs-esbuild)
 147 |   - [Single-file executable](https://bun.com/docs/bundler/executables)
 148 |   - [CSS](https://bun.com/docs/bundler/css)
 149 |   - [HTML](https://bun.com/docs/bundler/html)
 150 |   - [Hot Module Replacement (HMR)](https://bun.com/docs/bundler/hmr)
 151 |   - [Full-stack with HTML imports](https://bun.com/docs/bundler/fullstack)
 152 | 
 153 | - Test runner
 154 |   - [`bun test`](https://bun.com/docs/cli/test)
 155 |   - [Writing tests](https://bun.com/docs/test/writing)
 156 |   - [Watch mode](https://bun.com/docs/test/hot)
 157 |   - [Lifecycle hooks](https://bun.com/docs/test/lifecycle)
 158 |   - [Mocks](https://bun.com/docs/test/mocks)
 159 |   - [Snapshots](https://bun.com/docs/test/snapshots)
 160 |   - [Dates and times](https://bun.com/docs/test/time)
 161 |   - [DOM testing](https://bun.com/docs/test/dom)
 162 |   - [Code coverage](https://bun.com/docs/test/coverage)
 163 |   - [Configuration](https://bun.com/docs/test/configuration)
 164 |   - [Discovery](https://bun.com/docs/test/discovery)
 165 |   - [Reporters](https://bun.com/docs/test/reporters)
 166 |   - [Runtime Behavior](https://bun.com/docs/test/runtime-behavior)
 167 | 
 168 | - Package runner
 169 |   - [`bunx`](https://bun.com/docs/cli/bunx)
 170 | 
 171 | - API
 172 |   - [HTTP server (`Bun.serve`)](https://bun.com/docs/api/http)
 173 |   - [WebSockets](https://bun.com/docs/api/websockets)
 174 |   - [Workers](https://bun.com/docs/api/workers)
 175 |   - [Binary data](https://bun.com/docs/api/binary-data)
 176 |   - [Streams](https://bun.com/docs/api/streams)
 177 |   - [File I/O (`Bun.file`)](https://bun.com/docs/api/file-io)
 178 |   - [import.meta](https://bun.com/docs/api/import-meta)
 179 |   - [SQLite (`bun:sqlite`)](https://bun.com/docs/api/sqlite)
 180 |   - [PostgreSQL (`Bun.sql`)](https://bun.com/docs/api/sql)
 181 |   - [Redis (`Bun.redis`)](https://bun.com/docs/api/redis)
 182 |   - [S3 Client (`Bun.s3`)](https://bun.com/docs/api/s3)
 183 |   - [FileSystemRouter](https://bun.com/docs/api/file-system-router)
 184 |   - [TCP sockets](https://bun.com/docs/api/tcp)
 185 |   - [UDP sockets](https://bun.com/docs/api/udp)
 186 |   - [Globals](https://bun.com/docs/api/globals)
 187 |   - [$ Shell](https://bun.com/docs/runtime/shell)
 188 |   - [Child processes (spawn)](https://bun.com/docs/api/spawn)
 189 |   - [Transpiler (`Bun.Transpiler`)](https://bun.com/docs/api/transpiler)
 190 |   - [Hashing](https://bun.com/docs/api/hashing)
 191 |   - [Colors (`Bun.color`)](https://bun.com/docs/api/color)
 192 |   - [Console](https://bun.com/docs/api/console)
 193 |   - [FFI (`bun:ffi`)](https://bun.com/docs/api/ffi)
 194 |   - [C Compiler (`bun:ffi` cc)](https://bun.com/docs/api/cc)
 195 |   - [HTMLRewriter](https://bun.com/docs/api/html-rewriter)
 196 |   - [Testing (`bun:test`)](https://bun.com/docs/api/test)
 197 |   - [Cookies (`Bun.Cookie`)](https://bun.com/docs/api/cookie)
 198 |   - [Utils](https://bun.com/docs/api/utils)
 199 |   - [Node-API](https://bun.com/docs/api/node-api)
 200 |   - [Glob (`Bun.Glob`)](https://bun.com/docs/api/glob)
 201 |   - [Semver (`Bun.semver`)](https://bun.com/docs/api/semver)
 202 |   - [DNS](https://bun.com/docs/api/dns)
 203 |   - [fetch API extensions](https://bun.com/docs/api/fetch)
 204 | 
 205 | ## Guides
 206 | 
 207 | - Binary
 208 |   - [Convert a Blob to a string](https://bun.com/guides/binary/blob-to-string)
 209 |   - [Convert a Buffer to a blob](https://bun.com/guides/binary/buffer-to-blob)
 210 |   - [Convert a Blob to a DataView](https://bun.com/guides/binary/blob-to-dataview)
 211 |   - [Convert a Buffer to a string](https://bun.com/guides/binary/buffer-to-string)
 212 |   - [Convert a Blob to a ReadableStream](https://bun.com/guides/binary/blob-to-stream)
 213 |   - [Convert a Blob to a Uint8Array](https://bun.com/guides/binary/blob-to-typedarray)
 214 |   - [Convert a DataView to a string](https://bun.com/guides/binary/dataview-to-string)
 215 |   - [Convert a Uint8Array to a Blob](https://bun.com/guides/binary/typedarray-to-blob)
 216 |   - [Convert a Blob to an ArrayBuffer](https://bun.com/guides/binary/blob-to-arraybuffer)
 217 |   - [Convert an ArrayBuffer to a Blob](https://bun.com/guides/binary/arraybuffer-to-blob)
 218 |   - [Convert a Buffer to a Uint8Array](https://bun.com/guides/binary/buffer-to-typedarray)
 219 |   - [Convert a Uint8Array to a Buffer](https://bun.com/guides/binary/typedarray-to-buffer)
 220 |   - [Convert a Uint8Array to a string](https://bun.com/guides/binary/typedarray-to-string)
 221 |   - [Convert a Buffer to an ArrayBuffer](https://bun.com/guides/binary/buffer-to-arraybuffer)
 222 |   - [Convert an ArrayBuffer to a Buffer](https://bun.com/guides/binary/arraybuffer-to-buffer)
 223 |   - [Convert an ArrayBuffer to a string](https://bun.com/guides/binary/arraybuffer-to-string)
 224 |   - [Convert a Uint8Array to a DataView](https://bun.com/guides/binary/typedarray-to-dataview)
 225 |   - [Convert a Buffer to a ReadableStream](https://bun.com/guides/binary/buffer-to-readablestream)
 226 |   - [Convert a Uint8Array to an ArrayBuffer](https://bun.com/guides/binary/typedarray-to-arraybuffer)
 227 |   - [Convert an ArrayBuffer to a Uint8Array](https://bun.com/guides/binary/arraybuffer-to-typedarray)
 228 |   - [Convert an ArrayBuffer to an array of numbers](https://bun.com/guides/binary/arraybuffer-to-array)
 229 |   - [Convert a Uint8Array to a ReadableStream](https://bun.com/guides/binary/typedarray-to-readablestream)
 230 | 
 231 | - Ecosystem
 232 |   - [Use React and JSX](https://bun.com/guides/ecosystem/react)
 233 |   - [Use Gel with Bun](https://bun.com/guides/ecosystem/gel)
 234 |   - [Use Prisma with Bun](https://bun.com/guides/ecosystem/prisma)
 235 |   - [Add Sentry to a Bun app](https://bun.com/guides/ecosystem/sentry)
 236 |   - [Create a Discord bot](https://bun.com/guides/ecosystem/discordjs)
 237 |   - [Run Bun as a daemon with PM2](https://bun.com/guides/ecosystem/pm2)
 238 |   - [Use Drizzle ORM with Bun](https://bun.com/guides/ecosystem/drizzle)
 239 |   - [Build an app with Nuxt and Bun](https://bun.com/guides/ecosystem/nuxt)
 240 |   - [Build an app with Qwik and Bun](https://bun.com/guides/ecosystem/qwik)
 241 |   - [Build an app with Astro and Bun](https://bun.com/guides/ecosystem/astro)
 242 |   - [Build an app with Remix and Bun](https://bun.com/guides/ecosystem/remix)
 243 |   - [Build a frontend using Vite and Bun](https://bun.com/guides/ecosystem/vite)
 244 |   - [Build an app with Next.js and Bun](https://bun.com/guides/ecosystem/nextjs)
 245 |   - [Run Bun as a daemon with systemd](https://bun.com/guides/ecosystem/systemd)
 246 |   - [Deploy a Bun application on Render](https://bun.com/guides/ecosystem/render)
 247 |   - [Build an HTTP server using Hono and Bun](https://bun.com/guides/ecosystem/hono)
 248 |   - [Build an app with SvelteKit and Bun](https://bun.com/guides/ecosystem/sveltekit)
 249 |   - [Build an app with SolidStart and Bun](https://bun.com/guides/ecosystem/solidstart)
 250 |   - [Build an HTTP server using Elysia and Bun](https://bun.com/guides/ecosystem/elysia)
 251 |   - [Build an HTTP server using StricJS and Bun](https://bun.com/guides/ecosystem/stric)
 252 |   - [Containerize a Bun application with Docker](https://bun.com/guides/ecosystem/docker)
 253 |   - [Build an HTTP server using Express and Bun](https://bun.com/guides/ecosystem/express)
 254 |   - [Use Neon Postgres through Drizzle ORM](https://bun.com/guides/ecosystem/neon-drizzle)
 255 |   - [Server-side render (SSR) a React component](https://bun.com/guides/ecosystem/ssr-react)
 256 |   - [Read and write data to MongoDB using Mongoose and Bun](https://bun.com/guides/ecosystem/mongoose)
 257 |   - [Use Neon's Serverless Postgres with Bun](https://bun.com/guides/ecosystem/neon-serverless-postgres)
 258 | 
 259 | - HTMLRewriter
 260 |   - [Extract links from a webpage using HTMLRewriter](https://bun.com/guides/html-rewriter/extract-links)
 261 |   - [Extract social share images and Open Graph tags](https://bun.com/guides/html-rewriter/extract-social-meta)
 262 | 
 263 | - HTTP
 264 |   - [Hot reload an HTTP server](https://bun.com/guides/http/hot)
 265 |   - [Common HTTP server usage](https://bun.com/guides/http/server)
 266 |   - [Write a simple HTTP server](https://bun.com/guides/http/simple)
 267 |   - [Configure TLS on an HTTP server](https://bun.com/guides/http/tls)
 268 |   - [Send an HTTP request using fetch](https://bun.com/guides/http/fetch)
 269 |   - [Proxy HTTP requests using fetch()](https://bun.com/guides/http/proxy)
 270 |   - [Start a cluster of HTTP servers](https://bun.com/guides/http/cluster)
 271 |   - [Stream a file as an HTTP Response](https://bun.com/guides/http/stream-file)
 272 |   - [fetch with unix domain sockets in Bun](https://bun.com/guides/http/fetch-unix)
 273 |   - [Upload files via HTTP using FormData](https://bun.com/guides/http/file-uploads)
 274 |   - [Streaming HTTP Server with Async Iterators](https://bun.com/guides/http/stream-iterator)
 275 |   - [Streaming HTTP Server with Node.js Streams](https://bun.com/guides/http/stream-node-streams-in-bun)
 276 | 
 277 | - Install
 278 |   - [Add a dependency](https://bun.com/guides/install/add)
 279 |   - [Add a Git dependency](https://bun.com/guides/install/add-git)
 280 |   - [Add a peer dependency](https://bun.com/guides/install/add-peer)
 281 |   - [Add a trusted dependency](https://bun.com/guides/install/trusted)
 282 |   - [Add a development dependency](https://bun.com/guides/install/add-dev)
 283 |   - [Add a tarball dependency](https://bun.com/guides/install/add-tarball)
 284 |   - [Add an optional dependency](https://bun.com/guides/install/add-optional)
 285 |   - [Generate a yarn-compatible lockfile](https://bun.com/guides/install/yarnlock)
 286 |   - [Configuring a monorepo using workspaces](https://bun.com/guides/install/workspaces)
 287 |   - [Install a package under a different name](https://bun.com/guides/install/npm-alias)
 288 |   - [Install dependencies with Bun in GitHub Actions](https://bun.com/guides/install/cicd)
 289 |   - [Using bun install with Artifactory](https://bun.com/guides/install/jfrog-artifactory)
 290 |   - [Configure git to diff Bun's lockb lockfile](https://bun.com/guides/install/git-diff-bun-lockfile)
 291 |   - [Override the default npm registry for bun install](https://bun.com/guides/install/custom-registry)
 292 |   - [Using bun install with an Azure Artifacts npm registry](https://bun.com/guides/install/azure-artifacts)
 293 |   - [Migrate from npm install to bun install](https://bun.com/guides/install/from-npm-install-to-bun-install)
 294 |   - [Configure a private registry for an organization scope with bun install](https://bun.com/guides/install/registry-scope)
 295 | 
 296 | - Process
 297 |   - [Read from stdin](https://bun.com/guides/process/stdin)
 298 |   - [Listen for CTRL+C](https://bun.com/guides/process/ctrl-c)
 299 |   - [Spawn a child process](https://bun.com/guides/process/spawn)
 300 |   - [Listen to OS signals](https://bun.com/guides/process/os-signals)
 301 |   - [Parse command-line arguments](https://bun.com/guides/process/argv)
 302 |   - [Read stderr from a child process](https://bun.com/guides/process/spawn-stderr)
 303 |   - [Read stdout from a child process](https://bun.com/guides/process/spawn-stdout)
 304 |   - [Get the process uptime in nanoseconds](https://bun.com/guides/process/nanoseconds)
 305 |   - [Spawn a child process and communicate using IPC](https://bun.com/guides/process/ipc)
 306 | 
 307 | - Read file
 308 |   - [Read a JSON file](https://bun.com/guides/read-file/json)
 309 |   - [Check if a file exists](https://bun.com/guides/read-file/exists)
 310 |   - [Read a file as a string](https://bun.com/guides/read-file/string)
 311 |   - [Read a file to a Buffer](https://bun.com/guides/read-file/buffer)
 312 |   - [Get the MIME type of a file](https://bun.com/guides/read-file/mime)
 313 |   - [Watch a directory for changes](https://bun.com/guides/read-file/watch)
 314 |   - [Read a file as a ReadableStream](https://bun.com/guides/read-file/stream)
 315 |   - [Read a file to a Uint8Array](https://bun.com/guides/read-file/uint8array)
 316 |   - [Read a file to an ArrayBuffer](https://bun.com/guides/read-file/arraybuffer)
 317 | 
 318 | - Runtime
 319 |   - [Delete files](https://bun.com/guides/runtime/delete-file)
 320 |   - [Run a Shell Command](https://bun.com/guides/runtime/shell)
 321 |   - [Import a JSON file](https://bun.com/guides/runtime/import-json)
 322 |   - [Import a TOML file](https://bun.com/guides/runtime/import-toml)
 323 |   - [Set a time zone in Bun](https://bun.com/guides/runtime/timezone)
 324 |   - [Set environment variables](https://bun.com/guides/runtime/set-env)
 325 |   - [Re-map import paths](https://bun.com/guides/runtime/tsconfig-paths)
 326 |   - [Delete directories](https://bun.com/guides/runtime/delete-directory)
 327 |   - [Read environment variables](https://bun.com/guides/runtime/read-env)
 328 |   - [Import a HTML file as text](https://bun.com/guides/runtime/import-html)
 329 |   - [Install and run Bun in GitHub Actions](https://bun.com/guides/runtime/cicd)
 330 |   - [Debugging Bun with the web debugger](https://bun.com/guides/runtime/web-debugger)
 331 |   - [Install TypeScript declarations for Bun](https://bun.com/guides/runtime/typescript)
 332 |   - [Debugging Bun with the VS Code extension](https://bun.com/guides/runtime/vscode-debugger)
 333 |   - [Inspect memory usage using V8 heap snapshots](https://bun.com/guides/runtime/heap-snapshot)
 334 |   - [Define and replace static globals & constants](https://bun.com/guides/runtime/define-constant)
 335 |   - [Codesign a single-file JavaScript executable on macOS](https://bun.com/guides/runtime/codesign-macos-executable)
 336 | 
 337 | - Streams
 338 |   - [Convert a ReadableStream to JSON](https://bun.com/guides/streams/to-json)
 339 |   - [Convert a ReadableStream to a Blob](https://bun.com/guides/streams/to-blob)
 340 |   - [Convert a ReadableStream to a Buffer](https://bun.com/guides/streams/to-buffer)
 341 |   - [Convert a ReadableStream to a string](https://bun.com/guides/streams/to-string)
 342 |   - [Convert a ReadableStream to a Uint8Array](https://bun.com/guides/streams/to-typedarray)
 343 |   - [Convert a ReadableStream to an array of chunks](https://bun.com/guides/streams/to-array)
 344 |   - [Convert a Node.js Readable to JSON](https://bun.com/guides/streams/node-readable-to-json)
 345 |   - [Convert a ReadableStream to an ArrayBuffer](https://bun.com/guides/streams/to-arraybuffer)
 346 |   - [Convert a Node.js Readable to a Blob](https://bun.com/guides/streams/node-readable-to-blob)
 347 |   - [Convert a Node.js Readable to a string](https://bun.com/guides/streams/node-readable-to-string)
 348 |   - [Convert a Node.js Readable to an Uint8Array](https://bun.com/guides/streams/node-readable-to-uint8array)
 349 |   - [Convert a Node.js Readable to an ArrayBuffer](https://bun.com/guides/streams/node-readable-to-arraybuffer)
 350 | 
 351 | - Test
 352 |   - [Spy on methods in `bun test`](https://bun.com/guides/test/spy-on)
 353 |   - [Bail early with the Bun test runner](https://bun.com/guides/test/bail)
 354 |   - [Mock functions in `bun test`](https://bun.com/guides/test/mock-functions)
 355 |   - [Run tests in watch mode with Bun](https://bun.com/guides/test/watch-mode)
 356 |   - [Use snapshot testing in `bun test`](https://bun.com/guides/test/snapshot)
 357 |   - [Skip tests with the Bun test runner](https://bun.com/guides/test/skip-tests)
 358 |   - [Using Testing Library with Bun](https://bun.com/guides/test/testing-library)
 359 |   - [Update snapshots in `bun test`](https://bun.com/guides/test/update-snapshots)
 360 |   - [Run your tests with the Bun test runner](https://bun.com/guides/test/run-tests)
 361 |   - [Set the system time in Bun's test runner](https://bun.com/guides/test/mock-clock)
 362 |   - [Set a per-test timeout with the Bun test runner](https://bun.com/guides/test/timeout)
 363 |   - [Migrate from Jest to Bun's test runner](https://bun.com/guides/test/migrate-from-jest)
 364 |   - [Write browser DOM tests with Bun and happy-dom](https://bun.com/guides/test/happy-dom)
 365 |   - [Mark a test as a "todo" with the Bun test runner](https://bun.com/guides/test/todo-tests)
 366 |   - [Re-run tests multiple times with the Bun test runner](https://bun.com/guides/test/rerun-each)
 367 |   - [Generate code coverage reports with the Bun test runner](https://bun.com/guides/test/coverage)
 368 |   - [import, require, and test Svelte components with bun test](https://bun.com/guides/test/svelte-test)
 369 |   - [Set a code coverage threshold with the Bun test runner](https://bun.com/guides/test/coverage-threshold)
 370 | 
 371 | - Util
 372 |   - [Generate a UUID](https://bun.com/guides/util/javascript-uuid)
 373 |   - [Hash a password](https://bun.com/guides/util/hash-a-password)
 374 |   - [Escape an HTML string](https://bun.com/guides/util/escape-html)
 375 |   - [Get the current Bun version](https://bun.com/guides/util/version)
 376 |   - [Encode and decode base64 strings](https://bun.com/guides/util/base64)
 377 |   - [Compress and decompress data with gzip](https://bun.com/guides/util/gzip)
 378 |   - [Sleep for a fixed number of milliseconds](https://bun.com/guides/util/sleep)
 379 |   - [Detect when code is executed with Bun](https://bun.com/guides/util/detect-bun)
 380 |   - [Check if two objects are deeply equal](https://bun.com/guides/util/deep-equals)
 381 |   - [Compress and decompress data with DEFLATE](https://bun.com/guides/util/deflate)
 382 |   - [Get the absolute path to the current entrypoint](https://bun.com/guides/util/main)
 383 |   - [Get the directory of the current file](https://bun.com/guides/util/import-meta-dir)
 384 |   - [Check if the current file is the entrypoint](https://bun.com/guides/util/entrypoint)
 385 |   - [Get the file name of the current file](https://bun.com/guides/util/import-meta-file)
 386 |   - [Convert a file URL to an absolute path](https://bun.com/guides/util/file-url-to-path)
 387 |   - [Convert an absolute path to a file URL](https://bun.com/guides/util/path-to-file-url)
 388 |   - [Get the absolute path of the current file](https://bun.com/guides/util/import-meta-path)
 389 |   - [Get the path to an executable bin file](https://bun.com/guides/util/which-path-to-executable-bin)
 390 | 
 391 | - WebSocket
 392 |   - [Build a publish-subscribe WebSocket server](https://bun.com/guides/websocket/pubsub)
 393 |   - [Build a simple WebSocket server](https://bun.com/guides/websocket/simple)
 394 |   - [Enable compression for WebSocket messages](https://bun.com/guides/websocket/compression)
 395 |   - [Set per-socket contextual data on a WebSocket](https://bun.com/guides/websocket/context)
 396 | 
 397 | - Write file
 398 |   - [Delete a file](https://bun.com/guides/write-file/unlink)
 399 |   - [Write to stdout](https://bun.com/guides/write-file/stdout)
 400 |   - [Write a file to stdout](https://bun.com/guides/write-file/cat)
 401 |   - [Write a Blob to a file](https://bun.com/guides/write-file/blob)
 402 |   - [Write a string to a file](https://bun.com/guides/write-file/basic)
 403 |   - [Append content to a file](https://bun.com/guides/write-file/append)
 404 |   - [Write a file incrementally](https://bun.com/guides/write-file/filesink)
 405 |   - [Write a Response to a file](https://bun.com/guides/write-file/response)
 406 |   - [Copy a file to another location](https://bun.com/guides/write-file/file-cp)
 407 |   - [Write a ReadableStream to a file](https://bun.com/guides/write-file/stream)
 408 | 
 409 | ## Contributing
 410 | 
 411 | Refer to the [Project > Contributing](https://bun.com/docs/project/contributing) guide to start contributing to Bun.
 412 | 
 413 | ## License
 414 | 
 415 | Refer to the [Project > License](https://bun.com/docs/project/licensing) page for information about Bun's licensing.
```


---
## scripts/verify-baseline-static/CLAUDE.md

```
   1 | # verify-baseline-static — triage guide
   2 | 
   3 | Static ISA scanner. Disassembles every instruction in `.text` of a baseline
   4 | Bun binary and flags anything the baseline CPU can't decode. Catches `-march`
   5 | leaks at compile time, before they SIGILL on a user's machine.
   6 | 
   7 | This file is for triaging CI failures. For architecture details see
   8 | `README.md` and inline comments in `src/main.rs` / `src/aarch64.rs`.
   9 | 
  10 | ## This is a best-effort check, not a proof
  11 | 
  12 | A PASS here does **not** guarantee the binary is baseline-safe, and a FAIL
  13 | does not guarantee a real bug. Treat it as a sensitive smoke detector, not an
  14 | oracle. The emulator phase (`scripts/verify-baseline.ts`) is the complementary
  15 | check — together they catch most things; neither alone is bulletproof.
  16 | 
  17 | **Out of scope entirely (tool will never find these):**
  18 | 
  19 | - **JIT-emitted code.** JSC compiles JS/WASM to machine code at runtime; none
  20 |   of it exists in `.text` at scan time. If the JIT backend emits post-
  21 |   baseline instructions on a baseline CPU, this tool is blind to it. The
  22 |   emulator's `--jit-stress` path covers this.
  23 | - **Dynamically loaded code.** N-API addons, FFI callees, dlopen'd shared
  24 |   libs. Scanner only reads the `bun-profile` binary.
  25 | - **Gate correctness.** The tool does not verify that a CPUID gate actually
  26 |   checks the right bits. It trusts the allowlist. Feature ceilings catch the
  27 |   "code grew new features, gate wasn't updated" case, but a gate that was
  28 |   wrong from the start (checks AVX, uses AVX2) passes silently if the
  29 |   ceiling says `[AVX, AVX2]`.
  30 | 
  31 | **In scope but may miss:**
  32 | 
  33 | - x64 linear-sweep may desync on data-in-`.text` and skip real instructions
  34 |   that follow. Variable-length x86 encoding makes perfect code/data
  35 |   separation undecidable (`README.md:53-59`). aarch64 is more reliable
  36 |   (fixed-width words, `$d` mapping symbols mark data), but a missing mapping
  37 |   symbol can still hide a hit.
  38 | - Instructions deliberately ignored (TZCNT/XGETBV on x64, hint-space PAC/BTI
  39 |   on aarch64) could theoretically be misused; we assume the compiler's idiom
  40 |   is the only one.
  41 | 
  42 | **Can report false violations:**
  43 | 
  44 | - Data bytes in `.text` that happen to form a valid post-baseline encoding.
  45 |   Rare on ELF (LLVM puts tables in `.rodata`), common on Windows PE (MSVC
  46 |   inlines jump tables). See `README.md:61-74`.
  47 | 
  48 | When in doubt, the emulator is ground truth: `qemu -cpu Nehalem` and hit the
  49 | code path. SIGILL = real bug. No SIGILL = either gated or a data-in-text
  50 | false positive.
  51 | 
  52 | ## Which builds run this
  53 | 
  54 | `.buildkite/ci.mjs:592` — `needsBaselineVerification()`:
  55 | 
  56 | | Target                                          | Allowlist file              |
  57 | | ----------------------------------------------- | --------------------------- |
  58 | | `linux-x64-baseline`, `linux-x64-musl-baseline` | `allowlist-x64.txt`         |
  59 | | `windows-x64-baseline`                          | `allowlist-x64-windows.txt` |
  60 | | `linux-aarch64`, `linux-aarch64-musl`           | `allowlist-aarch64.txt`     |
  61 | 
  62 | x64 baseline = Nehalem (`-march=nehalem`, `cmake/CompilerFlags.cmake:33`).
  63 | aarch64 baseline = `armv8-a+crc` (`cmake/CompilerFlags.cmake:27-29`). aarch64
  64 | has no separate "baseline" build — the regular build _is_ the baseline.
  65 | 
  66 | ## Reproduce a CI failure locally
  67 | 
  68 | The scanner runs on the _CI-built_ `-profile` artifact. You can't reproduce by
  69 | building locally unless you build with the exact baseline toolchain. Download
  70 | the artifact instead.
  71 | 
  72 | 1. Get `<triplet>-profile.zip` from the failing build's `build-bun` step
  73 |    (Artifacts tab in Buildkite). Triplets look like `bun-linux-x64-baseline`,
  74 |    `bun-linux-aarch64-musl`, `bun-windows-x64-baseline`.
  75 | 
  76 | 2. Build and run the scanner (host arch is irrelevant — the scanner reads the
  77 |    binary's headers, it doesn't execute it):
  78 | 
  79 |    ```sh
  80 |    cargo build --release --manifest-path scripts/verify-baseline-static/Cargo.toml
  81 | 
  82 |    # Linux x64 baseline
  83 |    ./scripts/verify-baseline-static/target/release/verify-baseline-static \
  84 |      --binary bun-linux-x64-baseline-profile/bun-profile \
  85 |      --allowlist scripts/verify-baseline-static/allowlist-x64.txt
  86 | 
  87 |    # Linux aarch64
  88 |    ./scripts/verify-baseline-static/target/release/verify-baseline-static \
  89 |      --binary bun-linux-aarch64-profile/bun-profile \
  90 |      --allowlist scripts/verify-baseline-static/allowlist-aarch64.txt
  91 | 
  92 |    # Windows x64 baseline (PDB auto-discovered at <binary>.pdb)
  93 |    ./scripts/verify-baseline-static/target/release/verify-baseline-static \
  94 |      --binary bun-windows-x64-baseline-profile/bun-profile.exe \
  95 |      --allowlist scripts/verify-baseline-static/allowlist-x64-windows.txt
  96 |    ```
  97 | 
  98 | **Never scan the stripped release binary.** It has no `.symtab` (ELF) / no
  99 | `.pdb` (PE), so every hit becomes `<no-symbol@addr>` and nothing matches the
 100 | allowlist.
 101 | 
 102 | ## Reading the output
 103 | 
 104 | ```
 105 | VIOLATIONS (would SIGILL on Nehalem):
 106 | 
 107 |   _ZN7simdutf7haswell14implementation17some_new_functionEPKcm  [AVX, AVX2]  (42 insns)
 108 |     0x0000a1b2c3  Vpbroadcastb  (AVX2)
 109 |     0x0000a1b2d7  Vpshufb  (AVX)
 110 |     0x0000a1b2ee  Vpcmpeqb  (AVX)
 111 |     ... 39 more
 112 | 
 113 | ALLOWLISTED (suppressed, runtime-dispatched):
 114 |   ...
 115 |   -- 550 symbols, 18234 instructions total
 116 | 
 117 | STALE ALLOWLIST ENTRIES (no matching symbol found — remove these?):
 118 |   _ZN7simdutf7haswell14implementation13old_gone_funcEPKcm
 119 | 
 120 | SUMMARY:
 121 |   violations:  1 symbols, 42 instructions
 122 |   allowlisted: 550 symbols
 123 |   stale allowlist entries: 1
 124 |   FAIL
 125 | ```
 126 | 
 127 | - Violation line format: `symbol  [FEAT, ...]  (N insns)`. Copy the symbol
 128 |   name exactly when allowlisting — it's compared post-canonicalization.
 129 | - Feature names are iced-x86's `CpuidFeature` Debug names (x64) or the strings
 130 |   in `src/aarch64.rs:44-54` (aarch64). They must match the allowlist brackets
 131 |   character-for-character.
 132 | - `STALE` entries are informational, not an error. One allowlist covers both
 133 |   glibc and musl; a symbol LTO'd away on one libc shows STALE on the other.
 134 | 
 135 | ## Triage: is this an allowlist entry or a real bug?
 136 | 
 137 | The tool found post-baseline instructions in some symbol. Two possibilities:
 138 | 
 139 | **A. Runtime-dispatched.** The symbol only runs after a CPUID/HWCAP gate
 140 | decides the CPU supports it. This is fine — allowlist it.
 141 | 
 142 | **B. Not gated.** A `-march` flag leaked into a translation unit that's always
 143 | executed. Real bug, will SIGILL on baseline hardware. Fix the compile flags.
 144 | 
 145 | ### Deciding which
 146 | 
 147 | **Identify the dependency.** Demangle the symbol (`c++filt`, or recognize the
 148 | prefix: `_ZN7simdutf` = simdutf, `_ZN3bun` + `N_AVX2`/`N_SVE` = Bun's Highway
 149 | code, `_RNv` + `memchr` = Rust memchr, etc). Search the allowlist for that
 150 | dependency — if neighbors are there under an existing `# Gate: ...` header,
 151 | this is almost certainly (A).
 152 | 
 153 | **Find the gate.** Grep for the symbol name (unmangled) in the dependency's
 154 | source. Trace up to the caller — there should be a CPUID check, a dispatcher
 155 | table, an HWCAP test. Known patterns:
 156 | 
 157 | | Dependency                            | Gate                                                        | Where                                      |
 158 | | ------------------------------------- | ----------------------------------------------------------- | ------------------------------------------ |
 159 | | simdutf                               | `set_best()` — CPUID first call, cached atomic ptr          | `vendor/` or WebKit's bundled copy         |
 160 | | Highway (Bun)                         | `HWY_DYNAMIC_DISPATCH` → `hwy::SupportedTargets()`          | `src/bun.js/bindings/highway_strings.cpp`  |
 161 | | BoringSSL                             | `OPENSSL_ia32cap_P` global, set at init                     | `vendor/boringssl/crypto/cpu_intel.c`      |
 162 | | zstd                                  | `ZSTD_cpuid()`                                              | `vendor/zstd/lib/common/cpu.h`             |
 163 | | libdeflate                            | `libdeflate_init_x86_cpu_features()` / `HWCAP_ASIMDDP`      | `vendor/libdeflate/lib/x86/cpu_features.c` |
 164 | | Rust `memchr`                         | `is_x86_feature_detected!()`                                | (via lolhtml dep)                          |
 165 | | compiler-rt outline-atomics (aarch64) | `__aarch64_have_lse_atomics` (= `AT_HWCAP & HWCAP_ATOMICS`) | compiler-rt builtin                        |
 166 | 
 167 | **If no gate exists:** (B). Usually a subbuild that ignored
 168 | `ENABLE_BASELINE` and picked up host `-march=native`. Fix the
 169 | `cmake/targets/Build*.cmake` for that dep. Confirm with the emulator (the
 170 | ground-truth check):
 171 | 
 172 | ```sh
 173 | qemu-x86_64 -cpu Nehalem ./bun-profile <code path that hits it>   # x64 → SIGILL = bug
 174 | qemu-aarch64 -cpu cortex-a53 ./bun-profile <code path>             # aarch64
 175 | ```
 176 | 
 177 | ### Data-in-`.text` false positives (x64, mostly Windows)
 178 | 
 179 | Linear-sweep decode means data bytes in `.text` can happen to form a valid
 180 | instruction encoding. LLVM puts tables in `.rodata` so ELF builds are usually
 181 | clean; MSVC inlines jump tables and `static const` arrays into `.text`.
 182 | 
 183 | Signs of a false positive:
 184 | 
 185 | - Symbol is a lookup table or a function you _know_ contains no SIMD.
 186 | - Reported instruction count is tiny (1–3) inside an otherwise-non-SIMD symbol.
 187 | - `objdump -d` around the reported address shows `ret` then byte soup — no
 188 |   stack frame setup, no control flow leading to it.
 189 | 
 190 | If confirmed: allowlist the symbol. Note the reason in the group comment.
 191 | 
 192 | ## Adding an allowlist entry
 193 | 
 194 | Append the symbol to the appropriate file. Group with its neighbors under the
 195 | existing `# Gate: ...` header; if no existing group matches, add one:
 196 | 
 197 | ```
 198 | # ----------------------------------------------------------------------------
 199 | # <dependency> <variant>. Gate: <what checks CPUID/HWCAP>.
 200 | # (N symbols)
 201 | # ----------------------------------------------------------------------------
 202 | symbol_name_exactly_as_the_tool_printed_it  [FEAT1, FEAT2]
 203 | ```
 204 | 
 205 | **Always use a feature ceiling** (`[...]`). A blanket pass (no brackets)
 206 | defeats the "did the gate get updated when the dep grew AVX-512?" check
 207 | (`src/main.rs:616-621`). List exactly the features the tool reported; that's
 208 | what the gate currently checks.
 209 | 
 210 | **x64 feature names** (iced-x86 Debug strings — must match exactly):
 211 | `AVX`, `AVX2`, `FMA`, `FMA4`, `BMI1`, `BMI2`, `MOVBE`, `ADX`, `RDRAND`,
 212 | `AES`, `PCLMULQDQ`, `VAES`, `VPCLMULQDQ`, `SHA`, `AVX512F`, `AVX512BW`,
 213 | `AVX512DQ`, `AVX512VL`, `AVX512_VBMI`, `AVX512_VBMI2`, `AVX512_VNNI`,
 214 | `AVX512_VPOPCNTDQ`, `AVX512_FP16`, `AVX_VNNI`, …
 215 | 
 216 | **aarch64 feature names:** `LSE`, `SVE`, `RCPC`, `DotProd`, `JSCVT`, `RDM`,
 217 | `PAC(non-hint)`.
 218 | 
 219 | ### Special symbol forms
 220 | 
 221 | **Rust v0 mangling — `<rust-hash>`.** Rust symbols contain a crate-hash
 222 | (`Cs[base62]_`) that changes across target triples and toolchains. The tool
 223 | canonicalizes both sides (`src/main.rs:196-227`), so allowlist entries should
 224 | use `<rust-hash>` in place of the hash:
 225 | 
 226 | ```
 227 | # Tool reports:
 228 |   _RNvMNtNtNtNtCs5QMN7YRSXc3_6memchr4arch6x86_644avx26memchrNtB2_3One13find_raw_avx2  [AVX, AVX2]
 229 | # Allowlist as:
 230 |   _RNvMNtNtNtNt<rust-hash>6memchr4arch6x86_644avx26memchrNtB2_3One13find_raw_avx2  [AVX, AVX2]
 231 | ```
 232 | 
 233 | Either form works (the tool canonicalizes both before comparing), but
 234 | `<rust-hash>` survives toolchain bumps.
 235 | 
 236 | **Windows `<lib:NAME.lib>`.** When PDB has no per-function record for a hit
 237 | (stripped CRT objects, anonymized staticlib helpers), the tool falls back to
 238 | section-contribution attribution: the linker-map "which `.lib` did this byte
 239 | come from" data. These attributions are stable across link layout changes.
 240 | Allowlist them literally:
 241 | 
 242 | ```
 243 | <lib:lolhtml.lib>  [AVX, AVX2]
 244 | ```
 245 | 
 246 | **`<no-symbol@0x...>`** — the address fell in padding between functions or the
 247 | binary is stripped. If you see these for every violation, you're scanning the
 248 | wrong binary (use `-profile`). If it's just one or two, it's usually inter-
 249 | function padding that decoded as something; investigate with `objdump -d`
 250 | around that address and, if it's genuinely junk, add a brief `# padding at
 251 | <addr range>` comment with a blanket-pass entry.
 252 | 
 253 | ### PDB coverage drift (Windows)
 254 | 
 255 | A function may get an `S_LPROC32` record (real mangled name) on one toolchain
 256 | and fall through to `<lib:...>` on another. If the same code flips between
 257 | forms across CI runs, allowlist both.
 258 | 
 259 | ## Deliberately ignored (not reported even if found)
 260 | 
 261 | See `src/main.rs:94-135` and `src/aarch64.rs`:
 262 | 
 263 | - **TZCNT** (x64) — decodes as REP BSF on pre-BMI1; LLVM preloads dest with
 264 |   operand-width so the `src==0` case matches. (LZCNT is NOT ignored —
 265 |   `BSR` ≠ `LZCNT` for nonzero inputs and LLVM never emits it for Nehalem.)
 266 | - **XGETBV** (x64) — needed by every AVX gate; a stray one SIGILLs at
 267 |   startup so the emulator catches it trivially.
 268 | - **ENDBR64 (CET_IBT), RDSSP/INCSSP (CET_SS hint-space subset)** (x64) —
 269 |   NOP-encoded on pre-CET by design. The rest of CET_SS (WRSSD/RSTORSSP/
 270 |   SETSSBSY etc.) IS flagged — dedicated opcode slots that #UD on pre-CET.
 271 | - **PACIASP/AUTIASP/BTI** (aarch64) — HINT-space, architecturally NOP on
 272 |   pre-PAC CPUs. (`LDRAA`/`LDRAB` are _not_ HINT-space and _are_ reported.)
 273 | - **3DNow!, SMM, Cyrix, VIA** (x64) — no toolchain targeting x86-64 emits
 274 |   these. When their `0f xx` encodings show up, it's data.
```


---
## src/AGENTS.md

```
   1 | ## Zig
   2 | 
   3 | Syntax reminders:
   4 | 
   5 | - Private fields are fully supported in Zig with the `#` prefix. `struct { #foo: u32 };` makes a struct with a private field named `#foo`.
   6 | - Decl literals in Zig are recommended. `const decl: Decl = .{ .binding = 0, .value = 0 };`
   7 | 
   8 | Conventions:
   9 | 
  10 | - Prefer `@import` at the **bottom** of the file, but the auto formatter will move them so you don't need to worry about it.
  11 | - **Never** use `@import()` inline inside of functions. **Always** put them at the bottom of the file or containing struct. Imports in Zig are free of side-effects, so there's no such thing as a "dynamic" import.
  12 | - You must be patient with the build.
  13 | 
  14 | ## Prefer Bun APIs over `std`
  15 | 
  16 | **Always use `bun.*` APIs instead of `std.*`.** The `bun` namespace (`@import("bun")`) provides cross-platform wrappers that preserve OS error info and never use `unreachable`. Using `std.fs`, `std.posix`, or `std.os` directly is wrong in this codebase.
  17 | 
  18 | | Instead of                                                   | Use                                  |
  19 | | ------------------------------------------------------------ | ------------------------------------ |
  20 | | `std.base64`                                                 | `bun.base64`                         |
  21 | | `std.crypto.sha{...}`                                        | `bun.sha.Hashers.{...}`              |
  22 | | `std.fs.cwd()`                                               | `bun.FD.cwd()`                       |
  23 | | `std.fs.File`                                                | `bun.sys.File`                       |
  24 | | `std.fs.path.join/dirname/basename`                          | `bun.path.join/dirname/basename`     |
  25 | | `std.mem.eql/indexOf/startsWith` (for strings)               | `bun.strings.eql/indexOf/startsWith` |
  26 | | `std.posix.O` / `std.posix.mode_t` / `std.posix.fd_t`        | `bun.O` / `bun.Mode` / `bun.FD`      |
  27 | | `std.posix.open/read/write/stat/mkdir/unlink/rename/symlink` | `bun.sys.*` equivalents              |
  28 | | `std.process.Child`                                          | `bun.spawnSync`                      |
  29 | 
  30 | ## `bun.sys` — System Calls (`src/sys.zig`)
  31 | 
  32 | All return `Maybe(T)` — a tagged union of `.result: T` or `.err: bun.sys.Error`:
  33 | 
  34 | ```zig
  35 | const fd = switch (bun.sys.open(path, bun.O.RDONLY, 0)) {
  36 |     .result => |fd| fd,
  37 |     .err => |err| return .{ .err = err },
  38 | };
  39 | // Or: const fd = try bun.sys.open(path, bun.O.RDONLY, 0).unwrap();
  40 | ```
  41 | 
  42 | Key functions (all take `bun.FileDescriptor`, not `std.posix.fd_t`):
  43 | 
  44 | - `open`, `openat`, `openA` (non-sentinel) → `Maybe(bun.FileDescriptor)`
  45 | - `read`, `readAll`, `pread` → `Maybe(usize)`
  46 | - `write`, `pwrite`, `writev` → `Maybe(usize)`
  47 | - `stat`, `fstat`, `lstat` → `Maybe(bun.Stat)`
  48 | - `mkdir`, `unlink`, `rename`, `symlink`, `chmod`, `fchmod`, `fchown` → `Maybe(void)`
  49 | - `readlink`, `getFdPath`, `getcwd` → `Maybe` of path slice
  50 | - `getFileSize`, `dup`, `sendfile`, `mmap`
  51 | 
  52 | Use `bun.O.RDONLY`, `bun.O.WRONLY | bun.O.CREAT | bun.O.TRUNC`, etc. for open flags.
  53 | 
  54 | ### `bun.sys.File` (`src/sys/File.zig`)
  55 | 
  56 | Higher-level file handle wrapping `bun.FileDescriptor`:
  57 | 
  58 | ```zig
  59 | // One-shot read: open + read + close
  60 | const bytes = switch (bun.sys.File.readFrom(bun.FD.cwd(), path, allocator)) {
  61 |     .result => |b| b,
  62 |     .err => |err| return .{ .err = err },
  63 | };
  64 | 
  65 | // One-shot write: open + write + close
  66 | switch (bun.sys.File.writeFile(bun.FD.cwd(), path, data)) {
  67 |     .result => {},
  68 |     .err => |err| return .{ .err = err },
  69 | }
  70 | ```
  71 | 
  72 | Key methods:
  73 | 
  74 | - `File.open/openat/makeOpen` → `Maybe(File)` (`makeOpen` creates parent dirs)
  75 | - `file.read/readAll/write/writeAll` — single or looped I/O
  76 | - `file.readToEnd(allocator)` — read entire file into allocated buffer
  77 | - `File.readFrom(dir_fd, path, allocator)` — open + read + close
  78 | - `File.writeFile(dir_fd, path, data)` — open + write + close
  79 | - `file.stat()`, `file.close()`, `file.writer()`, `file.reader()`
  80 | 
  81 | ### `bun.FD` (`src/fd.zig`)
  82 | 
  83 | Cross-platform file descriptor. Use `bun.FD.cwd()` for cwd, `bun.invalid_fd` for sentinel, `fd.close()` to close.
  84 | 
  85 | ### `bun.sys.Error` (`src/sys/Error.zig`)
  86 | 
  87 | Preserves errno, syscall tag, and file path. Convert to JS: `err.toSystemError().toErrorInstance(globalObject)`.
  88 | 
  89 | ## `bun.strings` — String Utilities (`src/string/immutable.zig`)
  90 | 
  91 | SIMD-accelerated string operations. Use instead of `std.mem` for strings.
  92 | 
  93 | ```zig
  94 | // Searching
  95 | strings.indexOf(haystack, needle)         // ?usize
  96 | strings.contains(haystack, needle)        // bool
  97 | strings.containsChar(haystack, char)      // bool
  98 | strings.indexOfChar(haystack, char)       // ?u32
  99 | strings.indexOfAny(str, comptime chars)   // ?OptionalUsize (SIMD-accelerated)
 100 | 
 101 | // Comparison
 102 | strings.eql(a, b)                                    // bool
 103 | strings.eqlComptime(str, comptime literal)            // bool — optimized
 104 | strings.eqlCaseInsensitiveASCII(a, b, comptime true)  // 3rd arg = check_len
 105 | 
 106 | // Prefix/Suffix
 107 | strings.startsWith(str, prefix)                    // bool
 108 | strings.endsWith(str, suffix)                      // bool
 109 | strings.hasPrefixComptime(str, comptime prefix)    // bool — optimized
 110 | strings.hasSuffixComptime(str, comptime suffix)    // bool — optimized
 111 | 
 112 | // Trimming
 113 | strings.trim(str, comptime chars)    // strip from both ends
 114 | strings.trimSpaces(str)              // strip whitespace
 115 | 
 116 | // Encoding conversions
 117 | strings.toUTF8Alloc(allocator, utf16)          // ![]u8
 118 | strings.toUTF16Alloc(allocator, utf8)          // !?[]u16
 119 | strings.toUTF8FromLatin1(allocator, latin1)    // !?Managed(u8)
 120 | strings.firstNonASCII(slice)                   // ?u32
 121 | ```
 122 | 
 123 | Bun handles UTF-8, Latin-1, and UTF-16/WTF-16 because JSC uses Latin-1 and UTF-16 internally. Latin-1 is NOT UTF-8 — bytes 128-255 are single chars in Latin-1 but invalid UTF-8.
 124 | 
 125 | ### `bun.String` (`src/string.zig`)
 126 | 
 127 | Bridges Zig and JavaScriptCore. Prefer over `ZigString` in new code.
 128 | 
 129 | ```zig
 130 | const s = bun.String.cloneUTF8(utf8_slice);    // copies into WTFStringImpl
 131 | const s = bun.String.borrowUTF8(utf8_slice);   // no copy, caller keeps alive
 132 | const utf8 = s.toUTF8(allocator);              // ZigString.Slice
 133 | defer utf8.deinit();
 134 | const js_value = s.toJS(globalObject);
 135 | 
 136 | // Create a JS string value directly from UTF-8 bytes:
 137 | const js_str = try bun.String.createUTF8ForJS(globalObject, utf8_slice);
 138 | ```
 139 | 
 140 | ## `bun.path` — Path Manipulation (`src/resolver/resolve_path.zig`)
 141 | 
 142 | Use instead of `std.fs.path`. Platform param: `.auto` (current platform), `.posix`, `.windows`, `.loose` (both separators).
 143 | 
 144 | ```zig
 145 | // Join paths — uses threadlocal buffer, result must be copied if it needs to persist
 146 | bun.path.join(&.{ dir, filename }, .auto)
 147 | bun.path.joinZ(&.{ dir, filename }, .auto)  // null-terminated
 148 | 
 149 | // Join into a caller-provided buffer
 150 | bun.path.joinStringBuf(&buf, &.{ a, b }, .auto)
 151 | bun.path.joinStringBufZ(&buf, &.{ a, b }, .auto)  // null-terminated
 152 | 
 153 | // Resolve against an absolute base (like Node.js path.resolve)
 154 | bun.path.joinAbsString(cwd, &.{ relative_path }, .auto)
 155 | bun.path.joinAbsStringBufZ(cwd, &buf, &.{ relative_path }, .auto)
 156 | 
 157 | // Path components
 158 | bun.path.dirname(path, .auto)
 159 | bun.path.basename(path)
 160 | 
 161 | // Relative path between two absolute paths
 162 | bun.path.relative(from, to)
 163 | bun.path.relativeAlloc(allocator, from, to)
 164 | 
 165 | // Normalize (resolve `.` and `..`)
 166 | bun.path.normalizeBuf(path, &buf, .auto)
 167 | 
 168 | // Null-terminate a path into a buffer
 169 | bun.path.z(path, &buf)  // returns [:0]const u8
 170 | ```
 171 | 
 172 | Use `bun.PathBuffer` for path buffers: `var buf: bun.PathBuffer = undefined;`
 173 | 
 174 | For pooled path buffers (avoids 64KB stack allocations on Windows):
 175 | 
 176 | ```zig
 177 | const buf = bun.path_buffer_pool.get();
 178 | defer bun.path_buffer_pool.put(buf);
 179 | ```
 180 | 
 181 | ## URL Parsing
 182 | 
 183 | Prefer `bun.jsc.URL` (WHATWG-compliant, backed by WebKit C++) over `bun.URL.parse` (internal, doesn't properly handle errors or invalid URLs).
 184 | 
 185 | ```zig
 186 | // Parse a URL string (returns null if invalid)
 187 | const url = bun.jsc.URL.fromUTF8(href_string) orelse return error.InvalidURL;
 188 | defer url.deinit();
 189 | 
 190 | url.protocol()   // bun.String
 191 | url.pathname()   // bun.String
 192 | url.search()     // bun.String
 193 | url.hash()       // bun.String (includes leading '#')
 194 | url.port()       // u32 (maxInt(u32) if not set, otherwise u16 range)
 195 | 
 196 | // NOTE: host/hostname are SWAPPED vs JS:
 197 | url.host()       // hostname WITHOUT port (opposite of JS!)
 198 | url.hostname()   // hostname WITH port (opposite of JS!)
 199 | 
 200 | // Normalize a URL string (percent-encode, punycode, etc.)
 201 | const normalized = bun.jsc.URL.hrefFromString(bun.String.borrowUTF8(input));
 202 | if (normalized.tag == .Dead) return error.InvalidURL;
 203 | defer normalized.deref();
 204 | 
 205 | // Join base + relative URLs
 206 | const joined = bun.jsc.URL.join(base_str, relative_str);
 207 | defer joined.deref();
 208 | 
 209 | // Convert between file paths and file:// URLs
 210 | const file_url = bun.jsc.URL.fileURLFromString(path_str);     // path → file://
 211 | const file_path = bun.jsc.URL.pathFromFileURL(url_str);       // file:// → path
 212 | ```
 213 | 
 214 | ## MIME Types (`src/http/MimeType.zig`)
 215 | 
 216 | ```zig
 217 | const MimeType = bun.http.MimeType;
 218 | 
 219 | // Look up by file extension (without leading dot)
 220 | const mime = MimeType.byExtension("html");          // MimeType{ .value = "text/html", .category = .html }
 221 | const mime = MimeType.byExtensionNoDefault("xyz");  // ?MimeType (null if unknown)
 222 | 
 223 | // Category checks
 224 | mime.category  // .javascript, .css, .html, .json, .image, .text, .wasm, .font, .video, .audio, ...
 225 | mime.category.isCode()
 226 | ```
 227 | 
 228 | Common constants: `MimeType.javascript`, `MimeType.json`, `MimeType.html`, `MimeType.css`, `MimeType.text`, `MimeType.wasm`, `MimeType.ico`, `MimeType.other`.
 229 | 
 230 | ## Memory & Allocators
 231 | 
 232 | **Use `bun.default_allocator` for almost everything.** It's backed by mimalloc.
 233 | 
 234 | `bun.handleOom(expr)` converts `error.OutOfMemory` into a crash without swallowing other errors:
 235 | 
 236 | ```zig
 237 | const buf = bun.handleOom(allocator.alloc(u8, size));  // correct
 238 | // NOT: allocator.alloc(u8, size) catch bun.outOfMemory()  — could swallow non-OOM errors
 239 | ```
 240 | 
 241 | ## Environment Variables (`src/env_var.zig`)
 242 | 
 243 | Type-safe, cached environment variable accessors via `bun.env_var`:
 244 | 
 245 | ```zig
 246 | bun.env_var.HOME.get()                              // ?[]const u8
 247 | bun.env_var.CI.get()                                // ?bool
 248 | bun.env_var.BUN_CONFIG_DNS_TIME_TO_LIVE_SECONDS.get() // u64 (has default: 30)
 249 | ```
 250 | 
 251 | ## Logging (`src/output.zig`)
 252 | 
 253 | ```zig
 254 | const log = bun.Output.scoped(.MY_FEATURE, .visible);  // .hidden = opt-in via BUN_DEBUG_MY_FEATURE=1
 255 | log("processing {d} items", .{count});
 256 | 
 257 | // Color output (convenience wrappers auto-detect TTY):
 258 | bun.Output.pretty("<green>success<r>: {s}\n", .{msg});
 259 | bun.Output.prettyErrorln("<red>error<r>: {s}", .{msg});
 260 | ```
 261 | 
 262 | ## Spawning Subprocesses (`src/bun.js/api/bun/process.zig`)
 263 | 
 264 | Use `bun.spawnSync` instead of `std.process.Child`:
 265 | 
 266 | ```zig
 267 | switch (bun.spawnSync(&.{
 268 |     .argv = argv,
 269 |     .envp = null, // inherit parent env
 270 |     .cwd = cwd,
 271 |     .stdout = .buffer,   // capture
 272 |     .stderr = .inherit,  // pass through
 273 |     .stdin = .ignore,
 274 | 
 275 |     .windows = if (bun.Environment.isWindows) .{
 276 |         .loop = bun.jsc.EventLoopHandle.init(bun.jsc.MiniEventLoop.initGlobal(env, null)),
 277 |     },
 278 | }) catch return) {
 279 |     .err => |err| { /* bun.sys.Error */ },
 280 |     .result => |result| {
 281 |         defer result.deinit();
 282 |         const stdout = result.stdout.items;
 283 |         if (result.status.isOK()) { ... }
 284 |     },
 285 | }
 286 | ```
 287 | 
 288 | Options: `argv: []const []const u8`, `envp: ?[*:null]?[*:0]const u8` (null = inherit), `argv0: ?[*:0]const u8`. Stdio: `.inherit`, `.ignore`, `.buffer`.
 289 | 
 290 | ## Common Patterns
 291 | 
 292 | ```zig
 293 | // Read a file
 294 | const contents = switch (bun.sys.File.readFrom(bun.FD.cwd(), path, allocator)) {
 295 |     .result => |bytes| bytes,
 296 |     .err => |err| { globalObject.throwValue(err.toSystemError().toErrorInstance(globalObject)); return .zero; },
 297 | };
 298 | 
 299 | // Create directories recursively
 300 | bun.makePath(dir.stdDir(), sub_path) catch |err| { ... };
 301 | 
 302 | // Hashing
 303 | bun.hash(bytes)    // u64 — wyhash
 304 | bun.hash32(bytes)  // u32
 305 | ```
```


---
## src/CLAUDE.md

```
   1 | ## Zig
   2 | 
   3 | Syntax reminders:
   4 | 
   5 | - Private fields are fully supported in Zig with the `#` prefix. `struct { #foo: u32 };` makes a struct with a private field named `#foo`.
   6 | - Decl literals in Zig are recommended. `const decl: Decl = .{ .binding = 0, .value = 0 };`
   7 | 
   8 | Conventions:
   9 | 
  10 | - Prefer `@import` at the **bottom** of the file, but the auto formatter will move them so you don't need to worry about it.
  11 | - **Never** use `@import()` inline inside of functions. **Always** put them at the bottom of the file or containing struct. Imports in Zig are free of side-effects, so there's no such thing as a "dynamic" import.
  12 | - You must be patient with the build.
  13 | 
  14 | ## Prefer Bun APIs over `std`
  15 | 
  16 | **Always use `bun.*` APIs instead of `std.*`.** The `bun` namespace (`@import("bun")`) provides cross-platform wrappers that preserve OS error info and never use `unreachable`. Using `std.fs`, `std.posix`, or `std.os` directly is wrong in this codebase.
  17 | 
  18 | | Instead of                                                   | Use                                  |
  19 | | ------------------------------------------------------------ | ------------------------------------ |
  20 | | `std.base64`                                                 | `bun.base64`                         |
  21 | | `std.crypto.sha{...}`                                        | `bun.sha.Hashers.{...}`              |
  22 | | `std.fs.cwd()`                                               | `bun.FD.cwd()`                       |
  23 | | `std.fs.File`                                                | `bun.sys.File`                       |
  24 | | `std.fs.path.join/dirname/basename`                          | `bun.path.join/dirname/basename`     |
  25 | | `std.mem.eql/indexOf/startsWith` (for strings)               | `bun.strings.eql/indexOf/startsWith` |
  26 | | `std.posix.O` / `std.posix.mode_t` / `std.posix.fd_t`        | `bun.O` / `bun.Mode` / `bun.FD`      |
  27 | | `std.posix.open/read/write/stat/mkdir/unlink/rename/symlink` | `bun.sys.*` equivalents              |
  28 | | `std.process.Child`                                          | `bun.spawnSync`                      |
  29 | 
  30 | ## `bun.sys` — System Calls (`src/sys.zig`)
  31 | 
  32 | All return `Maybe(T)` — a tagged union of `.result: T` or `.err: bun.sys.Error`:
  33 | 
  34 | ```zig
  35 | const fd = switch (bun.sys.open(path, bun.O.RDONLY, 0)) {
  36 |     .result => |fd| fd,
  37 |     .err => |err| return .{ .err = err },
  38 | };
  39 | // Or: const fd = try bun.sys.open(path, bun.O.RDONLY, 0).unwrap();
  40 | ```
  41 | 
  42 | Key functions (all take `bun.FileDescriptor`, not `std.posix.fd_t`):
  43 | 
  44 | - `open`, `openat`, `openA` (non-sentinel) → `Maybe(bun.FileDescriptor)`
  45 | - `read`, `readAll`, `pread` → `Maybe(usize)`
  46 | - `write`, `pwrite`, `writev` → `Maybe(usize)`
  47 | - `stat`, `fstat`, `lstat` → `Maybe(bun.Stat)`
  48 | - `mkdir`, `unlink`, `rename`, `symlink`, `chmod`, `fchmod`, `fchown` → `Maybe(void)`
  49 | - `readlink`, `getFdPath`, `getcwd` → `Maybe` of path slice
  50 | - `getFileSize`, `dup`, `sendfile`, `mmap`
  51 | 
  52 | Use `bun.O.RDONLY`, `bun.O.WRONLY | bun.O.CREAT | bun.O.TRUNC`, etc. for open flags.
  53 | 
  54 | ### `bun.sys.File` (`src/sys/File.zig`)
  55 | 
  56 | Higher-level file handle wrapping `bun.FileDescriptor`:
  57 | 
  58 | ```zig
  59 | // One-shot read: open + read + close
  60 | const bytes = switch (bun.sys.File.readFrom(bun.FD.cwd(), path, allocator)) {
  61 |     .result => |b| b,
  62 |     .err => |err| return .{ .err = err },
  63 | };
  64 | 
  65 | // One-shot write: open + write + close
  66 | switch (bun.sys.File.writeFile(bun.FD.cwd(), path, data)) {
  67 |     .result => {},
  68 |     .err => |err| return .{ .err = err },
  69 | }
  70 | ```
  71 | 
  72 | Key methods:
  73 | 
  74 | - `File.open/openat/makeOpen` → `Maybe(File)` (`makeOpen` creates parent dirs)
  75 | - `file.read/readAll/write/writeAll` — single or looped I/O
  76 | - `file.readToEnd(allocator)` — read entire file into allocated buffer
  77 | - `File.readFrom(dir_fd, path, allocator)` — open + read + close
  78 | - `File.writeFile(dir_fd, path, data)` — open + write + close
  79 | - `file.stat()`, `file.close()`, `file.writer()`, `file.reader()`
  80 | 
  81 | ### `bun.FD` (`src/fd.zig`)
  82 | 
  83 | Cross-platform file descriptor. Use `bun.FD.cwd()` for cwd, `bun.invalid_fd` for sentinel, `fd.close()` to close.
  84 | 
  85 | ### `bun.sys.Error` (`src/sys/Error.zig`)
  86 | 
  87 | Preserves errno, syscall tag, and file path. Convert to JS: `err.toSystemError().toErrorInstance(globalObject)`.
  88 | 
  89 | ## `bun.strings` — String Utilities (`src/string/immutable.zig`)
  90 | 
  91 | SIMD-accelerated string operations. Use instead of `std.mem` for strings.
  92 | 
  93 | ```zig
  94 | // Searching
  95 | strings.indexOf(haystack, needle)         // ?usize
  96 | strings.contains(haystack, needle)        // bool
  97 | strings.containsChar(haystack, char)      // bool
  98 | strings.indexOfChar(haystack, char)       // ?u32
  99 | strings.indexOfAny(str, comptime chars)   // ?OptionalUsize (SIMD-accelerated)
 100 | 
 101 | // Comparison
 102 | strings.eql(a, b)                                    // bool
 103 | strings.eqlComptime(str, comptime literal)            // bool — optimized
 104 | strings.eqlCaseInsensitiveASCII(a, b, comptime true)  // 3rd arg = check_len
 105 | 
 106 | // Prefix/Suffix
 107 | strings.startsWith(str, prefix)                    // bool
 108 | strings.endsWith(str, suffix)                      // bool
 109 | strings.hasPrefixComptime(str, comptime prefix)    // bool — optimized
 110 | strings.hasSuffixComptime(str, comptime suffix)    // bool — optimized
 111 | 
 112 | // Trimming
 113 | strings.trim(str, comptime chars)    // strip from both ends
 114 | strings.trimSpaces(str)              // strip whitespace
 115 | 
 116 | // Encoding conversions
 117 | strings.toUTF8Alloc(allocator, utf16)          // ![]u8
 118 | strings.toUTF16Alloc(allocator, utf8)          // !?[]u16
 119 | strings.toUTF8FromLatin1(allocator, latin1)    // !?Managed(u8)
 120 | strings.firstNonASCII(slice)                   // ?u32
 121 | ```
 122 | 
 123 | Bun handles UTF-8, Latin-1, and UTF-16/WTF-16 because JSC uses Latin-1 and UTF-16 internally. Latin-1 is NOT UTF-8 — bytes 128-255 are single chars in Latin-1 but invalid UTF-8.
 124 | 
 125 | ### `bun.String` (`src/string.zig`)
 126 | 
 127 | Bridges Zig and JavaScriptCore. Prefer over `ZigString` in new code.
 128 | 
 129 | ```zig
 130 | const s = bun.String.cloneUTF8(utf8_slice);    // copies into WTFStringImpl
 131 | const s = bun.String.borrowUTF8(utf8_slice);   // no copy, caller keeps alive
 132 | const utf8 = s.toUTF8(allocator);              // ZigString.Slice
 133 | defer utf8.deinit();
 134 | const js_value = s.toJS(globalObject);
 135 | 
 136 | // Create a JS string value directly from UTF-8 bytes:
 137 | const js_str = try bun.String.createUTF8ForJS(globalObject, utf8_slice);
 138 | ```
 139 | 
 140 | ## `bun.path` — Path Manipulation (`src/resolver/resolve_path.zig`)
 141 | 
 142 | Use instead of `std.fs.path`. Platform param: `.auto` (current platform), `.posix`, `.windows`, `.loose` (both separators).
 143 | 
 144 | ```zig
 145 | // Join paths — uses threadlocal buffer, result must be copied if it needs to persist
 146 | bun.path.join(&.{ dir, filename }, .auto)
 147 | bun.path.joinZ(&.{ dir, filename }, .auto)  // null-terminated
 148 | 
 149 | // Join into a caller-provided buffer
 150 | bun.path.joinStringBuf(&buf, &.{ a, b }, .auto)
 151 | bun.path.joinStringBufZ(&buf, &.{ a, b }, .auto)  // null-terminated
 152 | 
 153 | // Resolve against an absolute base (like Node.js path.resolve)
 154 | bun.path.joinAbsString(cwd, &.{ relative_path }, .auto)
 155 | bun.path.joinAbsStringBufZ(cwd, &buf, &.{ relative_path }, .auto)
 156 | 
 157 | // Path components
 158 | bun.path.dirname(path, .auto)
 159 | bun.path.basename(path)
 160 | 
 161 | // Relative path between two absolute paths
 162 | bun.path.relative(from, to)
 163 | bun.path.relativeAlloc(allocator, from, to)
 164 | 
 165 | // Normalize (resolve `.` and `..`)
 166 | bun.path.normalizeBuf(path, &buf, .auto)
 167 | 
 168 | // Null-terminate a path into a buffer
 169 | bun.path.z(path, &buf)  // returns [:0]const u8
 170 | ```
 171 | 
 172 | Use `bun.PathBuffer` for path buffers: `var buf: bun.PathBuffer = undefined;`
 173 | 
 174 | For pooled path buffers (avoids 64KB stack allocations on Windows):
 175 | 
 176 | ```zig
 177 | const buf = bun.path_buffer_pool.get();
 178 | defer bun.path_buffer_pool.put(buf);
 179 | ```
 180 | 
 181 | ## URL Parsing
 182 | 
 183 | Prefer `bun.jsc.URL` (WHATWG-compliant, backed by WebKit C++) over `bun.URL.parse` (internal, doesn't properly handle errors or invalid URLs).
 184 | 
 185 | ```zig
 186 | // Parse a URL string (returns null if invalid)
 187 | const url = bun.jsc.URL.fromUTF8(href_string) orelse return error.InvalidURL;
 188 | defer url.deinit();
 189 | 
 190 | url.protocol()   // bun.String
 191 | url.pathname()   // bun.String
 192 | url.search()     // bun.String
 193 | url.hash()       // bun.String (includes leading '#')
 194 | url.port()       // u32 (maxInt(u32) if not set, otherwise u16 range)
 195 | 
 196 | // NOTE: host/hostname are SWAPPED vs JS:
 197 | url.host()       // hostname WITHOUT port (opposite of JS!)
 198 | url.hostname()   // hostname WITH port (opposite of JS!)
 199 | 
 200 | // Normalize a URL string (percent-encode, punycode, etc.)
 201 | const normalized = bun.jsc.URL.hrefFromString(bun.String.borrowUTF8(input));
 202 | if (normalized.tag == .Dead) return error.InvalidURL;
 203 | defer normalized.deref();
 204 | 
 205 | // Join base + relative URLs
 206 | const joined = bun.jsc.URL.join(base_str, relative_str);
 207 | defer joined.deref();
 208 | 
 209 | // Convert between file paths and file:// URLs
 210 | const file_url = bun.jsc.URL.fileURLFromString(path_str);     // path → file://
 211 | const file_path = bun.jsc.URL.pathFromFileURL(url_str);       // file:// → path
 212 | ```
 213 | 
 214 | ## MIME Types (`src/http/MimeType.zig`)
 215 | 
 216 | ```zig
 217 | const MimeType = bun.http.MimeType;
 218 | 
 219 | // Look up by file extension (without leading dot)
 220 | const mime = MimeType.byExtension("html");          // MimeType{ .value = "text/html", .category = .html }
 221 | const mime = MimeType.byExtensionNoDefault("xyz");  // ?MimeType (null if unknown)
 222 | 
 223 | // Category checks
 224 | mime.category  // .javascript, .css, .html, .json, .image, .text, .wasm, .font, .video, .audio, ...
 225 | mime.category.isCode()
 226 | ```
 227 | 
 228 | Common constants: `MimeType.javascript`, `MimeType.json`, `MimeType.html`, `MimeType.css`, `MimeType.text`, `MimeType.wasm`, `MimeType.ico`, `MimeType.other`.
 229 | 
 230 | ## Memory & Allocators
 231 | 
 232 | **Use `bun.default_allocator` for almost everything.** It's backed by mimalloc.
 233 | 
 234 | `bun.handleOom(expr)` converts `error.OutOfMemory` into a crash without swallowing other errors:
 235 | 
 236 | ```zig
 237 | const buf = bun.handleOom(allocator.alloc(u8, size));  // correct
 238 | // NOT: allocator.alloc(u8, size) catch bun.outOfMemory()  — could swallow non-OOM errors
 239 | ```
 240 | 
 241 | ## Environment Variables (`src/env_var.zig`)
 242 | 
 243 | Type-safe, cached environment variable accessors via `bun.env_var`:
 244 | 
 245 | ```zig
 246 | bun.env_var.HOME.get()                              // ?[]const u8
 247 | bun.env_var.CI.get()                                // ?bool
 248 | bun.env_var.BUN_CONFIG_DNS_TIME_TO_LIVE_SECONDS.get() // u64 (has default: 30)
 249 | ```
 250 | 
 251 | ## Logging (`src/output.zig`)
 252 | 
 253 | ```zig
 254 | const log = bun.Output.scoped(.MY_FEATURE, .visible);  // .hidden = opt-in via BUN_DEBUG_MY_FEATURE=1
 255 | log("processing {d} items", .{count});
 256 | 
 257 | // Color output (convenience wrappers auto-detect TTY):
 258 | bun.Output.pretty("<green>success<r>: {s}\n", .{msg});
 259 | bun.Output.prettyErrorln("<red>error<r>: {s}", .{msg});
 260 | ```
 261 | 
 262 | ## Spawning Subprocesses (`src/bun.js/api/bun/process.zig`)
 263 | 
 264 | Use `bun.spawnSync` instead of `std.process.Child`:
 265 | 
 266 | ```zig
 267 | switch (bun.spawnSync(&.{
 268 |     .argv = argv,
 269 |     .envp = null, // inherit parent env
 270 |     .cwd = cwd,
 271 |     .stdout = .buffer,   // capture
 272 |     .stderr = .inherit,  // pass through
 273 |     .stdin = .ignore,
 274 | 
 275 |     .windows = if (bun.Environment.isWindows) .{
 276 |         .loop = bun.jsc.EventLoopHandle.init(bun.jsc.MiniEventLoop.initGlobal(env, null)),
 277 |     },
 278 | }) catch return) {
 279 |     .err => |err| { /* bun.sys.Error */ },
 280 |     .result => |result| {
 281 |         defer result.deinit();
 282 |         const stdout = result.stdout.items;
 283 |         if (result.status.isOK()) { ... }
 284 |     },
 285 | }
 286 | ```
 287 | 
 288 | Options: `argv: []const []const u8`, `envp: ?[*:null]?[*:0]const u8` (null = inherit), `argv0: ?[*:0]const u8`. Stdio: `.inherit`, `.ignore`, `.buffer`.
 289 | 
 290 | ## Common Patterns
 291 | 
 292 | ```zig
 293 | // Read a file
 294 | const contents = switch (bun.sys.File.readFrom(bun.FD.cwd(), path, allocator)) {
 295 |     .result => |bytes| bytes,
 296 |     .err => |err| { globalObject.throwValue(err.toSystemError().toErrorInstance(globalObject)); return .zero; },
 297 | };
 298 | 
 299 | // Create directories recursively
 300 | bun.makePath(dir.stdDir(), sub_path) catch |err| { ... };
 301 | 
 302 | // Hashing
 303 | bun.hash(bytes)    // u64 — wyhash
 304 | bun.hash32(bytes)  // u32
 305 | ```
```


---
## src/bun.js/bindings/libuv/README.md

```
   1 | # libuv copied headers
   2 | 
   3 | These are copied headers from libuv which are used by `bun uv-posix-stubs` to generate stubs which crash with a helpful error message when a NAPI
   4 | module tries to access a libuv function which is not supported in Bun.
   5 | 
   6 | libuv commit hash: bb706f5fe71827f667f0bce532e95ce0698a498d
   7 | 
   8 | ## Generating symbol stubs
   9 | 
  10 | 1. Clone libuv repo using the above hash
  11 | 2. Use the following command to get the list of symbols: `llvm-nm -g libuv.dylib | grep _uv &> symbols.txt`, you're gonna have to clean them up a bit this is not automated sorry ( ͡° ͜ʖ ͡°)
  12 | 3. Update `src/symbol.txt` and `src/linker.lds` and `src/symbols.dyn`
  13 | 4. Update the `symbols` list in `generate_uv_posix_stubs.ts`
  14 | 5. Run `bun uv-posix-stubs`
```


---
## src/bun.js/bindings/node/http/llhttp/README.md

```
   1 | Sources are from [llhttp](https://github.com/nodejs/llhttp) 9.3.0 (36151b9a7d6320072e24e472a769a5e09f9e969d)
   2 | 
   3 | Keep this in sync with:
   4 | 
   5 | - `src/bun.js/bindings/ProcessBindingHTTPParser.cpp`
   6 | - `packages/bun-types/overrides.d.ts`
   7 | 
   8 | ```
   9 | npm ci && make
  10 | ```
  11 | 
  12 | then copy:
  13 | 
  14 | - ./build/llhttp.h
  15 | - ./build/c/llhttp.c
  16 | - ./src/native/api.h
  17 | - ./src/native/api.c
  18 | - ./src/native/http.c
```


---
## src/bun.js/bindings/v8/AGENTS.md

```
   1 | # V8 C++ API Implementation Guide
   2 | 
   3 | This directory contains Bun's implementation of the V8 C++ API on top of JavaScriptCore. This allows native Node.js modules that use V8 APIs to work with Bun.
   4 | 
   5 | ## Architecture Overview
   6 | 
   7 | Bun implements V8 APIs by creating a compatibility layer that:
   8 | 
   9 | - Maps V8's `Local<T>` handles to JSC's `JSValue` system
  10 | - Uses handle scopes to manage memory lifetimes similar to V8
  11 | - Provides V8-compatible object layouts that inline V8 functions can read
  12 | - Manages tagged pointers for efficient value representation
  13 | 
  14 | For detailed background, see the blog series:
  15 | 
  16 | - [Part 1: Introduction and challenges](https://bun.com/blog/how-bun-supports-v8-apis-without-using-v8-part-1.md)
  17 | - [Part 2: Memory layout and object representation](https://bun.com/blog/how-bun-supports-v8-apis-without-using-v8-part-2.md)
  18 | - [Part 3: Garbage collection and primitives](https://bun.com/blog/how-bun-supports-v8-apis-without-using-v8-part-3.md)
  19 | 
  20 | ## Directory Structure
  21 | 
  22 | ```
  23 | src/bun.js/bindings/v8/
  24 | ├── v8.h                    # Main header with V8_UNIMPLEMENTED macro
  25 | ├── v8_*.h                  # V8 compatibility headers
  26 | ├── V8*.h                   # V8 class headers (Number, String, Object, etc.)
  27 | ├── V8*.cpp                 # V8 class implementations
  28 | ├── shim/                   # Internal implementation details
  29 | │   ├── Handle.h            # Handle and ObjectLayout implementation
  30 | │   ├── HandleScopeBuffer.h # Handle scope memory management
  31 | │   ├── TaggedPointer.h     # V8-style tagged pointer implementation
  32 | │   ├── Map.h               # V8 Map objects for inline function compatibility
  33 | │   ├── GlobalInternals.h   # V8 global state management
  34 | │   ├── InternalFieldObject.h # Objects with internal fields
  35 | │   └── Oddball.h           # Primitive values (undefined, null, true, false)
  36 | ├── node.h                  # Node.js module registration compatibility
  37 | └── real_v8.h              # Includes real V8 headers when needed
  38 | ```
  39 | 
  40 | ## Implementing New V8 APIs
  41 | 
  42 | ### 1. Create Header and Implementation Files
  43 | 
  44 | Create `V8NewClass.h`:
  45 | 
  46 | ```cpp
  47 | #pragma once
  48 | 
  49 | #include "v8.h"
  50 | #include "V8Local.h"
  51 | #include "V8Isolate.h"
  52 | 
  53 | namespace v8 {
  54 | 
  55 | class NewClass : public Data {
  56 | public:
  57 |     BUN_EXPORT static Local<NewClass> New(Isolate* isolate, /* parameters */);
  58 |     BUN_EXPORT /* return_type */ SomeMethod() const;
  59 | 
  60 |     // Add other methods as needed
  61 | };
  62 | 
  63 | } // namespace v8
  64 | ```
  65 | 
  66 | Create `V8NewClass.cpp`:
  67 | 
  68 | ```cpp
  69 | #include "V8NewClass.h"
  70 | #include "V8HandleScope.h"
  71 | #include "v8_compatibility_assertions.h"
  72 | 
  73 | ASSERT_V8_TYPE_LAYOUT_MATCHES(v8::NewClass)
  74 | 
  75 | namespace v8 {
  76 | 
  77 | Local<NewClass> NewClass::New(Isolate* isolate, /* parameters */)
  78 | {
  79 |     // Implementation - typically:
  80 |     // 1. Create JSC value
  81 |     // 2. Get current handle scope
  82 |     // 3. Create local handle
  83 |     return isolate->currentHandleScope()->createLocal<NewClass>(isolate->vm(), /* JSC value */);
  84 | }
  85 | 
  86 | /* return_type */ NewClass::SomeMethod() const
  87 | {
  88 |     // Implementation - typically:
  89 |     // 1. Convert this Local to JSValue via localToJSValue()
  90 |     // 2. Perform JSC operations
  91 |     // 3. Return converted result
  92 |     auto jsValue = localToJSValue();
  93 |     // ... JSC operations ...
  94 |     return /* result */;
  95 | }
  96 | 
  97 | } // namespace v8
  98 | ```
  99 | 
 100 | ### 2. Add Symbol Exports
 101 | 
 102 | For each new C++ method, you must add the mangled symbol names to multiple files:
 103 | 
 104 | #### a. Add to `src/napi/napi.zig`
 105 | 
 106 | Find the `V8API` struct (around line 1801) and add entries for both GCC/Clang and MSVC:
 107 | 
 108 | ```zig
 109 | const V8API = if (!bun.Environment.isWindows) struct {
 110 |     // ... existing functions ...
 111 |     pub extern fn _ZN2v88NewClass3NewEPNS_7IsolateE/* parameters */() *anyopaque;
 112 |     pub extern fn _ZNK2v88NewClass10SomeMethodEv() *anyopaque;
 113 | } else struct {
 114 |     // ... existing functions ...
 115 |     pub extern fn @"?New@NewClass@v8@@SA?AV?$Local@VNewClass@v8@@@2@PEAVIsolate@2@/* parameters */@Z"() *anyopaque;
 116 |     pub extern fn @"?SomeMethod@NewClass@v8@@QEBA/* return_type */XZ"() *anyopaque;
 117 | };
 118 | ```
 119 | 
 120 | **To get the correct mangled names:**
 121 | 
 122 | For **GCC/Clang** (Unix):
 123 | 
 124 | ```bash
 125 | # Build your changes first
 126 | bun bd --help  # This compiles your code
 127 | 
 128 | # Extract symbols
 129 | nm build/CMakeFiles/bun-debug.dir/src/bun.js/bindings/v8/V8NewClass.cpp.o | grep "T _ZN2v8"
 130 | ```
 131 | 
 132 | For **MSVC** (Windows):
 133 | 
 134 | ```powershell
 135 | # Use the provided PowerShell script in the comments:
 136 | dumpbin .\build\CMakeFiles\bun-debug.dir\src\bun.js\bindings\v8\V8NewClass.cpp.obj /symbols | where-object { $_.Contains(' v8::') } | foreach-object { (($_ -split "\|")[1] -split " ")[1] } | ForEach-Object { "extern fn @`"${_}`"() *anyopaque;" }
 137 | ```
 138 | 
 139 | #### b. Add to Symbol Files
 140 | 
 141 | Add to `src/symbols.txt` (without leading underscore):
 142 | 
 143 | ```
 144 | _ZN2v88NewClass3NewEPNS_7IsolateE...
 145 | _ZNK2v88NewClass10SomeMethodEv
 146 | ```
 147 | 
 148 | Add to `src/symbols.dyn` (with leading underscore and semicolons):
 149 | 
 150 | ```
 151 | {
 152 |     __ZN2v88NewClass3NewEPNS_7IsolateE...;
 153 |     __ZNK2v88NewClass10SomeMethodEv;
 154 | }
 155 | ```
 156 | 
 157 | **Note:** `src/symbols.def` is Windows-only and typically doesn't contain V8 symbols.
 158 | 
 159 | ### 3. Add Tests
 160 | 
 161 | Create tests in `test/v8/v8-module/main.cpp`:
 162 | 
 163 | ```cpp
 164 | void test_new_class_feature(const FunctionCallbackInfo<Value> &info) {
 165 |     Isolate* isolate = info.GetIsolate();
 166 | 
 167 |     // Test your new V8 API
 168 |     Local<NewClass> obj = NewClass::New(isolate, /* parameters */);
 169 |     auto result = obj->SomeMethod();
 170 | 
 171 |     // Print results for comparison with Node.js
 172 |     std::cout << "Result: " << result << std::endl;
 173 | 
 174 |     info.GetReturnValue().Set(Undefined(isolate));
 175 | }
 176 | ```
 177 | 
 178 | Add the test to the registration section:
 179 | 
 180 | ```cpp
 181 | void Init(Local<Object> exports, Local<Value> module, Local<Context> context) {
 182 |     // ... existing functions ...
 183 |     NODE_SET_METHOD(exports, "test_new_class_feature", test_new_class_feature);
 184 | }
 185 | ```
 186 | 
 187 | Add test case to `test/v8/v8.test.ts`:
 188 | 
 189 | ```typescript
 190 | describe("NewClass", () => {
 191 |   it("can use new feature", async () => {
 192 |     await checkSameOutput("test_new_class_feature", []);
 193 |   });
 194 | });
 195 | ```
 196 | 
 197 | ### 4. Handle Special Cases
 198 | 
 199 | #### Objects with Internal Fields
 200 | 
 201 | If implementing objects that need internal fields, extend `InternalFieldObject`:
 202 | 
 203 | ```cpp
 204 | // In your .h file
 205 | class MyObject : public InternalFieldObject {
 206 |     // ... implementation
 207 | };
 208 | ```
 209 | 
 210 | #### Primitive Values
 211 | 
 212 | For primitive values, ensure they work with the `Oddball` system in `shim/Oddball.h`.
 213 | 
 214 | #### Template Classes
 215 | 
 216 | For `ObjectTemplate` or `FunctionTemplate` implementations, see existing patterns in `V8ObjectTemplate.cpp` and `V8FunctionTemplate.cpp`.
 217 | 
 218 | ## Memory Management Guidelines
 219 | 
 220 | ### Handle Scopes
 221 | 
 222 | - All V8 values must be created within an active handle scope
 223 | - Use `isolate->currentHandleScope()->createLocal<T>()` to create handles
 224 | - Handle scopes automatically clean up when destroyed
 225 | 
 226 | ### JSC Integration
 227 | 
 228 | - Use `localToJSValue()` to convert V8 handles to JSC values
 229 | - Use `JSC::WriteBarrier` for heap-allocated references
 230 | - Implement `visitChildren()` for custom heap objects
 231 | 
 232 | ### Tagged Pointers
 233 | 
 234 | - Small integers (±2^31) are stored directly as Smis
 235 | - Objects use pointer tagging with map pointers
 236 | - Doubles are stored in object layouts with special maps
 237 | 
 238 | ## Testing Strategy
 239 | 
 240 | ### Comprehensive Testing
 241 | 
 242 | The V8 test suite compares output between Node.js and Bun for the same C++ code:
 243 | 
 244 | 1. **Install Phase**: Sets up identical module builds for Node.js and Bun
 245 | 2. **Build Phase**: Compiles native modules using node-gyp
 246 | 3. **Test Phase**: Runs identical C++ functions and compares output
 247 | 
 248 | ### Test Categories
 249 | 
 250 | - **Primitives**: undefined, null, booleans, numbers, strings
 251 | - **Objects**: creation, property access, internal fields
 252 | - **Arrays**: creation, length, iteration, element access
 253 | - **Functions**: callbacks, templates, argument handling
 254 | - **Memory**: handle scopes, garbage collection, external data
 255 | - **Advanced**: templates, inheritance, error handling
 256 | 
 257 | ### Adding New Tests
 258 | 
 259 | 1. Add C++ test function to `test/v8/v8-module/main.cpp`
 260 | 2. Register function in the module exports
 261 | 3. Add test case to `test/v8/v8.test.ts` using `checkSameOutput()`
 262 | 4. Run with: `bun bd test test/v8/v8.test.ts -t "your test name"`
 263 | 
 264 | ## Debugging Tips
 265 | 
 266 | ### Build and Test
 267 | 
 268 | ```bash
 269 | # Build debug version (takes ~5 minutes)
 270 | bun bd --help
 271 | 
 272 | # Run V8 tests
 273 | bun bd test test/v8/v8.test.ts
 274 | 
 275 | # Run specific test
 276 | bun bd test test/v8/v8.test.ts -t "can create small integer"
 277 | ```
 278 | 
 279 | ### Common Issues
 280 | 
 281 | **Symbol Not Found**: Ensure mangled names are correctly added to `napi.zig` and symbol files.
 282 | 
 283 | **Segmentation Fault**: Usually indicates inline V8 functions are reading incorrect memory layouts. Check `Map` setup and `ObjectLayout` structure.
 284 | 
 285 | **GC Issues**: Objects being freed prematurely. Ensure proper `WriteBarrier` usage and `visitChildren()` implementation.
 286 | 
 287 | **Type Mismatches**: Use `v8_compatibility_assertions.h` macros to verify type layouts match V8 expectations.
 288 | 
 289 | ### Debug Logging
 290 | 
 291 | Use `V8_UNIMPLEMENTED()` macro for functions not yet implemented:
 292 | 
 293 | ```cpp
 294 | void MyClass::NotYetImplemented() {
 295 |     V8_UNIMPLEMENTED();
 296 | }
 297 | ```
 298 | 
 299 | ## Advanced Topics
 300 | 
 301 | ### Inline Function Compatibility
 302 | 
 303 | Many V8 functions are inline and compiled into native modules. The memory layout must exactly match what these functions expect:
 304 | 
 305 | - Objects start with tagged pointer to `Map`
 306 | - Maps have instance type at offset 12
 307 | - Handle scopes store tagged pointers
 308 | - Primitive values at fixed global offsets
 309 | 
 310 | ### Cross-Platform Considerations
 311 | 
 312 | - Symbol mangling differs between GCC/Clang and MSVC
 313 | - Handle calling conventions (JSC uses System V on Unix)
 314 | - Ensure `BUN_EXPORT` visibility on all public functions
 315 | - Test on all target platforms via CI
 316 | 
 317 | ## Contributing
 318 | 
 319 | When contributing V8 API implementations:
 320 | 
 321 | 1. **Follow existing patterns** in similar classes
 322 | 2. **Add comprehensive tests** that compare with Node.js
 323 | 3. **Update all symbol files** with correct mangled names
 324 | 4. **Document any special behavior** or limitations
 325 | 
 326 | For questions about V8 API implementation, refer to the blog series linked above or examine existing implementations in this directory.
```


---
## src/bun.js/bindings/v8/CLAUDE.md

```
   1 | # V8 C++ API Implementation Guide
   2 | 
   3 | This directory contains Bun's implementation of the V8 C++ API on top of JavaScriptCore. This allows native Node.js modules that use V8 APIs to work with Bun.
   4 | 
   5 | ## Architecture Overview
   6 | 
   7 | Bun implements V8 APIs by creating a compatibility layer that:
   8 | 
   9 | - Maps V8's `Local<T>` handles to JSC's `JSValue` system
  10 | - Uses handle scopes to manage memory lifetimes similar to V8
  11 | - Provides V8-compatible object layouts that inline V8 functions can read
  12 | - Manages tagged pointers for efficient value representation
  13 | 
  14 | For detailed background, see the blog series:
  15 | 
  16 | - [Part 1: Introduction and challenges](https://bun.com/blog/how-bun-supports-v8-apis-without-using-v8-part-1.md)
  17 | - [Part 2: Memory layout and object representation](https://bun.com/blog/how-bun-supports-v8-apis-without-using-v8-part-2.md)
  18 | - [Part 3: Garbage collection and primitives](https://bun.com/blog/how-bun-supports-v8-apis-without-using-v8-part-3.md)
  19 | 
  20 | ## Directory Structure
  21 | 
  22 | ```
  23 | src/bun.js/bindings/v8/
  24 | ├── v8.h                    # Main header with V8_UNIMPLEMENTED macro
  25 | ├── v8_*.h                  # V8 compatibility headers
  26 | ├── V8*.h                   # V8 class headers (Number, String, Object, etc.)
  27 | ├── V8*.cpp                 # V8 class implementations
  28 | ├── shim/                   # Internal implementation details
  29 | │   ├── Handle.h            # Handle and ObjectLayout implementation
  30 | │   ├── HandleScopeBuffer.h # Handle scope memory management
  31 | │   ├── TaggedPointer.h     # V8-style tagged pointer implementation
  32 | │   ├── Map.h               # V8 Map objects for inline function compatibility
  33 | │   ├── GlobalInternals.h   # V8 global state management
  34 | │   ├── InternalFieldObject.h # Objects with internal fields
  35 | │   └── Oddball.h           # Primitive values (undefined, null, true, false)
  36 | ├── node.h                  # Node.js module registration compatibility
  37 | └── real_v8.h              # Includes real V8 headers when needed
  38 | ```
  39 | 
  40 | ## Implementing New V8 APIs
  41 | 
  42 | ### 1. Create Header and Implementation Files
  43 | 
  44 | Create `V8NewClass.h`:
  45 | 
  46 | ```cpp
  47 | #pragma once
  48 | 
  49 | #include "v8.h"
  50 | #include "V8Local.h"
  51 | #include "V8Isolate.h"
  52 | 
  53 | namespace v8 {
  54 | 
  55 | class NewClass : public Data {
  56 | public:
  57 |     BUN_EXPORT static Local<NewClass> New(Isolate* isolate, /* parameters */);
  58 |     BUN_EXPORT /* return_type */ SomeMethod() const;
  59 | 
  60 |     // Add other methods as needed
  61 | };
  62 | 
  63 | } // namespace v8
  64 | ```
  65 | 
  66 | Create `V8NewClass.cpp`:
  67 | 
  68 | ```cpp
  69 | #include "V8NewClass.h"
  70 | #include "V8HandleScope.h"
  71 | #include "v8_compatibility_assertions.h"
  72 | 
  73 | ASSERT_V8_TYPE_LAYOUT_MATCHES(v8::NewClass)
  74 | 
  75 | namespace v8 {
  76 | 
  77 | Local<NewClass> NewClass::New(Isolate* isolate, /* parameters */)
  78 | {
  79 |     // Implementation - typically:
  80 |     // 1. Create JSC value
  81 |     // 2. Get current handle scope
  82 |     // 3. Create local handle
  83 |     return isolate->currentHandleScope()->createLocal<NewClass>(isolate->vm(), /* JSC value */);
  84 | }
  85 | 
  86 | /* return_type */ NewClass::SomeMethod() const
  87 | {
  88 |     // Implementation - typically:
  89 |     // 1. Convert this Local to JSValue via localToJSValue()
  90 |     // 2. Perform JSC operations
  91 |     // 3. Return converted result
  92 |     auto jsValue = localToJSValue();
  93 |     // ... JSC operations ...
  94 |     return /* result */;
  95 | }
  96 | 
  97 | } // namespace v8
  98 | ```
  99 | 
 100 | ### 2. Add Symbol Exports
 101 | 
 102 | For each new C++ method, you must add the mangled symbol names to multiple files:
 103 | 
 104 | #### a. Add to `src/napi/napi.zig`
 105 | 
 106 | Find the `V8API` struct (around line 1801) and add entries for both GCC/Clang and MSVC:
 107 | 
 108 | ```zig
 109 | const V8API = if (!bun.Environment.isWindows) struct {
 110 |     // ... existing functions ...
 111 |     pub extern fn _ZN2v88NewClass3NewEPNS_7IsolateE/* parameters */() *anyopaque;
 112 |     pub extern fn _ZNK2v88NewClass10SomeMethodEv() *anyopaque;
 113 | } else struct {
 114 |     // ... existing functions ...
 115 |     pub extern fn @"?New@NewClass@v8@@SA?AV?$Local@VNewClass@v8@@@2@PEAVIsolate@2@/* parameters */@Z"() *anyopaque;
 116 |     pub extern fn @"?SomeMethod@NewClass@v8@@QEBA/* return_type */XZ"() *anyopaque;
 117 | };
 118 | ```
 119 | 
 120 | **To get the correct mangled names:**
 121 | 
 122 | For **GCC/Clang** (Unix):
 123 | 
 124 | ```bash
 125 | # Build your changes first
 126 | bun bd --help  # This compiles your code
 127 | 
 128 | # Extract symbols
 129 | nm build/CMakeFiles/bun-debug.dir/src/bun.js/bindings/v8/V8NewClass.cpp.o | grep "T _ZN2v8"
 130 | ```
 131 | 
 132 | For **MSVC** (Windows):
 133 | 
 134 | ```powershell
 135 | # Use the provided PowerShell script in the comments:
 136 | dumpbin .\build\CMakeFiles\bun-debug.dir\src\bun.js\bindings\v8\V8NewClass.cpp.obj /symbols | where-object { $_.Contains(' v8::') } | foreach-object { (($_ -split "\|")[1] -split " ")[1] } | ForEach-Object { "extern fn @`"${_}`"() *anyopaque;" }
 137 | ```
 138 | 
 139 | #### b. Add to Symbol Files
 140 | 
 141 | Add to `src/symbols.txt` (without leading underscore):
 142 | 
 143 | ```
 144 | _ZN2v88NewClass3NewEPNS_7IsolateE...
 145 | _ZNK2v88NewClass10SomeMethodEv
 146 | ```
 147 | 
 148 | Add to `src/symbols.dyn` (with leading underscore and semicolons):
 149 | 
 150 | ```
 151 | {
 152 |     __ZN2v88NewClass3NewEPNS_7IsolateE...;
 153 |     __ZNK2v88NewClass10SomeMethodEv;
 154 | }
 155 | ```
 156 | 
 157 | **Note:** `src/symbols.def` is Windows-only and typically doesn't contain V8 symbols.
 158 | 
 159 | ### 3. Add Tests
 160 | 
 161 | Create tests in `test/v8/v8-module/main.cpp`:
 162 | 
 163 | ```cpp
 164 | void test_new_class_feature(const FunctionCallbackInfo<Value> &info) {
 165 |     Isolate* isolate = info.GetIsolate();
 166 | 
 167 |     // Test your new V8 API
 168 |     Local<NewClass> obj = NewClass::New(isolate, /* parameters */);
 169 |     auto result = obj->SomeMethod();
 170 | 
 171 |     // Print results for comparison with Node.js
 172 |     std::cout << "Result: " << result << std::endl;
 173 | 
 174 |     info.GetReturnValue().Set(Undefined(isolate));
 175 | }
 176 | ```
 177 | 
 178 | Add the test to the registration section:
 179 | 
 180 | ```cpp
 181 | void Init(Local<Object> exports, Local<Value> module, Local<Context> context) {
 182 |     // ... existing functions ...
 183 |     NODE_SET_METHOD(exports, "test_new_class_feature", test_new_class_feature);
 184 | }
 185 | ```
 186 | 
 187 | Add test case to `test/v8/v8.test.ts`:
 188 | 
 189 | ```typescript
 190 | describe("NewClass", () => {
 191 |   it("can use new feature", async () => {
 192 |     await checkSameOutput("test_new_class_feature", []);
 193 |   });
 194 | });
 195 | ```
 196 | 
 197 | ### 4. Handle Special Cases
 198 | 
 199 | #### Objects with Internal Fields
 200 | 
 201 | If implementing objects that need internal fields, extend `InternalFieldObject`:
 202 | 
 203 | ```cpp
 204 | // In your .h file
 205 | class MyObject : public InternalFieldObject {
 206 |     // ... implementation
 207 | };
 208 | ```
 209 | 
 210 | #### Primitive Values
 211 | 
 212 | For primitive values, ensure they work with the `Oddball` system in `shim/Oddball.h`.
 213 | 
 214 | #### Template Classes
 215 | 
 216 | For `ObjectTemplate` or `FunctionTemplate` implementations, see existing patterns in `V8ObjectTemplate.cpp` and `V8FunctionTemplate.cpp`.
 217 | 
 218 | ## Memory Management Guidelines
 219 | 
 220 | ### Handle Scopes
 221 | 
 222 | - All V8 values must be created within an active handle scope
 223 | - Use `isolate->currentHandleScope()->createLocal<T>()` to create handles
 224 | - Handle scopes automatically clean up when destroyed
 225 | 
 226 | ### JSC Integration
 227 | 
 228 | - Use `localToJSValue()` to convert V8 handles to JSC values
 229 | - Use `JSC::WriteBarrier` for heap-allocated references
 230 | - Implement `visitChildren()` for custom heap objects
 231 | 
 232 | ### Tagged Pointers
 233 | 
 234 | - Small integers (±2^31) are stored directly as Smis
 235 | - Objects use pointer tagging with map pointers
 236 | - Doubles are stored in object layouts with special maps
 237 | 
 238 | ## Testing Strategy
 239 | 
 240 | ### Comprehensive Testing
 241 | 
 242 | The V8 test suite compares output between Node.js and Bun for the same C++ code:
 243 | 
 244 | 1. **Install Phase**: Sets up identical module builds for Node.js and Bun
 245 | 2. **Build Phase**: Compiles native modules using node-gyp
 246 | 3. **Test Phase**: Runs identical C++ functions and compares output
 247 | 
 248 | ### Test Categories
 249 | 
 250 | - **Primitives**: undefined, null, booleans, numbers, strings
 251 | - **Objects**: creation, property access, internal fields
 252 | - **Arrays**: creation, length, iteration, element access
 253 | - **Functions**: callbacks, templates, argument handling
 254 | - **Memory**: handle scopes, garbage collection, external data
 255 | - **Advanced**: templates, inheritance, error handling
 256 | 
 257 | ### Adding New Tests
 258 | 
 259 | 1. Add C++ test function to `test/v8/v8-module/main.cpp`
 260 | 2. Register function in the module exports
 261 | 3. Add test case to `test/v8/v8.test.ts` using `checkSameOutput()`
 262 | 4. Run with: `bun bd test test/v8/v8.test.ts -t "your test name"`
 263 | 
 264 | ## Debugging Tips
 265 | 
 266 | ### Build and Test
 267 | 
 268 | ```bash
 269 | # Build debug version (takes ~5 minutes)
 270 | bun bd --help
 271 | 
 272 | # Run V8 tests
 273 | bun bd test test/v8/v8.test.ts
 274 | 
 275 | # Run specific test
 276 | bun bd test test/v8/v8.test.ts -t "can create small integer"
 277 | ```
 278 | 
 279 | ### Common Issues
 280 | 
 281 | **Symbol Not Found**: Ensure mangled names are correctly added to `napi.zig` and symbol files.
 282 | 
 283 | **Segmentation Fault**: Usually indicates inline V8 functions are reading incorrect memory layouts. Check `Map` setup and `ObjectLayout` structure.
 284 | 
 285 | **GC Issues**: Objects being freed prematurely. Ensure proper `WriteBarrier` usage and `visitChildren()` implementation.
 286 | 
 287 | **Type Mismatches**: Use `v8_compatibility_assertions.h` macros to verify type layouts match V8 expectations.
 288 | 
 289 | ### Debug Logging
 290 | 
 291 | Use `V8_UNIMPLEMENTED()` macro for functions not yet implemented:
 292 | 
 293 | ```cpp
 294 | void MyClass::NotYetImplemented() {
 295 |     V8_UNIMPLEMENTED();
 296 | }
 297 | ```
 298 | 
 299 | ## Advanced Topics
 300 | 
 301 | ### Inline Function Compatibility
 302 | 
 303 | Many V8 functions are inline and compiled into native modules. The memory layout must exactly match what these functions expect:
 304 | 
 305 | - Objects start with tagged pointer to `Map`
 306 | - Maps have instance type at offset 12
 307 | - Handle scopes store tagged pointers
 308 | - Primitive values at fixed global offsets
 309 | 
 310 | ### Cross-Platform Considerations
 311 | 
 312 | - Symbol mangling differs between GCC/Clang and MSVC
 313 | - Handle calling conventions (JSC uses System V on Unix)
 314 | - Ensure `BUN_EXPORT` visibility on all public functions
 315 | - Test on all target platforms via CI
 316 | 
 317 | ## Contributing
 318 | 
 319 | When contributing V8 API implementations:
 320 | 
 321 | 1. **Follow existing patterns** in similar classes
 322 | 2. **Add comprehensive tests** that compare with Node.js
 323 | 3. **Update all symbol files** with correct mangled names
 324 | 4. **Document any special behavior** or limitations
 325 | 
 326 | For questions about V8 API implementation, refer to the blog series linked above or examine existing implementations in this directory.
```


---
## src/bun.js/event_loop/README.md

```
   1 | # Bun Event Loop Architecture
   2 | 
   3 | This document explains how Bun's event loop works, including task draining, microtasks, process.nextTick, setTimeout ordering, and I/O polling integration.
   4 | 
   5 | ## Overview
   6 | 
   7 | Bun's event loop is built on top of **uSockets** (a cross-platform event loop based on epoll/kqueue) and integrates with **JavaScriptCore's** microtask queue and a custom **process.nextTick** queue. The event loop processes tasks in a specific order to ensure correct JavaScript semantics while maximizing performance.
   8 | 
   9 | ## Core Components
  10 | 
  11 | ### 1. Task Queue (`src/bun.js/event_loop/Task.zig`)
  12 | 
  13 | A tagged pointer union containing various async task types (file I/O, network requests, timers, etc.). Tasks are queued by various subsystems and drained by the main event loop.
  14 | 
  15 | ### 2. Immediate Tasks (`event_loop.zig:14-15`)
  16 | 
  17 | Two separate queues for `setImmediate()`:
  18 | 
  19 | - **`immediate_tasks`**: Tasks to run on the current tick
  20 | - **`next_immediate_tasks`**: Tasks to run on the next tick
  21 | 
  22 | This prevents infinite loops when `setImmediate` is called within a `setImmediate` callback.
  23 | 
  24 | ### 3. Concurrent Task Queue (`event_loop.zig:17`)
  25 | 
  26 | Thread-safe queue for tasks enqueued from worker threads or async operations. These are moved to the main task queue before processing.
  27 | 
  28 | ### 4. Deferred Task Queue (`src/bun.js/event_loop/DeferredTaskQueue.zig`)
  29 | 
  30 | For operations that should be batched and deferred until after microtasks drain (e.g., buffered HTTP response writes, file sink flushes). This avoids excessive system calls while maintaining responsiveness.
  31 | 
  32 | ### 5. Process.nextTick Queue (`src/bun.js/bindings/JSNextTickQueue.cpp`)
  33 | 
  34 | Node.js-compatible implementation of `process.nextTick()`, which runs before microtasks but after each task.
  35 | 
  36 | ### 6. Microtask Queue (JavaScriptCore VM)
  37 | 
  38 | Built-in JSC microtask queue for promises and queueMicrotask.
  39 | 
  40 | ## Event Loop Flow
  41 | 
  42 | ### Main Tick Flow (`event_loop.zig:477-513`)
  43 | 
  44 | ```
  45 | ┌─────────────────────────────────────┐
  46 | │  1. Tick concurrent tasks           │ ← Move tasks from concurrent queue
  47 | └──────────────┬──────────────────────┘
  48 |                │
  49 |                ▼
  50 | ┌─────────────────────────────────────┐
  51 | │  2. Process GC timer                │
  52 | └──────────────┬──────────────────────┘
  53 |                │
  54 |                ▼
  55 | ┌─────────────────────────────────────┐
  56 | │  3. Drain regular task queue        │ ← tickQueueWithCount()
  57 | │     For each task:                  │
  58 | │       - Run task                    │
  59 | │       - Release weak refs           │
  60 | │       - Drain microtasks            │
  61 | │     (See detailed flow below)       │
  62 | └──────────────┬──────────────────────┘
  63 |                │
  64 |                ▼
  65 | ┌─────────────────────────────────────┐
  66 | │  4. Handle rejected promises        │
  67 | └─────────────────────────────────────┘
  68 | ```
  69 | 
  70 | ### autoTick Flow (`event_loop.zig:349-401`)
  71 | 
  72 | This is called when the event loop is active and needs to wait for I/O:
  73 | 
  74 | ```
  75 | ┌─────────────────────────────────────┐
  76 | │  1. Tick immediate tasks            │ ← setImmediate() callbacks
  77 | └──────────────┬──────────────────────┘
  78 |                │
  79 |                ▼
  80 | ┌─────────────────────────────────────┐
  81 | │  2. Update date header timer        │
  82 | └──────────────┬──────────────────────┘
  83 |                │
  84 |                ▼
  85 | ┌─────────────────────────────────────┐
  86 | │  3. Process GC timer                │
  87 | └──────────────┬──────────────────────┘
  88 |                │
  89 |                ▼
  90 | ┌─────────────────────────────────────┐
  91 | │  4. Poll I/O via uSockets            │ ← epoll_wait/kevent with timeout
  92 | │     (epoll_kqueue.c:251-320)        │
  93 | │     - Dispatch ready polls          │
  94 | │     - Each I/O event treated as task│
  95 | └──────────────┬──────────────────────┘
  96 |                │
  97 |                ▼
  98 | ┌─────────────────────────────────────┐
  99 | │  5. Drain timers (POSIX)            │ ← setTimeout/setInterval callbacks
 100 | └──────────────┬──────────────────────┘
 101 |                │
 102 |                ▼
 103 | ┌─────────────────────────────────────┐
 104 | │  6. Call VM.onAfterEventLoop()      │
 105 | └──────────────┬──────────────────────┘
 106 |                │
 107 |                ▼
 108 | ┌─────────────────────────────────────┐
 109 | │  7. Handle rejected promises        │
 110 | └─────────────────────────────────────┘
 111 | ```
 112 | 
 113 | ## Task Draining Algorithm
 114 | 
 115 | ### For Regular Tasks (`Task.zig:97-512`)
 116 | 
 117 | For each task dequeued from the task queue:
 118 | 
 119 | ```
 120 | ┌─────────────────────────────────────────────────────────────┐
 121 | │ FOR EACH TASK in task queue:                                │
 122 | │                                                              │
 123 | │   1. RUN THE TASK (Task.zig:135-506)                        │
 124 | │      └─> Execute task.runFromJSThread() or equivalent       │
 125 | │                                                              │
 126 | │   2. DRAIN MICROTASKS (Task.zig:508)                        │
 127 | │      └─> drainMicrotasksWithGlobal()                        │
 128 | │          │                                                   │
 129 | │          ├─> RELEASE WEAK REFS (event_loop.zig:129)         │
 130 | │          │   └─> VM.releaseWeakRefs()                       │
 131 | │          │                                                   │
 132 | │          ├─> CALL JSC__JSGlobalObject__drainMicrotasks()    │
 133 | │          │   (ZigGlobalObject.cpp:2793-2840)                │
 134 | │          │   │                                               │
 135 | │          │   ├─> IF nextTick queue exists and not empty:    │
 136 | │          │   │   └─> Call processTicksAndRejections()       │
 137 | │          │   │       (ProcessObjectInternals.ts:295-335)    │
 138 | │          │   │       │                                       │
 139 | │          │   │       └─> DO-WHILE loop:                     │
 140 | │          │   │           ├─> Process ALL nextTick callbacks │
 141 | │          │   │           │   (with try/catch & async ctx)   │
 142 | │          │   │           │                                   │
 143 | │          │   │           └─> drainMicrotasks()              │
 144 | │          │   │               (promises, queueMicrotask)     │
 145 | │          │   │           WHILE queue not empty              │
 146 | │          │   │                                               │
 147 | │          │   └─> ALWAYS call vm.drainMicrotasks() again     │
 148 | │          │       (safety net for any remaining microtasks)  │
 149 | │          │                                                   │
 150 | │          └─> RUN DEFERRED TASK QUEUE (event_loop.zig:136-138)│
 151 | │              └─> deferred_tasks.run()                       │
 152 | │                  (buffered writes, file sink flushes, etc.) │
 153 | │                                                              │
 154 | └─────────────────────────────────────────────────────────────┘
 155 | ```
 156 | 
 157 | ### Key Points
 158 | 
 159 | #### Process.nextTick Ordering (`ZigGlobalObject.cpp:2818-2829`)
 160 | 
 161 | The process.nextTick queue is special:
 162 | 
 163 | - It runs **before** microtasks
 164 | - After processing **all** nextTick callbacks in the current batch, microtasks are drained
 165 | - This creates batched processing with interleaving between nextTick generations and promises:
 166 | 
 167 | ```javascript
 168 | Promise.resolve().then(() => console.log("promise 1"));
 169 | process.nextTick(() => {
 170 |   console.log("nextTick 1");
 171 |   Promise.resolve().then(() => console.log("promise 2"));
 172 | });
 173 | process.nextTick(() => console.log("nextTick 2"));
 174 | 
 175 | // Output:
 176 | // nextTick 1
 177 | // nextTick 2
 178 | // promise 1
 179 | // promise 2
 180 | ```
 181 | 
 182 | If a nextTick callback schedules another nextTick, it goes to the next batch:
 183 | 
 184 | ```javascript
 185 | process.nextTick(() => {
 186 |   console.log("nextTick 1");
 187 |   process.nextTick(() => console.log("nextTick 3"));
 188 |   Promise.resolve().then(() => console.log("promise 2"));
 189 | });
 190 | process.nextTick(() => console.log("nextTick 2"));
 191 | Promise.resolve().then(() => console.log("promise 1"));
 192 | 
 193 | // Output:
 194 | // nextTick 1
 195 | // nextTick 2
 196 | // promise 1
 197 | // promise 2
 198 | // nextTick 3
 199 | ```
 200 | 
 201 | The implementation (`ProcessObjectInternals.ts:295-335`):
 202 | 
 203 | ```typescript
 204 | function processTicksAndRejections() {
 205 |   var tock;
 206 |   do {
 207 |     while ((tock = queue.shift()) !== null) {
 208 |       // Run the callback with async context
 209 |       try {
 210 |         callback(...args);
 211 |       } catch (e) {
 212 |         reportUncaughtException(e);
 213 |       }
 214 |     }
 215 | 
 216 |     drainMicrotasks(); // ← Drain promises after each batch
 217 |   } while (!queue.isEmpty());
 218 | }
 219 | ```
 220 | 
 221 | #### Deferred Task Queue (`DeferredTaskQueue.zig:44-61`)
 222 | 
 223 | Runs after microtasks to batch operations:
 224 | 
 225 | - Used for buffered HTTP writes, file sink flushes
 226 | - Prevents re-entrancy issues
 227 | - Balances latency vs. throughput
 228 | 
 229 | The queue maintains a map of `(pointer, task_fn)` pairs and runs each task. If a task returns `true`, it remains in the queue for the next drain; if `false`, it's removed.
 230 | 
 231 | ## I/O Polling Integration
 232 | 
 233 | ### uSockets Event Loop (`epoll_kqueue.c:251-320`)
 234 | 
 235 | The I/O poll is integrated into the event loop via `us_loop_run_bun_tick()`:
 236 | 
 237 | ```
 238 | ┌─────────────────────────────────────────────────────────────┐
 239 | │ us_loop_run_bun_tick():                                      │
 240 | │                                                              │
 241 | │   1. EMIT PRE-CALLBACK (us_internal_loop_pre)               │
 242 | │                                                              │
 243 | │   2. CALL Bun__JSC_onBeforeWait(jsc_vm)                     │
 244 | │      └─> Notify VM we're about to block                     │
 245 | │                                                              │
 246 | │   3. POLL I/O                                               │
 247 | │      ├─> epoll_pwait2() [Linux]                             │
 248 | │      └─> kevent64() [macOS/BSD]                             │
 249 | │          └─> Block with timeout until I/O ready             │
 250 | │                                                              │
 251 | │   4. FOR EACH READY POLL:                                   │
 252 | │      │                                                       │
 253 | │      ├─> Check events & errors                              │
 254 | │      │                                                       │
 255 | │      └─> us_internal_dispatch_ready_poll()                  │
 256 | │          │                                                   │
 257 | │          └─> This enqueues tasks or callbacks that will:    │
 258 | │              - Add tasks to the concurrent task queue       │
 259 | │              - Eventually trigger drainMicrotasks           │
 260 | │                                                              │
 261 | │   5. EMIT POST-CALLBACK (us_internal_loop_post)             │
 262 | │                                                              │
 263 | └─────────────────────────────────────────────────────────────┘
 264 | ```
 265 | 
 266 | ### I/O Events Handling
 267 | 
 268 | When I/O becomes ready (socket readable/writable, file descriptor ready):
 269 | 
 270 | 1. The poll is dispatched via `us_internal_dispatch_ready_poll()` or `Bun__internal_dispatch_ready_poll()`
 271 | 2. This triggers the appropriate callback **synchronously during the I/O poll phase**
 272 | 3. The callback may:
 273 |    - Directly execute JavaScript (must use `EventLoop.enter()/exit()`)
 274 |    - Enqueue a task to the concurrent task queue for later processing
 275 |    - Update internal state and return (e.g., `FilePoll.onUpdate()`)
 276 | 4. If JavaScript is called via `enter()/exit()`, microtasks are drained when `entered_event_loop_count` reaches 0
 277 | 
 278 | **Important**: I/O callbacks don't automatically get the microtask draining behavior - they must explicitly wrap JS calls in `enter()/exit()` or use `runCallback()` to ensure proper microtask handling. This is why some I/O operations enqueue tasks to the concurrent queue instead of running JavaScript directly.
 279 | 
 280 | ## setTimeout and setInterval Ordering
 281 | 
 282 | Timers are handled differently based on platform:
 283 | 
 284 | ### POSIX (`event_loop.zig:396`)
 285 | 
 286 | ```zig
 287 | ctx.timer.drainTimers(ctx);
 288 | ```
 289 | 
 290 | Timers are drained after I/O polling. Each timer callback:
 291 | 
 292 | 1. Is wrapped in `enter()`/`exit()`
 293 | 2. Triggers microtask draining after execution
 294 | 3. Can enqueue new tasks
 295 | 
 296 | ### Windows
 297 | 
 298 | Uses the uv_timer_t mechanism integrated into the uSockets loop.
 299 | 
 300 | ### Timer vs. setImmediate Ordering
 301 | 
 302 | ```javascript
 303 | setTimeout(() => console.log("timeout"), 0);
 304 | setImmediate(() => console.log("immediate"));
 305 | 
 306 | // Output is typically:
 307 | // immediate
 308 | // timeout
 309 | ```
 310 | 
 311 | This is because:
 312 | 
 313 | - `setImmediate` runs in `tickImmediateTasks()` before I/O polling
 314 | - `setTimeout` fires after I/O polling (even with 0ms)
 315 | - However, this can vary based on timing and event loop state
 316 | 
 317 | ## Enter/Exit Mechanism
 318 | 
 319 | The event loop uses a counter to track when to drain microtasks:
 320 | 
 321 | ```zig
 322 | pub fn enter(this: *EventLoop) void {
 323 |     this.entered_event_loop_count += 1;
 324 | }
 325 | 
 326 | pub fn exit(this: *EventLoop) void {
 327 |     const count = this.entered_event_loop_count;
 328 |     if (count == 1 and !this.virtual_machine.is_inside_deferred_task_queue) {
 329 |         this.drainMicrotasksWithGlobal(this.global, this.virtual_machine.jsc_vm) catch {};
 330 |     }
 331 |     this.entered_event_loop_count -= 1;
 332 | }
 333 | ```
 334 | 
 335 | This ensures microtasks are only drained once per top-level event loop task, even if JavaScript calls into native code which calls back into JavaScript multiple times.
 336 | 
 337 | ## Summary
 338 | 
 339 | The Bun event loop processes work in this order:
 340 | 
 341 | 1. **Immediate tasks** (setImmediate)
 342 | 2. **I/O polling** (epoll/kqueue)
 343 | 3. **Timer callbacks** (setTimeout/setInterval)
 344 | 4. **Regular tasks** from the task queue
 345 |    - For each task:
 346 |      - Run the task
 347 |      - Release weak references
 348 |      - Check for nextTick queue
 349 |        - If active: Run nextTick callbacks, drain microtasks after each
 350 |        - If not: Just drain microtasks
 351 |      - Drain deferred task queue
 352 | 5. **Handle rejected promises**
 353 | 
 354 | This architecture ensures:
 355 | 
 356 | - ✅ Correct Node.js semantics for process.nextTick vs. promises
 357 | - ✅ Efficient batching of I/O operations
 358 | - ✅ Minimal microtask latency
 359 | - ✅ Prevention of infinite loops from self-enqueueing tasks
 360 | - ✅ Proper async context propagation
```


---
## src/bundler/linker_context/README.md

```
   1 | # LinkerContext Documentation
   2 | 
   3 | This directory contains functions on the `LinkerContext` struct which have been logically split up into separate files.
   4 | 
   5 | Many of the functions/files represent a pass or step over the bundle graph or chunks etc.
   6 | 
   7 | ## Overview
   8 | 
   9 | The `LinkerContext` is the central orchestrator for Bun's bundling process. After the parser has created an AST representation of all input files, the `LinkerContext` takes over to perform linking, optimization, code splitting, and final code generation.
  10 | 
  11 | The LinkerContext operates in several main phases:
  12 | 
  13 | ## Main Functions
  14 | 
  15 | ### 1. `load()` - LinkerContext.zig:187
  16 | 
  17 | **Purpose**: Initializes the LinkerContext with bundle data and prepares the graph for linking.
  18 | 
  19 | **What it does**:
  20 | 
  21 | - Sets up the parse graph reference
  22 | - Configures code splitting and logging
  23 | - Loads entry points and reachable files into the graph
  24 | - Initializes wait groups for parallel processing
  25 | - Sets up runtime symbol references (`__esm`, `__commonJS`)
  26 | - Configures module/exports references for different output formats (CJS, IIFE)
  27 | 
  28 | **Key responsibilities**:
  29 | 
  30 | - Graph initialization and configuration
  31 | - Runtime symbol setup
  32 | - Entry point processing
  33 | - Memory management setup
  34 | 
  35 | ### 2. `link()` - LinkerContext.zig:294
  36 | 
  37 | **Purpose**: The main linking orchestrator that coordinates all bundling phases.
  38 | 
  39 | **What it does**:
  40 | 
  41 | 1. Calls `load()` to initialize the context
  42 | 2. Computes source map data if needed
  43 | 3. **Phase 1**: `scanImportsAndExports()` - Analyzes all imports/exports across modules
  44 | 4. **Phase 2**: `treeShakingAndCodeSplitting()` - Eliminates dead code and determines chunk boundaries
  45 | 5. **Phase 3**: `computeChunks()` - Creates the final chunk structure
  46 | 6. **Phase 4**: `computeCrossChunkDependencies()` - Resolves dependencies between chunks
  47 | 7. Follows symbol references to ensure consistency
  48 | 
  49 | **Key responsibilities**:
  50 | 
  51 | - Orchestrates the entire linking pipeline
  52 | - Error handling at each phase
  53 | - Memory corruption checks (in debug builds)
  54 | - Returns the final chunk array
  55 | 
  56 | ### 3. `generateChunksInParallel()` - generateChunksInParallel.zig:1
  57 | 
  58 | **Purpose**: Generates the final output files from chunks using parallel processing.
  59 | 
  60 | **What it does**:
  61 | 
  62 | 1. **Symbol Renaming Phase**: Renames symbols in each chunk in parallel to avoid conflicts
  63 | 2. **Source Map Processing**: Handles line offset calculations for source maps
  64 | 3. **CSS Preparation**: Processes CSS chunks, removing duplicate rules in serial order
  65 | 4. **Code Generation Phase**: Generates compile results for each part in parallel
  66 |    - JavaScript chunks: Generates code for each part range
  67 |    - CSS chunks: Processes CSS imports and generates stylesheets
  68 |    - HTML chunks: Processes HTML files
  69 | 5. **Post-processing Phase**: Finalizes chunks with cross-chunk imports/exports
  70 | 6. **Output Phase**: Either writes files to disk or returns in-memory results
  71 | 
  72 | **Key responsibilities**:
  73 | 
  74 | - Parallel processing coordination
  75 | - Final code generation
  76 | - Source map finalization
  77 | - File output management
  78 | 
  79 | ## Linking Pipeline Files
  80 | 
  81 | ### Core Analysis Phase
  82 | 
  83 | #### `scanImportsAndExports.zig`
  84 | 
  85 | **Purpose**: Analyzes all import/export relationships across the module graph, determining module compatibility, resolving dependencies, and setting up the foundation for code generation. This is the critical first phase of linking that establishes how modules will interact in the final bundle.
  86 | 
  87 | **Core Algorithm**: The function operates in 6 distinct steps, each building on the previous to create a complete understanding of the module graph:
  88 | 
  89 | **Step 1: Determine CommonJS Module Classification**
  90 | This step analyzes import patterns to decide which modules must be treated as CommonJS vs ECMAScript modules, which affects how they're bundled and accessed.
  91 | 
  92 | _What happens_:
  93 | 
  94 | - Examines each import record to understand how modules are being used
  95 | - Marks modules as CommonJS when required by import patterns or file characteristics
  96 | - Sets up wrapper flags that determine code generation strategy
  97 | 
  98 | _Key decision logic_:
  99 | 
 100 | ```javascript
 101 | // Import star or default import from a module with no ES6 exports
 102 | // forces that module to be treated as CommonJS
 103 | import * as ns from "./empty-file"; // Forces './empty-file' to be CJS
 104 | import defaultValue from "./empty-file"; // Forces './empty-file' to be CJS
 105 | 
 106 | // Regular named imports don't force CommonJS treatment
 107 | import { namedExport } from "./empty-file"; // './empty-file' stays ES6 compatible
 108 | ```
 109 | 
 110 | _Critical edge cases handled_:
 111 | 
 112 | - `require()` calls always force the target module to be CommonJS
 113 | - Dynamic imports (`import()`) behave like `require()` when code splitting is disabled
 114 | - Modules with `force_cjs_to_esm` flag get special ESM wrapper treatment
 115 | - Entry points get different wrapper treatment based on output format
 116 | 
 117 | _Example transformation_:
 118 | 
 119 | ```javascript
 120 | // Input: module-a.js (has no exports)
 121 | // No code, just an empty file
 122 | 
 123 | // Input: module-b.js
 124 | import * as a from "./module-a.js";
 125 | console.log(a);
 126 | 
 127 | // Result: module-a.js is marked as exports_kind = .cjs, wrap = .cjs
 128 | // This ensures the namespace object 'a' exists at runtime
 129 | ```
 130 | 
 131 | **Step 2: Dependency Wrapper Propagation**
 132 | This step ensures that any module importing a CommonJS module is properly set up to handle the wrapper functions that will be generated.
 133 | 
 134 | _What happens_:
 135 | 
 136 | - Traverses dependency chains to mark files that need wrapper functions
 137 | - Propagates wrapper requirements up the dependency tree
 138 | - Handles export star statements with dynamic exports
 139 | 
 140 | _Algorithm_:
 141 | 
 142 | ```javascript
 143 | // For each module that needs wrapping:
 144 | function wrap(sourceIndex) {
 145 |   if (alreadyWrapped[sourceIndex]) return;
 146 | 
 147 |   // Mark this module as wrapped
 148 |   flags[sourceIndex].wrap = (isCommonJS ? .cjs : .esm);
 149 | 
 150 |   // Recursively wrap all modules that import this one
 151 |   for (importRecord in allImportsOfThisModule) {
 152 |     wrap(importRecord.sourceIndex);
 153 |   }
 154 | }
 155 | ```
 156 | 
 157 | _Example cascade_:
 158 | 
 159 | ```javascript
 160 | // File hierarchy:
 161 | // entry.js → utils.js → legacy.cjs
 162 | 
 163 | // legacy.cjs (CommonJS module)
 164 | exports.helper = function () {
 165 |   return "help";
 166 | };
 167 | 
 168 | // utils.js (imports CommonJS)
 169 | import { helper } from "./legacy.cjs"; // Forces utils.js to be wrapped
 170 | 
 171 | // entry.js (imports wrapped module)
 172 | import { helper } from "./utils.js"; // Forces entry.js to be wrapped
 173 | 
 174 | // Result: All three files get wrapper functions to maintain compatibility
 175 | ```
 176 | 
 177 | **Step 3: Resolve Export Star Statements**
 178 | This step processes `export * from 'module'` statements by collecting all the actual exports from target modules and making them available in the current module.
 179 | 
 180 | _What happens_:
 181 | 
 182 | - Recursively traverses export star chains to collect all re-exported names
 183 | - Handles export star conflicts when multiple modules export the same name
 184 | - Ignores export stars from CommonJS modules (since their exports aren't statically analyzable)
 185 | - Generates code for expression-style loaders (JSON, CSS modules, etc.)
 186 | 
 187 | _Export star resolution algorithm_:
 188 | 
 189 | ```javascript
 190 | // For: export * from './moduleA'; export * from './moduleB';
 191 | function resolveExportStars(currentModule) {
 192 |   for (exportStarTarget in currentModule.exportStars) {
 193 |     // Skip if target is CommonJS (exports not statically known)
 194 |     if (exportStarTarget.isCommonJS) continue;
 195 | 
 196 |     // Add all named exports from target, except 'default'
 197 |     for (exportName in exportStarTarget.namedExports) {
 198 |       if (exportName === "default") continue; // export * never re-exports default
 199 | 
 200 |       if (!currentModule.resolvedExports[exportName]) {
 201 |         currentModule.resolvedExports[exportName] =
 202 |           exportStarTarget.exports[exportName];
 203 |       } else {
 204 |         // Mark as potentially ambiguous - multiple sources for same name
 205 |         currentModule.resolvedExports[exportName].potentiallyAmbiguous = true;
 206 |       }
 207 |     }
 208 | 
 209 |     // Recursively resolve nested export stars
 210 |     resolveExportStars(exportStarTarget);
 211 |   }
 212 | }
 213 | ```
 214 | 
 215 | _Example resolution_:
 216 | 
 217 | ```javascript
 218 | // constants.js
 219 | export const API_URL = "https://api.example.com";
 220 | export const VERSION = "1.0.0";
 221 | 
 222 | // utils.js
 223 | export const formatDate = date => date.toISOString();
 224 | export const API_URL = "https://dev.api.example.com"; // Conflict!
 225 | 
 226 | // index.js
 227 | export * from "./constants.js";
 228 | export * from "./utils.js";
 229 | 
 230 | // Result: index.js exports formatDate, VERSION, and API_URL (marked as potentially ambiguous)
 231 | // Bundler will emit warning about API_URL conflict
 232 | ```
 233 | 
 234 | _Expression-style loader code generation_:
 235 | During this step, files loaded with expression-style loaders (JSON, CSS modules, text files) have their lazy export statements converted to actual module exports:
 236 | 
 237 | ```javascript
 238 | // styles.module.css → generates:
 239 | var styles_module_default = {
 240 |   container: "container_abc123",
 241 |   button: "button_def456 container_abc123", // includes composes
 242 | };
 243 | 
 244 | // data.json → generates:
 245 | var data_default = { "name": "example", "version": "1.0" };
 246 | ```
 247 | 
 248 | **Step 4: Match Imports with Exports**
 249 | This step connects import statements with their corresponding export definitions, creating the binding relationships needed for code generation.
 250 | 
 251 | _What happens_:
 252 | 
 253 | - For each import in each file, finds the corresponding export definition
 254 | - Handles re-exports by tracing through export chains
 255 | - Creates dependency relationships between parts of different files
 256 | - Handles CommonJS compatibility for import/export objects
 257 | - Creates wrapper parts for modules that need runtime wrappers
 258 | 
 259 | _Import matching algorithm_:
 260 | 
 261 | ```javascript
 262 | // For: import { helper } from './utils.js';
 263 | function matchImport(importRef, importSourceIndex) {
 264 |   let targetModule = importSourceIndex;
 265 |   let targetRef = importRef;
 266 | 
 267 |   // If this import is actually a re-export, follow the chain
 268 |   while (importsToBindMap[targetModule][targetRef]) {
 269 |     const reExportData = importsToBindMap[targetModule][targetRef];
 270 |     targetModule = reExportData.sourceIndex;
 271 |     targetRef = reExportData.importRef;
 272 |   }
 273 | 
 274 |   // Add dependency from importing part to all parts that declare the symbol
 275 |   const declaringParts = symbolToPartsMap[targetModule][targetRef];
 276 |   for (partIndex of declaringParts) {
 277 |     importingPart.dependencies.add({
 278 |       sourceIndex: targetModule,
 279 |       partIndex: partIndex,
 280 |     });
 281 |   }
 282 | }
 283 | ```
 284 | 
 285 | _Example import resolution_:
 286 | 
 287 | ```javascript
 288 | // math.js
 289 | export const PI = 3.14159;
 290 | export function square(x) {
 291 |   return x * x;
 292 | } // Declared in part 0
 293 | 
 294 | // utils.js
 295 | export { PI, square } from "./math.js"; // Re-export in part 0
 296 | 
 297 | // app.js
 298 | import { square } from "./utils.js"; // Part 1 imports square
 299 | console.log(square(5)); // Usage in part 1
 300 | 
 301 | // Result: app.js part 1 depends on math.js part 0 (where square is declared)
 302 | // The re-export through utils.js is tracked but doesn't create additional dependencies
 303 | ```
 304 | 
 305 | _CommonJS compatibility handling_:
 306 | 
 307 | ```javascript
 308 | // For CommonJS entry points in ES module output format:
 309 | if (isEntryPoint && outputFormat === 'esm' && moduleKind === 'cjs') {
 310 |   // Mark exports/module symbols as unbound so they don't get renamed
 311 |   symbols[exportsRef].kind = .unbound; // Keep "exports" name
 312 |   symbols[moduleRef].kind = .unbound;  // Keep "module" name
 313 | }
 314 | ```
 315 | 
 316 | **Step 5: Create Namespace Exports**
 317 | This step generates the namespace export objects that ES6 import star statements and CommonJS interop require.
 318 | 
 319 | _What happens_:
 320 | 
 321 | - Executed in parallel across all reachable files for performance
 322 | - Creates export objects for modules that need them (CommonJS modules, star imports)
 323 | - Resolves ambiguous re-exports by choosing the first declaration found
 324 | - Generates sorted export alias lists for deterministic output
 325 | 
 326 | _Namespace object creation logic_:
 327 | 
 328 | ```javascript
 329 | // For a module with exports: { helper, version, DEFAULT }
 330 | // Creates namespace object like:
 331 | {
 332 |   helper: helper_symbol_ref,
 333 |   version: version_symbol_ref,
 334 |   default: DEFAULT_symbol_ref,
 335 |   [Symbol.toStringTag]: 'Module',
 336 |   __esModule: true // For CommonJS interop
 337 | }
 338 | ```
 339 | 
 340 | _Example_:
 341 | 
 342 | ```javascript
 343 | // utils.js
 344 | export const helper = () => "help";
 345 | export const version = "1.0";
 346 | export default "DEFAULT_VALUE";
 347 | 
 348 | // app.js
 349 | import * as utils from "./utils.js";
 350 | console.log(utils.helper()); // Accesses namespace object
 351 | 
 352 | // Generated namespace object for utils.js:
 353 | var utils_exports = {
 354 |   helper: helper,
 355 |   version: version,
 356 |   default: "DEFAULT_VALUE",
 357 |   __esModule: true,
 358 | };
 359 | ```
 360 | 
 361 | **Step 6: Bind Imports to Exports**
 362 | The final step creates the actual dependency relationships and generates runtime symbol imports for bundler helper functions.
 363 | 
 364 | _What happens_:
 365 | 
 366 | - Generates symbol import declarations for runtime helper functions (`__toESM`, `__toCommonJS`, etc.)
 367 | - Creates entry point dependencies to ensure all exports are included
 368 | - Sets up cross-chunk binding code for code splitting scenarios
 369 | - Handles wrapper function dependencies and exports object dependencies
 370 | 
 371 | _Runtime helper usage examples_:
 372 | 
 373 | ```javascript
 374 | // __toESM: Used when importing CommonJS with ES6 syntax
 375 | import utils from "./commonjs-module.js";
 376 | // Generates: __toESM(require('./commonjs-module.js'))
 377 | 
 378 | // __toCommonJS: Used when requiring ES6 module
 379 | const utils = require("./es6-module.js");
 380 | // Generates: __toCommonJS(es6_module_exports)
 381 | 
 382 | // __require: Used for external require() calls in non-CommonJS output
 383 | const path = require("path");
 384 | // Generates: __require('path')
 385 | 
 386 | // __reExport: Used for export star from external modules
 387 | export * from "external-package";
 388 | // Generates: __reExport(exports, require('external-package'))
 389 | ```
 390 | 
 391 | _Entry point dependency handling_:
 392 | 
 393 | ```javascript
 394 | // For entry points, ensure all exports are included in final bundle
 395 | for (exportAlias of entryPointExports) {
 396 |   const exportDef = resolvedExports[exportAlias];
 397 |   const declaringParts = getPartsDeclaringSymbol(
 398 |     exportDef.sourceIndex,
 399 |     exportDef.ref,
 400 |   );
 401 | 
 402 |   // Add dependencies from entry point to all parts that declare exports
 403 |   entryPointPart.dependencies.addAll(declaringParts);
 404 | }
 405 | ```
 406 | 
 407 | _Wrapper function dependency setup_:
 408 | 
 409 | ```javascript
 410 | // When a module needs wrapping, other modules must depend on its wrapper
 411 | if (targetModule.needsWrapper) {
 412 |   // Import the wrapper function instead of direct module access
 413 |   currentPart.dependencies.add({
 414 |     sourceIndex: targetModule.index,
 415 |     ref: targetModule.wrapperRef, // Points to require_moduleName() function
 416 |   });
 417 | 
 418 |   // For ES6 imports of CommonJS, add __toESM wrapper
 419 |   if (importKind !== "require" && targetModule.isCommonJS) {
 420 |     record.wrapWithToESM = true;
 421 |     generateRuntimeSymbolImport("__toESM");
 422 |   }
 423 | }
 424 | ```
 425 | 
 426 | **Key Data Structures Modified**:
 427 | 
 428 | - `exports_kind[]`: Classification of each module (`.cjs`, `.esm`, `.esm_with_dynamic_fallback`, `.none`)
 429 | - `flags[].wrap`: Wrapper type needed (`.none`, `.cjs`, `.esm`)
 430 | - `resolved_exports[]`: Map of export names to their source definitions
 431 | - `imports_to_bind[]`: Map of import references to their target definitions
 432 | - `parts[].dependencies[]`: Cross-file part dependencies for bundling
 433 | - `import_records[].wrap_with_*`: Flags for runtime wrapper function calls
 434 | 
 435 | **Error Handling**: The function includes comprehensive validation:
 436 | 
 437 | - CSS modules `composes` property validation across files
 438 | - Top-level await compatibility checking
 439 | - Export star ambiguity detection and warning
 440 | - Import resolution failure detection
 441 | 
 442 | **Performance Optimizations**:
 443 | 
 444 | - Step 5 runs in parallel across all files using worker thread pool
 445 | - Symbol table mutations are batched to avoid memory allocations
 446 | - Dependency graph updates use pre-allocated capacity
 447 | - Export star cycle detection prevents infinite loops
 448 | 
 449 | This function is the foundation of Bun's module compatibility system, ensuring that mixed ES6/CommonJS codebases work correctly while enabling optimal bundling strategies.
 450 | 
 451 | #### `doStep5.zig`
 452 | 
 453 | **Purpose**: Creates namespace exports for every file.
 454 | 
 455 | **Key functions**:
 456 | 
 457 | - Generates namespace exports for CommonJS files
 458 | - Handles import star statements
 459 | - Resolves ambiguous re-exports
 460 | - Creates sorted export alias lists
 461 | 
 462 | ### Optimization Phase
 463 | 
 464 | #### `renameSymbolsInChunk.zig`
 465 | 
 466 | **Purpose**: Performs symbol renaming within individual chunks to eliminate naming conflicts, enable minification, and ensure proper scoping isolation. This function is critical for generating final output code where variables can be safely renamed without breaking references.
 467 | 
 468 | **Why Symbol Management is Necessary**: When bundling multiple JavaScript files, Bun faces several fundamental challenges:
 469 | 
 470 | 1. **Namespace Collisions**: Multiple files may use the same variable names, creating conflicts when combined:
 471 | 
 472 |    ```javascript
 473 |    // file-a.js
 474 |    const config = { api: "prod" };
 475 | 
 476 |    // file-b.js
 477 |    const config = { debug: true }; // ← Collision when bundled together
 478 |    ```
 479 | 
 480 | 2. **Scope Preservation**: Each file's original scope boundaries must be maintained even when merged into a single output file.
 481 | 
 482 | 3. **Import/Export Resolution**: References between files need to be tracked and correctly linked in the final bundle.
 483 | 
 484 | 4. **Minification Optimization**: For production builds, identifier names should be shortened for maximum compression while preserving program semantics.
 485 | 
 486 | **Why the Ref System Exists**: Bun's `Ref` struct solves the parallel parsing problem that occurs when processing thousands of files simultaneously:
 487 | 
 488 | ```zig
 489 | pub const Ref = packed struct(u64) {
 490 |     inner_index: u31,        // Symbol index within the source file
 491 |     tag: enum(u2) {          // Type of reference (symbol, invalid, etc.)
 492 |         invalid,
 493 |         allocated_name,
 494 |         source_contents_slice,
 495 |         symbol,
 496 |     },
 497 |     source_index: u31,       // Index of the source file containing the symbol
 498 | }
 499 | ```
 500 | 
 501 | **Core Algorithm**: The function operates by analyzing all symbols within a chunk, computing reserved names that cannot be used, and then applying either minification-based renaming (for optimized builds) or number-based renaming (for readable builds).
 502 | 
 503 | **Phase 1: Reserved Name Computation**
 504 | The function starts by identifying names that cannot be used for renamed symbols:
 505 | 
 506 | _What happens_:
 507 | 
 508 | - Computes initial reserved names based on output format (e.g., browser globals, Node.js builtins)
 509 | - Scans all module scopes in the chunk to find existing symbol names that must be preserved
 510 | - Builds a complete set of "forbidden" identifiers for this chunk
 511 | 
 512 | _Example reserved names_:
 513 | 
 514 | ```javascript
 515 | // For browser output format:
 516 | ["window", "document", "console", "setTimeout", "fetch", ...]
 517 | 
 518 | // For Node.js output format:
 519 | ["require", "module", "exports", "process", "Buffer", "__dirname", ...]
 520 | 
 521 | // Plus any existing identifiers in the code:
 522 | ["myExistingFunction", "API_KEY", "UserClass", ...]
 523 | ```
 524 | 
 525 | **Phase 2: Cross-Chunk Import Analysis**
 526 | Since chunks can import symbols from other chunks, we need to track these external dependencies:
 527 | 
 528 | _What happens_:
 529 | 
 530 | - Collects all imports from other chunks (`chunk.content.javascript.imports_from_other_chunks`)
 531 | - Converts each `Ref` to a `StableRef` for sorting (includes stable source index for deterministic ordering)
 532 | - Sorts imports to ensure consistent renaming across builds
 533 | 
 534 | _StableRef structure_:
 535 | 
 536 | ```zig
 537 | // Enables deterministic cross-chunk symbol ordering
 538 | StableRef {
 539 |     stable_source_index: u32,  // Consistent index across builds
 540 |     ref: Ref,                  // Original symbol reference
 541 | }
 542 | ```
 543 | 
 544 | _Example cross-chunk imports_:
 545 | 
 546 | ```javascript
 547 | // Chunk A exports:
 548 | export const utilityFunction = () => { ... };
 549 | 
 550 | // Chunk B imports and uses:
 551 | import { utilityFunction } from './chunk-a';  // ← Tracked as cross-chunk import
 552 | ```
 553 | 
 554 | **Phase 3A: Minification Path (when `minify_identifiers` is enabled)**
 555 | For production builds, the function uses frequency-based minification for optimal compression:
 556 | 
 557 | _Algorithm steps_:
 558 | 
 559 | 1. **Character Frequency Analysis**:
 560 |    - Analyzes character usage across all files in the chunk
 561 |    - Builds frequency map to generate shortest possible identifiers
 562 |    - Common patterns get shorter names (e.g., `a`, `b`, `c` for most used symbols)
 563 | 
 564 | 2. **Symbol Usage Counting**:
 565 |    - Counts how often each symbol is used throughout the chunk
 566 |    - Prioritizes frequently-used symbols for shortest names
 567 |    - Includes special handling for `exports` and `module` references
 568 | 
 569 | 3. **Slot Allocation**:
 570 |    - Determines available "slots" for minified names at each scope level
 571 |    - Ensures nested scopes don't conflict with parent scopes
 572 |    - Allocates shortest identifiers to most frequently used symbols
 573 | 
 574 | _Example minification output_:
 575 | 
 576 | ```javascript
 577 | // Input:
 578 | function calculateUserMetrics(userData, configuration) {
 579 |   const processedData = processConfiguration(userData, configuration);
 580 |   return generateMetrics(processedData);
 581 | }
 582 | 
 583 | // Minified output:
 584 | function a(b, c) {
 585 |   const d = e(b, c);
 586 |   return f(d);
 587 | }
 588 | ```
 589 | 
 590 | **Phase 3B: Number-Based Path (when minification is disabled)**
 591 | For development builds, uses readable incremental naming:
 592 | 
 593 | _What happens_:
 594 | 
 595 | - Creates a `NumberRenamer` that assigns predictable names
 596 | - Uses patterns like `var_1`, `var_2`, `fn_1`, `fn_2` for conflicting symbols
 597 | - Maintains readable output for debugging while avoiding conflicts
 598 | 
 599 | _Example number-based output_:
 600 | 
 601 | ```javascript
 602 | // Input with conflicts:
 603 | function test() {
 604 |   var x = 1;
 605 | }
 606 | function test2() {
 607 |   var x = 2;
 608 | } // Conflict with first 'x'
 609 | 
 610 | // Number-renamed output:
 611 | function test() {
 612 |   var x = 1;
 613 | }
 614 | function test2() {
 615 |   var x_1 = 2;
 616 | } // Renamed to avoid conflict
 617 | ```
 618 | 
 619 | **Phase 4: Wrapper-Specific Symbol Handling**
 620 | Different module wrapper types require special symbol scoping:
 621 | 
 622 | _CommonJS Wrapper Handling_ (`wrap = .cjs`):
 623 | 
 624 | ```javascript
 625 | // Generated wrapper structure:
 626 | var require_moduleName = __commonJS((exports, module) => {
 627 |   // Original module code here with isolated scope
 628 |   exports.foo = 123;
 629 | });
 630 | ```
 631 | 
 632 | - The wrapper function (`require_moduleName`) is added to top-level scope
 633 | - External imports are hoisted outside the wrapper to top-level scope
 634 | - Module code runs in isolated scope to prevent naming conflicts
 635 | 
 636 | _ESM Wrapper Handling_ (`wrap = .esm`):
 637 | 
 638 | ```javascript
 639 | // Generated wrapper structure:
 640 | var moduleName_exports = {};
 641 | __export(moduleName_exports, { foo: () => foo });
 642 | let init_moduleName = __esm(() => {
 643 |   // Original module code here - variables are hoisted outside
 644 |   foo = 123;
 645 | });
 646 | ```
 647 | 
 648 | - The init function (`init_moduleName`) is added to top-level scope
 649 | - Variables are hoisted outside the wrapper, so no new scope isolation needed
 650 | 
 651 | **Phase 5: Part-by-Part Symbol Processing**
 652 | The function processes each part (logical code section) within files:
 653 | 
 654 | _For each part_:
 655 | 
 656 | 1. **Liveness Check**: Skip dead/unused parts to avoid unnecessary work
 657 | 2. **Declared Symbol Registration**: Add all symbols declared in this part to appropriate scope
 658 | 3. **Scope Traversal**: Recursively process nested scopes (functions, blocks, etc.)
 659 | 4. **Memory Management**: Reset temporary allocations between parts for efficiency
 660 | 
 661 | _Example part processing_:
 662 | 
 663 | ```javascript
 664 | // Part 1: Top-level declarations
 665 | const API_URL = 'https://api.example.com';
 666 | function fetchData() { ... }
 667 | 
 668 | // Part 2: Conditional export
 669 | if (development) {
 670 |   export { debugTools };  // Only included if reachable
 671 | }
 672 | ```
 673 | 
 674 | **Key Data Structures and Ref Methods**:
 675 | 
 676 | _Essential Ref methods used throughout_:
 677 | 
 678 | - `ref.isValid()` - returns `this.tag != .invalid`
 679 | - `ref.sourceIndex()` - returns which file the symbol originated from
 680 | - `ref.innerIndex()` - returns the symbol's index within that file
 681 | - `ref.getSymbol(symbol_table)` - retrieves the actual symbol data
 682 | 
 683 | _Symbol table organization_:
 684 | 
 685 | ```zig
 686 | // Two-dimensional array structure enables fast parallel merging
 687 | symbol_table[source_index][inner_index] = Symbol {
 688 |     original_name: "myVariable",
 689 |     link: renamed_symbol_ref,  // Points to final renamed version
 690 |     // ... other symbol data
 691 | }
 692 | ```
 693 | 
 694 | **Error Handling and Edge Cases**:
 695 | 
 696 | - **Circular Dependencies**: Handles modules that import each other
 697 | - **Reserved Word Conflicts**: Avoids JavaScript keywords and runtime globals
 698 | - **Nested Scope Conflicts**: Ensures inner scopes don't shadow outer symbols incorrectly
 699 | - **Cross-Chunk Reference Integrity**: Maintains symbol connections across chunk boundaries
 700 | 
 701 | **Performance Optimizations**:
 702 | 
 703 | - **Pre-allocated Collections**: Uses capacity hints to avoid dynamic growth
 704 | - **Stable Sorting**: Ensures deterministic output across builds
 705 | - **Memory Pool Reuse**: Resets temporary allocators between operations
 706 | - **Parallel-Safe Design**: Prepares data structures for potential future parallelization
 707 | 
 708 | **Integration with Other Phases**:
 709 | This function runs after chunk computation but before final code generation, ensuring that:
 710 | 
 711 | - All cross-chunk dependencies are known
 712 | - Symbol usage patterns are finalized
 713 | - Scope boundaries are established
 714 | - No further symbol table mutations will occur
 715 | 
 716 | The renamed symbols are then used during final code generation to produce output with optimal identifier names while maintaining semantic correctness.
 717 | 
 718 | ### Chunk Computation Phase
 719 | 
 720 | #### `computeChunks.zig`
 721 | 
 722 | **Purpose**: Determines the final chunk structure based on entry points and code splitting.
 723 | 
 724 | **Key functions**:
 725 | 
 726 | - Creates separate chunks for each entry point
 727 | - Groups related files into chunks
 728 | - Handles CSS chunking strategies
 729 | - Manages HTML chunk creation
 730 | - Assigns unique keys and templates to chunks
 731 | 
 732 | #### `computeCrossChunkDependencies.zig`
 733 | 
 734 | **Purpose**: Resolves dependencies between different chunks.
 735 | 
 736 | **Key functions**:
 737 | 
 738 | - Analyzes imports between chunks
 739 | - Sets up cross-chunk binding code
 740 | - Handles dynamic imports across chunks
 741 | - Manages chunk metadata for dependency resolution
 742 | 
 743 | #### `findAllImportedPartsInJSOrder.zig`
 744 | 
 745 | **Purpose**: Determines the order of parts within JavaScript chunks.
 746 | 
 747 | **Key functions**:
 748 | 
 749 | - Orders files by distance from entry point
 750 | - Handles part dependencies within chunks
 751 | - Manages import precedence
 752 | - Ensures proper evaluation order
 753 | 
 754 | #### `findImportedCSSFilesInJSOrder.zig`
 755 | 
 756 | **Purpose**: Determines CSS file ordering for JavaScript chunks that import CSS.
 757 | 
 758 | **Key functions**:
 759 | 
 760 | - Orders CSS imports within JS chunks
 761 | - Handles CSS dependency resolution
 762 | - Manages CSS-in-JS import patterns
 763 | 
 764 | #### `findImportedFilesInCSSOrder.zig`
 765 | 
 766 | **Purpose**: Determines the import order for CSS files.
 767 | 
 768 | **Key functions**:
 769 | 
 770 | - Processes CSS @import statements
 771 | - Handles CSS dependency chains
 772 | - Manages CSS asset imports
 773 | 
 774 | ### Code Generation Phase
 775 | 
 776 | #### `generateCodeForFileInChunkJS.zig`
 777 | 
 778 | **Purpose**: Generates JavaScript code for a specific file within a chunk.
 779 | 
 780 | **Key functions**:
 781 | 
 782 | - Converts AST statements to code
 783 | - Handles different module formats (ESM, CJS, IIFE)
 784 | - Manages HMR (Hot Module Replacement) code generation
 785 | - Processes wrapper functions and runtime calls
 786 | 
 787 | #### `generateCompileResultForJSChunk.zig`
 788 | 
 789 | **Purpose**: Worker function that generates compile results for JavaScript chunks in parallel.
 790 | 
 791 | **Key functions**:
 792 | 
 793 | - Thread-safe chunk compilation
 794 | - Memory management for worker threads
 795 | - Error handling in parallel context
 796 | - Integration with thread pool
 797 | 
 798 | #### `generateCompileResultForCssChunk.zig`
 799 | 
 800 | **Purpose**: Worker function that generates compile results for CSS chunks in parallel.
 801 | 
 802 | **Key functions**:
 803 | 
 804 | - CSS printing and minification
 805 | - Asset URL resolution
 806 | - CSS import processing
 807 | - Thread-safe CSS compilation
 808 | 
 809 | #### `generateCompileResultForHtmlChunk.zig`
 810 | 
 811 | **Purpose**: Worker function that generates compile results for HTML chunks.
 812 | 
 813 | **Key functions**:
 814 | 
 815 | - HTML processing and transformation
 816 | - Asset reference resolution
 817 | - HTML minification
 818 | - Script/stylesheet injection
 819 | 
 820 | #### `generateCodeForLazyExport.zig`
 821 | 
 822 | **Purpose**: Generates code for expression-style loaders that defer code generation until linking.
 823 | 
 824 | **Key functions**:
 825 | 
 826 | - Deferred code generation for expression-style loaders
 827 | - CSS modules export object creation with local scope names
 828 | - Handles CSS `composes` property resolution across files
 829 | - Converts lazy export statements to proper module exports (CJS or ESM)
 830 | 
 831 | **What are expression-style loaders?**: These are file loaders (like JSON, CSS, text, NAPI, etc.) that generate a JavaScript expression to represent the file content rather than executing imperative code. The expression is wrapped in a lazy export statement during parsing, and actual code generation is deferred until linking when the final export format is known.
 832 | 
 833 | **Example - JSON/Text files**: When you import `data.json` containing `{"name": "example"}`, the expression-style loader creates a lazy export with the expression `{name: "example"}`. During linking, `generateCodeForLazyExport` converts this to:
 834 | 
 835 | ```javascript
 836 | // For ESM output:
 837 | var data_default = { name: "example" };
 838 | 
 839 | // For CJS output:
 840 | module.exports = { name: "example" };
 841 | ```
 842 | 
 843 | **Example - CSS Modules**: For a CSS module file `styles.module.css` with:
 844 | 
 845 | ```css
 846 | .container {
 847 |   background: blue;
 848 | }
 849 | .button {
 850 |   composes: container;
 851 |   border: none;
 852 | }
 853 | ```
 854 | 
 855 | The function generates:
 856 | 
 857 | ```javascript
 858 | var styles_module_default = {
 859 |   container: "container_-MSaAA",
 860 |   button: "container_-MSaAA button_-MSaAA", // includes composed classes
 861 | };
 862 | ```
 863 | 
 864 | The function resolves `composes` relationships by visiting the referenced classes and building template literals that combine the scoped class names.
 865 | 
 866 | ### Statement Processing
 867 | 
 868 | #### `convertStmtsForChunk.zig`
 869 | 
 870 | **Purpose**: Converts and transforms AST statements for final inclusion in output chunks, handling the critical process of adapting module-level statements for different output formats and wrapper contexts.
 871 | 
 872 | **Why this function is necessary**:
 873 | When bundling modules, Bun often needs to wrap module code in runtime functions to preserve module semantics (like namespace objects, CommonJS compatibility, etc.). This creates a challenge: ES module import/export statements MUST remain at the top level of the output file, but the module's actual code might need to be wrapped in a function. This function solves this by carefully separating statements that must stay at the top level from those that can be wrapped.
 874 | 
 875 | **Core responsibilities**:
 876 | 
 877 | 1. **Module Wrapper Management**: Determines which statements can be placed inside wrapper functions vs. which must remain at the top level
 878 | 
 879 | 2. **Import/Export Statement Processing**: Transforms import/export syntax based on output format and bundling context
 880 |    - Converts `export * from 'path'` to import statements when needed
 881 |    - Strips export keywords when bundling (since internal modules don't need exports)
 882 |    - Handles re-export runtime function calls
 883 | 
 884 | 3. **CommonJS Compatibility**: Adds special handling for CommonJS entry points that need both ESM and CJS export objects
 885 | 
 886 | 4. **Statement Placement Strategy**: Distributes statements across four categories:
 887 |    - `outside_wrapper_prefix`: Top-level statements before any wrapper (imports/exports)
 888 |    - `inside_wrapper_prefix`: Code that runs at the start of wrapper functions (re-exports)
 889 |    - `inside_wrapper_suffix`: The main module body (actual code)
 890 |    - `outside_wrapper_suffix`: Code after wrapper functions
 891 | 
 892 | **Key transformation patterns**:
 893 | 
 894 | **Pattern 1: Export Stripping**
 895 | 
 896 | ```javascript
 897 | // Input (when bundling):
 898 | export function greet() { return 'hello'; }
 899 | export const name = 'world';
 900 | export default 42;
 901 | 
 902 | // Output (exports removed since internal to bundle):
 903 | function greet() { return 'hello'; }
 904 | const name = 'world';
 905 | var default = 42;
 906 | ```
 907 | 
 908 | **Pattern 2: Import/Export Statement Extraction**
 909 | When a module needs wrapping (due to namespace preservation), import/export statements are extracted to the top level:
 910 | 
 911 | ```javascript
 912 | // Input module that needs wrapping:
 913 | import * as utils from "./utils.js";
 914 | export const data = utils.process();
 915 | 
 916 | // Output with wrapper:
 917 | import * as utils from "./utils.js"; // ← extracted to outside_wrapper_prefix
 918 | var init_module = __esm(() => {
 919 |   // ← wrapper function
 920 |   const data = utils.process(); // ← inside wrapper
 921 | });
 922 | ```
 923 | 
 924 | **Pattern 3: Re-export Runtime Handling**
 925 | 
 926 | ```javascript
 927 | // Input:
 928 | export * from "./external-module";
 929 | 
 930 | // Output (when external module needs runtime re-export):
 931 | import * as ns from "./external-module"; // ← outside_wrapper_prefix
 932 | __reExport(exports, ns, module.exports); // ← inside_wrapper_prefix (runtime call)
 933 | ```
 934 | 
 935 | **Pattern 4: CommonJS Entry Point Dual Exports**
 936 | For CommonJS entry points, the function creates dual export objects:
 937 | 
 938 | ```javascript
 939 | // Internal ESM export object (no __esModule marker):
 940 | var exports = {};
 941 | 
 942 | // External CommonJS export object (with __esModule marker):
 943 | __reExport(exports, targetModule, module.exports); // module.exports gets __esModule
 944 | ```
 945 | 
 946 | **Example: Complex Module Transformation**
 947 | 
 948 | Input file with mixed imports/exports:
 949 | 
 950 | ```javascript
 951 | // demo.js
 952 | import * as utils from "./utils.js";
 953 | export * from "./constants.js";
 954 | export const greeting = "hello";
 955 | export default function () {
 956 |   return utils.format(greeting);
 957 | }
 958 | 
 959 | // When utils namespace is accessed dynamically elsewhere:
 960 | const prop = "format";
 961 | utils[prop]("test"); // Forces namespace preservation
 962 | ```
 963 | 
 964 | After `convertStmtsForChunk` processing with wrapping enabled:
 965 | 
 966 | ```javascript
 967 | // outside_wrapper_prefix (top-level):
 968 | import * as utils from './utils.js';
 969 | import * as ns_constants from './constants.js';
 970 | 
 971 | // inside_wrapper_prefix (start of wrapper):
 972 | __reExport(exports, ns_constants);
 973 | 
 974 | // inside_wrapper_suffix (main module body in wrapper):
 975 | var init_demo = __esm(() => {
 976 |   const greeting = 'hello';
 977 |   function default() { return utils.format(greeting); }
 978 |   // exports object setup...
 979 | });
 980 | ```
 981 | 
 982 | **Statement processing algorithm**:
 983 | 
 984 | 1. **Analyze context**: Determine if wrapping is needed and if exports should be stripped
 985 | 2. **Process each statement**:
 986 |    - Import statements → Extract to `outside_wrapper_prefix` if wrapping
 987 |    - Export statements → Transform or remove based on bundling context
 988 |    - Regular statements → Place in `inside_wrapper_suffix`
 989 |    - Re-export calls → Generate runtime code in `inside_wrapper_prefix`
 990 | 3. **Handle special cases**: Default exports, re-exports, CommonJS compatibility
 991 | 
 992 | **Critical edge cases handled**:
 993 | 
 994 | - **Export star from external modules**: Converted to import + runtime re-export call
 995 | - **Dynamic namespace access**: Preserves namespace objects when static analysis can't determine access patterns
 996 | - **Mixed module formats**: Handles ESM → CJS conversion while preserving semantics
 997 | - **Circular dependencies**: Ensures proper initialization order through wrapper placement
 998 | 
 999 | This function is essential for maintaining JavaScript module semantics across different output formats while enabling optimal bundling strategies.
1000 | 
1001 | #### `convertStmtsForChunkForDevServer.zig`
1002 | 
1003 | **Purpose**: Special statement conversion for development server (HMR).
1004 | 
1005 | **Key functions**:
1006 | 
1007 | - HMR-specific code generation
1008 | - Development-time optimizations
1009 | - Live reload integration
1010 | 
1011 | ### Post-Processing Phase
1012 | 
1013 | #### `prepareCssAstsForChunk.zig`
1014 | 
1015 | **Purpose**: Prepares CSS ASTs before final processing.
1016 | 
1017 | **Key functions**:
1018 | 
1019 | - CSS rule deduplication
1020 | - CSS optimization passes
1021 | - Asset reference resolution
1022 | 
1023 | #### `postProcessJSChunk.zig`
1024 | 
1025 | **Purpose**: Final processing of JavaScript chunks after code generation.
1026 | 
1027 | **Key functions**:
1028 | 
1029 | - Cross-chunk binding code generation
1030 | - Final minification passes
1031 | - Source map integration
1032 | - Output formatting
1033 | 
1034 | #### `postProcessCSSChunk.zig`
1035 | 
1036 | **Purpose**: Final processing of CSS chunks.
1037 | 
1038 | **Key functions**:
1039 | 
1040 | - CSS rule optimization
1041 | - Asset URL finalization
1042 | - CSS minification
1043 | - Source map generation
1044 | 
1045 | #### `postProcessHTMLChunk.zig`
1046 | 
1047 | **Purpose**: Final processing of HTML chunks.
1048 | 
1049 | **Key functions**:
1050 | 
1051 | - HTML optimization
1052 | - Asset reference injection
1053 | - Script/stylesheet linking
1054 | - HTML minification
1055 | 
1056 | ### Output Phase
1057 | 
1058 | #### `writeOutputFilesToDisk.zig`
1059 | 
1060 | **Purpose**: Writes all generated chunks and assets to the filesystem.
1061 | 
1062 | **Key functions**:
1063 | 
1064 | - File system operations
1065 | - Directory creation
1066 | - Chunk serialization
1067 | - Source map file generation
1068 | - Asset copying
1069 | 
1070 | ## Data Flow
1071 | 
1072 | 1. **Input**: Parsed AST from all source files
1073 | 2. **Load Phase**: Initialize graph and runtime symbols
1074 | 3. **Analysis Phase**: Scan imports/exports, determine module relationships
1075 | 4. **Optimization Phase**: Tree shaking, code splitting, symbol renaming
1076 | 5. **Chunk Phase**: Compute final chunk structure and dependencies
1077 | 6. **Generation Phase**: Generate code for each chunk in parallel
1078 | 7. **Post-processing Phase**: Finalize chunks with cross-chunk code
1079 | 8. **Output Phase**: Write files to disk or return in-memory
1080 | 
1081 | ## Parallelization Strategy
1082 | 
1083 | The LinkerContext makes extensive use of parallel processing:
1084 | 
1085 | - **Symbol renaming**: Each chunk's symbols are renamed in parallel
1086 | - **Code generation**: Each part range is compiled in parallel
1087 | - **CSS processing**: CSS chunks are processed in parallel
1088 | - **Source maps**: Source map calculations are parallelized
1089 | - **Post-processing**: Final chunk processing happens in parallel
1090 | 
1091 | This parallelization significantly improves bundling performance for large applications.
```


---
## src/css/README.md

```
   1 | # CSS
   2 | 
   3 | This is the code for Bun's CSS parser. This code is derived from the [Lightning CSS](https://github.com/parcel-bundler/lightningcss) (huge, huge thanks to Devon Govett and contributors) project and the [Servo](https://github.com/servo/servo) project.
```


---
## src/deps/uucode/README.md

```
   1 | # uucode (Micro/µ Unicode)
   2 | 
   3 | A fast and flexible unicode library, fully configurable at build time.
   4 | 
   5 | ## Basic usage
   6 | 
   7 | ```zig
   8 | const uucode = @import("uucode");
   9 | 
  10 | var cp: u21 = undefined;
  11 | 
  12 | //////////////////////
  13 | // `get` properties
  14 | 
  15 | cp = 0x2200; // ∀
  16 | uucode.get(.general_category, cp) // .symbol_math
  17 | uucode.TypeOf(.general_category) // uucode.types.GeneralCategory
  18 | 
  19 | cp = 0x03C2; // ς
  20 | uucode.get(.simple_uppercase_mapping, cp) // U+03A3 == Σ
  21 | 
  22 | cp = 0x21C1; // ⇁
  23 | uucode.get(.name, cp) // "RIGHTWARDS HARPOON WITH BARB DOWNWARDS"
  24 | 
  25 | // Many of the []const u21 fields need a single item buffer passed to `with`:
  26 | var buffer: [1]u21 = undefined;
  27 | cp = 0x00DF; // ß
  28 | uucode.get(.uppercase_mapping, cp).with(&buffer, cp) // "SS"
  29 | 
  30 | //////////////////////
  31 | // `getAll` to get a group of properties for a code point together.
  32 | 
  33 | cp = 0x03C2; // ς
  34 | 
  35 | // The first argument is the name/index of the table.
  36 | const data = uucode.getAll("0", cp);
  37 | 
  38 | data.simple_uppercase_mapping // U+03A3 == Σ
  39 | data.general_category // .letter_lowercase
  40 | @TypeOf(data) == uucode.TypeOfAll("0")
  41 | 
  42 | //////////////////////
  43 | // utf8.Iterator
  44 | 
  45 | var it = uucode.utf8.Iterator.init("😀😅😻👺");
  46 | it.next(); // 0x1F600
  47 | it.i; // 4 (bytes into the utf8 string)
  48 | it.peek(); // 0x1F605
  49 | it.next(); // 0x1F605
  50 | it.next(); // 0x1F63B
  51 | it.next(); // 0x1F47A
  52 | 
  53 | //////////////////////
  54 | // grapheme.Iterator / grapheme.utf8Iterator
  55 | 
  56 | var it = uucode.grapheme.utf8Iterator("👩🏽‍🚀🇨🇭👨🏻‍🍼")
  57 | 
  58 | // (which is equivalent to:)
  59 | var it = uucode.grapheme.Iterator(uccode.utf8.Iterator).init(.init("👩🏽‍🚀🇨🇭👨🏻‍🍼"));
  60 | 
  61 | // `nextCodePoint` advances one code point at a time, indicating a new grapheme
  62 | // with `is_break = true`.
  63 | it.nextCodePoint(); // { .code_point = 0x1F469; .is_break = false } // 👩
  64 | it.i; // 4 (bytes into the utf8 string)
  65 | 
  66 | it.peekCodePoint(); // { .code_point = 0x1F3FD; .is_break = false } // 🏽
  67 | it.nextCodePoint(); // { .code_point = 0x1F3FD; .is_break = false } // 🏽
  68 | it.nextCodePoint(); // { .code_point = 0x200D; .is_break = false } // Zero width joiner
  69 | it.nextCodePoint(); // { .code_point = 0x1F680; .is_break = true } // 🚀
  70 | 
  71 | // `nextGrapheme` advances until the start of the next grapheme cluster
  72 | const result = it.nextGrapheme(); // { .start = 15; .end = 23 }
  73 | it.i; // "👩🏽‍🚀🇨🇭".len
  74 | str[result.?.start..result.?.end]; // "🇨🇭"
  75 | 
  76 | const result = it.peekGrapheme();
  77 | str[result.?.start..result.?.end]; // "👨🏻‍🍼"
  78 | 
  79 | //////////////////////
  80 | // grapheme.isBreak
  81 | 
  82 | var break_state: uucode.grapheme.BreakState = .default;
  83 | 
  84 | var cp1: u21 = 0x1F469; // 👩
  85 | var cp2: u21 = 0x1F3FD; // 🏽
  86 | uucode.grapheme.isBreak(cp1, cp2, &break_state); // false
  87 | 
  88 | cp1 = cp2;
  89 | cp2 = 0x200D; // Zero width joiner
  90 | uucode.grapheme.isBreak(cp1, cp2, &break_state); // false
  91 | 
  92 | cp1 = cp2;
  93 | cp2 = 0x1F680; // 🚀
  94 | // The combined grapheme cluster is 👩🏽‍🚀 (woman astronaut)
  95 | uucode.grapheme.isBreak(cp1, cp2, &break_state); // false
  96 | 
  97 | cp1 = cp2;
  98 | cp2 = 0x1F468; // 👨
  99 | uucode.grapheme.isBreak(cp1, cp2, &break_state); // true
 100 | 
 101 | //////////////////////
 102 | // x.grapheme.wcwidth{,Next,Remaining} / x.grapheme.utf8Wcwidth
 103 | 
 104 | const str = "ò👨🏻‍❤️‍👨🏿_";
 105 | var it = uucode.grapheme.utf8Iterator(str);
 106 | 
 107 | // Requires the `wcwidth` builtin extension (see below)
 108 | uucode.x.grapheme.wcwidth(it); // 1 for 'ò'
 109 | 
 110 | uucode.x.grapheme.wcwidthNext(&it); // 1 for 'ò'
 111 | const result = it.peekGrapheme();
 112 | str[result.?.start..result.?.end]; // "👨🏻‍❤️‍👨🏿"
 113 | 
 114 | uucode.x.grapheme.wcwidthRemaining(&it); // 3 for "👨🏻‍❤️‍👨🏿_"
 115 | 
 116 | uucode.x.grapheme.utf8Wcwidth(str); // 4 for the whole string
 117 | ```
 118 | 
 119 | See [src/config.zig](./src/config.zig) for the names of all fields.
 120 | 
 121 | ## Configuration
 122 | 
 123 | Only include the Unicode fields you actually use:
 124 | 
 125 | ```zig
 126 | // In `build.zig`:
 127 | if (b.lazyDependency("uucode", .{
 128 |     .target = target,
 129 |     .optimize = optimize,
 130 |     .fields = @as([]const []const u8, &.{
 131 |         "name",
 132 |         "general_category",
 133 |         "case_folding_simple",
 134 |         "is_alphabetic",
 135 |         // ...
 136 |     }),
 137 | })) |dep| {
 138 |     step.root_module.addImport("uucode", dep.module("uucode"));
 139 | }
 140 | ```
 141 | 
 142 | ### Multiple tables
 143 | 
 144 | Fields can be split into multiple tables using `field_0` through `fields_9`, to optimize how fields are stored and accessed (with no code changes needed).
 145 | 
 146 | ```zig
 147 | // In `build.zig`:
 148 | if (b.lazyDependency("uucode", .{
 149 |     .target = target,
 150 |     .optimize = optimize,
 151 |     .fields_0 = @as([]const []const u8, &.{
 152 |         "general_category",
 153 |         "case_folding_simple",
 154 |         "is_alphabetic",
 155 |     }),
 156 |     .fields_1 = @as([]const []const u8, &.{
 157 |         // ...
 158 |     }),
 159 |     .fields_2 = @as([]const []const u8, &.{
 160 |         // ...
 161 |     }),
 162 |     // ... `fields_3` to `fields_9`
 163 | })) |dep| {
 164 |     step.root_module.addImport("uucode", dep.module("uucode"));
 165 | }
 166 | ```
 167 | 
 168 | ### Builtin extensions
 169 | 
 170 | `uucode` includes builtin extensions that add derived properties. Use `extensions` or `extensions_0` through `extensions_9` to include them:
 171 | 
 172 | ```zig
 173 | // In `build.zig`:
 174 | if (b.lazyDependency("uucode", .{
 175 |     .target = target,
 176 |     .optimize = optimize,
 177 |     .extensions = @as([]const []const u8, &.{
 178 |         "wcwidth",
 179 |     }),
 180 |     .fields = @as([]const []const u8, &.{
 181 |         // Make sure to also include the extension's fields here:
 182 |         "wcwidth_standalone",
 183 |         "wcwidth_zero_in_grapheme",
 184 |         ...
 185 |         "general_category",
 186 |     }),
 187 | })) |dep| {
 188 |     step.root_module.addImport("uucode", dep.module("uucode"));
 189 | }
 190 | 
 191 | // In your code:
 192 | uucode.get(.wcwidth_standalone, 0x26F5) // ⛵ == 2
 193 | ```
 194 | 
 195 | See [src/x/config.x.zig](src/x/config.x.zig) for the full list of builtin extensions.
 196 | 
 197 | ### Advanced configuration
 198 | 
 199 | ```zig
 200 | ///////////////////////////////////////////////////////////
 201 | // In `build.zig`:
 202 | 
 203 | b.dependency("uucode", .{
 204 |     .target = target,
 205 |     .optimize = optimize,
 206 |     .build_config_path = b.path("src/build/uucode_config.zig"),
 207 | 
 208 |     // Alternatively, use a string literal:
 209 |     //.@"build_config.zig" = "..."
 210 | })
 211 | 
 212 | ///////////////////////////////////////////////////////////
 213 | // In `src/build/uucode_config.zig`:
 214 | 
 215 | const std = @import("std");
 216 | const config = @import("config.zig");
 217 | 
 218 | // Use `config.x.zig` for builtin extensions:
 219 | const config_x = @import("config.x.zig");
 220 | 
 221 | const d = config.default;
 222 | const wcwidth = config_x.wcwidth;
 223 | 
 224 | // Or build your own extension:
 225 | const emoji_odd_or_even = config.Extension{
 226 |     .inputs = &.{"is_emoji"},
 227 |     .compute = &computeEmojiOddOrEven,
 228 |     .fields = &.{
 229 |         .{ .name = "emoji_odd_or_even", .type = EmojiOddOrEven },
 230 |     },
 231 | };
 232 | 
 233 | fn computeEmojiOddOrEven(
 234 |     allocator: std.mem.Allocator,
 235 |     cp: u21,
 236 |     data: anytype,
 237 |     backing: anytype,
 238 |     tracking: anytype,
 239 | ) std.mem.Allocator.Error!void {
 240 |     // allocator is an ArenaAllocator, so don't worry about freeing
 241 |     _ = allocator;
 242 | 
 243 |     // backing and tracking are only used for slice types (see
 244 |     // src/build/test_build_config.zig for examples).
 245 |     _ = backing;
 246 |     _ = tracking;
 247 | 
 248 |     if (!data.is_emoji) {
 249 |         data.emoji_odd_or_even = .not_emoji;
 250 |     } else if (cp % 2 == 0) {
 251 |         data.emoji_odd_or_even = .even_emoji;
 252 |     } else {
 253 |         data.emoji_odd_or_even = .odd_emoji;
 254 |     }
 255 | }
 256 | 
 257 | // Types must be marked `pub`
 258 | pub const EmojiOddOrEven = enum(u2) {
 259 |     not_emoji,
 260 |     even_emoji,
 261 |     odd_emoji,
 262 | };
 263 | 
 264 | // Configure tables with the `tables` declaration.
 265 | // The only required field is `fields`, and the rest have reasonable defaults.
 266 | pub const tables = [_]config.Table{
 267 |     .{
 268 |         // Optional name, to be able to `getAll("foo")` rather than e.g.
 269 |         // `getAll("0")`
 270 |         .name = "foo",
 271 | 
 272 |         // A two stage table can be slightly faster if the data is small. The
 273 |         // default `.auto` will pick a reasonable value, but to get the
 274 |         // absolute best performance run benchmarks with `.two` or `.three`
 275 |         // on realistic data.
 276 |         .stages = .three,
 277 | 
 278 |         // The default `.auto` value decide whether the final data stage struct
 279 |         // should be a `packed struct` (.@"packed") or a regular Zig `struct`.
 280 |         .packing = .unpacked,
 281 | 
 282 |         .extensions = &.{
 283 |             emoji_odd_or_even,
 284 |             wcwidth,
 285 |         },
 286 | 
 287 |         .fields = &.{
 288 |             // Don't forget to include the extension's fields here.
 289 |             emoji_odd_or_even.field("emoji_odd_or_even"),
 290 |             wcwidth.field("wcwidth_standalone"),
 291 |             wcwidth.field("wcwidth_zero_in_grapheme"),
 292 | 
 293 |             // See `src/config.zig` for everything that can be overriden.
 294 |             // In this example, we're embedding 15 bytes into the `stage3` data,
 295 |             // and only names longer than that need to use the `backing` slice.
 296 |             d.field("name").override(.{
 297 |                 .embedded_len = 15,
 298 |                 .max_offset = 986096, // run once to get the correct number
 299 |             }),
 300 | 
 301 |             d.field("general_category"),
 302 |             d.field("block"),
 303 |             // ...
 304 |         },
 305 |     },
 306 | };
 307 | 
 308 | // Turn on debug logging:
 309 | pub const log_level = .debug;
 310 | 
 311 | ///////////////////////////////////////////////////////////
 312 | // In your code:
 313 | 
 314 | const uucode = @import("uucode");
 315 | 
 316 | uucode.get(.wcwidth_standalone, 0x26F5) // ⛵ == 2
 317 | 
 318 | uucode.get(.emoji_odd_or_even, 0x1F34B) // 🍋 == .odd_emoji
 319 | 
 320 | ```
 321 | 
 322 | ## Code architecture
 323 | 
 324 | The architecture works in a few layers:
 325 | 
 326 | - Layer 1 (`src/build/Ucd.zig`): Parses the Unicode Character Database (UCD).
 327 | - Layer 2 (`src/build/tables.zig`): Generates table data written to a zig file.
 328 | - Layer 3 (`src/root.zig`): Exposes methods to fetch information from the built tables.
 329 | 
 330 | ## History and acknowledgments
 331 | 
 332 | `uucode` began out of work on the [Ghostty terminal](https://ghostty.org/) on [an issue to upgrade dependencies](https://github.com/ghostty-org/ghostty/issues/5694), where the experience modifying [zg](https://codeberg.org/atman/zg/) gave the confidence to build a fresh new library.
 333 | 
 334 | `uucode` builds upon the Unicode performance work done in Ghostty, [as outlined in this excellent Devlog](https://mitchellh.com/writing/ghostty-devlog-006). The 3-stage lookup tables, as mentioned in that Devlog, come from [this article](https://here-be-braces.com/fast-lookup-of-unicode-properties/).
 335 | 
 336 | ## License
 337 | 
 338 | `uucode` is available under an MIT License. See [./LICENSE.md](./LICENSE.md) for the license text and an index of licenses for code used in the repo.
 339 | 
 340 | ## Resources
 341 | 
 342 | See [./RESOURCES.md](./RESOURCES.md) for a list of resources used to build `uucode`.
```


---
## src/js/AGENTS.md

```
   1 | # JavaScript Builtins in Bun
   2 | 
   3 | Write JS builtins for Bun's Node.js compatibility and APIs. Run `bun bd` after changes.
   4 | 
   5 | ## Directory Structure
   6 | 
   7 | - `builtins/` - Individual functions (`*CodeGenerator(vm)` in C++)
   8 | - `node/` - Node.js modules (`node:fs`, `node:path`)
   9 | - `bun/` - Bun modules (`bun:ffi`, `bun:sqlite`)
  10 | - `thirdparty/` - NPM replacements (`ws`, `node-fetch`)
  11 | - `internal/` - Internal modules
  12 | 
  13 | ## Writing Modules
  14 | 
  15 | Modules are NOT ES modules:
  16 | 
  17 | ```typescript
  18 | const EventEmitter = require("node:events"); // String literals only
  19 | const { validateFunction } = require("internal/validators");
  20 | 
  21 | export default {
  22 |   myFunction() {
  23 |     if (!$isCallable(callback)) {
  24 |       throw $ERR_INVALID_ARG_TYPE("cb", "function", callback);
  25 |     }
  26 |   },
  27 | };
  28 | ```
  29 | 
  30 | ## Writing Builtin Functions
  31 | 
  32 | ```typescript
  33 | export function initializeReadableStream(
  34 |   this: ReadableStream,
  35 |   underlyingSource,
  36 |   strategy,
  37 | ) {
  38 |   if (!$isObject(underlyingSource)) {
  39 |     throw new TypeError(
  40 |       "ReadableStream constructor takes an object as first argument",
  41 |     );
  42 |   }
  43 |   $putByIdDirectPrivate(this, "state", $streamReadable);
  44 | }
  45 | ```
  46 | 
  47 | C++ access:
  48 | 
  49 | ```cpp
  50 | object->putDirectBuiltinFunction(vm, globalObject, identifier,
  51 |   readableStreamInitializeReadableStreamCodeGenerator(vm), 0);
  52 | ```
  53 | 
  54 | ## $ Globals and Special Syntax
  55 | 
  56 | **CRITICAL**: Use `.$call` and `.$apply`, never `.call` or `.apply`:
  57 | 
  58 | ```typescript
  59 | // ✗ WRONG - User can tamper
  60 | callback.call(undefined, arg1);
  61 | fn.apply(undefined, args);
  62 | 
  63 | // ✓ CORRECT - Tamper-proof
  64 | callback.$call(undefined, arg1);
  65 | fn.$apply(undefined, args);
  66 | 
  67 | // $ prefix for private APIs
  68 | const arr = $Array.from(...);           // Private globals
  69 | map.$set(key, value);                   // Private methods
  70 | const newArr = $newArrayWithSize(5);    // JSC intrinsics
  71 | $debug("Module loaded:", name);         // Debug (stripped in release)
  72 | $assert(condition, "message");          // Assertions (stripped in release)
  73 | ```
  74 | 
  75 | **Platform detection**: `process.platform` and `process.arch` are inlined and dead-code eliminated
  76 | 
  77 | ## Validation and Errors
  78 | 
  79 | ```typescript
  80 | const { validateFunction } = require("internal/validators");
  81 | 
  82 | function myAPI(callback) {
  83 |   if (!$isCallable(callback)) {
  84 |     throw $ERR_INVALID_ARG_TYPE("callback", "function", callback);
  85 |   }
  86 | }
  87 | ```
  88 | 
  89 | ## Build Process
  90 | 
  91 | `Source TS/JS → Preprocessor → Bundler → C++ Headers`
  92 | 
  93 | 1. Assign numeric IDs (A-Z sorted)
  94 | 2. Replace `$` with `__intrinsic__`, `require("x")` with `$requireId(n)`
  95 | 3. Bundle, convert `export default` to `return`
  96 | 4. Replace `__intrinsic__` with `@`, inline into C++
  97 | 
  98 | ModuleLoader.zig loads modules by numeric ID via `InternalModuleRegistry.cpp`.
  99 | 
 100 | ## Key Rules
 101 | 
 102 | - Use `.$call`/`.$apply` not `.call`/`.apply`
 103 | - String literal `require()` only
 104 | - Export via `export default {}`
 105 | - Use JSC intrinsics for performance
 106 | - Run `bun bd` after changes
```


---
## src/js/CLAUDE.md

```
   1 | # JavaScript Builtins in Bun
   2 | 
   3 | Write JS builtins for Bun's Node.js compatibility and APIs. Run `bun bd` after changes.
   4 | 
   5 | ## Directory Structure
   6 | 
   7 | - `builtins/` - Individual functions (`*CodeGenerator(vm)` in C++)
   8 | - `node/` - Node.js modules (`node:fs`, `node:path`)
   9 | - `bun/` - Bun modules (`bun:ffi`, `bun:sqlite`)
  10 | - `thirdparty/` - NPM replacements (`ws`, `node-fetch`)
  11 | - `internal/` - Internal modules
  12 | 
  13 | ## Writing Modules
  14 | 
  15 | Modules are NOT ES modules:
  16 | 
  17 | ```typescript
  18 | const EventEmitter = require("node:events"); // String literals only
  19 | const { validateFunction } = require("internal/validators");
  20 | 
  21 | export default {
  22 |   myFunction() {
  23 |     if (!$isCallable(callback)) {
  24 |       throw $ERR_INVALID_ARG_TYPE("cb", "function", callback);
  25 |     }
  26 |   },
  27 | };
  28 | ```
  29 | 
  30 | ## Writing Builtin Functions
  31 | 
  32 | ```typescript
  33 | export function initializeReadableStream(
  34 |   this: ReadableStream,
  35 |   underlyingSource,
  36 |   strategy,
  37 | ) {
  38 |   if (!$isObject(underlyingSource)) {
  39 |     throw new TypeError(
  40 |       "ReadableStream constructor takes an object as first argument",
  41 |     );
  42 |   }
  43 |   $putByIdDirectPrivate(this, "state", $streamReadable);
  44 | }
  45 | ```
  46 | 
  47 | C++ access:
  48 | 
  49 | ```cpp
  50 | object->putDirectBuiltinFunction(vm, globalObject, identifier,
  51 |   readableStreamInitializeReadableStreamCodeGenerator(vm), 0);
  52 | ```
  53 | 
  54 | ## $ Globals and Special Syntax
  55 | 
  56 | **CRITICAL**: Use `.$call` and `.$apply`, never `.call` or `.apply`:
  57 | 
  58 | ```typescript
  59 | // ✗ WRONG - User can tamper
  60 | callback.call(undefined, arg1);
  61 | fn.apply(undefined, args);
  62 | 
  63 | // ✓ CORRECT - Tamper-proof
  64 | callback.$call(undefined, arg1);
  65 | fn.$apply(undefined, args);
  66 | 
  67 | // $ prefix for private APIs
  68 | const arr = $Array.from(...);           // Private globals
  69 | map.$set(key, value);                   // Private methods
  70 | const newArr = $newArrayWithSize(5);    // JSC intrinsics
  71 | $debug("Module loaded:", name);         // Debug (stripped in release)
  72 | $assert(condition, "message");          // Assertions (stripped in release)
  73 | ```
  74 | 
  75 | **Platform detection**: `process.platform` and `process.arch` are inlined and dead-code eliminated
  76 | 
  77 | ## Validation and Errors
  78 | 
  79 | ```typescript
  80 | const { validateFunction } = require("internal/validators");
  81 | 
  82 | function myAPI(callback) {
  83 |   if (!$isCallable(callback)) {
  84 |     throw $ERR_INVALID_ARG_TYPE("callback", "function", callback);
  85 |   }
  86 | }
  87 | ```
  88 | 
  89 | ## Build Process
  90 | 
  91 | `Source TS/JS → Preprocessor → Bundler → C++ Headers`
  92 | 
  93 | 1. Assign numeric IDs (A-Z sorted)
  94 | 2. Replace `$` with `__intrinsic__`, `require("x")` with `$requireId(n)`
  95 | 3. Bundle, convert `export default` to `return`
  96 | 4. Replace `__intrinsic__` with `@`, inline into C++
  97 | 
  98 | ModuleLoader.zig loads modules by numeric ID via `InternalModuleRegistry.cpp`.
  99 | 
 100 | ## Key Rules
 101 | 
 102 | - Use `.$call`/`.$apply` not `.call`/`.apply`
 103 | - String literal `require()` only
 104 | - Export via `export default {}`
 105 | - Use JSC intrinsics for performance
 106 | - Run `bun bd` after changes
```


---
## src/js/README.md

```
   1 | # JS Modules
   2 | 
   3 | **TLDR**: If anything here changes, re-run `bun run build`.
   4 | 
   5 | - `./node` contains all `node:*` modules
   6 | - `./bun` contains all `bun:*` modules
   7 | - `./thirdparty` contains npm modules we replace like `ws`
   8 | - `./internal` contains modules that aren't assigned to the module resolver
   9 | 
  10 | Each `.ts`/`.js` file above is assigned a numeric id at compile time and inlined into an array of lazily initialized modules. Internal modules referencing each other is extremely optimized, skipping the module resolver entirely.
  11 | 
  12 | ## Builtins Syntax
  13 | 
  14 | Within these files, the `$` prefix on variables can be used to access private property names as well as JSC intrinsics.
  15 | 
  16 | ```ts
  17 | // Many globals have private versions which are impossible for the user to
  18 | // tamper with. Though, these global variables are auto-prefixed by the bundler.
  19 | const hello = $Array.from(...);
  20 | 
  21 | // Similar situation with prototype values. These aren't autoprefixed since it depends on type.
  22 | something.$then(...);
  23 | map.$set(...);
  24 | 
  25 | // Internal variables we define
  26 | $requireMap.$has("elysia");
  27 | 
  28 | // JSC engine intrinsics. These usually translate directly to bytecode instructions.
  29 | const arr = $newArrayWithSize(5);
  30 | // A side effect of this is that using an intrinsic incorrectly like
  31 | // this will fail to parse and cause a segfault.
  32 | console.log($getInternalField)
  33 | ```
  34 | 
  35 | V8 has a [similar feature](https://v8.dev/blog/embedded-builtins) to this syntax (they use `%` instead)
  36 | 
  37 | On top of this, we have some special functions that are handled by the builtin preprocessor:
  38 | 
  39 | - `require` works, but it must be passed a **string literal** that resolves to a module within `src/js`. This call gets replaced with `$getInternalField($internalModuleRegistry, <number>)`, which directly loads the module by its generated numerical ID, skipping the resolver for inter-internal modules.
  40 | 
  41 | - `$debug()` is exactly like console.log, but is stripped in release builds. It is disabled by default, requiring you to pass one of: `BUN_DEBUG_MODULE_NAME=1`, `BUN_DEBUG_JS=1`, or `BUN_DEBUG_ALL=1`. You can also do `if($debug) {}` to check if debug env var is set.
  42 | 
  43 | - `$assert()` in debug builds will assert the condition, but it is stripped in release builds. If an assertion fails, the program continues to run, but an error is logged in the console containing the original source condition and any extra messages specified.
  44 | 
  45 | - `IS_BUN_DEVELOPMENT` is inlined to be `true` in all development builds.
  46 | 
  47 | - `process.platform` and `process.arch` is properly inlined and DCE'd. Do use this to run different code on different platforms.
  48 | 
  49 | ## Builtin Modules
  50 | 
  51 | Files in `node`, `bun`, `thirdparty`, and `internal` are all bundled as "modules". These go through the preprocessor to construct a JS function, where `export default`/`export function`/etc are converted into a `return` statement. Due to this, non-type `import` statements are not supported.
  52 | 
  53 | By using `export default`, this controls the result of using `require` to import the module. When ESM imports this module (userland), all properties on this object are available as named exports. Named exports are preprocessed into properties on this default object.
  54 | 
  55 | ```ts
  56 | const fs = require("fs"); // load another builtin module
  57 | 
  58 | export default {
  59 |   hello: 2,
  60 |   world: 3,
  61 | };
  62 | ```
  63 | 
  64 | Keep in mind that **these are not ES modules**. `export default` is only syntax sugar to assign to the variable `$exports`, which is actually how the module exports its contents.
  65 | 
  66 | To actually wire up one of these modules to the resolver, that is done separately in `module_resolver.zig`. Maybe in the future we can do codegen for it.
  67 | 
  68 | ## Builtin Functions
  69 | 
  70 | `./functions` contains isolated functions. Each function within is bundled separately, meaning you may not use global variables, non-type `import`s, and even directly referencing the other functions in these files. `require` is still resolved the same way it does in the modules.
  71 | 
  72 | In function files, these are accessible in C++ by using `<file><function>CodeGenerator(vm)`, for example:
  73 | 
  74 | ```c
  75 | object->putDirectBuiltinFunction(
  76 |   vm,
  77 |   globalObject,
  78 |   identifier,
  79 |   // ReadableStream.ts, `function readableStreamToJSON()`
  80 |   // This returns a FunctionExecutable* (extends JSCell*, but not JSFunction*).
  81 |   readableStreamReadableStreamToJSONCodeGenerator(vm),
  82 |   JSC::PropertyAttribute::DontDelete | 0
  83 | );
  84 | ```
  85 | 
  86 | ## Building
  87 | 
  88 | Run `bun run build` to bundle all the builtins. The output is placed in `build/debug/js`, where these files are loaded dynamically by `bun-debug` (an exact filepath is inlined into the binary pointing at where you cloned bun, so moving the binary to another machine may not work). In a release build, these get minified and inlined into the binary (Please commit those generated headers).
  89 | 
  90 | If you change the list of files or functions, you will have to run `bun run build`.
  91 | 
  92 | ## Notes on how the build process works
  93 | 
  94 | _This isn't really required knowledge to use it, but a rough overview of how ./\_codegen/\* works_
  95 | 
  96 | The build process is built on top of Bun's bundler. The first step is scanning all modules and assigning each a numerical ID. The order is determined by an A-Z sort.
  97 | 
  98 | The `$` for private names is actually a lie, and in JSC it actually uses `@`; though that is a syntax error in regular JS/TS, so we opted for better IDE support. So first we have to pre-process the files to spot all instances of `$` at the start of an identifier and we convert it to `__intrinsic__`. We also scan for `require(string)` and replace it with `$requireId(n)` after resolving it to the integer id, which is defined in `./functions/Module.ts`. `export default` is transformed into `return ...;`, however this transform is a little more complicated that a string replace because it supports that not being the final statement, and access to the underlying variable `$exports`, etc.
  99 | 
 100 | The preprocessor is smart enough to not replace `$` in strings, comments, regex, etc. However, it is not a real JS parser and instead a recursive regex-based nightmare, so may hit some edge cases. Yell at Chloe if it breaks.
 101 | 
 102 | The module is then printed like:
 103 | 
 104 | ```ts
 105 | // @ts-nocheck
 106 | $$capture_start$$(function () {
 107 |   const path = __intrinsic__requireId(23);
 108 |   // user code is pasted here
 109 |   return {
 110 |     cool: path,
 111 |   };
 112 | }).$$capture_end$$;
 113 | ```
 114 | 
 115 | This capture thing is used to extract the function declaration afterwards, this is more useful in the functions case where functions can have arguments, or be async functions.
 116 | 
 117 | After bundling, the inner part is extracted, and then `__intrinsic__` is replaced to `@`.
 118 | 
 119 | These can then be inlined into C++ headers and loaded with `createBuiltin`. This is done in `InternalModuleRegistry.cpp`.
```


---
## src/js/eval/README.md

```
   1 | These are not bundled as builtin modules and instead are minified.
```


---
## src/js/internal/util/README.md

```
   1 | # node-inspect-extracted
   2 | 
   3 | Vendored copy of [node-inspect-extracted](https://github.com/hildjj/node-inspect-extracted) with adaptations for Bun.
   4 | Some features not relevant to Bun have been removed. Others might be added or modified.
   5 | 
   6 | This library provides an as-faithful-as-possible implementation of Node.js's
   7 | [`util.inspect`](https://nodejs.org/api/util.html#util_util_inspect_object_options) function.
   8 | 
   9 | This is currently done for compatibility reasons. In the future, this should be replaced with a 100% native implementation.
  10 | 
  11 | ## API
  12 | 
  13 | The following [`util`](https://nodejs.org/api/util.html) functions:
  14 | 
  15 | - [`inspect(object[,showHidden|options[,depth [, colors]]])`](https://nodejs.org/api/util.html#util_util_inspect_object_showhidden_depth_colors)
  16 | - [`format(format[, ...args])`](https://nodejs.org/api/util.html#util_util_format_format_args)
  17 | - [`formatWithOptions(inspectOptions, format[, ...args])`](https://nodejs.org/api/util.html#util_util_formatwithoptions_inspectoptions_format_args)
  18 | 
  19 | <!--And these extras:
  20 | 
  21 | - `stylizeWithColor(str, styleType)`: colorize `str` with ANSI escapes according to the styleType
  22 | - `stylizeWithHTML(str, styleType)`: colorize `str` with HTML span tags
  23 | 
  24 | ## Colors
  25 | 
  26 | If you specify `{colors: true}` in the inspect options, you will get ANSI
  27 | escape codes, just as you would in Node. That's unlikely to be helpful to you
  28 | on the Web, so you might want `stylizeWithHTML`, which is also exported from the package:
  29 | 
  30 | ```js
  31 | inspect(
  32 |   { a: 1 },
  33 |   {
  34 |     compact: false,
  35 |     stylize: stylizeWithHTML,
  36 |   },
  37 | );
  38 | ```
  39 | 
  40 | which yields this ugly HTML:
  41 | 
  42 | ```html
  43 | { a: <span style="color:yellow;">1</span> }
  44 | ```
  45 | 
  46 | If you want better HTML, the [lightly-documented](https://nodejs.org/api/util.html#util_custom_inspection_functions_on_objects) `stylize` option requires
  47 | a function that takes two parameters, a string, and a class name. The mappings
  48 | from class names to colors is in `inspect.styles`, so start with this:
  49 | 
  50 | ```js
  51 | function stylizeWithHTML(str, styleType) {
  52 |   const style = inspect.styles[styleType];
  53 |   if (style !== undefined) {
  54 |     return `<span style="color:${style};">${str}</span>`;
  55 |   }
  56 |   return str;
  57 | }
  58 | ```-->
  59 | 
  60 | ## Known Limitations
  61 | 
  62 | - Objects that have been mangled with `Object.setPrototypeOf`
  63 |   do not retain their original type information.
  64 |   [[bug](https://github.com/hildjj/node-inspect-extracted/issues/3)]
  65 | - `WeakMap` and `WeakSet` will not show their contents, because those contents
  66 |   cannot be iterated over in unprivileged code.
  67 | - Colorful stack traces are not completely accurate with respect to what
  68 |   modules are Node-internal. This doesn't matter on the Web.
  69 | 
  70 | ## LICENSE
  71 | 
  72 | This code is an adaptation of the Node.js internal implementation, mostly from
  73 | the file lib/internal/util/inspect.js, which does not have the Joyent
  74 | copyright header. The maintainers of this package will not assert copyright
  75 | over this code, but will assign ownership to the Node.js contributors, with
  76 | the same license as specified in the Node.js codebase; the portion adapted
  77 | here should all be plain MIT license.
```


---
## src/node-fallbacks/README.md

```
   1 | # Browser polyfills for `bun build --target=browser`
   2 | 
   3 | When using `bun build --target=browser`, if you attempt to import a Node.js module, Bun will load a polyfill for that module in an attempt to let your code still work even though it's not running in Node.js or a server.
   4 | 
   5 | For example, if you import `zlib`, the `node-fallbacks/zlib.js` file will be loaded.
   6 | 
   7 | ## Not used by Bun's runtime
   8 | 
   9 | These files are _not_ used by Bun's runtime. They are only used for the `bun build --target=browser` command.
  10 | 
  11 | If you're interested in contributing to Bun's Node.js compatibility, please see the [`src/js` directory](https://github.com/oven-sh/bun/tree/main/src/js).
```


---
## src/unicode/uucode/CLAUDE.md

```
   1 | # uucode Integration for Grapheme Breaking
   2 | 
   3 | ## What This Is
   4 | 
   5 | This directory contains Bun's integration with the [uucode](https://github.com/jacobsandlund/uucode) Unicode library (vendored at `src/deps/uucode/`). It generates the lookup tables that power Bun's grapheme cluster breaking — including GB9c (Indic Conjunct Break) support.
   6 | 
   7 | The runtime code lives in `src/string/immutable/grapheme.zig`. This directory only contains **build-time** code for regenerating tables.
   8 | 
   9 | ## Architecture
  10 | 
  11 | ```
  12 | src/deps/uucode/           ← Vendored uucode library (MIT, don't modify)
  13 | src/unicode/uucode/        ← THIS DIRECTORY: build-time integration
  14 |   ├── uucode_config.zig    ← Configures which uucode fields to generate
  15 |   ├── grapheme_gen.zig     ← Generator binary: queries uucode → writes tables
  16 |   ├── lut.zig              ← 3-level lookup table generator
  17 |   └── CLAUDE.md            ← You are here
  18 | 
  19 | src/string/immutable/      ← Runtime code (no uucode dependency)
  20 |   ├── grapheme.zig         ← Grapheme break API + precomputed decision table
  21 |   ├── grapheme_tables.zig  ← PRE-GENERATED property tables (committed)
  22 |   └── visible.zig          ← String width calculation (uses grapheme.zig)
  23 | ```
  24 | 
  25 | ## How It Works
  26 | 
  27 | ### Runtime (zero uucode dependency)
  28 | 
  29 | `grapheme.zig` does two table lookups per codepoint pair, with no branching:
  30 | 
  31 | 1. **Property lookup**: `grapheme_tables.zig` maps codepoint → `Properties` (width, grapheme_break enum, emoji_vs_base) via a 3-level lookup table (~100KB)
  32 | 2. **Break decision**: A comptime-precomputed 8KB array maps `(BreakState, gb1, gb2)` → `(break_result, new_state)` covering all 5×17×17 = 1445 permutations
  33 | 
  34 | The break algorithm (including GB9c Indic, GB11 Emoji ZWJ, GB12/13 Regional Indicators) runs only at **comptime** to populate this array. At runtime it's a single array index.
  35 | 
  36 | ### Key Types
  37 | 
  38 | - `GraphemeBreakNoControl` — `enum(u5)` with 17 values (the "no control" variant strips CR/LF/Control since Bun handles those externally)
  39 | - `BreakState` — `enum(u3)` with 5 states: `default`, `regional_indicator`, `extended_pictographic`, `indic_conjunct_break_consonant`, `indic_conjunct_break_linker`
  40 | - `Properties` — `packed struct` with `width: u2`, `grapheme_break: GraphemeBreakNoControl`, `emoji_vs_base: bool`
  41 | 
  42 | ### Table Generation (build-time only)
  43 | 
  44 | `grapheme_gen.zig` is compiled as a standalone binary that:
  45 | 
  46 | 1. Initializes uucode (which parses the UCD data in `src/deps/uucode/ucd/`)
  47 | 2. Iterates all 2^21 codepoints
  48 | 3. Queries `uucode.get(.width, cp)`, `.grapheme_break_no_control`, `.is_emoji_vs_base`
  49 | 4. Feeds them through `lut.zig`'s 3-level table generator
  50 | 5. Writes `grapheme_tables.zig` to stdout
  51 | 
  52 | ## How to Regenerate Tables
  53 | 
  54 | Run this when updating the vendored uucode (e.g., for a new Unicode version):
  55 | 
  56 | ```bash
  57 | zig build generate-grapheme-tables
  58 | ```
  59 | 
  60 | This uses Bun's vendored zig at `vendor/zig/zig`. The generated file is committed at `src/string/immutable/grapheme_tables.zig`.
  61 | 
  62 | **Normal builds never run the generator** — they just compile the committed `grapheme_tables.zig`.
  63 | 
  64 | ## How to Update Unicode Version
  65 | 
  66 | Use the update script:
  67 | 
  68 | ```bash
  69 | # From a local directory (e.g., zig cache after updating build.zig.zon in Ghostty):
  70 | ./scripts/update-uucode.sh ~/.cache/zig/p/uucode-0.2.0-xxxxx/
  71 | 
  72 | # From a URL:
  73 | ./scripts/update-uucode.sh https://deps.files.ghostty.org/uucode-xxxxx.tar.gz
  74 | 
  75 | # Default (uses latest in ~/.cache/zig/p/):
  76 | ./scripts/update-uucode.sh
  77 | ```
  78 | 
  79 | The script handles everything: copies the source, regenerates tables, and prints next steps.
  80 | 
  81 | Manual steps if needed:
  82 | 
  83 | 1. Update `src/deps/uucode/` with the new uucode release (which includes new UCD data)
  84 | 2. Run `vendor/zig/zig build generate-grapheme-tables`
  85 | 3. Verify: `bun bd test test/js/bun/util/stringWidth.test.ts`
  86 | 4. Commit the updated `src/deps/uucode/` and `src/string/immutable/grapheme_tables.zig`
  87 | 
  88 | ## Relationship to Ghostty
  89 | 
  90 | This implementation mirrors [Ghostty's approach](https://github.com/ghostty-org/ghostty/tree/main/src/unicode) (same author as uucode). Key correspondences:
  91 | 
  92 | | Ghostty                        | Bun                                        |
  93 | | ------------------------------ | ------------------------------------------ |
  94 | | `src/unicode/grapheme.zig`     | `src/string/immutable/grapheme.zig`        |
  95 | | `src/unicode/lut.zig`          | `src/unicode/uucode/lut.zig`               |
  96 | | `src/unicode/props_uucode.zig` | `src/unicode/uucode/grapheme_gen.zig`      |
  97 | | `src/unicode/props_table.zig`  | `src/string/immutable/grapheme_tables.zig` |
  98 | | `src/build/uucode_config.zig`  | `src/unicode/uucode/uucode_config.zig`     |
  99 | 
 100 | Differences: Ghostty generates tables every build; Bun pre-generates and commits them. Bun's `grapheme.zig` is fully self-contained with no runtime uucode import.
 101 | 
 102 | ## What `uucode_config.zig` Controls
 103 | 
 104 | This tells uucode which properties to compute into its tables:
 105 | 
 106 | - `width` — derived from `wcwidth_standalone` and `wcwidth_zero_in_grapheme`
 107 | - `grapheme_break_no_control` — the 17-value enum for grapheme break rules
 108 | - `is_emoji_vs_base` — whether VS16 (U+FE0F) makes a codepoint width-2
 109 | 
 110 | ## Adding New Properties
 111 | 
 112 | If you need additional Unicode properties (e.g., for a new width calculation):
 113 | 
 114 | 1. Add the field to `uucode_config.zig`'s `tables` array
 115 | 2. Add the field to `Properties` in both `grapheme_gen.zig` and `grapheme.zig`
 116 | 3. Update the output format in `grapheme_gen.zig`'s `main()`
 117 | 4. Regenerate: `vendor/zig/zig build generate-grapheme-tables`
```


---
## test/AGENTS.md

```
   1 | To run tests:
   2 | 
   3 | ```sh
   4 | bun bd test <...test file>
   5 | ```
   6 | 
   7 | To run a command with your debug build of Bun:
   8 | 
   9 | ```sh
  10 | bun bd <...cmd>
  11 | ```
  12 | 
  13 | Note that compiling Bun may take up to 2.5 minutes. It is slow!
  14 | 
  15 | **CRITICAL**: Do not use `bun test` to run tests. It will not have your changes. `bun bd test <...test file>` is the correct command, which compiles your code automatically.
  16 | 
  17 | ## Testing style
  18 | 
  19 | Use `bun:test` with files that end in `*.test.{ts,js,jsx,tsx,mjs,cjs}`. If it's a test/js/node/test/{parallel,sequential}/\*.js without a .test.extension, use `bun bd <file>` instead of `bun bd test <file>` since those expect exit code 0 and don't use bun's test runner.
  20 | 
  21 | - **Do not write flaky tests**. Unless explicitly asked, **never wait for time to pass in tests**. Always wait for the condition to be met instead of waiting for an arbitrary amount of time. **Never use hardcoded port numbers**. Always use `port: 0` to get a random port.
  22 | - **Prefer concurrent tests over sequential tests**: When multiple tests in the same file spawn processes or write files, make them concurrent with `test.concurrent` or `describe.concurrent` unless it's very difficult to make them concurrent.
  23 | 
  24 | ### Spawning processes
  25 | 
  26 | #### Spawning Bun in tests
  27 | 
  28 | When spawning Bun processes, use `bunExe` and `bunEnv` from `harness`. This ensures the same build of Bun is used to run the test and ensures debug logging is silenced.
  29 | 
  30 | ##### Use `-e` for single-file tests
  31 | 
  32 | ```ts
  33 | import { bunEnv, bunExe, tempDir } from "harness";
  34 | import { test, expect } from "bun:test";
  35 | 
  36 | test("single-file test spawns a Bun process", async () => {
  37 |   await using proc = Bun.spawn({
  38 |     cmd: [bunExe(), "-e", "console.log('Hello, world!')"],
  39 |     env: bunEnv,
  40 |   });
  41 | 
  42 |   const [stdout, stderr, exitCode] = await Promise.all([
  43 |     proc.stdout.text(),
  44 |     proc.stderr.text(),
  45 |     proc.exited,
  46 |   ]);
  47 | 
  48 |   expect(stderr).toBe("");
  49 |   expect(stdout).toBe("Hello, world!\n");
  50 |   expect(exitCode).toBe(0);
  51 | });
  52 | ```
  53 | 
  54 | ##### When multi-file tests are required:
  55 | 
  56 | ```ts
  57 | import { bunEnv, bunExe, tempDir } from "harness";
  58 | import { test, expect } from "bun:test";
  59 | 
  60 | test("multi-file test spawns a Bun process", async () => {
  61 |   // If a test MUST use multiple files:
  62 |   using dir = tempDir("my-test-prefix", {
  63 |     "my.fixture.ts": `
  64 |       import { foo } from "./foo.ts";
  65 |       foo();
  66 |     `,
  67 |     "foo.ts": `
  68 |       export function foo() {
  69 |         console.log("Hello, world!");
  70 |       }
  71 |     `,
  72 |   });
  73 | 
  74 |   await using proc = Bun.spawn({
  75 |     cmd: [bunExe(), "my.fixture.ts"],
  76 |     env: bunEnv,
  77 |     cwd: String(dir),
  78 |   });
  79 | 
  80 |   const [stdout, stderr, exitCode] = await Promise.all([
  81 | 
  82 |     // ReadableStream in Bun supports:
  83 |     //  - `await stream.text()`
  84 |     //  - `await stream.json()`
  85 |     //  - `await stream.bytes()`
  86 |     //  - `await stream.blob()`
  87 |     proc.stdout.text(),
  88 |     proc.stderr.text(),
  89 | 
  90 |     proc.exitCode,
  91 |   ]);
  92 | 
  93 |   expect(stdout).toBe("Hello, world!");
  94 |   expect(stderr).toBe("");
  95 |   expect(exitCode).toBe(0);
  96 | ```
  97 | 
  98 | When a test file spawns a Bun process, we like for that file to end in `*-fixture.ts`. This is a convention that helps us identify the file as a test fixture and not a test itself.
  99 | 
 100 | Generally, `await using` or `using` is a good idea to ensure proper resource cleanup. This works in most Bun APIs like Bun.listen, Bun.connect, Bun.spawn, Bun.serve, etc.
 101 | 
 102 | #### Async/await in tests
 103 | 
 104 | Prefer async/await over callbacks.
 105 | 
 106 | When callbacks must be used and it's just a single callback, use `Promise.withResolvers` to create a promise that can be resolved or rejected from a callback.
 107 | 
 108 | ```ts
 109 | const ws = new WebSocket("ws://localhost:8080");
 110 | const { promise, resolve, reject } = Promise.withResolvers<void>(); // Can specify any type here for resolution value
 111 | ws.onopen = resolve;
 112 | ws.onclose = reject;
 113 | await promise;
 114 | ```
 115 | 
 116 | If it's several callbacks, it's okay to use callbacks. We aren't a stickler for this.
 117 | 
 118 | ### No timeouts
 119 | 
 120 | **CRITICAL**: Do not set a timeout on tests. Bun already has timeouts.
 121 | 
 122 | ### Use port 0 to get a random port
 123 | 
 124 | Most APIs in Bun support `port: 0` to get a random port. Never hardcode ports. Avoid using your own random port number function.
 125 | 
 126 | ### Creating temporary files
 127 | 
 128 | Use `tempDirWithFiles` to create a temporary directory with files.
 129 | 
 130 | ```ts
 131 | import { tempDir } from "harness";
 132 | import path from "node:path";
 133 | 
 134 | test("creates a temporary directory with files", () => {
 135 |   using dir = tempDir("my-test-prefix", {
 136 |     "file.txt": "Hello, world!",
 137 |   });
 138 | 
 139 |   expect(await Bun.file(path.join(String(dir), "file.txt")).text()).toBe(
 140 |     "Hello, world!",
 141 |   );
 142 | });
 143 | ```
 144 | 
 145 | ### Strings
 146 | 
 147 | To create a repetitive string, use `Buffer.alloc(count, fill).toString()` instead of `"A".repeat(count)`. "".repeat is very slow in debug JavaScriptCore builds.
 148 | 
 149 | ### Test Organization
 150 | 
 151 | - Use `describe` blocks for grouping related tests
 152 | - Regression tests for specific issues go in `/test/regression/issue/${issueNumber}.test.ts`. If there's no issue number, do not put them in the regression directory.
 153 | - Unit tests for specific features are organized by module (e.g., `/test/js/bun/`, `/test/js/node/`)
 154 | - Integration tests are in `/test/integration/`
 155 | 
 156 | ### Nested/complex object equality
 157 | 
 158 | Prefer usage of `.toEqual` rather than many `.toBe` assertions for nested or complex objects.
 159 | 
 160 | <example>
 161 | 
 162 | BAD (try to avoid doing this):
 163 | 
 164 | ```ts
 165 | expect(result).toHaveLength(3);
 166 | expect(result[0].optional).toBe(null);
 167 | expect(result[1].optional).toBe("middle-value"); // CRITICAL: middle item's value must be preserved
 168 | expect(result[2].optional).toBe(null);
 169 | ```
 170 | 
 171 | **GOOD (always prefer this):**
 172 | 
 173 | ```ts
 174 | expect(result).toEqual([
 175 |   { optional: null },
 176 |   { optional: "middle-value" }, // CRITICAL: middle item's value must be preserved
 177 |   { optional: null },
 178 | ]);
 179 | ```
 180 | 
 181 | </example>
 182 | 
 183 | ### Common Imports from `harness`
 184 | 
 185 | ```ts
 186 | import {
 187 |   bunExe, // Path to Bun executable
 188 |   bunEnv, // Environment variables for Bun
 189 |   tempDirWithFiles, // Create temporary test directories with files
 190 |   tmpdirSync, // Create empty temporary directory
 191 |   isMacOS, // Platform checks
 192 |   isWindows,
 193 |   isPosix,
 194 |   gcTick, // Trigger garbage collection
 195 |   withoutAggressiveGC, // Disable aggressive GC for performance tests
 196 | } from "harness";
 197 | ```
 198 | 
 199 | ### Error Testing
 200 | 
 201 | Always check exit codes and test error scenarios:
 202 | 
 203 | ```ts
 204 | test("handles errors", async () => {
 205 |   await using proc = Bun.spawn({
 206 |     cmd: [bunExe(), "run", "invalid.js"],
 207 |     env: bunEnv,
 208 |   });
 209 | 
 210 |   const exitCode = await proc.exited;
 211 |   expect(exitCode).not.toBe(0);
 212 | 
 213 |   // For synchronous errors
 214 |   expect(() => someFunction()).toThrow("Expected error message");
 215 | });
 216 | ```
 217 | 
 218 | ### Avoid dynamic import & require
 219 | 
 220 | **Only** use dynamic import or require when the test is specifically testing something relataed to dynamic import or require. Otherwise, **always use module-scope import statements**.
 221 | 
 222 | **BAD, do not do this**:
 223 | 
 224 | ```ts
 225 | test("foo", async () => {
 226 |   // BAD: Unnecessary usage of dynamic import.
 227 |   const { readFile } = await import("node:fs");
 228 | 
 229 |   expect(await readFile("ok.txt")).toBe("");
 230 | });
 231 | ```
 232 | 
 233 | **GOOD, do this:**
 234 | 
 235 | ```ts
 236 | import { readFile } from "node:fs";
 237 | test("foo", async () => {
 238 |   expect(await readFile("ok.txt")).toBe("");
 239 | });
 240 | ```
 241 | 
 242 | ### Test Utilities
 243 | 
 244 | - Use `describe.each()` for parameterized tests
 245 | - Use `toMatchSnapshot()` for snapshot testing
 246 | - Use `beforeAll()`, `afterEach()`, `beforeEach()` for setup/teardown
 247 | - Track resources (servers, clients) in arrays for cleanup in `afterEach()`
```


---
## test/CLAUDE.md

```
   1 | To run tests:
   2 | 
   3 | ```sh
   4 | bun bd test <...test file>
   5 | ```
   6 | 
   7 | To run a command with your debug build of Bun:
   8 | 
   9 | ```sh
  10 | bun bd <...cmd>
  11 | ```
  12 | 
  13 | Note that compiling Bun may take up to 2.5 minutes. It is slow!
  14 | 
  15 | **CRITICAL**: Do not use `bun test` to run tests. It will not have your changes. `bun bd test <...test file>` is the correct command, which compiles your code automatically.
  16 | 
  17 | ## Testing style
  18 | 
  19 | Use `bun:test` with files that end in `*.test.{ts,js,jsx,tsx,mjs,cjs}`. If it's a test/js/node/test/{parallel,sequential}/\*.js without a .test.extension, use `bun bd <file>` instead of `bun bd test <file>` since those expect exit code 0 and don't use bun's test runner.
  20 | 
  21 | - **Do not write flaky tests**. Unless explicitly asked, **never wait for time to pass in tests**. Always wait for the condition to be met instead of waiting for an arbitrary amount of time. **Never use hardcoded port numbers**. Always use `port: 0` to get a random port.
  22 | - **Prefer concurrent tests over sequential tests**: When multiple tests in the same file spawn processes or write files, make them concurrent with `test.concurrent` or `describe.concurrent` unless it's very difficult to make them concurrent.
  23 | 
  24 | ### Spawning processes
  25 | 
  26 | #### Spawning Bun in tests
  27 | 
  28 | When spawning Bun processes, use `bunExe` and `bunEnv` from `harness`. This ensures the same build of Bun is used to run the test and ensures debug logging is silenced.
  29 | 
  30 | ##### Use `-e` for single-file tests
  31 | 
  32 | ```ts
  33 | import { bunEnv, bunExe, tempDir } from "harness";
  34 | import { test, expect } from "bun:test";
  35 | 
  36 | test("single-file test spawns a Bun process", async () => {
  37 |   await using proc = Bun.spawn({
  38 |     cmd: [bunExe(), "-e", "console.log('Hello, world!')"],
  39 |     env: bunEnv,
  40 |   });
  41 | 
  42 |   const [stdout, stderr, exitCode] = await Promise.all([
  43 |     proc.stdout.text(),
  44 |     proc.stderr.text(),
  45 |     proc.exited,
  46 |   ]);
  47 | 
  48 |   expect(stderr).toBe("");
  49 |   expect(stdout).toBe("Hello, world!\n");
  50 |   expect(exitCode).toBe(0);
  51 | });
  52 | ```
  53 | 
  54 | ##### When multi-file tests are required:
  55 | 
  56 | ```ts
  57 | import { bunEnv, bunExe, tempDir } from "harness";
  58 | import { test, expect } from "bun:test";
  59 | 
  60 | test("multi-file test spawns a Bun process", async () => {
  61 |   // If a test MUST use multiple files:
  62 |   using dir = tempDir("my-test-prefix", {
  63 |     "my.fixture.ts": `
  64 |       import { foo } from "./foo.ts";
  65 |       foo();
  66 |     `,
  67 |     "foo.ts": `
  68 |       export function foo() {
  69 |         console.log("Hello, world!");
  70 |       }
  71 |     `,
  72 |   });
  73 | 
  74 |   await using proc = Bun.spawn({
  75 |     cmd: [bunExe(), "my.fixture.ts"],
  76 |     env: bunEnv,
  77 |     cwd: String(dir),
  78 |   });
  79 | 
  80 |   const [stdout, stderr, exitCode] = await Promise.all([
  81 | 
  82 |     // ReadableStream in Bun supports:
  83 |     //  - `await stream.text()`
  84 |     //  - `await stream.json()`
  85 |     //  - `await stream.bytes()`
  86 |     //  - `await stream.blob()`
  87 |     proc.stdout.text(),
  88 |     proc.stderr.text(),
  89 | 
  90 |     proc.exitCode,
  91 |   ]);
  92 | 
  93 |   expect(stdout).toBe("Hello, world!");
  94 |   expect(stderr).toBe("");
  95 |   expect(exitCode).toBe(0);
  96 | ```
  97 | 
  98 | When a test file spawns a Bun process, we like for that file to end in `*-fixture.ts`. This is a convention that helps us identify the file as a test fixture and not a test itself.
  99 | 
 100 | Generally, `await using` or `using` is a good idea to ensure proper resource cleanup. This works in most Bun APIs like Bun.listen, Bun.connect, Bun.spawn, Bun.serve, etc.
 101 | 
 102 | #### Async/await in tests
 103 | 
 104 | Prefer async/await over callbacks.
 105 | 
 106 | When callbacks must be used and it's just a single callback, use `Promise.withResolvers` to create a promise that can be resolved or rejected from a callback.
 107 | 
 108 | ```ts
 109 | const ws = new WebSocket("ws://localhost:8080");
 110 | const { promise, resolve, reject } = Promise.withResolvers<void>(); // Can specify any type here for resolution value
 111 | ws.onopen = resolve;
 112 | ws.onclose = reject;
 113 | await promise;
 114 | ```
 115 | 
 116 | If it's several callbacks, it's okay to use callbacks. We aren't a stickler for this.
 117 | 
 118 | ### No timeouts
 119 | 
 120 | **CRITICAL**: Do not set a timeout on tests. Bun already has timeouts.
 121 | 
 122 | ### Use port 0 to get a random port
 123 | 
 124 | Most APIs in Bun support `port: 0` to get a random port. Never hardcode ports. Avoid using your own random port number function.
 125 | 
 126 | ### Creating temporary files
 127 | 
 128 | Use `tempDirWithFiles` to create a temporary directory with files.
 129 | 
 130 | ```ts
 131 | import { tempDir } from "harness";
 132 | import path from "node:path";
 133 | 
 134 | test("creates a temporary directory with files", () => {
 135 |   using dir = tempDir("my-test-prefix", {
 136 |     "file.txt": "Hello, world!",
 137 |   });
 138 | 
 139 |   expect(await Bun.file(path.join(String(dir), "file.txt")).text()).toBe(
 140 |     "Hello, world!",
 141 |   );
 142 | });
 143 | ```
 144 | 
 145 | ### Strings
 146 | 
 147 | To create a repetitive string, use `Buffer.alloc(count, fill).toString()` instead of `"A".repeat(count)`. "".repeat is very slow in debug JavaScriptCore builds.
 148 | 
 149 | ### Test Organization
 150 | 
 151 | - Use `describe` blocks for grouping related tests
 152 | - Regression tests for specific issues go in `/test/regression/issue/${issueNumber}.test.ts`. If there's no issue number, do not put them in the regression directory.
 153 | - Unit tests for specific features are organized by module (e.g., `/test/js/bun/`, `/test/js/node/`)
 154 | - Integration tests are in `/test/integration/`
 155 | 
 156 | ### Nested/complex object equality
 157 | 
 158 | Prefer usage of `.toEqual` rather than many `.toBe` assertions for nested or complex objects.
 159 | 
 160 | <example>
 161 | 
 162 | BAD (try to avoid doing this):
 163 | 
 164 | ```ts
 165 | expect(result).toHaveLength(3);
 166 | expect(result[0].optional).toBe(null);
 167 | expect(result[1].optional).toBe("middle-value"); // CRITICAL: middle item's value must be preserved
 168 | expect(result[2].optional).toBe(null);
 169 | ```
 170 | 
 171 | **GOOD (always prefer this):**
 172 | 
 173 | ```ts
 174 | expect(result).toEqual([
 175 |   { optional: null },
 176 |   { optional: "middle-value" }, // CRITICAL: middle item's value must be preserved
 177 |   { optional: null },
 178 | ]);
 179 | ```
 180 | 
 181 | </example>
 182 | 
 183 | ### Common Imports from `harness`
 184 | 
 185 | ```ts
 186 | import {
 187 |   bunExe, // Path to Bun executable
 188 |   bunEnv, // Environment variables for Bun
 189 |   tempDirWithFiles, // Create temporary test directories with files
 190 |   tmpdirSync, // Create empty temporary directory
 191 |   isMacOS, // Platform checks
 192 |   isWindows,
 193 |   isPosix,
 194 |   gcTick, // Trigger garbage collection
 195 |   withoutAggressiveGC, // Disable aggressive GC for performance tests
 196 | } from "harness";
 197 | ```
 198 | 
 199 | ### Error Testing
 200 | 
 201 | Always check exit codes and test error scenarios:
 202 | 
 203 | ```ts
 204 | test("handles errors", async () => {
 205 |   await using proc = Bun.spawn({
 206 |     cmd: [bunExe(), "run", "invalid.js"],
 207 |     env: bunEnv,
 208 |   });
 209 | 
 210 |   const exitCode = await proc.exited;
 211 |   expect(exitCode).not.toBe(0);
 212 | 
 213 |   // For synchronous errors
 214 |   expect(() => someFunction()).toThrow("Expected error message");
 215 | });
 216 | ```
 217 | 
 218 | ### Avoid dynamic import & require
 219 | 
 220 | **Only** use dynamic import or require when the test is specifically testing something relataed to dynamic import or require. Otherwise, **always use module-scope import statements**.
 221 | 
 222 | **BAD, do not do this**:
 223 | 
 224 | ```ts
 225 | test("foo", async () => {
 226 |   // BAD: Unnecessary usage of dynamic import.
 227 |   const { readFile } = await import("node:fs");
 228 | 
 229 |   expect(await readFile("ok.txt")).toBe("");
 230 | });
 231 | ```
 232 | 
 233 | **GOOD, do this:**
 234 | 
 235 | ```ts
 236 | import { readFile } from "node:fs";
 237 | test("foo", async () => {
 238 |   expect(await readFile("ok.txt")).toBe("");
 239 | });
 240 | ```
 241 | 
 242 | ### Test Utilities
 243 | 
 244 | - Use `describe.each()` for parameterized tests
 245 | - Use `toMatchSnapshot()` for snapshot testing
 246 | - Use `beforeAll()`, `afterEach()`, `beforeEach()` for setup/teardown
 247 | - Track resources (servers, clients) in arrays for cleanup in `afterEach()`
```


---
## test/js/node/test/parallel/CLAUDE.md

```
   1 | # Node.js Compatibility Tests
   2 | 
   3 | These are official Node.js tests from the Node.js repository.
   4 | 
   5 | ## Important Notes
   6 | 
   7 | - These are Node.js compatibility tests **not written by Bun**, so we cannot modify these tests
   8 | - The tests pass by exiting with code 0
   9 | 
  10 | ## Running Tests
  11 | 
  12 | To run these tests with a debug build:
  13 | 
  14 | ```bash
  15 | bun bd <file-path>
  16 | ```
  17 | 
  18 | Note: `bun bd test <file-path>` does **not** work since these tests are meant to be run directly without the Bun test runner.
```
