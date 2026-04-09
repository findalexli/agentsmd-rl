# Fix Swift Export for Inline Classes with Reference Types

## Problem

The Swift export feature in the Kotlin compiler crashes when generating Swift bindings for inline/value classes that wrap reference types (non-primitive types).

## Context

When Kotlin's Swift export generates initialization code for value classes (formerly called inline classes), it needs to handle the case where the value class wraps a reference type differently from primitive types. The issue is in how the generated code casts the uninitialized instance.

## Where to Look

The relevant code is in the Swift export module:

- **File**: `native/swift/sir-light-classes/src/org/jetbrains/sir/lightclasses/nodes/SirInitFromKtSymbol.kt`

This file handles generating Swift initialization code from Kotlin symbols. Look for where it generates the `createUninitializedInstance` call and handles the resulting type.

## The Bug

When generating initialization code for an inline/value class that wraps a reference type (like a custom class), the generated Kotlin code doesn't properly cast the result. This causes a type mismatch because `createUninitializedInstance<T>()` returns type `T`, but for inline classes with reference types, this needs to be cast to `Any?` for proper interoperability.

## What You Need to Do

1. Identify where the initialization code is generated in `SirInitFromKtSymbol.kt`
2. Add logic to detect when the containing declaration is an inline/value class (`isInline` property)
3. When generating the initialization expression for inline classes, add an explicit cast to `Any?`

## Hint

You'll need to:
- Import `org.jetbrains.kotlin.analysis.api.components.containingDeclaration`
- Check if the `containingDeclaration` of the symbol is a `KaNamedClassSymbol` with `isInline` property
- Conditionally append ` as Any?` to the generated code when dealing with inline classes

## Verification

After your fix:
- The `sir-light-classes` module should compile successfully
- The generated code for inline classes with reference types should include the proper cast
