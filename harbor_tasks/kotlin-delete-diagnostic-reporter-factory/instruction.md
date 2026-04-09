# Task: Remove DiagnosticReporterFactory

## Problem

The `DiagnosticReporterFactory` in `compiler/frontend.common/src/org/jetbrains/kotlin/diagnostics/DiagnosticReporterFactory.kt` is a factory object that provides a single method `createReporter()` which simply instantiates `DiagnosticsCollectorImpl`. This factory is no longer necessary since there's only one reasonable implementation of `BaseDiagnosticsCollector`.

Your task is to:
1. Delete the `DiagnosticReporterFactory.kt` file entirely
2. Update the one usage of this factory in `plugins/compose/compiler-hosted/integration-tests/src/jvmTest/kotlin/androidx/compose/compiler/plugins/kotlin/facade/K2CompilerFacade.kt` to directly instantiate `DiagnosticsCollectorImpl` instead

## What to verify

After your changes:
- The file `compiler/frontend.common/src/org/jetbrains/kotlin/diagnostics/DiagnosticReporterFactory.kt` should not exist
- `K2CompilerFacade.kt` should import `DiagnosticsCollectorImpl` directly
- `K2CompilerFacade.kt` should call `DiagnosticsCollectorImpl()` instead of `DiagnosticReporterFactory.createReporter()`
- The Kotlin compiler and Compose integration tests should still compile successfully

## Key files

1. File to delete:
   - `compiler/frontend.common/src/org/jetbrains/kotlin/diagnostics/DiagnosticReporterFactory.kt`

2. File to modify:
   - `plugins/compose/compiler-hosted/integration-tests/src/jvmTest/kotlin/androidx/compose/compiler/plugins/kotlin/facade/K2CompilerFacade.kt`

## Build verification

You can verify your changes compile correctly by running:
```bash
./gradlew :compiler:frontend.common:compileKotlin -q --no-daemon
./gradlew :plugins:compose:compiler-hosted:integration-tests:compileTestKotlin -q --no-daemon
```
