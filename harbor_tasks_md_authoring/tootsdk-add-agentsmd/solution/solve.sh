#!/usr/bin/env bash
set -euo pipefail

cd /workspace/tootsdk

# Idempotency guard
if grep -qF "Tests use JSON fixtures from real server responses located in `Tests/TootSDKTest" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,14 +1,13 @@
 # CLAUDE.md
 
-This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
-
 ## Commands
 
 ### Building and Testing
 
-- **Build**: `make build` or `swift build`
+- **Build**: `make build` or `swift build` (use `xcrun swift build` to avoid toolchain conflicts)
 - **Test**: `make test` or `swift test`
 - **Auto-format**: `make lint` - applies formatting and fixes lint issues across Sources, Tests, and Examples
+- **Clean**: `make clean` or `swift package clean`
 
 ### Single Test Execution
 
@@ -17,8 +16,13 @@ Run individual test files using:
 ```bash
 swift test --filter TestClassName
 swift test --filter TestClassName.testMethodName
+# Example: swift test --filter FlavourTests.testDetectsMastodon4
 ```
 
+### Testing with Fixtures
+
+Tests use JSON fixtures from real server responses located in `Tests/TootSDKTests/Resources/`. Use the helper function `localObject<T>(_ type: T.Type, _ filename: String)` to load fixtures in tests.
+
 ## Architecture
 
 ### Core Structure
@@ -47,16 +51,22 @@ TootSDK is a Swift Package Manager library that provides a unified SDK for inter
 
 **Client Extensions** (`Sources/TootSDK/TootClient/TootClient+*.swift`)
 
-- Functionality is split across multiple extensions by feature area:
-  - Account management, Posts, Timelines, Notifications
-  - Lists, Filters, Media, Streaming, etc.
+- Functionality is split across 20+ extensions by feature area:
+  - `TootClient+Account.swift` - Account management, profiles, relationships
+  - `TootClient+Post.swift` - Creating, editing, boosting posts
+  - `TootClient+TimeLine.swift` - Home, local, federated timelines
+  - `TootClient+Notifications.swift` - Push notifications, mentions
+  - `TootClient+Streaming.swift` - WebSocket streaming API
+  - `TootClient+Media.swift` - Media upload and processing
 - Each extension focuses on a specific API domain
 
 **Streaming Support** (`Sources/TootSDK/TootClient/Streaming/`)
 
 - WebSocket-based real-time streaming for timelines and notifications
+- Actor-based `StreamingClient` for connection lifecycle management
 - Async sequence support for event processing
-- Handles connection management and reconnection
+- Automatic retry with exponential backoff
+- Multiple subscribers per timeline with automatic cleanup
 
 **HTML Rendering** (`Sources/TootSDK/HTMLRendering/`)
 
@@ -104,7 +114,8 @@ TootSDK is a Swift Package Manager library that provides a unified SDK for inter
 ### Development Guidelines
 
 - Avoid new dependencies without strong justification
-- Test data must be anonymized before inclusion
+- Test data must be anonymized before inclusion (example.com domains, Lorem Ipsum content)
 - All public methods require documentation
-- Maintain cross-platform compatibility
+- Maintain cross-platform compatibility (no UIKit/AppKit specific code in core)
 - Follow Swift API Design Guidelines
+- Use conventional commit messages for version control
PATCH

echo "Gold patch applied."
