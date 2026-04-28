#!/usr/bin/env bash
set -euo pipefail

cd /workspace/wordpress-playground

# Idempotency guard
if grep -qF "3. **Supporting packages**: `packages/nx-extensions/` (custom NX executors), `pa" "AGENTS.md" && grep -qF "CLAUDE.md" "CLAUDE.md" && grep -qF "- **Asyncify** \u2014 Older approach. Transforms synchronous C code to be pausable/re" "packages/php-wasm/compile/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,296 @@
+<!--
+MAINTENANCE: Update this file when:
+- Adding/removing npm scripts in package.json
+- Changing the monorepo structure (new packages, major refactors)
+- Modifying build/test workflows
+- Adding new architectural patterns or conventions
+- Updating Node.js/npm version requirements
+-->
+
+# AGENTS.md
+
+This file provides guidance to AI coding agents when working with code in this repository.
+
+## Project Overview
+
+WordPress Playground is a monorepo that runs WordPress and PHP entirely in WebAssembly, enabling zero-setup WordPress environments in browsers, Node.js, and CLIs. The project consists of two major architectural layers and several supporting packages:
+
+1. **PHP-WASM Layer** (`packages/php-wasm/*`): Emscripten-compiled PHP runtime for web and Node.js
+2. **Playground Layer** (`packages/playground/*`): WordPress-specific tooling, client libraries, and applications
+3. **Supporting packages**: `packages/nx-extensions/` (custom NX executors), `packages/docs/` (Docusaurus documentation site), `packages/meta/` (ESLint plugin, changelog tooling), `packages/bun-extensions/` and `packages/vite-extensions/` (build tooling)
+
+## Build System
+
+This is an NX monorepo with npm workspaces. All commands use NX for task orchestration.
+
+**Node.js version**: This project requires a specific Node.js version (defined in `.nvmrc` and the `engines` field in root `package.json`). Before running any commands, ensure the correct version is active (e.g., via `nvm use` or other version manager).
+
+### Common Commands
+
+```bash
+# Development
+npm run dev                              # Start website dev server (localhost:5400)
+npm run dev:docs                         # Start documentation site
+npx nx dev playground-cli server         # Run CLI from source
+
+# Building
+npm run build                            # Build all packages
+npm run build:website                    # Build the main website
+npm run build:docs                       # Build documentation
+npx nx build <package-name>              # Build specific package
+
+# Testing
+npm test                                 # Run all tests
+npx nx test <package-name>               # Test specific package
+npx nx e2e playground-website            # Run end-to-end tests
+
+# Running a single test file
+npx nx test <package-name> --testFile=<test-file-name>
+
+# Linting & Formatting
+npm run lint                             # Lint all packages
+npm run typecheck                        # Type check all packages
+npm run format                           # Format code with Prettier
+npm run format:uncommitted               # Format only uncommitted files
+
+# PHP Recompilation (advanced)
+npm run recompile:php:web                # Recompile all PHP versions for web
+npm run recompile:php:node               # Recompile all PHP versions for Node.js
+npx nx recompile-php:jspi php-wasm-web -- --PHP_VERSION=8.4
+npx nx recompile-php:asyncify php-wasm-node -- --PHP_VERSION=8.3
+
+# WordPress Builds
+npm run rebuild:wordpress-builds         # Rebuild all WordPress versions
+```
+
+### Package Naming Convention
+
+- `@php-wasm/<name>`: PHP runtime and utilities
+- `@wp-playground/<name>`: WordPress Playground features and tools
+
+## Architecture
+
+### Client-Remote Communication
+
+The core architecture uses an iframe-based isolation model:
+
+```
+@wp-playground/client (parent window)
+    ↓ postMessage API
+@wp-playground/remote (iframe content, runs PHP)
+    ↓
+@php-wasm/web (PHP runtime)
+    ↓
+@php-wasm/universal (abstract interface)
+```
+
+**Key packages:**
+
+- `@wp-playground/client`: JavaScript API for embedding Playground in iframes
+- `@wp-playground/remote`: The HTML application running inside the iframe
+- `@php-wasm/web`: Browser-based PHP runtime (uses Emscripten WASM)
+- `@php-wasm/node`: Node.js-based PHP runtime
+- `@php-wasm/universal`: Abstract interface shared by web and node implementations
+
+### Blueprint System
+
+Blueprints are declarative JSON configurations that define WordPress site states. Located in `@wp-playground/blueprints`.
+
+**Key concepts:**
+
+- Blueprint steps execute sequentially (e.g., `installPlugin`, `login`, `runPHP`)
+- Two execution modes: V1 (TypeScript runner) and V2 (experimental PHP runner)
+- Steps are defined in `packages/playground/blueprints/src/lib/steps/`
+- Each step has a `.ts` implementation and `.spec.ts` test file
+
+**Common blueprint steps:**
+
+- `installPlugin`, `activatePlugin`: Plugin management
+- `installTheme`, `activateTheme`: Theme management
+- `login`: User authentication
+- `runPHP`, `runPHPWithOptions`: Execute PHP code
+- `defineWpConfigConsts`: Modify wp-config.php
+- `importWxr`, `importWordPressFiles`: Import content
+
+**Schema generation:** Blueprint JSON schemas are auto-generated from TypeScript types.
+After modifying step interfaces, rebuild with `npx nx build playground-blueprints`.
+The schema is NOT auto-rebuilt in `npm run dev` mode.
+
+### Storage & Sync
+
+- `@wp-playground/storage`: Provides filesystem backends (IndexedDB in browser, filesystem in Node)
+- `@wp-playground/sync`: Multi-client synchronization for collaborative editing
+- `@php-wasm/fs-journal`: Tracks filesystem changes for synchronization
+
+### WordPress Builds
+
+`@wp-playground/wordpress-builds` compiles specific WordPress versions into the playground format. Each version is tested and bundled separately.
+
+### Multi-Runtime PHP Support
+
+PHP binaries are compiled separately for:
+
+- **Web (browser)**: Asyncify and JSPI variants for different browser capabilities
+- **Node.js**: Native async/await support
+
+Version-specific builds: `@php-wasm/web-7-4` through `@php-wasm/web-8-5` (and corresponding node-builds)
+
+## Development Conventions
+
+### TypeScript
+
+- **Type imports must be explicit**: Use `import type { Foo } from 'bar'` (required for Node.js type stripping)
+- **No parameter properties**: TypeScript parameter properties are not supported by Node.js type stripping
+- Module resolution: `bundler` mode in tsconfig
+- Target: ES2021 with ESNext modules
+- Path aliases defined in `tsconfig.base.json` for cross-package imports
+
+### Code Style
+
+- **Comment length**: Max 100 characters per line (enforced by ESLint)
+- **No console.log**: Disallowed except in tests and bin/ scripts
+- **Consistent type imports**: Required by `@typescript-eslint/consistent-type-imports`
+- **Module boundaries**: Enforced via `@nx/enforce-module-boundaries`
+    - Packages tagged `scope:web-client` cannot be depended on by others
+    - `scope:independent-from-php-binaries` packages cannot depend on `scope:php-binaries`
+- **Function ordering:** First caller, then callee. When function A calls function B, write first A, then B.
+- **Method ordering:** First public, then protected, then private. Respect **Function ordering** as well.
+
+### Testing
+
+- **Test files**: Co-located with implementation as `*.spec.ts`
+- **Test runner**: Vitest (via `@nx/vite:test`) for most packages; some packages use Jest (via `@nx/jest`)
+- **Coverage**: Reports to `coverage/packages/<package-name>`
+- **E2E tests**: Playwright and Cypress for website testing
+- **Always fix failing tests**: Never skip failing tests; fix the code to make tests pass
+
+### Package Structure
+
+All published packages follow this pattern:
+
+```
+packages/[layer]/[package-name]/
+├── src/
+│   ├── index.ts              # Main entry point
+│   └── lib/                  # Implementation
+├── package.json              # npm metadata
+├── project.json              # NX build configuration
+├── tsconfig.json             # Base TypeScript config
+├── tsconfig.lib.json         # Library build config
+├── tsconfig.spec.json        # Test config
+└── README.md                 # Package documentation
+```
+
+Some packages have their own `AGENTS.md` with package-specific guidance. Check
+for one when working within a package.
+
+### Publishing
+
+- **Dual format**: All packages publish both ESM (`.js`) and CommonJS (`.cjs`)
+- **publishConfig.directory**: Points to `dist/packages/[layer]/[package-name]`
+- **Lerna**: Used for coordinated multi-package publishing (`npm run release`)
+- **Exports field**: Defines both `import` and `require` conditions
+- Version management: All packages versioned together (see `lerna.json` for current version)
+
+## Special Workflows
+
+### Running Tests from Source
+
+```bash
+# Individual package test
+npx nx test playground-blueprints
+
+# Run specific test file
+npx nx test playground-blueprints --testFile=activate-plugin.spec.ts
+
+# Run with coverage
+npx nx test playground-blueprints --coverage
+
+# E2E tests
+npx nx e2e playground-website
+```
+
+### CLI Development
+
+The Playground CLI (`@wp-playground/cli`) can be run directly from source:
+
+```bash
+npx nx dev playground-cli server --wp=6.8 --php=8.4 --auto-mount
+```
+
+**CLI features:**
+
+- `--auto-mount`: Automatically detect and mount plugin/theme/WordPress directory
+- `--blueprint=<path>`: Execute a blueprint JSON file
+- `--mount=<src>:<dest>`: Manually mount directories
+- `--login`: Auto-login as admin
+- `--php=<version>`: Choose PHP version (7.4-8.5)
+- `--wp=<version>`: Choose WordPress version
+
+### Git Operations
+
+- **Default branch**: `trunk` is the primary development branch
+- **Never use bare `git push`**: Always specify remote and branch explicitly
+- **Shallow clone recommended**: `git clone -b trunk --single-branch --depth 1 --recurse-submodules`
+- **Submodules**: isomorphic-git submodule provides browser-based git operations
+
+### Working with PHP Binaries
+
+PHP binaries are pre-compiled and committed to the repository. Recompilation is rarely needed but can be done with:
+
+```bash
+# Recompile all PHP versions for web
+npm run recompile:php:web
+
+# Recompile specific PHP version with JSPI
+npx nx recompile-php:jspi php-wasm-web -- --PHP_VERSION=8.4
+
+# Debug builds (with DWARF info)
+npx nx recompile-php:all php-wasm-node -- --WITH_DEBUG=yes
+
+# Source maps for debugging
+npx nx recompile-php:all php-wasm-node -- --WITH_SOURCEMAPS=yes
+```
+
+### Custom NX Executors
+
+Located in `packages/nx-extensions/src/executors/`:
+
+- `build`: Builds packages
+- `built-script`: Runs scripts from built output
+- `package-json`: Generates package.json with correct exports
+- `assert-built-esm-and-cjs`: Verifies dual-format build
+- `package-for-self-hosting`: Creates distributable archives
+
+## Key Files & Directories
+
+- `nx.json`: NX workspace configuration
+- `tsconfig.base.json`: TypeScript path aliases and compiler options
+- `package.json`: Root package with all npm scripts
+- `lerna.json`: Version management and publish configuration
+- `.eslintrc.json`: ESLint rules including module boundaries
+- `packages/playground/blueprints/src/lib/steps/`: Blueprint step implementations
+- `packages/php-wasm/universal/`: Core PHP abstraction layer
+- `packages/php-wasm/compile/`: Docker/Emscripten PHP build pipeline
+- `packages/playground/website/`: Main demo application
+- `packages/playground/cli/`: CLI tool implementation
+- `packages/docs/`: Docusaurus documentation site
+- `packages/meta/`: Internal tooling (ESLint plugin, changelog)
+- `isomorphic-git/`: Git operations in browser (submodule)
+
+## Documentation
+
+- Deployed to https://wordpress.github.io/wordpress-playground/
+- Built with Docusaurus in `packages/docs/`
+- API reference generated with TypeDoc from package source
+
+## Important Notes
+
+- **Backwards compatibility**: Breaking changes are acceptable and often useful
+  during development, but must be surfaced to the developer. When creating a PR,
+  clearly document any breaking changes in the PR description. Key downstream
+  consumers include Telex, Studio, and wp-env
+- **Offline support**: Website can be built for offline use with service workers
+- **WordPress major and beta versions**: Auto-refreshed via GitHub Actions
+- **SQLite integration**: WordPress uses SQLite by default (no MySQL required)
+- **Security**: Iframe-based isolation prevents untrusted code execution in parent window
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,281 +1 @@
-<!--
-MAINTENANCE: Update this file when:
-- Adding/removing npm scripts in package.json
-- Changing the monorepo structure (new packages, major refactors)
-- Modifying build/test workflows
-- Adding new architectural patterns or conventions
-- Updating Node.js/npm version requirements
--->
-
-# CLAUDE.md
-
-This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
-
-## Project Overview
-
-WordPress Playground is a monorepo that runs WordPress and PHP entirely in WebAssembly, enabling zero-setup WordPress environments in browsers, Node.js, and CLIs. The project consists of two major architectural layers:
-
-1. **PHP-WASM Layer** (`packages/php-wasm/*`): Emscripten-compiled PHP runtime for web and Node.js
-2. **Playground Layer** (`packages/playground/*`): WordPress-specific tooling, client libraries, and applications
-
-## Build System
-
-This is an NX monorepo with npm workspaces. All commands use NX for task orchestration.
-
-### Common Commands
-
-```bash
-# Development
-npm run dev                    # Start website dev server (localhost:5400)
-npm run dev:docs              # Start documentation site
-npx nx dev playground-cli server  # Run CLI from source
-
-# Building
-npm run build                 # Build all packages
-npm run build:website         # Build the main website
-npm run build:docs           # Build documentation
-npx nx build <package-name>  # Build specific package
-
-# Testing
-npm test                      # Run all tests
-npx nx test <package-name>   # Test specific package
-npx nx e2e playground-website # Run end-to-end tests
-
-# Linting & Formatting
-npm run lint                  # Lint all packages
-npm run typecheck             # Type check all packages
-npm run format                # Format code with Prettier
-npm run format:uncommitted    # Format only uncommitted files
-
-# PHP Recompilation (advanced)
-npm run recompile:php:web     # Recompile all PHP versions for web
-npm run recompile:php:node    # Recompile all PHP versions for Node.js
-npx nx recompile-php:jspi php-wasm-web -- --PHP_VERSION=8.4
-npx nx recompile-php:asyncify php-wasm-node -- --PHP_VERSION=8.3
-
-# WordPress Builds
-npm run rebuild:wordpress-builds  # Rebuild all WordPress versions
-
-# Running a single test file
-npx nx test <package-name> --testFile=<test-file-name>
-```
-
-### Package Naming Convention
-
-- `@php-wasm/<name>`: PHP runtime and utilities
-- `@wp-playground/<name>`: WordPress Playground features and tools
-
-## Architecture
-
-### Client-Remote Communication
-
-The core architecture uses an iframe-based isolation model:
-
-```
-@wp-playground/client (parent window)
-    ↓ postMessage API
-@wp-playground/remote (iframe content, runs PHP)
-    ↓
-@php-wasm/web (PHP runtime)
-    ↓
-@php-wasm/universal (abstract interface)
-```
-
-**Key packages:**
-
-- `@wp-playground/client`: JavaScript API for embedding Playground in iframes
-- `@wp-playground/remote`: The HTML application running inside the iframe
-- `@php-wasm/web`: Browser-based PHP runtime (uses Emscripten WASM)
-- `@php-wasm/node`: Node.js-based PHP runtime
-- `@php-wasm/universal`: Abstract interface shared by web and node implementations
-
-### Blueprint System
-
-Blueprints are declarative JSON configurations that define WordPress site states. Located in `@wp-playground/blueprints`.
-
-**Key concepts:**
-
-- Blueprint steps execute sequentially (e.g., `installPlugin`, `login`, `runPHP`)
-- Two execution modes: V1 (TypeScript runner) and V2 (experimental PHP runner)
-- Steps are defined in `packages/playground/blueprints/src/lib/steps/`
-- Each step has a `.ts` implementation and `.spec.ts` test file
-
-**Common blueprint steps:**
-
-- `installPlugin`, `activatePlugin`: Plugin management
-- `installTheme`, `activateTheme`: Theme management
-- `login`: User authentication
-- `runPHP`, `runPHPWithOptions`: Execute PHP code
-- `defineWpConfigConsts`: Modify wp-config.php
-- `importWxr`, `importWordPressFiles`: Import content
-
-### Storage & Sync
-
-- `@wp-playground/storage`: Provides filesystem backends (IndexedDB in browser, filesystem in Node)
-- `@wp-playground/sync`: Multi-client synchronization for collaborative editing
-- `@php-wasm/fs-journal`: Tracks filesystem changes for synchronization
-
-### WordPress Builds
-
-`@wp-playground/wordpress-builds` compiles specific WordPress versions into the playground format. Each version is tested and bundled separately.
-
-### Multi-Runtime PHP Support
-
-PHP binaries are compiled separately for:
-
-- **Web (browser)**: Asyncify and JSPI variants for different browser capabilities
-- **Node.js**: Native async/await support
-
-Version-specific builds: `@php-wasm/web-7-4` through `@php-wasm/web-8-5` (and corresponding node-builds)
-
-## Development Conventions
-
-### TypeScript
-
-- **Type imports must be explicit**: Use `import type { Foo } from 'bar'` (required for Node.js type stripping)
-- **No parameter properties**: TypeScript parameter properties are not supported by Node.js type stripping
-- Module resolution: `bundler` mode in tsconfig
-- Target: ES2021 with ESNext modules
-- Path aliases defined in `tsconfig.base.json` for cross-package imports
-
-### Code Style
-
-- **Comment length**: Max 100 characters per line (enforced by ESLint)
-- **No console.log**: Disallowed except in tests and bin/ scripts
-- **Consistent type imports**: Required by `@typescript-eslint/consistent-type-imports`
-- **Module boundaries**: Enforced via `@nx/enforce-module-boundaries`
-    - Packages tagged `scope:web-client` cannot be depended on by others
-    - `scope:independent-from-php-binaries` packages cannot depend on `scope:php-binaries`
-- **Function ordering:** First caller, then callee. When function A calls function B, write first A, then B.
-- **Method ordering:** First public, then protected, then private. Respect **Function ordering** as well.
-
-### Testing
-
-- **Test files**: Co-located with implementation as `*.spec.ts`
-- **Test runner**: Vitest (via `@nx/vite:test`)
-- **Coverage**: Reports to `coverage/packages/<package-name>`
-- **E2E tests**: Playwright and Cypress for website testing
-- **Always fix failing tests**: Never skip failing tests; fix the code to make tests pass
-
-### Package Structure
-
-All published packages follow this pattern:
-
-```
-packages/[layer]/[package-name]/
-├── src/
-│   ├── index.ts              # Main entry point
-│   └── lib/                  # Implementation
-├── package.json              # npm metadata
-├── project.json              # NX build configuration
-├── tsconfig.json             # Base TypeScript config
-├── tsconfig.lib.json         # Library build config
-├── tsconfig.spec.json        # Test config
-└── README.md                 # Package documentation
-```
-
-### Publishing
-
-- **Dual format**: All packages publish both ESM (`.js`) and CommonJS (`.cjs`)
-- **publishConfig.directory**: Points to `dist/packages/[layer]/[package-name]`
-- **Lerna**: Used for coordinated multi-package publishing (`npm run release`)
-- **Exports field**: Defines both `import` and `require` conditions
-- Version management: All packages versioned together (currently 3.0.42)
-
-## Special Workflows
-
-### Running Tests from Source
-
-```bash
-# Individual package test
-npx nx test playground-blueprints
-
-# Run specific test file
-npx nx test playground-blueprints --testFile=activate-plugin.spec.ts
-
-# Run with coverage
-npx nx test playground-blueprints --coverage
-
-# E2E tests
-npx nx e2e playground-website
-```
-
-### CLI Development
-
-The Playground CLI (`@wp-playground/cli`) can be run directly from source:
-
-```bash
-nvm use
-npx nx dev playground-cli server --wp=6.8 --php=8.4 --auto-mount
-```
-
-**CLI features:**
-
-- `--auto-mount`: Automatically detect and mount plugin/theme/WordPress directory
-- `--blueprint=<path>`: Execute a blueprint JSON file
-- `--mount=<src>:<dest>`: Manually mount directories
-- `--login`: Auto-login as admin
-- `--php=<version>`: Choose PHP version (7.4-8.5)
-- `--wp=<version>`: Choose WordPress version
-
-### Git Operations
-
-- **Never use bare `git push`**: Always specify remote and branch explicitly
-- **Shallow clone recommended**: `git clone -b trunk --single-branch --depth 1 --recurse-submodules`
-- **Submodules**: isomorphic-git submodule provides browser-based git operations
-
-### Working with PHP Binaries
-
-PHP binaries are pre-compiled and committed to the repository. Recompilation is rarely needed but can be done with:
-
-```bash
-# Recompile all PHP versions for web
-npm run recompile:php:web
-
-# Recompile specific PHP version with JSPI
-npx nx recompile-php:jspi php-wasm-web -- --PHP_VERSION=8.4
-
-# Debug builds (with DWARF info)
-npx nx recompile-php:all php-wasm-node -- --WITH_DEBUG=yes
-
-# Source maps for debugging
-npx nx recompile-php:all php-wasm-node -- --WITH_SOURCEMAPS=yes
-```
-
-### Custom NX Executors
-
-Located in `packages/nx-extensions/src/executors/`:
-
-- `package-json`: Generates package.json with correct exports
-- `assert-built-esm-and-cjs`: Verifies dual-format build
-- `package-for-self-hosting`: Creates distributable archives
-
-## Key Files & Directories
-
-- `nx.json`: NX workspace configuration
-- `tsconfig.base.json`: TypeScript path aliases and compiler options
-- `package.json`: Root package with all npm scripts
-- `.eslintrc.json`: ESLint rules including module boundaries
-- `packages/playground/blueprints/src/lib/steps/`: Blueprint step implementations
-- `packages/php-wasm/universal/`: Core PHP abstraction layer
-- `packages/playground/website/`: Main demo application
-- `packages/playground/cli/`: CLI tool implementation
-- `isomorphic-git/`: Git operations in browser (submodule)
-
-## Node.js Version
-
-Review the package.json file for the required Node.js version. At the time of writing, it's Node.js >= 20.18.3 (LTS) and npm >= 10.1.0.
-
-## Documentation
-
-- Main docs: https://wordpress.github.io/wordpress-playground/
-- Built with Docusaurus in `packages/docs/`
-- API reference generated with TypeDoc from package source
-
-## Important Notes
-
-- **No backwards-compatibility guarantees**: This is experimental software
-- **Offline support**: Website can be built for offline use with service workers
-- **WordPress major and beta versions**: Auto-refreshed via GitHub Actions
-- **SQLite integration**: WordPress uses SQLite by default (no MySQL required)
-- **Security**: Iframe-based isolation prevents untrusted code execution in parent window
+@AGENTS.md
diff --git a/packages/php-wasm/compile/AGENTS.md b/packages/php-wasm/compile/AGENTS.md
@@ -0,0 +1,92 @@
+# PHP-WASM Compile
+
+This package compiles PHP and its C library dependencies to WebAssembly using
+Emscripten and Docker. It is not a TypeScript package — it's a Makefile + Dockerfile
+build pipeline.
+
+## Build Flow
+
+```
+base-image (Emscripten + build tools)
+    ↓
+Makefile targets (compile C libraries to .a files)
+    ↓
+php/Dockerfile (compile PHP with extensions, linking libraries)
+    ↓
+build.js (orchestrate Docker builds, extract WASM output)
+    ↓
+Output: packages/php-wasm/{web,node}-builds/<version>/{asyncify,jspi}/
+```
+
+## Key Files
+
+- `build.js` — Entry point. Parses arguments, builds base image, runs PHP Docker
+  build, extracts WASM output. Invoked by NX targets in `php-wasm-web`/`php-wasm-node`.
+- `Makefile` — Compiles all C libraries. Each library has Asyncify and JSPI targets.
+  Run `make all` to rebuild everything, or target individual libraries like
+  `make libz_jspi`.
+- `base-image/Dockerfile` — Ubuntu + Emscripten toolchain. All other builds depend
+  on this image (`playground-php-wasm:base`).
+- `php/Dockerfile` — The main PHP compilation. ~2400 lines. Accepts 20+ `--build-arg`
+  flags for extensions and configuration.
+
+## Two Compilation Variants
+
+Every library and the PHP binary are built in two variants:
+
+- **Asyncify** — Older approach. Transforms synchronous C code to be pausable/resumable.
+  Works in all browsers but adds overhead.
+- **JSPI** (JavaScript Promise Integration) — Modern approach. Better performance,
+  requires newer browsers. Uses `-fwasm-exceptions` and `-sSUPPORT_LONGJMP=wasm`.
+
+Libraries are stored under `<library>/{asyncify,jspi}/dist/`.
+
+### Asyncify and `ASYNCIFY_IMPORTS`
+
+Asyncify lets synchronous C code pause and resume across JavaScript async
+boundaries. This requires telling Emscripten which functions may appear on
+the call stack during an async operation. In `php/Dockerfile`:
+
+- **`ASYNCIFY_IMPORTS`** — Functions at the JS ↔ WASM boundary that trigger
+  async pauses: `invoke_*` glue functions (indirect calls) and JS bridge
+  functions like `js_open_process`, `js_fd_read`, `wasm_poll_socket`, etc.
+- **`ASYNCIFY_ONLY`** — Internal PHP/library functions that may be on the
+  stack when an async pause happens (~200+ functions covering networking,
+  image processing, XML/SOAP, etc.).
+
+If a function is missing from either list, the runtime crashes with
+**`RuntimeError: unreachable`**. The `@php-wasm/universal` package detects
+this and reports which functions may be missing.
+
+To fix missing functions, use the automated workflow:
+
+```bash
+npm run fix-asyncify
+```
+
+This iteratively recompiles PHP, runs tests, detects crashes, adds the
+missing functions to the Dockerfile, and repeats until all tests pass.
+
+JSPI does not need these lists — it uses native stack switching and only
+requires `JSPI_IMPORTS` (async boundary functions) and `JSPI_EXPORTS`
+(WASM functions callable from JS), both much smaller.
+
+## Custom PHP Extensions
+
+Located in subdirectories of this package:
+
+- `php-wasm-memory-storage/` — Workaround for Emscripten's incomplete mmap/munmap
+- `php-wasm-dns-polyfill/` — DNS lookups for the WASM environment
+- `php-post-message-to-js/` — JS ↔ PHP communication bridge
+- `opcache/` — OPcache adapted for WASM (with version-specific patches for PHP 8.4+)
+
+## Critical Constraints
+
+- **Emscripten version is pinned** in `base-image/Dockerfile`. Changing it requires
+  rebuilding ALL libraries from scratch. Do not upgrade without understanding the
+  implications.
+- **Library dist/ directories are committed** to the repository. They contain
+  pre-built `.a` files and headers. Recompilation is rarely needed.
+- **PHP version-specific patches** exist in `php/Dockerfile`, especially for OPcache
+  (PHP 8.4 renamed configuration variables). Check version guards when adding support
+  for new PHP versions.
PATCH

echo "Gold patch applied."
