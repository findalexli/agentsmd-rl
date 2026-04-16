# Fix Swift Export Coroutines Import Handling

## Problem

The Swift Export feature in Kotlin/Native has a bug in its coroutine bridge code generation for async functions. Two related issues exist in the SIR providers within the `native/swift/sir-providers/` directory tree (package `org.jetbrains.kotlin.sir.providers.impl.BridgeProvider`):

1. **Wildcard import**: The coroutine import generation produces `kotlinx.coroutines.*` as a catch-all wildcard instead of listing each coroutine type explicitly.

2. **Unaliased function call**: Extension functions like `launch` from kotlinx.coroutines are imported using a safe import name convention (the fully qualified name with dots replaced by underscores) to avoid naming conflicts. However, the bridge code that invokes the coroutine still references `launch` by its plain unaliased name, creating a mismatch between the aliased import and the call site.

## Expected Behavior After Fix

### Explicit Coroutine Imports

The wildcard import `kotlinx.coroutines.*` must be eliminated. Instead, each coroutine type used in bridge code should appear as an explicit import:
- `kotlinx.coroutines.CancellationException`
- `kotlinx.coroutines.CoroutineScope`
- `kotlinx.coroutines.CoroutineStart`
- `kotlinx.coroutines.Dispatchers`

The `launch` extension function also needs an explicit import with its safe alias. The import for launch should be constructed as `FqName("kotlinx.coroutines.launch")` and formatted using its safe import name (e.g., accessed as `it.safeImportName` within a builder lambda).

The import list construction should use `buildList` since the logic involves multiple conditional additions.

### Aliased Launch Call

The coroutine launch in the bridge template must use `.kotlinx_coroutines_launch(` instead of the unaliased `.launch(`. The safe import name for `kotlinx.coroutines.launch` is `kotlinx_coroutines_launch` — this is the fully qualified name with dots replaced by underscores.

### Reusable safeImportName on FqName

The safe import name computation should be extracted as a reusable extension property on `FqName` with signature `private val FqName.safeImportName: String`, implemented by joining the FqName's path segments with underscores via `pathSegments().joinToString`.

The existing `BridgeFunctionDescriptor.safeImportName` should delegate to this FqName extension: `get() = kotlinFqName.safeImportName`.

### No Wildcard

The `additionalImports` function must not produce `kotlinx.coroutines.*` anywhere in its import generation logic.

## Constraints

- Do NOT modify golden test data files — those represent expected outputs.
