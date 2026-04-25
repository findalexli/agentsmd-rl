# Task: Fix Swift Export Flow Support in Contravariant Positions

## Problem

Kotlin's Swift Export feature fails when `kotlinx.coroutines.flow.Flow<T>` types appear in contravariant positions (function parameters). Flow types work correctly as return types, but using them as parameter types causes bridging code generation failures — Flow parameters are treated as unsupported generic types and rejected by the visibility checker.

## Scope

The relevant source files are in the `org.jetbrains.kotlin.sir.providers.impl` package:
- `native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirTypeProviderImpl.kt`
- `native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirVisibilityCheckerImpl.kt`

## Requirements

### Flow Type Interception (SirTypeProviderImpl)

`SirTypeProviderImpl` defines `FLOW_CLASS_IDS` in its companion object. These class IDs must be present:
- `kotlinx/coroutines/flow/Flow`
- `kotlinx/coroutines/flow/StateFlow`
- `kotlinx/coroutines/flow/MutableStateFlow`

The Flow type interception must work in **all** variance positions, not just covariant (return type) positions. The check for Flow types must use the pattern:

```kotlin
if (kaType.classId in FLOW_CLASS_IDS)
```

This check must not be combined with any variance position restriction — Flow types should be intercepted whether they appear as return types or parameter types.

### Companion Object Visibility (SirTypeProviderImpl)

The companion object must be declared as `internal companion object` (not `private`) so that `SirVisibilityCheckerImpl` can reference `FLOW_CLASS_IDS` across files within the same module.

### Flow Type Support (SirVisibilityCheckerImpl)

The `hasUnboundInputTypeParameters` function must treat Flow types as supported. It must contain the pattern:

```kotlin
if (classType.classId in SirTypeProviderImpl.FLOW_CLASS_IDS) return@let false
```

This ensures Flow types are recognized as supported during visibility checking.

### Cross-file Reference

`SirVisibilityCheckerImpl` must reference `SirTypeProviderImpl.FLOW_CLASS_IDS` directly. The companion object visibility in `SirTypeProviderImpl` must allow this reference, and the resulting code must compile correctly.
