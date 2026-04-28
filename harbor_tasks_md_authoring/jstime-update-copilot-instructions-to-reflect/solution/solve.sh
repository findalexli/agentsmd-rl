#!/usr/bin/env bash
set -euo pipefail

cd /workspace/jstime

# Idempotency guard
if grep -qF "For conformance tests, see [core/tests/CONFORMANCE_TESTS.md](../core/tests/CONFO" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -7,19 +7,23 @@ jstime is a minimal and performant JavaScript runtime built on top of the V8 Jav
 ### Architecture
 
 - **`jstime_core`** (`core/`): The core runtime library that wraps V8 and provides JavaScript APIs
-  - Built-in APIs: console, timers, fetch, URL, performance, microtask queue
-  - Module loading system with ES modules support
+  - Built-in APIs organized by standards:
+    - **WHATWG**: console, timers, fetch, URL, events (Event/EventTarget), base64, structured clone, microtask queue
+    - **W3C**: performance
+    - **Node.js compatible**: file system (fs/promises)
+  - Module loading system with ES modules and JSON modules support
   - Event loop implementation for async operations
+  - WebAssembly support via V8
 - **`jstime`** (`cli/`): Command-line interface with REPL support
-  - Interactive REPL with JavaScript auto-completion
+  - Interactive REPL with JavaScript auto-completion and command history
   - Script execution from files or stdin
   - V8 flags configuration
 
 ## Coding Standards
 
 ### Rust Conventions
 
-- **Edition**: Rust 2021
+- **Edition**: Rust 2024
 - **Formatting**: Code must pass `cargo fmt --all -- --check` (warnings treated as errors). Auto-format with `cargo fmt`.
 - **Linting**: Code must pass `cargo clippy -- -D warnings` (warnings treated as errors)
 - **Testing**: Run `cargo test` before committing
@@ -39,11 +43,15 @@ jstime is a minimal and performant JavaScript runtime built on top of the V8 Jav
 ## Key Dependencies
 
 - **v8** (140.2.0): V8 JavaScript engine bindings
-- **ureq** (2.10): HTTP client for fetch API implementation
+- **ureq** (3.1): HTTP client for fetch API implementation with connection pooling
 - **url** (2.5): URL parsing for URL API implementation
+- **urlencoding** (2.1): URL encoding/decoding utilities
+- **rustc-hash** (2.1): Fast non-cryptographic hashing for module maps
+- **filetime** (0.2): File timestamp manipulation for fs API
 - **lazy_static** (1.5.0): Lazy static initialization
-- **structopt**: CLI argument parsing (in cli crate)
-- **rustyline**: REPL implementation with line editing (in cli crate)
+- **rustyline** (17.0.2): REPL implementation with line editing (in cli crate)
+- **structopt** (0.3.26): CLI argument parsing (in cli crate)
+- **dirs** (6.0.0): User directories helper (in cli crate)
 
 ## Working with V8
 
@@ -75,22 +83,35 @@ jstime is a minimal and performant JavaScript runtime built on top of the V8 Jav
 
 ## Built-in APIs Implementation
 
-Built-in APIs are located in `core/src/builtins/`:
+Built-in APIs are located in `core/src/builtins/` and organized by standards body:
 
-- **console_impl.rs**: Console API (console.log, console.error, etc.)
-- **timers_impl.rs**: setTimeout, setInterval, clearTimeout, clearInterval
-- **fetch_impl.rs**: Fetch API (fetch, Headers, Request, Response)
-- **url_impl.rs**: URL and URLSearchParams
-- **performance_impl.rs**: performance.now()
-- **queue_microtask_impl.rs**: queueMicrotask()
+**WHATWG Standards** (`whatwg/`):
+- **console_impl.rs / console.js**: Console API (console.log, console.error, etc.)
+- **timers_impl.rs / timers.js**: setTimeout, setInterval, clearTimeout, clearInterval
+- **fetch_impl.rs / fetch.js**: Fetch API (fetch, Headers, Request, Response)
+- **url_impl.rs / url.js**: URL and URLSearchParams
+- **event_impl.rs / event.js**: Event and EventTarget
+- **base64_impl.rs / base64.js**: atob() and btoa() for base64 encoding/decoding
+- **structured_clone_impl.rs / structured_clone.js**: structuredClone() for deep cloning
+- **queue_microtask_impl.rs / queue_microtask.js**: queueMicrotask()
+
+**W3C Standards** (`w3c/`):
+- **performance_impl.rs / performance.js**: performance.now() and performance.timeOrigin
+
+**Node.js Compatible** (`node/`):
+- **fs_impl.rs / fs.js**: File system API (node:fs/promises module)
 
 ### Adding New Built-ins
 
