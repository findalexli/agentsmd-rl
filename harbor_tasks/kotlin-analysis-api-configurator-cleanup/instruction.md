# Analysis API Test Configurator Cleanup

## Problem

The `AnalysisApiFirTestConfiguratorFactory` in the Kotlin Analysis API contains a workaround that automatically converts `TestModuleKind.Source` and `TestModuleKind.ScriptSource` to `TestModuleKind.SourceLike`. This workaround was added during a transition period to avoid fixing non-generated tests immediately.

As the Analysis API has stabilized, this workaround should now be removed, and callers should use the simplified `AnalysisApiTestConfiguratorFactoryData()` constructor with default parameters instead of explicitly passing all parameters.

## Files to Modify

1. **analysis/analysis-api-fir/testFixtures/org/jetbrains/kotlin/analysis/api/fir/test/configurators/AnalysisApiFirTestConfiguratorFactory.kt**
   - Remove the workaround code block that converts `Source`/`ScriptSource` to `SourceLike`
   - The workaround is marked with a comment: "// This is a workaround for the transition time"

2. **generators/sir-tests-generator/main/org/jetbrains/kotlin/generators/tests/native/swift/sir/GenerateSirTests.kt**
   - Replace the explicit `AnalysisApiTestConfiguratorFactoryData(...)` constructor call with `AnalysisApiTestConfiguratorFactoryData()` using default parameters

3. **native/swift/swift-export-ide/tests-gen/org/jetbrains/kotlin/swiftexport/ide/SwiftExportInIdeTestGenerated.java**
   - Change `TestModuleKind.Source` to `TestModuleKind.SourceLike` in the test configurator data

4. **plugins/compose/compiler-hosted/src/test/kotlin/androidx/compose/compiler/plugins/kotlin/ComposeCompilerBoxTests.kt**
   - Replace explicit constructor parameters with `AnalysisApiTestConfiguratorFactoryData()`
   - Import `AnalysisApiTestConfigurator` explicitly
   - Call via `AnalysisApiFirTestConfiguratorFactory.createConfigurator(...)` instead of `createConfigurator(...)` directly

5. **plugins/kotlin-dataframe/testFixtures/org/jetbrains/kotlin/fir/dataframe/AbstractCompilerFacilityTestForDataFrame.kt**
   - Replace explicit constructor parameters with `AnalysisApiTestConfiguratorFactoryData()`
   - Import `AnalysisApiTestConfigurator` explicitly

6. **plugins/kotlinx-serialization/testFixtures/org/jetbrains/kotlinx/serialization/runners/AbstractCompilerFacilityTestForSerialization.kt**
   - Replace explicit constructor parameters with `AnalysisApiTestConfiguratorFactoryData()`
   - Import `AnalysisApiTestConfigurator` explicitly

## Goal

- Remove the workaround in `AnalysisApiFirTestConfiguratorFactory`
- All test configurators should use `AnalysisApiTestConfiguratorFactoryData()` with default parameters
- The code should compile successfully
- The generated test file should use `TestModuleKind.SourceLike` instead of `TestModuleKind.Source`

## Testing

After making changes, verify that the code compiles:
```bash
./gradlew :analysis:analysis-api-fir:compileTestFixturesKotlin -q
./gradlew :plugins:compose:compiler-hosted:compileTestKotlin -q
./gradlew :plugins:kotlinx-serialization:compileTestFixturesKotlin -q
```

## Notes

- This is an internal API change that simplifies test configuration
- The Analysis API uses `Ka` prefix for types (e.g., `KaSession`, `KaSymbol`)
- When working with test infrastructure, follow the conventions in `analysis/AGENTS.md`
