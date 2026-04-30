#!/usr/bin/env bash
set -euo pipefail

cd /workspace/anytype-swift

# Idempotency guard
if grep -qF "After making code changes, report them to the user who will verify compilation i" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -23,14 +23,8 @@ Anytype is a privacy-focused, local-first workspace application for iOS. Built w
    - Swift Package Manager (built-in)
    - If Dependencies/Middleware/Lib.xcframework is missing binaries, try `make generate`
 
-### Build & Test
-```bash
-# Normal build
-xcodebuild -scheme Anytype -configuration Debug -destination 'platform=iOS Simulator,name=iPhone 15' build
-
-# Compilation check
-xcodebuild -scheme Anytype -configuration Debug -destination 'platform=iOS Simulator,name=iPhone 15' build-for-testing
-```
+### Compilation Verification
+After making code changes, report them to the user who will verify compilation in Xcode (faster with caches).
 
 ### Essential Commands
 ```bash
@@ -410,4 +404,4 @@ git commit -m "IOS-4852 Add limit check for pinned spaces"
 **Incomplete Mock Updates (2025-01-16):** Refactored `spaceViewStorage` → `spaceViewsStorage` and `participantSpaceStorage` → `participantSpacesStorage` in production code, but forgot to update `MockView.swift` causing test failures. When renaming dependencies:
 1. Search for old names across entire codebase: `rg "oldName" --type swift`
 2. Update all references in tests, mocks, and DI registrations
-3. Run unit tests to verify: `xcodebuild -scheme Anytype -destination 'platform=iOS Simulator,name=iPhone 15' build-for-testing`
\ No newline at end of file
+3. Report changes to user for compilation verification
\ No newline at end of file
PATCH

echo "Gold patch applied."
