# Fix IrRichFunctionReference handling in Compose compiler

## Problem

The Compose compiler plugin fails to properly handle `IrRichFunctionReference` expressions introduced by the `IrRichCallableReferencesInKlibs` language feature. When this feature is enabled (particularly on Kotlin/Native targets), SAM conversions involving `@Composable` functional interfaces cause compilation errors.

The root cause is that several lowering passes in the Compose compiler do not visit `IrRichFunctionReference` nodes, leaving them untransformed. Specifically:

1. The SAM conversion lowering only runs on JVM platforms and lacks support for non-JVM platforms
2. Type remapping is not applied to the `overriddenFunctionSymbol` within rich function references
3. Composer parameters are not added to functions accessed through rich function references

## Affected Components

The fix involves three lowering passes in the Compose compiler:
- **ComposableFunInterfaceLowering** (`lower/ComposableFunInterfaceLowering.kt`): Handles SAM conversion for composable functional interfaces on Native platforms
- **ComposableTypeRemapper** (`lower/ComposableTypeRemapper.kt`): Remaps types for composable functions in rich function references
- **ComposerParamTransformer** (`lower/ComposerParamTransformer.kt`): Adds Composer parameters to composable functions accessed through rich function references

## Verification Criteria

After the fix is applied, the three lowering files must properly handle `IrRichFunctionReference` nodes:

1. **ComposableFunInterfaceLowering** must support Native platform alongside JVM for SAM conversion of composable functional interfaces when the `IrRichCallableReferencesInKlibs` feature is available.

2. **ComposableTypeRemapper** must visit and transform rich function references by remapping the `overriddenFunctionSymbol` when the referenced function needs composable remapping.

3. **ComposerParamTransformer** must visit and update the `overriddenFunctionSymbol` in rich function references to include composer parameters.

All three passes must properly invoke the parent class visitor method for rich function references to ensure complete traversal.