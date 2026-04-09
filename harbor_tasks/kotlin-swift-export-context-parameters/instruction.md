# Add Support for Context Parameters on Functional Types in Swift Export

## Problem

The Kotlin Swift Export feature currently does not properly handle context parameters on functional types. Context parameters (from Kotlin's context receivers feature) allow functions to require specific context objects without explicitly passing them as parameters.

When exporting Kotlin code with context parameters on functional types to Swift, the generated Swift code is incorrect - it fails to include the context parameters in the function type signature.

## Example

For Kotlin code like:
```kotlin
fun contextBlockA(block: context(ContextA, ContextB) Int.(String) -> Unit): Unit
```

The Swift export should generate a function type that includes the context parameters:
```swift
((main.ContextA, main.ContextB), Swift.Int32, Swift.String) -> Swift.Void
```

However, currently the context parameters are missing from the generated Swift code.

## Affected Files

The fix involves changes to the Swift Intermediate Representation (SIR) and related components:

1. **native/swift/sir/src/org/jetbrains/kotlin/sir/SirType.kt**
   - The `SirFunctionalType` class needs to support a list of context types

2. **native/swift/sir-printer/src/org/jetbrains/sir/printer/impl/SirAsSwiftSourcesPrinter.kt**
   - The printer needs to render context parameters in functional type signatures

3. **native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirTypeProviderImpl.kt**
   - The type provider needs to extract context receivers from Kotlin's `KaFunctionType`

4. **native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/StandaloneSirTypeNamer.kt**
   - The type namer needs to include context types when computing Kotlin FqNames

5. **native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/BridgeProvider/TypeBridging.kt**
   - The type bridging logic needs to handle context parameters when generating
     Kotlin-to-Swift and Swift-to-Kotlin conversions

## Requirements

1. `SirFunctionalType` must store context types separately from regular parameter types
2. The Swift printer must render context parameters before regular parameters
3. The type provider must extract context receivers from Kotlin function types
4. The type namer must account for context types when naming functional types
5. The type bridging must generate correct conversion code for context parameters
6. All existing tests must continue to pass
7. The sir-printer tests must pass with the new context parameter support

## Testing

You can run the sir-printer tests to verify your implementation:
```bash
./gradlew :native:swift:sir-printer:test
```

You can also compile individual modules:
```bash
./gradlew :native:swift:sir:compileKotlin
./gradlew :native:swift:sir-printer:compileKotlin
./gradlew :native:swift:sir-providers:compileKotlin
```
