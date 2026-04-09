# Task: Remove ForbidUsingSupertypesWithInaccessibleContentInTypeArguments Language Feature

## Problem

The Kotlin compiler currently has a language feature called `ForbidUsingSupertypesWithInaccessibleContentInTypeArguments` that controls whether to report a `MISSING_DEPENDENCY_SUPERCLASS_IN_TYPE_ARGUMENT` diagnostic for supertypes with inaccessible content in type arguments. This feature flag and its associated code should be removed - the behavior should now always be enabled (hardcoded).

## What Needs to Change

1. **Language Version Settings** (`core/language.version-settings/src/org/jetbrains/kotlin/config/LanguageVersionSettings.kt`)
   - Remove the `ForbidUsingSupertypesWithInaccessibleContentInTypeArguments` enum entry from the `LanguageFeature` enum

2. **API Signature File** (`core/language.version-settings/api/language.version-settings.api`)
   - Remove the corresponding API declaration for the removed enum entry

3. **FIR Missing Dependency Storage** (`compiler/fir/providers/src/org/jetbrains/kotlin/fir/types/FirMissingDependencyStorage.kt`)
   - Remove `TypeWithOrigin` data class that paired types with their origin
   - Remove `SupertypeOrigin` enum (with `TYPE_ARGUMENT` and `OTHER` values)
   - Simplify `getMissingSuperTypes` to return `Set<ConeKotlinType>` directly
   - Simplify `collectSuperTypes` to not track origin - it should just collect types without caring whether they came from type arguments or not
   - Simplify `findMissingSuperTypes` accordingly

4. **FIR Missing Dependency Supertype Utils** (`compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/FirMissingDependencySupertypeUtils.kt`)
   - Remove the check for `SupertypeOrigin.TYPE_ARGUMENT` that was emitting `MISSING_DEPENDENCY_SUPERCLASS_IN_TYPE_ARGUMENT`
   - The loop should iterate directly over types instead of pairs of (type, origin)

5. **Test Data Files** - Update all test files that reference this feature:
   - Remove `ForbidUsingSupertypesWithInaccessibleContentInTypeArguments` from all `// LANGUAGE:` directives
   - Remove `MISSING_DEPENDENCY_SUPERCLASS_IN_TYPE_ARGUMENT` diagnostic markers from expected test outputs
   - Files to check:
     - `compiler/testData/diagnostics/tests/multimodule/FalsePositiveInaccessibleTypeInDefaultArg.kt`
     - `compiler/testData/diagnostics/tests/multimodule/InaccessibleTypeEagerCheck.kt`
     - `compiler/testData/diagnostics/tests/multimodule/InaccessibleTypeEagerCheckForbidden.kt`
     - `compiler/testData/diagnostics/tests/multimodule/InaccessibleTypeEagerCheckJava.kt`
     - `compiler/testData/diagnostics/tests/multimodule/SupertypesWithInaccessibleTypeArguments.kt`
     - `compiler/testData/diagnostics/tests/multimodule/inaccessibleSupertypeVariousExperimental.kt`
     - `compiler/testData/diagnostics/tests/multimodule/inaccessibleSupertypeVariousExperimentalEnabled.kt`

## Verification

After the changes:
- The compiler should build successfully
- `LanguageFeature.ForbidUsingSupertypesWithInaccessibleContentInTypeArguments` should not exist anywhere in the codebase
- The `TypeWithOrigin` class and `SupertypeOrigin` enum should be removed
- The `MISSING_DEPENDENCY_SUPERCLASS_IN_TYPE_ARGUMENT` diagnostic should never be emitted

## Hints

- Start by finding where `ForbidUsingSupertypesWithInaccessibleContentInTypeArguments` is defined and referenced
- The FIR (Frontend IR) code in `compiler/fir/` is the new compiler frontend - focus your changes there
- Test data uses special comment syntax like `// LANGUAGE: +FeatureName` or `-FeatureName` to enable/disable features
- Diagnostic markers in test data look like `<!DIAGNOSTIC_NAME!>` around code that should trigger the diagnostic
