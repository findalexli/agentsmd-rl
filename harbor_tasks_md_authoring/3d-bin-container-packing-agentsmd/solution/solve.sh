#!/usr/bin/env bash
set -euo pipefail

cd /workspace/3d-bin-container-packing

# Idempotency guard
if grep -qF "Foundation layer of the 3D bin-packing library. Defines all public interfaces, a" "api/agents.md" && grep -qF "The main algorithmic engine. Implements all packager strategies (LAFF, brute-for" "core/agents.md" && grep -qF "Microbenchmark suite using the OpenJDK JMH framework. Measures throughput and la" "jmh/agents.md" && grep -qF "Parent POM aggregating all REST API modules. Defines shared dependency managemen" "open-api/agents.md" && grep -qF "Generated Apache HttpComponents Client 5 stubs for calling the Pack REST API. Pr" "open-api/open-api-client/agents.md" && grep -qF "Generated Jackson data model for the Pack REST API. Contains all request/respons" "open-api/open-api-model/agents.md" && grep -qF "Generated Spring server-side interface stubs for the Pack REST API. Provides `Pa" "open-api/open-api-server/agents.md" && grep -qF "Shared test utilities for the open-api modules. Provides common helpers, fixture" "open-api/open-api-test/agents.md" && grep -qF "Manages free-space bookkeeping during packing. Tracks 2D and 3D points that repr" "points/agents.md" && grep -qF "Shared testing utilities consumed by every other module's test scope. Provides c" "test/agents.md" && grep -qF "Captures intermediate algorithm states during packing for step-by-step visualisa" "visualizer/algorithm/agents.md" && grep -qF "Defines the JSON serialisation interfaces and data structures used to represent " "visualizer/api/agents.md" && grep -qF "Converts completed packing results into the JSON format consumed by the Three.js" "visualizer/packaging/agents.md" && grep -qF "Interactive 3D front-end for visualising packing results. Renders packed contain" "visualizer/viewer/agents.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/api/agents.md b/api/agents.md
@@ -0,0 +1,31 @@
+# API Module
+
+## Purpose
+Foundation layer of the 3D bin-packing library. Defines all public interfaces, abstract base classes, and core data structures that the rest of the system depends on. No algorithm logic lives here — only contracts.
+
+## Key Packages
+- `com.github.skjolber.packing.api` — Core types: `Packager`, `PackagerResult`, `PackagerResultBuilder`, `BoxStackValue`, `Rotation`, `Surface`
+- `com.github.skjolber.packing.api.packager` — Item source abstractions for boxes and containers
+- `com.github.skjolber.packing.api.packager.control` — Control framework: `ManifestControls`, `PlacementControls`, `PointControls`
+- `com.github.skjolber.packing.api.point` — Point-related interfaces used by free-space tracking
+- `com.github.skjolber.packing.api.validator` — Validation interfaces for placement correctness
+
+## Architecture Notes
+- This is the **dependency root** — no other internal modules are imported here.
+- All packager implementations in `core` implement `Packager<B>`.
+- Builder pattern is used heavily (`PackagerResultBuilder`).
+- Changes to interfaces here cascade to every module — be conservative.
+
+## Testing
+- JUnit 5, AssertJ, Mockito, jQwik (property-based)
+- No integration tests; unit tests only
+
+## Dependencies
+| Scope | Artifact |
+|-------|----------|
+| test  | junit-jupiter, assertj-core, mockito-core, jqwik |
+
+## Build
+```
+mvn test -pl api
+```
diff --git a/core/agents.md b/core/agents.md
@@ -0,0 +1,37 @@
+# Core Module
+
+## Purpose
+The main algorithmic engine. Implements all packager strategies (LAFF, brute-force, plain), box permutation/rotation iterators, deadline management for time-bounded packing, and placement validation.
+
+## Key Packages
+- `com.github.skjolber.packing.packer.laff` — Largest Area Fit First: `LargestAreaFitFirstPackager`, `FastLargestAreaFitFirstPackager`
+- `com.github.skjolber.packing.packer.bruteforce` — `BruteForcePackager`, `FastBruteForcePackager`, `ParallelBruteForcePackager`
+- `com.github.skjolber.packing.packer.plain` — `PlainPackager` (simple greedy)
+- `com.github.skjolber.packing.iterator` — `BoxItemPermutationRotationIterator`, `BoxItemGroupPermutationRotationIterator`, `FilteredBoxItemsPermutationRotationIterator`
+- `com.github.skjolber.packing.deadline` — `DeadlineCheckPackagerInterruptSupplier`, `PackagerInterruptSupplierBuilder`
+- `com.github.skjolber.packing.comparator` — Result comparators for selecting the best packing
+- `com.github.skjolber.packing.validator` — Runtime placement correctness checks
+
+## Architecture Notes
+- All packagers implement `Packager<B>` from **api**.
+- Depends on **points** for free-space tracking during placement.
+- Strategy pattern: swap packager implementations at construction time; the calling code interacts only via the `Packager` interface.
+- Deadline/interrupt pattern: callers supply a `Supplier<Boolean>` that the packager polls; return `true` to abort early.
+- `ParallelBruteForcePackager` uses a `ForkJoinPool`; avoid shared mutable state in iterators.
+- `Fast*` variants trade flexibility for reduced allocation and faster iteration.
+
+## Testing
+- JUnit 5, AssertJ, jQwik, junit-quickcheck
+- Property-based tests verify packing correctness across random inputs
+- Run: `mvn test -pl core`
+
+## Dependencies
+| Scope   | Artifact |
+|---------|----------|
+| compile | api, points |
+| test    | test module, junit-jupiter, assertj-core, jqwik, junit-quickcheck |
+
+## Build
+```
+mvn test -pl core
+```
diff --git a/jmh/agents.md b/jmh/agents.md
@@ -0,0 +1,40 @@
+# JMH Benchmarks Module
+
+## Purpose
+Microbenchmark suite using the OpenJDK JMH framework. Measures throughput and latency of packagers, iterators, and point calculators to detect regressions and guide performance optimisation.
+
+## Key Packages
+- `com.github.skjolber.packing.jmh` — Packager benchmarks (`PackagerBenchmark`, `DeadlineBenchmark`, `EgyPackagerBenchmark`, `TychoBenchmark`) and shared state classes
+- `com.github.skjolber.packing.jmh.iterator` — Iterator benchmarks (`DefaultIteratorBenchmark`, `ParallelIteratorBenchmark`)
+- `com.github.skjolber.packing.jmh.ep` — Enhanced-point calculator benchmarks
+
+## Architecture Notes
+- `@State(Scope.Benchmark)` classes set up packagers and test data once per benchmark run.
+- `BouwkampConverter` bridges test-module Bouwkamp codes into JMH benchmark inputs.
+- The Maven Shade plugin produces a fat JAR (`benchmarks.jar`) for running benchmarks in isolation.
+- JMH requires that benchmark methods are **not** inlined by the JIT — annotate with `@Benchmark`, never call them directly.
+- Output JSON results can be visualised at https://jmh.morethan.io.
+
+## Running Benchmarks
+```bash
+# Build the fat JAR
+mvn package -pl jmh -am -DskipTests
+
+# Run all benchmarks
+java -jar jmh/target/benchmarks.jar
+
+# Run a specific benchmark with custom settings
+java -jar jmh/target/benchmarks.jar PackagerBenchmark -f 1 -wi 3 -i 5 -rf json -rff results.json
+```
+
+## Dependencies
+| Scope   | Artifact |
+|---------|----------|
+| compile | core, points |
+| test    | test module, commons-io |
+| provided | jmh-core, jmh-generator-annprocess |
+
+## Build
+```
+mvn package -pl jmh -am -DskipTests
+```
diff --git a/open-api/agents.md b/open-api/agents.md
@@ -0,0 +1,25 @@
+# Open-API Parent Module
+
+## Purpose
+Parent POM aggregating all REST API modules. Defines shared dependency management and build configuration for the OpenAPI-generated code. The actual Pack API is a single POST `/pack` endpoint.
+
+## Sub-modules
+| Directory | Artifact | Role |
+|-----------|----------|------|
+| `open-api-model` | open-api-model | Generated Jackson data model |
+| `open-api-server` | open-api-server | Generated Spring server interfaces |
+| `open-api-client` | open-api-client | Generated Apache HttpClient 5 client |
+| `open-api-test` | open-api-test | Shared test utilities for the API |
+
+## API Specification
+The canonical source of truth is `open-api/3d-api.yaml` (OpenAPI 3.0). All model, server, and client code is **generated** — edit the spec, then regenerate; do not hand-edit generated sources.
+
+## Regenerating Code
+```bash
+mvn generate-sources -pl open-api/open-api-model,open-api/open-api-server,open-api/open-api-client
+```
+
+## Build
+```bash
+mvn install -pl open-api -am
+```
diff --git a/open-api/open-api-client/agents.md b/open-api/open-api-client/agents.md
@@ -0,0 +1,33 @@
+# Open-API Client Sub-module
+
+## Purpose
+Generated Apache HttpComponents Client 5 stubs for calling the Pack REST API. Provides a type-safe Java client that serialises `PackRequest` and deserialises `PackResponse` over HTTP.
+
+## Key Package
+`com.github.skjolber.packing.openapi.client.api` — `PackApi` client class
+
+## Architecture Notes
+- **All source files are generated** from `../3d-api.yaml`. Do not hand-edit.
+- Built on **Apache HttpComponents Client 5** (supports async and connection pooling).
+- Depends on **open-api-model** for request/response types.
+- Integration tests use **open-api-server** stubs (test scope) to run a local server.
+
+## Usage
+```java
+ApiClient client = new ApiClient();
+client.setBasePath("http://localhost:8080");
+PackApi api = new PackApi(client);
+PackResponse response = api.pack(request);
+```
+
+## Dependencies
+| Scope   | Artifact |
+|---------|----------|
+| compile | open-api-model |
+| compile | httpclient5, jackson-databind |
+| test    | open-api-server, truth |
+
+## Regenerating
+```bash
+mvn generate-sources -pl open-api/open-api-client
+```
diff --git a/open-api/open-api-model/agents.md b/open-api/open-api-model/agents.md
@@ -0,0 +1,24 @@
+# Open-API Model Sub-module
+
+## Purpose
+Generated Jackson data model for the Pack REST API. Contains all request/response POJOs produced by the OpenAPI Generator Maven plugin from `../3d-api.yaml`.
+
+## Key Package
+`com.github.skjolber.packing.openapi.model` — `PackRequest`, `PackResponse`, and related value types
+
+## Architecture Notes
+- **All source files are generated.** Do not edit them by hand; modify `3d-api.yaml` and re-run `mvn generate-sources`.
+- Uses Jackson annotations for JSON serialisation and Jakarta Validation annotations (`@NotNull`, `@Size`, etc.) for bean validation.
+- Swagger/OpenAPI 3 annotations (`@Schema`) are retained in generated code for documentation.
+
+## Dependencies
+| Scope   | Artifact |
+|---------|----------|
+| compile | jackson-databind, jackson-annotations |
+| compile | jakarta.validation-api |
+| compile | swagger-annotations |
+
+## Regenerating
+```bash
+mvn generate-sources -pl open-api/open-api-model
+```
diff --git a/open-api/open-api-server/agents.md b/open-api/open-api-server/agents.md
@@ -0,0 +1,36 @@
+# Open-API Server Sub-module
+
+## Purpose
+Generated Spring server-side interface stubs for the Pack REST API. Provides `PackApi` (and related interfaces) ready to be implemented by a Spring Boot `@RestController`.
+
+## Key Package
+`com.github.skjolber.packing.openapi.server.api` — `PackApi` interface with Spring `@RequestMapping` annotations
+
+## Architecture Notes
+- **All source files are generated** from `../3d-api.yaml`. Do not hand-edit.
+- Generated in **interface-only** mode — no implementation is provided. Wire a `@RestController` that implements `PackApi`.
+- Compatible with **Spring Boot 3** (Spring 7.x, Jakarta namespaces).
+- Depends on **open-api-model** for request/response types.
+
+## Implementing the API
+```java
+@RestController
+public class PackController implements PackApi {
+    @Override
+    public ResponseEntity<PackResponse> pack(PackRequest request) {
+        // delegate to a core Packager
+    }
+}
+```
+
+## Dependencies
+| Scope   | Artifact |
+|---------|----------|
+| compile | open-api-model |
+| compile | spring-web, spring-context |
+| compile | jakarta.annotation-api, jakarta.validation-api |
+
+## Regenerating
+```bash
+mvn generate-sources -pl open-api/open-api-server
+```
diff --git a/open-api/open-api-test/agents.md b/open-api/open-api-test/agents.md
@@ -0,0 +1,19 @@
+# Open-API Test Sub-module
+
+## Purpose
+Shared test utilities for the open-api modules. Provides common helpers, fixtures, and Mockito-based mocks reusable across `open-api-server` and `open-api-client` tests.
+
+## Architecture Notes
+- Consumed as a `test`-scoped dependency by the sibling open-api modules.
+- Currently minimal; grow this module to avoid duplication when adding integration tests across server/client.
+
+## Dependencies
+| Scope   | Artifact |
+|---------|----------|
+| compile | open-api-model, open-api-server |
+| compile | mockito-core |
+
+## Build
+```bash
+mvn test -pl open-api/open-api-test -am
+```
diff --git a/points/agents.md b/points/agents.md
@@ -0,0 +1,30 @@
+# Points Module
+
+## Purpose
+Manages free-space bookkeeping during packing. Tracks 2D and 3D points that represent candidate placement locations within a container. Provides point calculators that maintain and update the set of available positions as boxes are placed.
+
+## Key Packages
+- `com.github.skjolber.packing.ep.points2d` — 2D point types: `Point2D`, `DefaultPoint2D`, `XSupportPoint2D`, `YSupportPoint2D`, `Point2DList`, `Point2DFlagList`
+- `com.github.skjolber.packing.ep.points3d` — 3D point types: `Point3D`, `DefaultPoint3D`, plane-specific variants (`XYPlanePoint3D`, `XZPlanePoint3D`, `YZPlanePoint3D`)
+- Calculator strategies: `DefaultPointCalculator2D`, `MarkResetPointCalculator2D`
+
+## Architecture Notes
+- Depends only on **api**; no dependency on **core**.
+- Uses **Eclipse Collections** for performance-optimized list operations — prefer these over standard `java.util` collections.
+- `Point2DFlagList` uses bitmask flags to avoid object allocation in hot paths.
+- Plane-specific 3D variants encode which container walls support a placement, enabling smarter candidate filtering.
+
+## Testing
+- JUnit 5, AssertJ, jQwik (property-based tests verify point calculator invariants)
+- Run: `mvn test -pl points`
+
+## Dependencies
+| Scope   | Artifact |
+|---------|----------|
+| compile | api, eclipse-collections |
+| test    | test module, junit-jupiter, assertj-core, jqwik |
+
+## Build
+```
+mvn test -pl points
+```
diff --git a/test/agents.md b/test/agents.md
@@ -0,0 +1,29 @@
+# Test Module
+
+## Purpose
+Shared testing utilities consumed by every other module's test scope. Provides custom AssertJ assertions, Bouwkamp-code-based test data, and item/box generators for property-based and academic benchmark tests.
+
+## Key Packages
+- `com.github.skjolber.packing.test.assertj` — Fluent custom assertions: `ContainerAssert`, `PackagerAssert`, `StackAssert`, `StackPlacementAssert`, `Point3DAssert`
+- `com.github.skjolber.packing.test.bouwkamp` — Bouwkamp codes for squared-rectangle test cases: `BouwkampCodes`, `BouwkampCodeParser`, `BouwkampCodeDirectory`
+- `com.github.skjolber.packing.test` — Generic box/item generators used in property-based tests
+
+## Architecture Notes
+- This module is a **test utility library**, not a runnable application.
+- Consumed as a `test`-scoped dependency by **core**, **points**, **jmh**, and others.
+- Bouwkamp codes provide mathematically exact perfect-rectangle test cases (from http://www.squaring.net/) — useful for verifying exact fit without gaps.
+- `AssertJ` custom assertions should follow the `AbstractAssert<SELF, ACTUAL>` pattern.
+
+## Dependencies
+| Scope   | Artifact |
+|---------|----------|
+| compile | api |
+| compile | assertj-core, truth, truth-java8-extension |
+| compile | jackson-databind (test data serialization) |
+| compile | commons-math3 (statistical helpers) |
+| test    | junit-jupiter, jqwik, mockito-core |
+
+## Build
+```
+mvn test -pl test
+```
diff --git a/visualizer/algorithm/agents.md b/visualizer/algorithm/agents.md
@@ -0,0 +1,31 @@
+# Visualizer Algorithm Module
+
+## Purpose
+Captures intermediate algorithm states during packing for step-by-step visualisation. Records per-iteration decisions, metric snapshots, and filter operations so the viewer can replay the algorithm's internal reasoning.
+
+> **Status**: Work in progress — not yet released as a stable API.
+
+## Key Packages
+- `com.github.skjolber.packing.visualizer.api.packager` — Algorithm event types:
+  - `AlgorithmListener` — callback interface; implement to intercept algorithm events
+  - `PackagerAlgorithm`, `PackagerIteration`, `PackagerOperation` — event/state hierarchy
+  - `ContainerWorkspace` — snapshot of the container state at a given step
+  - `MetricVisualization` — numeric metric capture for charting
+  - `BoxFilter`, `ContainerFilter` — filter operation records
+
+## Architecture Notes
+- Depends on **core** (hooks into packager internals).
+- The `AlgorithmListener` interface is the primary extension point; wire it into a packager builder to receive events.
+- Because this module is unstable, avoid depending on it from production code in other modules.
+
+## Dependencies
+| Scope   | Artifact |
+|---------|----------|
+| compile | core |
+| compile | jackson-databind |
+| test    | junit-jupiter, assertj-core |
+
+## Build
+```bash
+mvn test -pl visualizer/algorithm -am
+```
diff --git a/visualizer/api/agents.md b/visualizer/api/agents.md
@@ -0,0 +1,27 @@
+# Visualizer API Module
+
+## Purpose
+Defines the JSON serialisation interfaces and data structures used to represent packing results for the Three.js viewer. Acts as the contract between the Java back-end and the front-end visualizer.
+
+## Key Packages
+- `com.github.skjolber.packing.visualizer.api.packaging` — Core visualizer types:
+  - `AbstractVisualizer`, `PackagingResultVisualizer` — root visualizer interfaces
+  - `BoxVisualizer`, `ContainerVisualizer`, `StackVisualizer`, `StackPlacementVisualizer` — per-object serialisation wrappers
+  - `PointVisualizer` — free-point visualisation
+  - `VisualizerPlugin` — extension point for custom rendering data
+
+## Architecture Notes
+- Depends on **core** (consumes `PackagerResult`, `StackPlacement`, etc.).
+- Jackson annotations drive JSON output format; the viewer (`visualizer/viewer`) parses this JSON — any field renaming is a breaking change to the front-end.
+- `VisualizerPlugin` follows the plugin pattern: implement and register to attach extra data to the JSON output.
+
+## Dependencies
+| Scope   | Artifact |
+|---------|----------|
+| compile | core |
+| compile | jackson-databind |
+
+## Build
+```bash
+mvn test -pl visualizer/api -am
+```
diff --git a/visualizer/packaging/agents.md b/visualizer/packaging/agents.md
@@ -0,0 +1,36 @@
+# Visualizer Packaging Module
+
+## Purpose
+Converts completed packing results into the JSON format consumed by the Three.js viewer. Bridges the core packing domain with the visualizer API.
+
+## Key Packages
+- `com.github.skjolber.packing.visualizer.packaging`
+  - `PackagingResultVisualizerFactory` — factory interface; use to produce a `PackagingResultVisualizer` from a `PackagerResult`
+  - `DefaultPackagingResultVisualizerFactory` — standard implementation
+  - `AbstractPackagingResultVisualizerFactory` — base class for custom factories
+
+## Architecture Notes
+- Depends on **core**, **api**, **points**, and **visualizer-api**.
+- The factory converts `PackagerResult` → `PackagingResultVisualizer` → JSON (via Jackson in `visualizer-api`).
+- To customise output (e.g., add colour coding), extend `AbstractPackagingResultVisualizerFactory` and attach `VisualizerPlugin` instances.
+- Keep this module free of Spring/framework dependencies so it can be used in standalone and server contexts.
+
+## Typical Usage
+```java
+PackagingResultVisualizerFactory factory = new DefaultPackagingResultVisualizerFactory();
+PackagingResultVisualizer visualizer = factory.visualizer(packagerResult);
+String json = objectMapper.writeValueAsString(visualizer);
+```
+
+## Dependencies
+| Scope   | Artifact |
+|---------|----------|
+| compile | api, core, points |
+| compile | visualizer-api |
+| compile | jackson-databind |
+| test    | test module, junit-jupiter |
+
+## Build
+```bash
+mvn test -pl visualizer/packaging -am
+```
diff --git a/visualizer/viewer/agents.md b/visualizer/viewer/agents.md
@@ -0,0 +1,50 @@
+# Visualizer Viewer
+
+## Purpose
+Interactive 3D front-end for visualising packing results. Renders packed containers and boxes in a Three.js scene, supports step-through navigation of results, and can display free placement points.
+
+## Technology Stack
+| Category | Technology |
+|----------|-----------|
+| Framework | React 18 |
+| 3D Graphics | Three.js 0.180 |
+| Language | TypeScript 4.9 + JavaScript |
+| Build tooling | Create React App (react-scripts 5) |
+| GUI controls | dat.GUI 0.7 |
+| Performance HUD | Stats.js |
+
+## Key Source Files
+- `src/index.js` — React entry point
+- `src/ThreeScene.js` — Three.js scene setup, camera, lighting, box/container mesh creation
+- `src/api.ts` — Typed API client for fetching packing JSON from the Java back-end
+- `src/utils.ts` — Geometry and colour utilities
+
+## Input Data Format
+Expects the JSON produced by `visualizer/packaging` (`DefaultPackagingResultVisualizerFactory`). Changes to that module's JSON schema are breaking changes here.
+
+## Keyboard Controls
+| Key | Action |
+|-----|--------|
+| A / D | Previous / next packaging step |
+| W / S | Previous / next point step |
+| P | Toggle free placement points |
+| 1 / 2 | Rotate XY plane |
+| Mouse wheel | Zoom |
+| Left-drag | Rotate view |
+| Right-drag | Pan view |
+
+## Development
+```bash
+cd visualizer/viewer
+npm install
+npm start        # dev server at http://localhost:3000
+```
+
+## Production Build
+```bash
+npm run build    # output in build/
+```
+
+## Notes
+- This directory is **not** a Maven module; it is built independently with npm.
+- No Java code lives here — all Java integration is via the JSON HTTP response from the server.
PATCH

echo "Gold patch applied."
