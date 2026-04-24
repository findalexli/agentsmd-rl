# Fix IrRichFunctionReference handling in Compose compiler

## Problem

The Compose compiler plugin fails to properly handle `IrRichFunctionReference` expressions that are introduced by the `IrRichCallableReferencesInKlibs` language feature. When this feature is enabled (particularly on Kotlin/Native targets), SAM conversions involving `@Composable` functional interfaces cause compilation errors.

Specifically, the compiler produces incorrect intermediate representation when processing composable functional interfaces on Native platforms, because certain lowering passes do not properly visit and transform `IrRichFunctionReference` nodes. This results in missing composer parameters, incorrect type remapping, and broken SAM conversion for composable interfaces.

## Expected Behavior

When the `IrRichCallableReferencesInKlibs` feature is enabled on Native platforms:
- SAM conversions for `@Composable` functional interfaces should work correctly
- Type remapping should be applied to all function references, including rich function references
- Composer parameters should be properly added to functions accessed through rich function references

## Relevant Files

The Compose compiler lowering passes that need modification are located in:
- `plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/lower/ComposableFunInterfaceLowering.kt`
- `plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/lower/ComposableTypeRemapper.kt`
- `plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/lower/ComposerParamTransformer.kt`

## Technical Details

The Kotlin compiler version in this repository is at git commit `56dd547`.

The following IR node types and members are involved:
- `IrRichFunctionReference` - the IR node type representing rich function references
- `IrRichFunctionReferenceImpl` - the concrete implementation class for rich function references
- `overriddenFunctionSymbol` - property on `IrRichFunctionReference` holding the overridden function symbol
- `visitRichFunctionReference` - the visitor method called when traversing `IrRichFunctionReference` nodes
- `selectSAMOverriddenFunction()` - utility to select the SAM-overridden function

Platform detection uses `isJvm()` and `isNative()` extensions on the platform configuration.

## Hint

The fix requires extending the Compose compiler's lowering passes to properly handle the `IrRichFunctionReference` IR node type. Specifically, you should:
- Review how the lowering passes currently handle `IrRichFunctionReference` nodes
- Ensure the platform check includes Native alongside JVM where appropriate
- Apply necessary transformations to the overridden function symbol when needed
- Ensure parent class visitor methods are properly invoked to maintain complete traversal
