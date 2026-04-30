#!/usr/bin/env bash
set -euo pipefail

cd /workspace/slint

# Idempotency guard
if grep -qF "`lsp/` (LSP server), `compiler/` (CLI), `viewer/` (hot-reload `.slint` viewer), " "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -2,17 +2,16 @@
 
 This file provides guidance to AI coding assistants when working with code in this repository.
 
-## Project Overview
-
-Slint is a declarative GUI toolkit for building native user interfaces across embedded systems, desktops, mobile, and web platforms. UIs are written in `.slint` markup files and connected to business logic in Rust, C++, JavaScript, or Python.
+Slint is a declarative GUI toolkit for embedded, desktop, mobile, and web.
+UIs are written in `.slint` markup and connected to Rust, C++, JavaScript, or Python business logic.
 
 ## Build Commands
 
 ### Rust (Primary)
 ```sh
 cargo build                                    # Build the workspace
-cargo build --release                          # Release build (use this flag whenever testing performance)
-cargo test                                     # Run tests (requires cargo build first!)
+cargo build --release                          # Release build (use whenever measuring performance)
+cargo test                                     # Run tests
 cargo build --workspace --exclude uefi-demo    # Build all examples
 ```
 
@@ -37,22 +36,33 @@ cd api/node && pnpm install
 
 ## Testing
 
-**Important**: Run `cargo build` before `cargo test` - the dynamic library must exist first.
+Don't run `cargo build` before `cargo test` — `cargo test` compiles what it needs.
 
 ### Test Drivers
 ```sh
-cargo test -p test-driver-interpreter         # Fast interpreter tests
-cargo test -p test-driver-rust                # Rust API tests
-cargo test -p test-driver-cpp                 # C++ tests (build slint-cpp first)
-cargo test -p test-driver-nodejs              # Node.js tests
-cargo test -p doctests                        # Documentation snippet tests
+cargo test -p test-driver-interpreter         # Fastest: interpreter-based
+cargo test -p test-driver-rust                # Rust API (slow to compile without SLINT_TEST_FILTER)
+cargo test -p test-driver-cpp                 # C++ (build slint-cpp first for the dynamic library)
+cargo test -p test-driver-nodejs              # Node.js
+cargo test -p doctests                        # Documentation snippets
 ```
 
-### Filtered Testing
+### Filtering .slint Test Cases
+
+The test drivers compile every `.slint` file under `tests/cases/` into a generated Rust test, which is slow.
+Set `SLINT_TEST_FILTER=<substring>` to limit the build to matching case files.
+
 ```sh
-tests/run_tests.sh rust layout     # Filter by name
+tests/run_tests.sh rust layout                 # Filter by name via the helper script
 ```
 
