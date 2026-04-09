# Swift Export: Support nullable Unit/Void types

## Problem

The Kotlin compiler's Swift Export feature (generating Swift bindings for Kotlin code) does not properly handle nullable Unit types (`Unit?`). When exporting Kotlin functions that return `Unit?` or accept `Unit?` parameters to Swift, the generated bridge code fails or produces incorrect results.

## Key file

The type bridging logic is in:
- `native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/BridgeProvider/TypeBridging.kt`

## What you need to do

1. Add support for bridging `Optional<Void>` (Swift's representation of Kotlin's `Unit?`)

2. The fix should:
   - Create a new bridge type specifically for `Optional<Void>` (similar to how `Optional<Nothing>` is handled)
   - Handle the Swift-to-Kotlin conversion: convert the boolean presence check to `Unit` or `null`
   - Handle the Kotlin-to-Swift conversion: convert `Unit?` to a boolean presence indicator
   - Update the bridge selection logic to use this new bridge when encountering `AsVoid` inside an `Optional` wrapper
   - Update the NS collection element bridging to handle the new bridge type

## Hints

- Look at how `AsOptionalNothing` (for `Optional<Never>`/Nothing?) is implemented - follow the same pattern
- The bridge should use `Boolean` as the underlying Kotlin type and `Bool` as the C type
- The value conversions need to handle:
  - Swift side: `Bool` ↔ `Void?` (using `nil` checks and `()` for non-nil)
  - Kotlin side: `Boolean` ↔ `Unit?` (using null checks and `Unit` value)
- Search for `AsNothing` and `AsOptionalNothing` to understand the pattern
- Also look at `AsVoid` to see how non-optional `Unit`/`Void` is handled

## Testing

After your fix, the following should work:
- Functions returning `Unit?` in Kotlin are correctly bridged to Swift functions returning `Void?`
- Functions accepting `Unit?` in Kotlin are correctly bridged to Swift functions accepting `Void?`
- The generated bridge code compiles without errors
