# Simplify Analysis API Test Configurator Usage

## Problem

The `AnalysisApiFirTestConfiguratorFactory` contains a workaround that maps `TestModuleKind.Source` and `TestModuleKind.ScriptSource` to `TestModuleKind.SourceLike` at the start of its factory method. This workaround was added as a temporary measure during a transition period to avoid fixing non-generated tests immediately.

As an internal API, the Analysis API should use as few explicit configurations as possible to not block its evolution. The presence of this remapping logic means tests are being configured indirectly through the factory rather than using the intended default configuration pattern.

## Files Involved

- `analysis/analysis-api-fir/testFixtures/org/jetbrains/kotlin/analysis/api/fir/test/configurators/AnalysisApiFirTestConfiguratorFactory.kt`
- `generators/sir-tests-generator/main/org/jetbrains/kotlin/generators/tests/native/swift/sir/GenerateSirTests.kt`
- `native/swift/swift-export-ide/tests-gen/org/jetbrains/kotlin/swiftexport/ide/SwiftExportInIdeTestGenerated.java`
- `plugins/compose/compiler-hosted/src/test/kotlin/androidx/compose/compiler/plugins/kotlin/ComposeCompilerBoxTests.kt`
- `plugins/kotlin-dataframe/testFixtures/org/jetbrains/kotlin/fir/dataframe/AbstractCompilerFacilityTestForDataFrame.kt`
- `plugins/kotlinx-serialization/testFixtures/org/jetbrains/kotlinx/serialization/runners/AbstractCompilerFacilityTestForSerialization.kt`

## Current Undesired Behavior

1. In `AnalysisApiFirTestConfiguratorFactory.kt`, the factory method reassigns its `data` parameter based on `data.moduleKind` before processing it further. When the module kind is `TestModuleKind.Source` or `TestModuleKind.ScriptSource`, it creates a copy with `TestModuleKind.SourceLike` instead.

2. Multiple test files construct `AnalysisApiTestConfiguratorFactoryData` with explicit parameters (`FrontendKind.Fir`, `TestModuleKind.Source`, `AnalysisSessionMode.Normal`, `AnalysisApiMode.Ide`) instead of relying on the class's default values.

3. The generated test file `SwiftExportInIdeTestGenerated.java` uses `TestModuleKind.Source` in its `AnalysisApiTestConfiguratorFactoryData` constructor, which relies on the workaround remapping.

4. Several test files use wildcard imports (`import org.jetbrains.kotlin.analysis.test.framework.test.configurators.*`) for the configurators package.

## Expected Behavior After Fix

1. The factory should use the `data` parameter directly without any remapping based on `moduleKind`. The `requireSupported(data)` call should remain at the start of the factory method.

2. All instantiations of `AnalysisApiTestConfiguratorFactoryData` in the listed test files should use the empty constructor `AnalysisApiTestConfiguratorFactoryData()` with no arguments, relying on default parameter values.

3. `SwiftExportInIdeTestGenerated.java` should use `TestModuleKind.SourceLike` directly instead of relying on remapping from `TestModuleKind.Source`.

4. Wildcard imports for `org.jetbrains.kotlin.analysis.test.framework.test.configurators` should be replaced with specific imports for the types actually used.

5. Copyright years in modified non-generated files should be updated to 2026.

## Specific Values Required

The tests verify the following specific patterns:

- The pattern `val data = when (data.moduleKind)` must NOT appear in `AnalysisApiFirTestConfiguratorFactory.kt`
- The pattern `TestModuleKind.Source, TestModuleKind.ScriptSource` must NOT appear in `AnalysisApiFirTestConfiguratorFactory.kt`
- The pattern `AnalysisApiTestConfiguratorFactoryData()` (empty constructor) must appear in:
  - `GenerateSirTests.kt`
  - `ComposeCompilerBoxTests.kt`
  - `AbstractCompilerFacilityTestForDataFrame.kt`
  - `AbstractCompilerFacilityTestForSerialization.kt`
- The pattern `TestModuleKind.SourceLike` must appear in `SwiftExportInIdeTestGenerated.java`
- `AnalysisApiFirTestConfiguratorFactory.createConfigurator` must be used in `AbstractCompilerFacilityTestForDataFrame.kt` and `AbstractCompilerFacilityTestForSerialization.kt`
