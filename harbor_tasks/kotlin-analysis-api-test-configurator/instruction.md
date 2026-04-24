# Simplify Analysis API Test Configurator Usage

## Problem

The `AnalysisApiFirTestConfiguratorFactory` contains legacy workaround code that was added during a transition period. This workaround maps certain module kinds at the factory level rather than letting tests use the default configuration directly.

As an internal API, the Analysis API should use as few explicit configurations as possible to not block its evolution. The presence of this remapping logic means tests are being configured indirectly through the factory rather than using the intended default configuration pattern.

## Files Involved

- `analysis/analysis-api-fir/testFixtures/org/jetbrains/kotlin/analysis/api/fir/test/configurators/AnalysisApiFirTestConfiguratorFactory.kt`
- `generators/sir-tests-generator/main/org/jetbrains/kotlin/generators/tests/native/swift/sir/GenerateSirTests.kt`
- `native/swift/swift-export-ide/tests-gen/org/jetbrains/kotlin/swiftexport/ide/SwiftExportInIdeTestGenerated.java`
- `plugins/compose/compiler-hosted/src/test/kotlin/androidx/compose/compiler/plugins/kotlin/ComposeCompilerBoxTests.kt`
- `plugins/kotlin-dataframe/testFixtures/org/jetbrains/kotlin/fir/dataframe/AbstractCompilerFacilityTestForDataFrame.kt`
- `plugins/kotlinx-serialization/testFixtures/org/jetbrains/kotlinx/serialization/runners/AbstractCompilerFacilityTestForSerialization.kt`

## Current Behavior (Before Fix)

1. The factory method in `AnalysisApiFirTestConfiguratorFactory.kt` has a reassignment block at its start that modifies the incoming `data` parameter based on the module kind. When certain module kinds are used, the factory creates a modified copy instead of using the parameter as-is.

2. Multiple test files construct `AnalysisApiTestConfiguratorFactoryData` with explicit parameters instead of relying on the class's default values.

3. The generated test file `SwiftExportInIdeTestGenerated.java` uses one module kind in its constructor, relying on the factory's remapping logic to work correctly.

4. Several test files use wildcard imports for the configurators package.

## Expected Behavior After Fix

1. The factory method should pass the `data` parameter through directly without any module-kind-based remapping. The `requireSupported(data)` call should remain at the start of the factory method.

2. All test files that instantiate `AnalysisApiTestConfiguratorFactoryData` should use the empty constructor `AnalysisApiTestConfiguratorFactoryData()` with no arguments, relying on default parameter values.

3. The generated test file should use the appropriate module kind that matches what the factory now expects as default (after the workaround is removed).

4. Wildcard imports for `org.jetbrains.kotlin.analysis.test.framework.test.configurators` should be replaced with specific imports for the types actually used.

5. Copyright years in modified non-generated files should be updated to 2026.