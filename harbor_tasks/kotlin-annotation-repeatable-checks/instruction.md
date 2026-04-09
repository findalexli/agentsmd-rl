# Fix Annotation Repeatable Checks Around ALL Use-Site Target

## Problem

The Kotlin FIR (Frontend IR) compiler is not correctly handling the `@all:` annotation use-site target when checking for repeated annotations. This leads to missing `REPEATED_ANNOTATION` errors in cases where the same annotation is applied with `@all:` and another specific target (like `@param:`, `@get:`, etc.).

Additionally, the `FirOptInMarkedDeclarationChecker` has overly complex use-site target checks that can be simplified by relying on declaration types instead.

## Issue Reference

KT-85005: The `@all:` use-site target causes annotation repeatable checks to miss conflicts because `AnnotationUseSiteTarget.ALL` isn't being properly excluded when determining the default use-site target for comparison.

## Files to Modify

1. **Primary fix location**: `compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/FirAnnotationHelpers.kt`
   - The `checkRepeatedAnnotation` function needs to exclude `AnnotationUseSiteTarget.ALL` when determining the use-site target for comparison

2. **Secondary fixes**:
   - `compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/declaration/FirOptInMarkedDeclarationChecker.kt` - Simplify use-site target checks
   - `compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/declaration/FirAnnotationChecker.kt` - Handle ALL target without crashing
   - `compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/declaration/FirSupertypesChecker.kt` - Add explanatory comment
   - `compiler/fir/fir-serialization/src/org/jetbrains/kotlin/fir/serialization/FirElementSerializer.kt` - Simplify serialization
   - `plugins/parcelize/parcelize-compiler/parcelize.k2/src/org/jetbrains/kotlin/parcelize/fir/diagnostics/FirParcelizePropertyChecker.kt` - Simplify hasIgnoredOnParcel

3. **Documentation**: Add KDoc to `FirAnnotation` and `FirAnnotationCall` in the generated tree and the generator

## Example Test Case

When an annotation is applied with both `@param:` and `@all:` on the same constructor parameter, or with `@property:` and `@all:` on the same property, the compiler should report `REPEATED_ANNOTATION` errors because `@all:` expands to multiple targets including those specific ones.

```kotlin
annotation class A

class B(
    @param:A
    @all:A  // Should trigger REPEATED_ANNOTATION (conflicts with @param:)
    val x: Int,

    @A
    @all:A  // Should trigger multiple REPEATED_ANNOTATION errors
    val y: Int,
)
```

## Guidance

The core issue is in `FirAnnotationHelpers.kt` in the `checkRepeatedAnnotation` function. When checking if an annotation is repeated, it compares use-site targets. However, `AnnotationUseSiteTarget.ALL` should be treated specially - it should be resolved to the actual default target(s) for comparison purposes, not compared as `ALL` directly.

Look at how `getDefaultUseSiteTarget` is used and consider when `ALL` should be resolved to its expansion targets versus when it should be treated as a distinct target.

For the `FirOptInMarkedDeclarationChecker`, the current code has complex conditions checking both `useSiteTarget` and declaration types. The fix simplifies this to primarily check declaration types, which is more reliable.

## Testing

The repository uses Gradle for building and testing. Key commands:

```bash
# Generate test runners after adding new test data
./gradlew generateTests

# Run FIR analysis tests
./gradlew :compiler:fir:analysis-tests:test

# Run specific test class
./gradlew :compiler:fir:analysis-tests:test --tests "org.jetbrains.kotlin.test.runners.PhasedJvmDiagnosticLightTreeTestGenerated"
```

When adding new test data files:
1. Add the `.kt` test file with proper directives (`// RUN_PIPELINE_TILL: FRONTEND`, `// ISSUE: KT-85005`, `// FIR_DUMP`)
2. Use inline diagnostic markers like `<!REPEATED_ANNOTATION!>` to assert expected errors
3. Run `./gradlew generateTests` to regenerate test runners
4. Run the test once to auto-generate `GENERATED_FIR_TAGS` footer
5. Run again to verify the test passes

## Expected Outcome

After the fix:
1. `REPEATED_ANNOTATION` errors are properly reported when `@all:` conflicts with specific targets
2. `FirOptInMarkedDeclarationChecker` has simplified logic using declaration types
3. `FirAnnotationChecker` handles `ALL` target gracefully without crashing
4. Serialization code is simplified
5. KDoc is added to annotation-related classes
