"""Behavioral checks for 3d-bin-container-packing-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/3d-bin-container-packing")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('api/agents.md')
    assert 'Foundation layer of the 3D bin-packing library. Defines all public interfaces, abstract base classes, and core data structures that the rest of the system depends on. No algorithm logic lives here — o' in text, "expected to find: " + 'Foundation layer of the 3D bin-packing library. Defines all public interfaces, abstract base classes, and core data structures that the rest of the system depends on. No algorithm logic lives here — o'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('api/agents.md')
    assert '- `com.github.skjolber.packing.api` — Core types: `Packager`, `PackagerResult`, `PackagerResultBuilder`, `BoxStackValue`, `Rotation`, `Surface`' in text, "expected to find: " + '- `com.github.skjolber.packing.api` — Core types: `Packager`, `PackagerResult`, `PackagerResultBuilder`, `BoxStackValue`, `Rotation`, `Surface`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('api/agents.md')
    assert '- `com.github.skjolber.packing.api.packager.control` — Control framework: `ManifestControls`, `PlacementControls`, `PointControls`' in text, "expected to find: " + '- `com.github.skjolber.packing.api.packager.control` — Control framework: `ManifestControls`, `PlacementControls`, `PointControls`'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('core/agents.md')
    assert 'The main algorithmic engine. Implements all packager strategies (LAFF, brute-force, plain), box permutation/rotation iterators, deadline management for time-bounded packing, and placement validation.' in text, "expected to find: " + 'The main algorithmic engine. Implements all packager strategies (LAFF, brute-force, plain), box permutation/rotation iterators, deadline management for time-bounded packing, and placement validation.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('core/agents.md')
    assert '- `com.github.skjolber.packing.iterator` — `BoxItemPermutationRotationIterator`, `BoxItemGroupPermutationRotationIterator`, `FilteredBoxItemsPermutationRotationIterator`' in text, "expected to find: " + '- `com.github.skjolber.packing.iterator` — `BoxItemPermutationRotationIterator`, `BoxItemGroupPermutationRotationIterator`, `FilteredBoxItemsPermutationRotationIterator`'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('core/agents.md')
    assert '- `com.github.skjolber.packing.packer.laff` — Largest Area Fit First: `LargestAreaFitFirstPackager`, `FastLargestAreaFitFirstPackager`' in text, "expected to find: " + '- `com.github.skjolber.packing.packer.laff` — Largest Area Fit First: `LargestAreaFitFirstPackager`, `FastLargestAreaFitFirstPackager`'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('jmh/agents.md')
    assert 'Microbenchmark suite using the OpenJDK JMH framework. Measures throughput and latency of packagers, iterators, and point calculators to detect regressions and guide performance optimisation.' in text, "expected to find: " + 'Microbenchmark suite using the OpenJDK JMH framework. Measures throughput and latency of packagers, iterators, and point calculators to detect regressions and guide performance optimisation.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('jmh/agents.md')
    assert '- `com.github.skjolber.packing.jmh` — Packager benchmarks (`PackagerBenchmark`, `DeadlineBenchmark`, `EgyPackagerBenchmark`, `TychoBenchmark`) and shared state classes' in text, "expected to find: " + '- `com.github.skjolber.packing.jmh` — Packager benchmarks (`PackagerBenchmark`, `DeadlineBenchmark`, `EgyPackagerBenchmark`, `TychoBenchmark`) and shared state classes'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('jmh/agents.md')
    assert '- `com.github.skjolber.packing.jmh.iterator` — Iterator benchmarks (`DefaultIteratorBenchmark`, `ParallelIteratorBenchmark`)' in text, "expected to find: " + '- `com.github.skjolber.packing.jmh.iterator` — Iterator benchmarks (`DefaultIteratorBenchmark`, `ParallelIteratorBenchmark`)'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('open-api/agents.md')
    assert 'Parent POM aggregating all REST API modules. Defines shared dependency management and build configuration for the OpenAPI-generated code. The actual Pack API is a single POST `/pack` endpoint.' in text, "expected to find: " + 'Parent POM aggregating all REST API modules. Defines shared dependency management and build configuration for the OpenAPI-generated code. The actual Pack API is a single POST `/pack` endpoint.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('open-api/agents.md')
    assert 'The canonical source of truth is `open-api/3d-api.yaml` (OpenAPI 3.0). All model, server, and client code is **generated** — edit the spec, then regenerate; do not hand-edit generated sources.' in text, "expected to find: " + 'The canonical source of truth is `open-api/3d-api.yaml` (OpenAPI 3.0). All model, server, and client code is **generated** — edit the spec, then regenerate; do not hand-edit generated sources.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('open-api/agents.md')
    assert 'mvn generate-sources -pl open-api/open-api-model,open-api/open-api-server,open-api/open-api-client' in text, "expected to find: " + 'mvn generate-sources -pl open-api/open-api-model,open-api/open-api-server,open-api/open-api-client'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('open-api/open-api-client/agents.md')
    assert 'Generated Apache HttpComponents Client 5 stubs for calling the Pack REST API. Provides a type-safe Java client that serialises `PackRequest` and deserialises `PackResponse` over HTTP.' in text, "expected to find: " + 'Generated Apache HttpComponents Client 5 stubs for calling the Pack REST API. Provides a type-safe Java client that serialises `PackRequest` and deserialises `PackResponse` over HTTP.'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('open-api/open-api-client/agents.md')
    assert '- Built on **Apache HttpComponents Client 5** (supports async and connection pooling).' in text, "expected to find: " + '- Built on **Apache HttpComponents Client 5** (supports async and connection pooling).'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('open-api/open-api-client/agents.md')
    assert '- Integration tests use **open-api-server** stubs (test scope) to run a local server.' in text, "expected to find: " + '- Integration tests use **open-api-server** stubs (test scope) to run a local server.'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('open-api/open-api-model/agents.md')
    assert 'Generated Jackson data model for the Pack REST API. Contains all request/response POJOs produced by the OpenAPI Generator Maven plugin from `../3d-api.yaml`.' in text, "expected to find: " + 'Generated Jackson data model for the Pack REST API. Contains all request/response POJOs produced by the OpenAPI Generator Maven plugin from `../3d-api.yaml`.'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('open-api/open-api-model/agents.md')
    assert '- Uses Jackson annotations for JSON serialisation and Jakarta Validation annotations (`@NotNull`, `@Size`, etc.) for bean validation.' in text, "expected to find: " + '- Uses Jackson annotations for JSON serialisation and Jakarta Validation annotations (`@NotNull`, `@Size`, etc.) for bean validation.'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('open-api/open-api-model/agents.md')
    assert '- **All source files are generated.** Do not edit them by hand; modify `3d-api.yaml` and re-run `mvn generate-sources`.' in text, "expected to find: " + '- **All source files are generated.** Do not edit them by hand; modify `3d-api.yaml` and re-run `mvn generate-sources`.'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('open-api/open-api-server/agents.md')
    assert 'Generated Spring server-side interface stubs for the Pack REST API. Provides `PackApi` (and related interfaces) ready to be implemented by a Spring Boot `@RestController`.' in text, "expected to find: " + 'Generated Spring server-side interface stubs for the Pack REST API. Provides `PackApi` (and related interfaces) ready to be implemented by a Spring Boot `@RestController`.'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('open-api/open-api-server/agents.md')
    assert '- Generated in **interface-only** mode — no implementation is provided. Wire a `@RestController` that implements `PackApi`.' in text, "expected to find: " + '- Generated in **interface-only** mode — no implementation is provided. Wire a `@RestController` that implements `PackApi`.'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('open-api/open-api-server/agents.md')
    assert '`com.github.skjolber.packing.openapi.server.api` — `PackApi` interface with Spring `@RequestMapping` annotations' in text, "expected to find: " + '`com.github.skjolber.packing.openapi.server.api` — `PackApi` interface with Spring `@RequestMapping` annotations'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('open-api/open-api-test/agents.md')
    assert 'Shared test utilities for the open-api modules. Provides common helpers, fixtures, and Mockito-based mocks reusable across `open-api-server` and `open-api-client` tests.' in text, "expected to find: " + 'Shared test utilities for the open-api modules. Provides common helpers, fixtures, and Mockito-based mocks reusable across `open-api-server` and `open-api-client` tests.'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('open-api/open-api-test/agents.md')
    assert '- Currently minimal; grow this module to avoid duplication when adding integration tests across server/client.' in text, "expected to find: " + '- Currently minimal; grow this module to avoid duplication when adding integration tests across server/client.'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('open-api/open-api-test/agents.md')
    assert '- Consumed as a `test`-scoped dependency by the sibling open-api modules.' in text, "expected to find: " + '- Consumed as a `test`-scoped dependency by the sibling open-api modules.'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('points/agents.md')
    assert 'Manages free-space bookkeeping during packing. Tracks 2D and 3D points that represent candidate placement locations within a container. Provides point calculators that maintain and update the set of a' in text, "expected to find: " + 'Manages free-space bookkeeping during packing. Tracks 2D and 3D points that represent candidate placement locations within a container. Provides point calculators that maintain and update the set of a'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('points/agents.md')
    assert '- `com.github.skjolber.packing.ep.points3d` — 3D point types: `Point3D`, `DefaultPoint3D`, plane-specific variants (`XYPlanePoint3D`, `XZPlanePoint3D`, `YZPlanePoint3D`)' in text, "expected to find: " + '- `com.github.skjolber.packing.ep.points3d` — 3D point types: `Point3D`, `DefaultPoint3D`, plane-specific variants (`XYPlanePoint3D`, `XZPlanePoint3D`, `YZPlanePoint3D`)'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('points/agents.md')
    assert '- `com.github.skjolber.packing.ep.points2d` — 2D point types: `Point2D`, `DefaultPoint2D`, `XSupportPoint2D`, `YSupportPoint2D`, `Point2DList`, `Point2DFlagList`' in text, "expected to find: " + '- `com.github.skjolber.packing.ep.points2d` — 2D point types: `Point2D`, `DefaultPoint2D`, `XSupportPoint2D`, `YSupportPoint2D`, `Point2DList`, `Point2DFlagList`'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('test/agents.md')
    assert "Shared testing utilities consumed by every other module's test scope. Provides custom AssertJ assertions, Bouwkamp-code-based test data, and item/box generators for property-based and academic benchma" in text, "expected to find: " + "Shared testing utilities consumed by every other module's test scope. Provides custom AssertJ assertions, Bouwkamp-code-based test data, and item/box generators for property-based and academic benchma"[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('test/agents.md')
    assert '- `com.github.skjolber.packing.test.assertj` — Fluent custom assertions: `ContainerAssert`, `PackagerAssert`, `StackAssert`, `StackPlacementAssert`, `Point3DAssert`' in text, "expected to find: " + '- `com.github.skjolber.packing.test.assertj` — Fluent custom assertions: `ContainerAssert`, `PackagerAssert`, `StackAssert`, `StackPlacementAssert`, `Point3DAssert`'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('test/agents.md')
    assert '- `com.github.skjolber.packing.test.bouwkamp` — Bouwkamp codes for squared-rectangle test cases: `BouwkampCodes`, `BouwkampCodeParser`, `BouwkampCodeDirectory`' in text, "expected to find: " + '- `com.github.skjolber.packing.test.bouwkamp` — Bouwkamp codes for squared-rectangle test cases: `BouwkampCodes`, `BouwkampCodeParser`, `BouwkampCodeDirectory`'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('visualizer/algorithm/agents.md')
    assert "Captures intermediate algorithm states during packing for step-by-step visualisation. Records per-iteration decisions, metric snapshots, and filter operations so the viewer can replay the algorithm's " in text, "expected to find: " + "Captures intermediate algorithm states during packing for step-by-step visualisation. Records per-iteration decisions, metric snapshots, and filter operations so the viewer can replay the algorithm's "[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('visualizer/algorithm/agents.md')
    assert '- The `AlgorithmListener` interface is the primary extension point; wire it into a packager builder to receive events.' in text, "expected to find: " + '- The `AlgorithmListener` interface is the primary extension point; wire it into a packager builder to receive events.'[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('visualizer/algorithm/agents.md')
    assert '- Because this module is unstable, avoid depending on it from production code in other modules.' in text, "expected to find: " + '- Because this module is unstable, avoid depending on it from production code in other modules.'[:80]


def test_signal_33():
    """Distinctive line from gold patch must be present."""
    text = _read('visualizer/api/agents.md')
    assert 'Defines the JSON serialisation interfaces and data structures used to represent packing results for the Three.js viewer. Acts as the contract between the Java back-end and the front-end visualizer.' in text, "expected to find: " + 'Defines the JSON serialisation interfaces and data structures used to represent packing results for the Three.js viewer. Acts as the contract between the Java back-end and the front-end visualizer.'[:80]


def test_signal_34():
    """Distinctive line from gold patch must be present."""
    text = _read('visualizer/api/agents.md')
    assert '- Jackson annotations drive JSON output format; the viewer (`visualizer/viewer`) parses this JSON — any field renaming is a breaking change to the front-end.' in text, "expected to find: " + '- Jackson annotations drive JSON output format; the viewer (`visualizer/viewer`) parses this JSON — any field renaming is a breaking change to the front-end.'[:80]


def test_signal_35():
    """Distinctive line from gold patch must be present."""
    text = _read('visualizer/api/agents.md')
    assert '- `BoxVisualizer`, `ContainerVisualizer`, `StackVisualizer`, `StackPlacementVisualizer` — per-object serialisation wrappers' in text, "expected to find: " + '- `BoxVisualizer`, `ContainerVisualizer`, `StackVisualizer`, `StackPlacementVisualizer` — per-object serialisation wrappers'[:80]


def test_signal_36():
    """Distinctive line from gold patch must be present."""
    text = _read('visualizer/packaging/agents.md')
    assert 'Converts completed packing results into the JSON format consumed by the Three.js viewer. Bridges the core packing domain with the visualizer API.' in text, "expected to find: " + 'Converts completed packing results into the JSON format consumed by the Three.js viewer. Bridges the core packing domain with the visualizer API.'[:80]


def test_signal_37():
    """Distinctive line from gold patch must be present."""
    text = _read('visualizer/packaging/agents.md')
    assert '- To customise output (e.g., add colour coding), extend `AbstractPackagingResultVisualizerFactory` and attach `VisualizerPlugin` instances.' in text, "expected to find: " + '- To customise output (e.g., add colour coding), extend `AbstractPackagingResultVisualizerFactory` and attach `VisualizerPlugin` instances.'[:80]


def test_signal_38():
    """Distinctive line from gold patch must be present."""
    text = _read('visualizer/packaging/agents.md')
    assert '- `PackagingResultVisualizerFactory` — factory interface; use to produce a `PackagingResultVisualizer` from a `PackagerResult`' in text, "expected to find: " + '- `PackagingResultVisualizerFactory` — factory interface; use to produce a `PackagingResultVisualizer` from a `PackagerResult`'[:80]


def test_signal_39():
    """Distinctive line from gold patch must be present."""
    text = _read('visualizer/viewer/agents.md')
    assert 'Interactive 3D front-end for visualising packing results. Renders packed containers and boxes in a Three.js scene, supports step-through navigation of results, and can display free placement points.' in text, "expected to find: " + 'Interactive 3D front-end for visualising packing results. Renders packed containers and boxes in a Three.js scene, supports step-through navigation of results, and can display free placement points.'[:80]


def test_signal_40():
    """Distinctive line from gold patch must be present."""
    text = _read('visualizer/viewer/agents.md')
    assert "Expects the JSON produced by `visualizer/packaging` (`DefaultPackagingResultVisualizerFactory`). Changes to that module's JSON schema are breaking changes here." in text, "expected to find: " + "Expects the JSON produced by `visualizer/packaging` (`DefaultPackagingResultVisualizerFactory`). Changes to that module's JSON schema are breaking changes here."[:80]


def test_signal_41():
    """Distinctive line from gold patch must be present."""
    text = _read('visualizer/viewer/agents.md')
    assert '- No Java code lives here — all Java integration is via the JSON HTTP response from the server.' in text, "expected to find: " + '- No Java code lives here — all Java integration is via the JSON HTTP response from the server.'[:80]

