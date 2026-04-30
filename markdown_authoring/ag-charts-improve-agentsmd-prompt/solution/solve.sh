#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ag-charts

# Idempotency guard
if grep -qF "-   **Baseline verification:** Expect to run `nx test ag-charts-community`, `nx " "tools/prompts/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/tools/prompts/AGENTS.md b/tools/prompts/AGENTS.md
@@ -2,6 +2,16 @@
 
 This file provides guidance to AI Agents when working with code in this repository.
 
+## Must-Know Checklist
+
+-   **Main constraint:** Community and enterprise runtime bundles stay dependency-free beyond AG Charts code.
+-   **Default branch:** Target `latest`; follow release/JIRA naming conventions below for topic branches.
+-   **Formatting:** Run `nx format` from the repo root before proposing commits.
+-   **Typechecking:** Run `nx build:types <package>` from the repo root before proposing commits.
+-   **Linting:** Run `nx lint <package>` from the repo root before proposing commits.
+-   **Baseline verification:** Expect to run `nx test ag-charts-community`, `nx test ag-charts-enterprise`, and `nx e2e ag-charts-website` after meaningful chart changes.
+-   **Context docs:** Skim `tools/prompts/technology-stack.md` for stack or architectural decisions before introducing new patterns.
+
 ## Project Overview
 
 AG Charts is a sophisticated TypeScript monorepo providing canvas-based JavaScript charting library with both community (MIT) and enterprise (commercial) versions. Built with Nx, it supports React, Angular, and Vue 3 frameworks.
@@ -20,60 +30,18 @@ For detailed information about preferred technologies and architectural constrai
 
 ## Essential Commands
 
-### Development Setup
-
-```bash
-yarn init                    # Install dependencies and setup
-nx clean                   # Clean all dist folders
-```
-
-### Building
-
-```bash
-nx build <package>           # Build specific package
-nx build:types <package>     # Generate TypeScript declarations
-nx build:package <package>   # Create ESM/CJS bundles
-nx build:umd <package>       # Create UMD browser bundles
-nx run-many -t build         # Build all packages
-```
-
-### Development Server
-
-```bash
-nx dev                       # Starts development Astro server and watch process (accessible on https://localhost:4600/)
-```
-
-### Testing
-
-```bash
-nx test <package>            # Run Jest unit tests
-nx e2e <package>            # Run Playwright E2E tests
-nx benchmark <package>       # Performance benchmarks
-nx lint <package>           # ESLint + custom rules
-```
-
-#### Running Specific Test Suites
-
-To run a single test suite or specific tests instead of the entire test suite:
-
-```bash
-# Run tests from a specific file
-nx test ag-charts-community --testPathPattern="lineSeries.test.ts"
-
-# Run tests matching a specific suite name (describe block)
-nx test ag-charts-community --testNamePattern="LineSeries"
-
-# Run tests from a specific path pattern
-nx test ag-charts-community --testPathPattern="series/cartesian/lineSeries"
-
-# Combine path and name patterns for more specific filtering
-nx test ag-charts-community --testPathPattern="lineSeries.test.ts" --testNamePattern="specific test name"
-
-# Run tests in watch mode for a specific file
-nx test ag-charts-community --watch --testPathPattern="lineSeries.test.ts"
-```
-
-Note: `--testPathPattern` matches against the file path, while `--testNamePattern` matches against test suite names (describe blocks) and individual test names (it blocks).
+-   `yarn init` – install dependencies after cloning or when the Yarn lockfile changes.
+-   `nx clean` – purge all dist folders when switching branches or before packaging releases.
+-   `nx format` – format repo files; run from the project root before committing.
+-   `nx build <package>` – compile a specific package after code edits.
+-   `nx build:types <package>` – regenerate declaration files when touching exported APIs.
+-   `nx build:package <package>` – create ESM/CJS bundles to validate publishable output.
+-   `nx build:umd <package>` – produce UMD bundles for browser distribution smoke-tests.
+-   `nx run-many -t build` – rebuild all packages when changes span the dependency graph.
+-   `nx test <package>` – execute Jest suites for the affected package.
+-   `nx e2e <package>` – run Playwright flows when altering website behaviour.
+-   `nx lint <package>` – apply ESLint and custom rules before final review.
+-   `nx benchmark <package>` – assess performance regressions; filter via `-- -t "pattern"` when needed.
 
 ## Slash Commands
 
