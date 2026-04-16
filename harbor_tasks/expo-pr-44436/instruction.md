# expo/expo#44436 — Fix uuid collision and stale pods cache for precompiled

## Bug 1: UUID collision after predictabilize_uuids

When `pod install` runs with precompiled modules enabled, the `generate_available_uuid_list` method produces UUIDs sequentially from a counter. After `predictabilize_uuids` reassigns existing UUIDs to deterministic values, this counter-based approach can generate UUIDs that collide with already-assigned IDs in the project, corrupting `Pods.xcodeproj`.

Symptoms:
- Running `pod install` produces duplicate UUIDs in the project file
- Xcode build failures or corrupted project state
- The sequential UUID counter restarts from a low offset after UUID predictabilization

Required behavior in `packages/expo-modules-autolinking/scripts/ios/cocoapods/installer.rb`:
- In the `perform_post_install_actions` method, after the original implementation runs, the project object must have a `generate_available_uuid_list` method that:
  - Is defined as a singleton method (dynamically attached to the project instance)
  - Uses cryptographically secure random UUID generation (from Ruby's SecureRandom module with sufficient entropy for 24-character hex strings)
  - Avoids collisions with existing UUIDs already present in the project

## Bug 2: Stale podspec cache on incremental install

When `EXPO_USE_PRECOMPILED_MODULES=1` is set, CocoaPods skips calling `store_podspec` for already-cached pods. On subsequent `pod install` runs, precompiled pods fall back to source builds because cached podspecs in the local podspecs directory are stale.

Symptoms:
- Incremental `pod install` runs do not use precompiled modules
- Pods fall back to slower source builds even when precompiled versions are available
- Cached `.podspec.json` files in the Local Podspecs directory are outdated
- Stale source-build artifacts remain in pod directories that lack the xcframework `Info.plist`

Required behavior in `packages/expo-modules-autolinking/scripts/ios/precompiled_modules.rb`:
- In the `clear_cocoapods_cache` method, alongside existing external cache clearing:
  - The code must clear cached `.podspec.json` files from the Local Podspecs directory (located at `Pods/Local Podspecs/` within the sandbox root)
  - For each pod directory in the Pods sandbox, the code must:
    - Check for the presence of the xcframework's `Info.plist` file at the path `{product_name}.xcframework/Info.plist` within the pod directory
    - Remove the entire pod directory when no xcframework Info.plist exists (indicating stale source-build artifacts)