-1. Create implementation in `core/src/builtins/`
-2. Register in `core/src/builtins/mod.rs`
-3. Add external references for V8
-4. Write conformance tests in `core/tests/`
-5. Update documentation in `docs/FEATURES.md`
+1. Create implementation in `core/src/builtins/` in the appropriate subdirectory:
+   - `whatwg/` for WHATWG standards (Fetch, URL, Console, Events, etc.)
+   - `w3c/` for W3C standards (Performance, etc.)
+   - `node/` for Node.js compatible APIs (fs/promises, etc.)
+2. Create both `*_impl.rs` (Rust) and `*.js` (JavaScript polyfill) files
+3. Register in `core/src/builtins/mod.rs` with external references
+4. Initialize in the global context
+5. Write tests in `core/tests/` (both feature tests and conformance tests)
+6. Update documentation in `docs/FEATURES.md`
 
 ## Testing
 
@@ -99,11 +120,26 @@ Built-in APIs are located in `core/src/builtins/`:
 - **`core/tests/test_api.rs`**: Core API tests (run_script, import)
 - **`core/tests/test_builtins.rs`**: Built-in function tests
 - **`core/tests/test_conformance_*.rs`**: WHATWG/W3C spec conformance tests
-- **`core/tests/common/mod.rs`**: Shared test utilities
+  - `test_conformance_base64.rs`: Base64 encoding (29 tests)
+  - `test_conformance_console.rs`: Console API (13 tests)
+  - `test_conformance_event.rs`: Event and EventTarget (tests)
+  - `test_conformance_fetch.rs`: Fetch API (32 tests)
+  - `test_conformance_performance.rs`: Performance API (19 tests)
+  - `test_conformance_timers.rs`: Timers API (17 tests)
+  - `test_conformance_url.rs`: URL API (26 tests)
+  - `test_conformance_webassembly.rs`: WebAssembly API (28 tests)
+  - `test_conformance_structured_clone.rs`: Structured clone (tests)
+  - `test_conformance_json_modules.rs`: JSON module imports (tests)
+- **`core/tests/test_*.rs`**: Feature-specific tests (timers, fetch, fs, webassembly)
+- **`core/tests/common/mod.rs`**: Shared test utilities (setup guards, helper functions)
+- **`core/tests/fixtures/`**: Test data and sample files organized by feature
 
 ### Test Patterns
 
 ```rust
+use jstime_core as jstime;
+mod common;
+
 #[test]
 fn test_example() {
     let _setup_guard = common::setup();
@@ -114,6 +150,8 @@ fn test_example() {
 }
 ```
 
+For conformance tests, see [core/tests/CONFORMANCE_TESTS.md](../core/tests/CONFORMANCE_TESTS.md) for detailed coverage information.
+
 ### Running Tests
 
 - All tests: `cargo test`