@@ -127,42 +95,46 @@ Core dependency chain: `ag-charts-core` → `ag-charts-types` → `ag-charts-loc
 
 ## Common Development Tasks
 
-### Adding New Chart Types
+### Quick Playbooks
+
+-   **Bug fix or feature work (core/community/enterprise)**
+    1. Update the affected implementation (typically under `packages/ag-charts-*/src/chart`).
+    2. Adjust public API surface in `packages/ag-charts-types` if signatures change.
+    3. Sync any dependent docs/examples.
+    4. Run `nx test ag-charts-community`, `nx test ag-charts-enterprise`, and targeted `nx benchmark` commands when performance is at risk.
+-   **Documentation/content update**
+    1. Modify the relevant `.mdoc` under `packages/ag-charts-website/src/content/docs/`.
+    2. Update `packages/ag-charts-website/src/content/docs-nav/nav.json` if navigation changes.
+    3. For significant doc changes, sanity-check with `nx e2e ag-charts-website`.
+-   **Example-only change**
+    1. Edit the example files (`index.html`, `main.ts`, optional `styles.css`/`data.ts`).
+    2. Mirror updates in the sibling `index.mdoc` docs page.
+    3. Run the relevant generation/typecheck command plus `nx validate-examples` (see [Example Validation + Building](#example-validation--building)).
 
-1. Implement in `packages/ag-charts-core/src/chart/series/`
-2. Register module in appropriate community/enterprise package
-3. Add TypeScript definitions in `packages/ag-charts-types/`
-4. Update documentation in `packages/ag-charts-website/`
-
-### Testing Changes
-
-Always run both unit and visual regression tests:
+### Adding New Chart Types
 
-```bash
-nx test ag-charts-community
-nx test ag-charts-enterprise
-nx e2e ag-charts-website
-```
+-   Implement the series in `packages/ag-charts-core/src/chart/series/`.
+-   Register the module in the matching community and/or enterprise package.
+-   Extend TypeScript definitions in `packages/ag-charts-types/`.
+-   Document the feature within `packages/ag-charts-website/` (including examples when appropriate).
 
 ### Performance Considerations
 
--   Use `nx benchmark` to check performance impact
--   Canvas rendering optimizations are critical
--   Memory profiling available through benchmark suite
+-   Use `nx benchmark` to check performance impact on hotspots.
+-   Focus on canvas rendering efficiency and memory churn.
+-   Enable `AG_BENCHMARK_DEBUG=1` locally for detailed memory output.
 
 ### Benchmarks
 
--   Benchmark tests are located in `packages/ag-charts-{community,enterprise}/benchmarks/`
--   Benchmarks include visual snapshot comparisons by default
--   The `BENCHMARK_SOFT_FAIL` environment variable is used in CI to disable snapshot comparisons for performance-only benchmark runs
--   Enterprise benchmarks re-export community benchmark utilities via `packages/ag-charts-enterprise/benchmarks/benchmark.ts`
+-   Benchmark suites live in `packages/ag-charts-{community,enterprise}/benchmarks/`.
+-   Visual snapshots run by default; set `BENCHMARK_SOFT_FAIL=1` in CI to skip them.
+-   Enterprise benchmarks re-export community utilities via `packages/ag-charts-enterprise/benchmarks/benchmark.ts`.
 
 #### Running Benchmarks
 
--   Use `nx benchmark ag-charts-community -- -t "initial load"` to run all 'initial load' tests for the community package
--   Use `nx benchmark ag-charts-enterprise -- -t "initial load"` to run all 'initial load' tests for the enterprise package
--   Due to the nx benchmark task construction using xargs, it's not possible to filter to specific test files - you must filter by test name pattern instead
--   For debug output showing memory breakdown, use: `AG_BENCHMARK_DEBUG=1 nx benchmark <package> -- -t "<test pattern>"`
+-   `nx benchmark ag-charts-community -- -t "initial load"` runs all "initial load" cases for community.
+-   `nx benchmark ag-charts-enterprise -- -t "initial load"` does the same for enterprise.
+-   Filtering is by test name pattern (xargs prevents targeting individual files).
 
 ## Technical Requirements
 
@@ -194,8 +166,7 @@ nx e2e ag-charts-website
 
 ## Documentation Resources
 
--   AG Charts architecture docs can be found at https://docs.ag-grid.com/architecture/charts/ag-charts-overview
-    -   This provides an overview of the important aspects of the ag-charts codebase, as well as links to deeper dives into specific aspects. Use this as a reference if you need help navigating the code.
+-   AG Charts architecture overview: https://docs.ag-grid.com/architecture/charts/ag-charts-overview (entry point to deeper design references).
 
 ## Production URLs
 
@@ -205,37 +176,24 @@ nx e2e ag-charts-website
 
 -   The staging base URLs for the Astro site is https://charts-staging.ag-grid.com/
     -   NOTE: That the `/charts` path prefix is not used for paths on the staging site.
--   Gallery examples on staging use the pattern: `https://charts-staging.ag-grid.com/gallery/[example-name]/`
-    -   Example: `https://charts-staging.ag-grid.com/gallery/simple-bar/`
-    -   Example: `https://charts-staging.ag-grid.com/gallery/bar-with-labels/`
 
 ## Development Server Notes
 