+Only drop the filter for a final full-suite run before committing.
+
+### Writing Slint Test Cases
+
+The `test` property in `tests/cases/*.slint` must be declared `out property<bool> test: ...;`.
+Without `out`, the compiler treats it as private and the driver passes the test vacuously.
+
 ### Syntax Tests (Compiler Errors)
 ```sh
 cargo test -p i-slint-compiler --features display-diagnostics --test syntax_tests
@@ -98,31 +108,15 @@ SLINT_CREATE_SCREENSHOTS=1 cargo test -p test-driver-screenshots  # Generate ref
 
 ### Language APIs (`api/`)
 
-- `rs/slint/` - Rust public crate
-- `rs/macros/` - `slint!` procedural macro
-- `rs/build/` - Build script support
-- `cpp/` - C++ API with CMake integration
-- `node/` - Node.js bindings (Neon)
-- `python/` - Python bindings (PyO3)
-- `wasm-interpreter/` - WebAssembly bindings for browser use
+Rust (`rs/slint/`, `rs/macros/` for `slint!`, `rs/build/`), C++ (`cpp/`, CMake), Node.js (`node/`, Neon), Python (`python/`, PyO3), WebAssembly (`wasm-interpreter/`).
 
-### Tools
+### Tools (`tools/`)
 
-- `tools/lsp/` - Language Server Protocol for editor integration
-- `tools/compiler/` - CLI compiler
-- `tools/viewer/` - .slint file viewer with hot reload
-- `tools/slintpad/` - Web-based Slint editor/playground
-- `tools/figma_import/` - Import designs from Figma
-- `tools/tr-extractor/` - Translation string extractor for i18n
-- `tools/updater/` - Migration tool for Slint version updates
+`lsp/` (LSP server), `compiler/` (CLI), `viewer/` (hot-reload `.slint` viewer), `slintpad/` (web playground), `figma_import/`, `tr-extractor/` (i18n), `updater/` (version migration).
 
 ### Editor Support (`editors/`)
 
-- `vscode/` - Visual Studio Code extension
-- `zed/` - Zed editor integration
-- `kate/` - Kate editor syntax highlighting
-- `sublime/` - Sublime Text support
-- `tree-sitter-slint/` - Tree-sitter grammar for syntax highlighting
+`vscode/`, `zed/`, `kate/`, `sublime/`, `tree-sitter-slint/`.
 
 ### Key Patterns
 
@@ -133,51 +127,39 @@ SLINT_CREATE_SCREENSHOTS=1 cargo test -p test-driver-screenshots  # Generate ref
 
 ## Version Control (Git)
 
-- The default git branch is `master`
+- The default git branch is `master`.
+- Prefer linear history — rebase or squash on merge.
 
 ## Code Style
 
-- Rust: `rustfmt` enforced in CI
-- C++: `clang-format` enforced in CI
-- Linear git history preferred (rebase/squash merges)
+- Rust: `rustfmt` enforced in CI.
+- C++: `clang-format` enforced in CI.
 
-## Platform Prerequisites
+### Comments and Docs
 
-### Linux
-```sh
-# Debian/Ubuntu
-sudo apt install libxcb-shape0-dev libxcb-xfixes0-dev libxkbcommon-dev \
-  libfontconfig-dev libssl-dev clang libavcodec-dev libavformat-dev \
-  libavutil-dev libavfilter-dev libavdevice-dev libasound2-dev pkg-config
-```
+- Follow `docs/astro/writing-style-guide.md` when writing *new* comments, doc comments, commit messages, or markdown.
+- But don't reformat existing prose to match the style.
 
-### macOS
-```sh
-xcode-select --install
-brew install pkg-config ffmpeg
-```
+## Platform Prerequisites
 
-### Windows
-- Enable symlinks: `git clone -c core.symlinks=true https://github.com/slint-ui/slint`
-- Install MSVC Build Tools
-- FFMPEG via vcpkg or manual installation
+See [`docs/building.md`](docs/building.md) for Linux/macOS/Windows system packages, FFMPEG setup, and the Windows symlink `git clone` flag.
 
 ## Deep Dive Documentation
 
