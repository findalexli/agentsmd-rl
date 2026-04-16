# Swift Export: Add SharedFlow and MutableSharedFlow Support

## Problem

The Swift Export feature currently supports `Flow`, `StateFlow`, and `MutableStateFlow` types from Kotlin coroutines. However, when exporting Kotlin code that uses `SharedFlow` or `MutableSharedFlow` types to Swift, the type information is not preserved correctly. Attempting to export code using these types may result in incorrect type mapping or errors.

## Required Behavior

The implementation must add support for the following types from the `kotlinx.coroutines.flow` package:

### 1. Kotlin Class IDs

The implementation must recognize these ClassId strings:
- `"kotlinx/coroutines/flow/SharedFlow"`
- `"kotlinx/coroutines/flow/MutableSharedFlow"`

These must be handled alongside the existing ClassId strings for `Flow`, `StateFlow`, and `MutableStateFlow`.

### 2. Files to Modify

The implementation requires changes to the following files:

- `native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/utils/KotlinRuntimeModule.kt`
- `native/swift/sir-light-classes/src/org/jetbrains/sir/lightclasses/nodes/SirProtocolFromKtSymbol.kt`
- `native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirTypeProviderImpl.kt`
- `native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/BridgeProvider/TypeBridging.kt`
- `native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/StandaloneSirTypeNamer.kt`
- `native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift`

### 3. Protocol Declarations

The `KotlinCoroutineSupportModule` must declare the following protocol and struct declarations with these exact names:

**Protocol names:**
- `KotlinSharedFlow`
- `KotlinTypedSharedFlow`
- `KotlinMutableSharedFlow`
- `KotlinTypedMutableSharedFlow`

**Struct names:**
- `_KotlinTypedSharedFlowImpl`
- `_KotlinTypedMutableSharedFlowImpl`

### 4. Type Mappings

The implementation must establish the following mappings:

- `SharedFlow` class ID maps to the `KotlinSharedFlow` protocol for support protocols
- `MutableSharedFlow` class ID maps to the `KotlinMutableSharedFlow` protocol for support protocols
- `SharedFlow` class ID maps to typed protocol `KotlinTypedSharedFlow`
- `MutableSharedFlow` class ID maps to typed protocol `KotlinTypedMutableSharedFlow`

### 5. Type Bridging

The type bridging must map typed protocols to their implementation structs:
- `KotlinTypedSharedFlow` → implementation struct `_KotlinTypedSharedFlowImpl`
- `KotlinTypedMutableSharedFlow` → implementation struct `_KotlinTypedMutableSharedFlowImpl`

### 6. Type Naming

SharedFlow types must be named with their fully qualified Kotlin names in the type namer:
- `KotlinTypedSharedFlow` → `"kotlinx.coroutines.flow.SharedFlow<...>"`
- `KotlinTypedMutableSharedFlow` → `"kotlinx.coroutines.flow.MutableSharedFlow<...>"`

### 7. Swift Protocol Definitions

The `KotlinCoroutineSupport.swift` file must define the following Swift protocols with this inheritance hierarchy:

**Protocol hierarchy:**
- `KotlinSharedFlow` extends `KotlinFlow`
- `KotlinStateFlow` extends `KotlinSharedFlow` (changed from extending `KotlinFlow` directly)
- `KotlinMutableSharedFlow` extends `KotlinSharedFlow`
- `KotlinMutableStateFlow` extends both `KotlinStateFlow` and `KotlinMutableSharedFlow`
- `KotlinTypedSharedFlow<Element>` extends `KotlinTypedFlow`
- `KotlinTypedStateFlow<Element>` extends `KotlinTypedSharedFlow` (changed from extending `KotlinTypedFlow` directly)
- `KotlinTypedMutableSharedFlow<Element>` extends both `KotlinTypedStateFlow` and `KotlinTypedMutableSharedFlow`

**Structs:**
- `_KotlinTypedSharedFlowImpl<Element>` implements `KotlinTypedSharedFlow`
- `_KotlinTypedMutableSharedFlowImpl<Element>` implements `KotlinTypedMutableSharedFlow`

**SharedFlow-specific protocol members:**
- `KotlinSharedFlow` must have a `replayCache` property
- `KotlinMutableSharedFlow` must have: `subscriptionCount` property, `emit(value:)` method, `resetReplayCache()` method, and `tryEmit(value:)` method

**MutableStateFlow improvements:**
- `KotlinTypedMutableStateFlow` must have its `value` setter marked as `nonmutating`
- `KotlinMutableStateFlow` must have a `compareAndSet(expect:update:)` method
- `KotlinTypedMutableStateFlow` must expose `compareAndSet(expect:update:)` that calls through to the wrapped mutable state flow

### 8. Type Information Preservation

The element type parameter from Kotlin's `SharedFlow<T>` and `MutableSharedFlow<T>` must be preserved through the translation to Swift.

### 9. Backward Compatibility

All existing StateFlow functionality must continue to work after the hierarchy changes.

## References

- The Kotlin coroutines type hierarchy follows the pattern: `Flow` → `SharedFlow` → `StateFlow`, with `MutableSharedFlow` and `MutableStateFlow` as mutable variants
- The ClassId strings follow the pattern: `kotlinx/coroutines/flow/{TypeName}`
