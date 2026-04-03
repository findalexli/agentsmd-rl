# Fix xcstrings stale extraction state in static framework targets

## Problem

When a static framework target has `.xcstrings` (string catalog) files with a companion resource bundle, building from Xcode marks all strings as `"extractionState": "stale"`. This modifies the `.xcstrings` file during every build, creating noise in source control and incorrectly flagging translated strings.

The issue occurs because `.xcstrings` files are currently added to the target's **Sources build phase** for code generation, just like `.xcassets`. However, unlike asset catalogs, string catalogs should not be in the Sources phase — Xcode's string extraction scans Sources for string references, and since the strings use `bundle: .module` (pointing to the companion bundle), Xcode cannot match them and marks everything stale.

## Expected Behavior

- `.xcstrings` files should NOT be added to the Sources build phase
- `.xcstrings` files should remain in the main target's **Resources build phase** so Xcode's string catalog editor can correctly associate string references in Swift code with catalog entries
- `.xcassets` files should continue to be added to Sources (this behavior is correct)
- After building, the `.xcstrings` file should remain unmodified

## Files to Look At

- `cli/Sources/TuistGenerator/Mappers/ResourcesProjectMapper.swift` — the mapper that decides which resource files go into Sources vs Resources build phases for static targets with companion bundles

## Documentation

After fixing the code, create an example fixture that demonstrates this scenario: an iOS app depending on a static framework with `.xcstrings` resources and a companion resource bundle. Add the example under `examples/xcode/` with a README documenting the workspace structure and what it verifies.