-For tasks requiring deeper architectural understanding, see:
-
-- **`docs/development/compiler-internals.md`** - Compiler pipeline, passes, LLR, code generation. Load when working on `internal/compiler/`.
-- **`docs/development/type-system.md`** - Type definitions, unit types, type conversions, name resolution, type register. Load when working on `langtype.rs`, `lookup.rs`, or type checking.
-- **`docs/development/property-binding-deep-dive.md`** - Reactive property system, dependency tracking, two-way bindings, PropertyTracker, ChangeTracker. Load when working on `internal/core/properties.rs` or debugging binding issues.
-- **`docs/development/custom-renderer.md`** - Renderer traits, drawing API, backend integration, testing. Load when working on `internal/renderers/` or fixing drawing bugs.
-- **`docs/development/animation-internals.md`** - Animation timing, easing curves, performance, debugging. Load when working on `internal/core/animations.rs` or animation-related issues.
-- **`docs/development/layout-system.md`** - Layout solving, constraints, GridLayout/BoxLayout, compile-time lowering. Load when working on `internal/core/layout.rs` or sizing/positioning bugs.
-- **`docs/development/python-tests.md`** - Python test infrastructure: pytest tests, Rust test driver, rebuilding slint-python, debugging compilation vs runtime issues. Load when working on Python tests or debugging `test-driver-python` failures.
-- **`docs/development/item-tree.md`** - Item tree structure, component instantiation, traversal, focus. Load when working on `internal/core/item_tree.rs`, event handling, or runtime component model.
-- **`docs/development/model-repeater-system.md`** - Model trait, VecModel, adapters (map/filter/sort), Repeater, ListView virtualization. Load when working on `internal/core/model.rs` or data binding in `for` loops.
-- **`docs/development/input-event-system.md`** - Mouse/touch/keyboard events, event routing, focus management, drag-drop, shortcuts. Load when working on `internal/core/input.rs` or event handling.
-- **`docs/development/text-layout.md`** - Text shaping, line breaking, paragraph layout, styled text parsing. Load when working on `internal/core/textlayout/` or text rendering.
-- **`docs/development/window-backend-integration.md`** - WindowAdapter trait, Platform trait, WindowEvent, popup management, backend implementations. Load when working on `internal/core/window.rs` or `internal/backends/`.
-- **`docs/development/lsp-architecture.md`** - LSP server, code completion, hover, semantic tokens, live preview. Load when working on `tools/lsp/` or IDE tooling.
-- **`docs/development/mcp-server.md`** - Embedded MCP server architecture, shared introspection layer, handle/arena system, HTTP transport, adding tools. Load when working on `internal/backends/testing/mcp_server.rs`, `introspection.rs`, or MCP-related features.
-- **`docs/development/ffi-language-bindings.md`** - C++/Node.js/Python bindings, cbindgen, FFI patterns, adding new cross-language APIs. Load when working on `api/` or internal FFI modules.
+Load the relevant file under `docs/development/` when working in the listed area:
+
+- `compiler-internals.md` — `internal/compiler/`: pipeline, passes, LLR, codegen.
+- `type-system.md` — `langtype.rs`, `lookup.rs`, type checking: unit types, conversions, name resolution, type register.
+- `property-binding-deep-dive.md` — `internal/core/properties.rs`, binding bugs: reactivity, dependency tracking, two-way bindings, PropertyTracker, ChangeTracker.
+- `custom-renderer.md` — `internal/renderers/`, drawing bugs: renderer traits, drawing API, backend integration.
+- `animation-internals.md` — `internal/core/animations.rs`: timing, easing curves, debugging.
+- `layout-system.md` — `internal/core/layout.rs`, sizing bugs: constraints, GridLayout/BoxLayout, compile-time lowering.
+- `python-tests.md` — Python tests, `test-driver-python`: pytest setup, rebuilding slint-python, compile vs runtime issues.
+- `item-tree.md` — `internal/core/item_tree.rs`, event handling, component model: item tree, instantiation, traversal, focus.
+- `model-repeater-system.md` — `internal/core/model.rs`, `for` loops: Model trait, VecModel, adapters, Repeater, ListView virtualization.
+- `input-event-system.md` — `internal/core/input.rs`, event handling: routing, focus, drag-drop, shortcuts.
+- `text-layout.md` — `internal/core/textlayout/`, text rendering: shaping, line breaking, styled text.
+- `window-backend-integration.md` — `internal/core/window.rs`, `internal/backends/`: WindowAdapter, Platform, WindowEvent, popups.
+- `lsp-architecture.md` — `tools/lsp/`, IDE tooling: completion, hover, semantic tokens, live preview.
+- `mcp-server.md` — `internal/backends/testing/mcp_server.rs`, `introspection.rs`: shared introspection layer, handle/arena, HTTP transport, adding tools.
+- `ffi-language-bindings.md` — `api/`, internal FFI: cbindgen, FFI patterns, adding cross-language APIs.
PATCH

echo "Gold patch applied."