--   Normally the Astro dev server is running on port 4600 (HTTPS) and you can just use it.
-    -   If using the puppeteer MCP tool, you must use the following configuration by default:
-        ```javascript
-        await puppeteer_navigate({
-            url: `${url}`,
-            allowDangerous: true, // Required for self-signed certificate
-            launchOptions: {
-                headless: true, // Required to avoid focus issues
-                args: ['--ignore-certificate-errors'],
-            },
-        });
-        ```
--   If you need to run the dev server, use `nx dev` to start it.
-    -   This includes an incremental watch and build of all packages and website.
--   `packages/ag-charts-website/src/content/gallery/data.json` is the source of truth for the gallery examples.
--   `packages/ag-charts-website/src/content/docs-nav/nav.json` is the source of truth for the website docs navigation.
--   Docs paths are mapped from repo paths:
-    -   `packages/ag-charts-website/src/content/docs/${pageName}/index.mdoc` => `/charts/javascript/${pageName}/`
+### Astro Dev Server Checklist
+
+-   Prefer the shared HTTPS server on port 4600 when available.
+-   When using the Puppeteer MCP tool, pass `allowDangerous: true`, run headless, and include `--ignore-certificate-errors` to handle the self-signed cert.
+-   Start a local watcher with `nx dev` whenever you need live rebuilds across packages and the website.
+-   `packages/ag-charts-website/src/content/gallery/data.json` owns gallery example metadata.
+-   `packages/ag-charts-website/src/content/docs-nav/nav.json` owns docs navigation structure.
+-   Docs map from `packages/ag-charts-website/src/content/docs/${pageName}/index.mdoc` to `/charts/javascript/${pageName}/`.
 
 ## Examples
 
 ### Repo to dev server paths
 
 -   Note that example paths are mapped from repo paths:
-    -   `packages/ag-charts-website/src/content/gallery/_examples/${exampleName}/index.html` => `/charts/gallery/${exampleName}`
+    -   `packages/ag-charts-website/src/content/gallery/_examples/${exampleName}/index.html` => `/charts/gallery/examples/${exampleName}`
     -   `packages/ag-charts-website/src/content/docs/${pageName}/_examples/${exampleName}/index.html` => `/charts/vanilla/${pageName}/examples/${exampleName}`
 
 ### Example Guidelines
@@ -255,17 +213,20 @@ nx e2e ag-charts-website
     -   Styles in `external/ag-website-shared/src/components/example-runner/styles/example-controls.css` are applied automatically, and should be favoured for presenting controls in examples.
 -   Examples typically have a `data.ts` with a `getData()` function (for single data-set examples) which includes the dataset used by the example.
 -   If a TData type is useful for the example, `data.ts` should also declare this.
--   AG Charts architecture docs can be found at https://docs.ag-grid.com/architecture/charts/ag-charts-overview
-    -   This provides an overview of the important aspects of the ag-charts codebase, as well as links to deeper dives into specific aspects. Use this as a reference if you need help navigating the code.
+-   For deeper architectural context, see [Documentation Resources](#documentation-resources).
 
 ### Example Validation + Building
 
--   For gallery examples run: `nx run ag-charts-website-gallery_${exampleName}_main.ts:generate`
-    -   For typechecking examples run: `nx run ag-charts-website-gallery_${exampleName}_main.ts:typecheck`
--   For docs examples run: `nx run ag-charts-website-${pageName}_${exampleName}_main.ts:generate`
-    -   For typechecking docs examples run: `nx run ag-charts-website-${pageName}_${exampleName}_main.ts:typecheck`
--   For all examples also run: `nx validate-examples` (NOTE: This does a batch `typecheck` which is VERY fast compared to running individual `typecheck` targets).
--   For adhoc examples to quickly test things or `-test` pages, adding `// @ag-skip-fws` to `main.ts` will disable framework (React, Angylar, Vue) variant generation.
+-   **Gallery example** (`packages/ag-charts-website/src/content/gallery/_examples/${exampleName}/`)
+    -   `nx run ag-charts-website-gallery_${exampleName}_main.ts:generate`
+    -   `nx run ag-charts-website-gallery_${exampleName}_main.ts:typecheck`
+-   **Docs example** (`packages/ag-charts-website/src/content/docs/${pageName}/_examples/${exampleName}/`)
+    -   `nx run ag-charts-website-${pageName}_${exampleName}_main.ts:generate`
+    -   `nx run ag-charts-website-${pageName}_${exampleName}_main.ts:typecheck`
+-   **All examples**
+    -   `nx validate-examples` (batch typecheck; much faster than individual targets).
+-   **Ad-hoc or `-test` examples**
+    -   Add `// @ag-skip-fws` to `main.ts` to skip framework variant generation.
 
 ## Releases
 
PATCH

echo "Gold patch applied."
