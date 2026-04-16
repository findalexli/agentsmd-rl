# Task: Report Warning on Underscore Variables with Implicit Unit Type

## Problem

The Kotlin FIR (Frontend IR) frontend does not currently report a warning when a variable named `_` (underscore) has its type implicitly inferred to `Unit`. This omission means developers may miss potentially unused values that could indicate bugs.

When the following code is compiled:
```kotlin
val _ = someFunctionReturningUnit()
```
The compiler should warn that an underscore-named variable is receiving a `Unit` type through implicit type inference, as this suggests a possible unintentional discard of a return value.

The warning should NOT be reported in these cases:
- When the type is explicitly declared: `val _: Unit = someFunction()`
- When the type is nullable Unit
- For lambda parameters: `{ _ -> ... }`
- For destructuring declarations: `val (a, b) = pair`

## Required Behavior

When implementing this feature, ensure the following specifications are met:

1. **Diagnostic Identity**: Define a new warning (not error) with the exact name `UNNAMED_PROPERTY_WITH_IMPLICIT_UNIT_TYPE` in the FIR diagnostics list.

2. **Error Message Content**: The human-readable error message displayed to users must contain the exact text `underscore property is inferred to` and mention `Unit`.

3. **Issue Tracking**: The test data file must include a reference to the YouTrack issue `KT-84618`.

4. **Test Data Requirements**: Create a test file at `compiler/testData/diagnostics/tests/unnamedLocalVariables/withUnitType.kt` containing:
   - A `RUN_PIPELINE_TILL: BACKEND` compiler directive
   - The `UnnamedLocalVariables` language feature flag enabled
   - A function named `testWithImplicit()` with at least 3 test cases where the warning should be triggered (implicit Unit inference)
   - A function named `testWithExplicit()` with cases where the warning should NOT be triggered (explicit type annotations)
   - Warning markers `<!UNNAMED_PROPERTY_WITH_IMPLICIT_UNIT_TYPE!>` placed at the implicit cases

5. **IDE Integration**: The Analysis API must expose this diagnostic through:
   - A converter class in `KaFirDataClassConverters.kt` named `UnnamedPropertyWithImplicitUnitTypeImpl`
   - A corresponding interface in `KaFirDiagnostics.kt`
   - An implementation class in `KaFirDiagnosticsImpl.kt`

6. **Scripting Compatibility**: Update the scripting test file at either:
   - `plugins/scripting/scripting-tests/testData/testScripts/unnamedLocalVariables.test.kts`, OR
   - `plugins/scripting/scripting-tests/testData/codegen/testScripts/unnamedLocalVariables.test.kts`
   
   Modify the `call()` function to return `Int` instead of implicitly returning `Unit`, preventing false positives from the new warning.

## Testing

Verify your implementation by running:
```
./gradlew :compiler:fir:analysis-tests:test -q
```

## Expected Diagnostic Behavior Summary

| Code Pattern | Should Report Warning? |
|--------------|----------------------|
| `val _ = Unit` | Yes |
| `val _ = returnUnit()` (function returns Unit) | Yes |
| `for (_ in arrayOf(Unit, Unit)) { }` | Yes |
| `when (val _ = returnUnit()) { ... }` | Yes |
| `val _: Unit = Unit` (explicit type annotation) | No |
| `val _ = returnNullableUnit()` (nullable Unit type) | No |
| Lambda params: `{ _ -> }` | No |
| Destructuring: `val (a, b) = pair` | No |