@@ -133,6 +171,16 @@ cargo run            # Run REPL
 cargo run -- file.js # Execute JavaScript file
 ```
 
+### Optimization
+
+The project uses aggressive optimization for release builds:
+- **LTO (Link-Time Optimization)**: Enabled for cross-crate optimizations
+- **codegen-units = 1**: Better runtime performance
+- **opt-level = 3**: Maximum optimization
+- **strip = true**: Smaller binary size
+
+See [PERFORMANCE.md](../PERFORMANCE.md) for detailed performance information.
+
 ### CI Requirements
 
 All PRs must pass:
@@ -148,30 +196,41 @@ jstime supports ES modules with:
 - Top-level `await`
 - Dynamic `import()`
 - File-based module resolution
+- JSON module imports (import data from './data.json')
+- `import.meta.url` for getting current module's URL
 
 ### Module Loading
 
 - Located in `core/src/js_loading.rs` and `core/src/module.rs`
 - Uses V8's module system
 - Resolves file paths relative to importing module
+- JSON files detected by `.json` extension and wrapped as ES modules
 
 ## Event Loop
 
 - Implementation in `core/src/event_loop.rs`
-- Handles timers, fetch requests, and other async operations
+- Handles timers, fetch requests, file operations, and other async operations
 - Uses `std::sync::mpsc` for communication between JS and Rust
 - Integrates with V8's microtask queue
+- Performance optimizations:
+  - Pre-allocated vectors for ready timers
+  - Early returns when no work to do
+  - Inlined hot path functions
 
 ## Common Development Tasks
 
 ### Adding a New JavaScript API
 
-1. Create implementation file in `core/src/builtins/`
-2. Define the Rust callback functions
-3. Register in `builtins/mod.rs` external references
-4. Initialize in the global context
-5. Write tests in `core/tests/`
-6. Document in `docs/FEATURES.md`
+1. Choose the appropriate subdirectory based on the standard:
+   - `core/src/builtins/whatwg/` for WHATWG standards
+   - `core/src/builtins/w3c/` for W3C standards
+   - `core/src/builtins/node/` for Node.js compatible APIs
+2. Create both `your_api_impl.rs` (Rust) and `your_api.js` (JavaScript polyfill) files
+3. Define the Rust callback functions with V8 bindings
+4. Register in `builtins/mod.rs` external references
+5. Initialize in the global context
+6. Write tests in `core/tests/` (both feature tests and conformance tests)
+7. Document in `docs/FEATURES.md`
 
 ### Debugging
 
@@ -190,29 +249,44 @@ jstime supports ES modules with:
 
 - Keep README.md updated with user-facing features
 - Update FEATURES.md when adding APIs
+- See ARCHITECTURE.md for detailed architecture information
+- See PERFORMANCE.md for performance optimization details
+- See CONTRIBUTING.md for development workflow
 - Add inline doc comments for public APIs
 - Follow existing documentation style
+- Update conformance test documentation in core/tests/CONFORMANCE_TESTS.md
 
 ## Best Practices
 
 1. **Minimize unsafe code**: Avoid `unsafe` unless necessary for V8 FFI
-2. **Test thoroughly**: Add both unit and conformance tests
+2. **Test thoroughly**: Add both unit tests and conformance tests
 3. **Keep it minimal**: jstime aims to be lightweight; avoid feature bloat
 4. **Follow specs**: Implement APIs according to WHATWG/W3C specifications
-5. **Performance matters**: Profile and optimize hot paths
+5. **Performance matters**: Profile and optimize hot paths; use pre-allocation where possible
 6. **Error messages**: Provide clear, actionable error messages
 7. **API stability**: Maintain backward compatibility for public APIs
+8. **Use FxHashMap**: For internal hash maps with small keys (faster than std HashMap)
+9. **Inline hot paths**: Add `#[inline]` to frequently called functions
+10. **Connection pooling**: Reuse HTTP connections in fetch API implementation
 
 ## Resources
 
 - [V8 Embedder's Guide](https://v8.dev/docs/embed)
 - [Rust V8 Bindings](https://docs.rs/v8/)
 - [WHATWG Standards](https://spec.whatwg.org/)
+- [W3C Standards](https://www.w3.org/TR/)
+- [Node.js Documentation](https://nodejs.org/api/)
 - [Project Repository](https://github.com/jstime/jstime)
+- [Architecture Documentation](../ARCHITECTURE.md)
+- [Performance Documentation](../PERFORMANCE.md)
+- [Features Documentation](../docs/FEATURES.md)
 
 ## Getting Help
 
 - Check existing issues and discussions
 - Review conformance tests for examples
 - Read V8 documentation for engine-specific questions
+- See [ARCHITECTURE.md](../ARCHITECTURE.md) for detailed architecture
+- See [core/tests/README.md](../core/tests/README.md) for testing patterns
+- See [core/src/builtins/README.md](../core/src/builtins/README.md) for built-in API structure
 - Follow project governance in GOVERNANCE.md
PATCH

echo "Gold patch applied."
