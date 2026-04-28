#!/usr/bin/env bash
set -euo pipefail

cd /workspace/auth0.swift

# Idempotency guard
if grep -qF "- **`Auth0.plist` vs `Info.plist`**: The SDK reads `ClientId`/`Domain` from `Aut" "AGENTS.md" && grep -qF "See @AGENTS.md for all coding guidelines, commands, project structure, code styl" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,227 +1,324 @@
-# AI Agent Guidelines for Auth0.swift SDK
+# AI Agent Guidelines for Auth0.swift
 
-This document provides context and guidelines for AI coding assistants working with the Auth0.swift SDK codebase.
+This document provides context and guidelines for AI coding assistants working with the Auth0.swift codebase.
 
 ## Project Overview
 
-**Auth0.swift** is an idiomatic Swift SDK for integrating Auth0 authentication and authorization into Apple platform applications (iOS, macOS, tvOS, watchOS). The SDK provides a comprehensive solution for:
+**Auth0.swift** is an idiomatic Swift SDK for integrating Auth0 authentication and authorization into Apple platform applications.
 
-  - **WebAuth**: Universal Login via `ASWebAuthenticationSession` (iOS 12+ / macOS 10.15+).
-  - **Authentication**: Direct API client (Login, Signup, User Info, Passwordless).
-  - **CredentialsManager**: Secure storage and automatic renewal of credentials.
-  - **Support**: Async/Await, Combine, and legacy Callback patterns.
+- **Language:** Swift 6.0 (swift-tools-version: 6.0, language mode: Swift 5)
+- **Tech Stack:** iOS 14+, macOS 11+, tvOS 14+, watchOS 7+, visionOS 1+, SPM, CocoaPods, Carthage
+- **Package Manager:** Swift Package Manager (primary), CocoaPods, Carthage
+- **Minimum Platform Version:** iOS 14, macOS 11, tvOS 14, watchOS 7, visionOS 1
 
-## Repository Structure
+---
 
-```text
-Auth0.swift/
-├── Auth0/                          # Main SDK Source
-│   ├── WebAuth/                    # Web Authentication (Universal Login)
-│   ├── Authentication/             # Authentication API Client
-│   ├── CredentialsManager/         # Secure Storage & Refresh Logic
-│   ├── Networking/                 # Network Layer (Request/Response)
-│   ├── Utils/                      # Validators, Extensions
-│   └── Auth0.swift                 # Main Entry Point
-├── Auth0Tests/                     # Unit Tests (XCTest + Quick/Nimble)
-├── Package.swift                   # Swift Package Manager Definition
-├── Auth0.podspec                   # CocoaPods Definition
-├── Cartfile                        # Carthage Definition
-└── README.md                       # Documentation
+## Commands
+
+> Copy-paste ready. These are the exact commands used in CI.
+
+```bash
+# Build (SPM)
+swift build
+
+# Run all tests (SPM)
+swift test
+
+# Run tests for a specific platform (xcodebuild — matches CI)
+xcodebuild test -scheme Auth0.iOS -destination 'platform=iOS Simulator,name=iPhone 15'
+xcodebuild test -scheme Auth0.macOS -destination 'platform=macOS'
+xcodebuild test -scheme Auth0.tvOS -destination 'platform=tvOS Simulator,name=Apple TV'
+
+# Lint
+swiftlint lint --reporter github-actions-logging
+
+# Coverage (iOS only, requires slather gem)
+bundle exec slather coverage -x --scheme Auth0.iOS Auth0.xcodeproj
+
+# Lint podspec
+bundle exec pod lib lint --allow-warnings --fail-fast
+
+# Generate documentation (DocC)
+swift package generate-documentation
+
+# Resolve SPM dependencies
+swift package resolve
+
+# Bootstrap Carthage dependencies (for Xcode development)
+carthage bootstrap --use-xcframeworks
+
+# Release (tags + publishes to CocoaPods)
+bundle exec fastlane release
 ```
 
-## Key Technical Decisions
+---
 
-### Architecture Patterns
+## Testing
 
-- **Protocol-Oriented**: Heavy use of protocols to define API contracts (`Authentication`, `WebAuth`, `CredentialsStorage`).
-- **Functional Options**: Used in WebAuth builder pattern (e.g., `.scope()`, `.connection()`).
-- **Concurrency**:
-  - **Primary**: Swift Concurrency (`async`/`await`) for modern targets.
-  - **Secondary**: Combine Publishers (via `.start()` returning `AnyPublisher`).
-  - **Legacy**: Result type Closures (`(Result<T, Auth0Error>) -> Void`).
+- **Framework:** Quick 7+ + Nimble 13+ (BDD), XCTest (underlying runner)
+- **Test Location:** `Auth0Tests/`
+- **Coverage Tool:** Slather + Codecov
+- **Coverage Threshold:** Tracked via Codecov (no hard gate, upload on iOS run)
 
-### Authentication Flow
+### Running Tests
 
-1.  **WebAuth** (Recommended):
-    - Uses `ASWebAuthenticationSession` to share cookies with the system browser.
-    - Handles PKCE (Proof Key for Code Exchange) automatically.
-    - Support for Ephemeral Sessions (no cookies).
+```bash
+# Run all tests via SPM
+swift test
 
-2.  **Authentication API**:
-    - Direct HTTP calls to Auth0 Authentication endpoints.
-    - Used for custom UI (Resource Owner Password) or non-interactive flows.
+# Run a specific test file (SPM — uses --filter with test class name)
+swift test --filter CredentialsManagerSpec
 
-### Credential Management
+# Run via xcodebuild (iOS)
+xcodebuild test -scheme Auth0.iOS -destination 'platform=iOS Simulator,name=iPhone 15'
+```
 
-- **CredentialsManager**: Abstraction for storing tokens.
-- **Storage**: Defaults to `SimpleKeychain` (a distinct Auth0 library) for Keychain access.
-- **Automatic Refresh**: Handles checking expiration and refreshing access tokens automatically when requesting credentials.
+### Testing Conventions
 
-## Development Guidelines
+- Test files are named `*Spec.swift` and use Quick's `describe/context/it` BDD DSL
+- Use `beforeEach` / `afterEach` for setup and teardown
+- Use `expect(...).to(...)` Nimble matchers (never `XCTAssert`)
+- Test all three concurrency patterns: async/await, Combine, and completion handlers
+- Cover three scenarios per feature: success, API error, network failure
+- Use `waitUntil` or `expect(...).toEventually(...)` for async tests with a 2s timeout
 
-### Code Style
+### Mocking & Test Utilities
 
-- **Language**: Swift 5.7+
-- **Formatting**: Adheres to SwiftLint rules (see `.swiftlint.yml`).
-- **Documentation**: 100% documentation coverage required for public APIs (Triple-slash `///`).
+- Protocol-based mocking: implement the protocol (e.g., `Authentication`, `CredentialsStorage`) in test-only types
+- `StubURLProtocol` + `NetworkStub` for HTTP-level mocking — register/unregister in `beforeEach`/`afterEach`
+- `URLProtocol.registerClass(StubURLProtocol.self)` pattern used consistently across all network specs
 
-### API Design Principles
+---
 
-When adding or modifying APIs, you must support the **Tri-brid Concurrency Model**:
+## Project Structure
 
-1.  **Async/Await** (Modern):
-    ```swift
-    func login() async throws -> Credentials
-    ```
-2.  **Combine** (Reactive):
-    ```swift
-    func login() -> AnyPublisher<Credentials, Auth0Error>
-    ```
-3.  **Completion Handler** (Legacy/ObjC):
-    ```swift
-    func login(completion: @escaping (Result<Credentials, Auth0Error>) -> Void)
-    ```
+```
+Auth0.swift/
+├── Auth0/                          # Main SDK source
+│   ├── Auth0.swift                 # Public entry point (Auth0.webAuth(), Auth0.authentication())
+│   ├── Authentication.swift        # Authentication protocol
+│   ├── Auth0Authentication.swift   # Authentication API client
+│   ├── WebAuth/                    # Universal Login via ASWebAuthenticationSession
+│   ├── CredentialsManager.swift    # Secure storage & automatic token refresh
+│   ├── Credentials.swift           # Token model
+│   ├── DPoP/                       # DPoP (Demonstrating Proof of Possession) support
+│   ├── MFA/                        # Multi-factor authentication flows
+│   ├── Networking/                 # Request/response layer
+│   ├── Auth0Error.swift            # Base error type
+│   ├── AuthenticationError.swift   # Authentication API errors
+│   ├── CredentialsManagerError.swift
+│   └── Version.swift               # SDK version constant
+├── Auth0Tests/                     # Unit tests (Quick/Nimble specs)
+├── Package.swift                   # SPM manifest
+├── Auth0.podspec                   # CocoaPods spec (kept in sync with Package.swift)
+├── Cartfile                        # Carthage dependencies
+├── .swiftlint.yml                  # SwiftLint configuration
+├── fastlane/                       # Release automation
+├── .github/workflows/              # CI: main.yml, claude-code-review.yml, sca_scan.yml
+├── Documentation.docc              # DocC documentation
+├── CHANGELOG.md                    # Keep a Changelog format
+├── CONTRIBUTING.md                 # Dev setup and contribution guide
+└── README.md                       # Quickstart
+```
 
-### Error Handling
+### Key Files
 
-- All errors must map to `Auth0Error`.
-- Specific domains:
-  - `AuthenticationError`: API failures.
-  - `WebAuthError`: User cancellation, browser issues.
+| File | Purpose |
+|------|---------|
+| `Auth0/Auth0.swift` | Public factory methods: `Auth0.webAuth()`, `Auth0.authentication()` |
+| `Auth0/CredentialsManager.swift` | Token storage, expiry checks, automatic refresh |
+| `Auth0/Version.swift` | SDK version string — update on every release |
+| `Auth0.podspec` | CocoaPods spec — must stay in sync with `Package.swift` |
+| `.swiftlint.yml` | Lint rules — `line_length: 500`, `type_body_length: 300/400` |
+| `fastlane/Fastfile` | `release` lane: tag + CocoaPods publish |
 
-### Testing Requirements
+---
 
-- **Frameworks**: XCTest, Quick, and Nimble.
-- **Mocking**: Use protocol-based mocking for `URLSession` and Storage.
-- **Coverage**: Ensure tests cover Success, Failure (API error), and Network Failure scenarios.
+## Code Style
 
-## Build & Testing Commands
+### Linter & Formatter
 
-```bash
-# Resolve Dependencies
-swift package resolve
+- **Linter:** SwiftLint — Config: `.swiftlint.yml`
+- Lints only the `Auth0/` directory (excludes `Carthage/`, `Pods/`)
+- Opt-in rule: `empty_count`; disabled: `void_function_in_ternary`, `large_tuple`, `blanket_disable_command`
+- `line_length: 500`, `type_body_length: 300` (warning) / `400` (error)
 
-# Build the SDK
-swift build
+### Naming Conventions
 
-# Run Tests
-swift test
+- Types: `PascalCase` (e.g., `CredentialsManager`, `WebAuthError`)
+- Functions/properties: `camelCase` (e.g., `accessToken`, `renewAuth`)
+- Constants: `PascalCase` private file-level constants in test files (e.g., `AccessToken`, `RefreshToken`)
+- Files: match primary type name (e.g., `CredentialsManager.swift`)
+- Test files: `*Spec.swift` suffix (e.g., `CredentialsManagerSpec.swift`)
+- Min identifier length: 3 characters (SwiftLint enforced)
 
-# Generate Documentation (DocC)
-swift package generate-documentation
+### API Design — Tri-brid Concurrency Model
+
+Every public async API **must** expose three variants:
+
+✅ Good — all three concurrency styles present:
+
+```swift
+// Async/Await (primary)
+func credentials() async throws -> Credentials
+
+// Combine
+func credentials() -> AnyPublisher<Credentials, CredentialsManagerError>
+
+// Completion handler
+func credentials(callback: @escaping (Result<Credentials, CredentialsManagerError>) -> Void)
 ```
 
-## Configuration Files
+❌ Bad — only one style, breaks existing integrations:
 
-### Package Management
+```swift
+// Missing Combine and completion handler variants
+func credentials() async throws -> Credentials
+```
+
+### Patterns
+
+- **Protocol-Oriented**: API contracts defined as protocols (`Authentication`, `WebAuth`, `CredentialsStorage`) — enables protocol-based mocking in tests
+- **Builder pattern**: WebAuth flow uses chained method calls (`.scope()`, `.connection()`, `.audience()`)
+- **Result type**: All completion handlers use `Result<T, Auth0Error>`
+- **@MainActor callbacks**: All public completion-handler APIs dispatch callbacks on the main actor
+
+---
 
-- **`Package.swift`**: Primary definition (SPM).
-- **`Auth0.podspec`**: Kept in sync for CocoaPods.
+## Git Workflow
 
-### Auth0 Configuration
+### Branch Naming
 
-While the SDK can be configured in code, it defaults to reading from `Auth0.plist` (or `Info.plist` in older setups):
+- Feature branches: `feat/<description>` or `feature/<description>`
+- Fix branches: `fix/<description>`
+- Release branches: `release/<version>` (e.g., `release/2.18.0`) — triggers RL Scanner on merge
+
+### Commit Messages
+
+Conventional Commits format:
 
-```xml
-<?xml version="1.0" encoding="UTF-8"?>
-<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
-<plist version="1.0">
-<dict>
-    <key>ClientId</key>
-    <string>YOUR_CLIENT_ID</string>
-    <key>Domain</key>
-    <string>YOUR_DOMAIN</string>
-</dict>
-</plist>
+```
+feat: add automatic retry for credential renewal
+fix: correct rl-wrapper flag from --suppress_output to --suppress-output
+chore: update SDK version to 2.18.0
+docs: update migration guide for v3
 ```
 
-## Dependencies
+### Pull Requests
+
+- CI runs: tests on iOS/macOS/tvOS (Xcode 16.1), SwiftLint, pod lib lint
+- Coverage uploaded to Codecov (iOS only)
+- Use PR template; reference Jira ticket or GitHub issue
+
+### Changelog
+
+Keep a Changelog format with categories: `Added`, `Changed`, `Deprecated`, `Fixed`, `Security`. Example:
+
+```markdown
+## [2.18.0](https://github.com/auth0/Auth0.swift/tree/2.18.0) (2026-03-05)
+**Added**
+- feat: make Auth0APIError.isRetryable public
+```
+
+---
+
+## Boundaries
+
+### ✅ Always Do
 
-- **JWTDecode.swift**: For decoding JWTs to extract claims/expiry (v4.0+, Swift 6 compliant).
-- **SimpleKeychain**: For Keychain access (iOS/macOS).
-- **Quick/Nimble**: (Test Target only) Behavior-driven testing.
+- Run `swift test` before committing
+- Follow SwiftLint rules — run `swiftlint lint` locally before pushing
+- Add `///` documentation to all new public APIs
+- Add unit tests covering success, API error, and network failure
+- Update `CHANGELOG.md` for every user-facing change
+- Implement all three concurrency variants (async/await, Combine, completion handler) for new async public APIs
+- Dispatch completion-handler callbacks on `@MainActor`
+- Use typed errors: `AuthenticationError`, `WebAuthError`, `CredentialsManagerError`
+- Update `Auth0/Version.swift` and `Auth0.podspec` together on releases
+
+### ⚠️ Ask First
+
+- Adding new dependencies to `Package.swift` / `Auth0.podspec`
+- Modifying public API signatures (source-breaking changes)
+- Changing minimum platform versions
+- Changes to `.github/workflows/` CI configuration
+- Modifying security-related code (PKCE, DPoP, token storage, state validation)
+- Updating `Auth0.podspec` — must stay in sync with `Package.swift`
+
+### 🚫 Never Do
+
+- Commit secrets, API keys, or tokens
+- Log access tokens, refresh tokens, or ID tokens — anywhere
+- Disable PKCE for WebAuth flows
+- Store tokens in `UserDefaults` — always use `CredentialsManager` + `SimpleKeychain`
+- Modify `Carthage/`, `Pods/`, or build output directories
+- Remove or skip failing tests without fixing them
+- Break public API backward compatibility without explicit approval and a migration guide
+- Modify auto-generated files (DocC output, SPM-resolved lock files) by hand
+
+---
 
 ## Security Considerations
 
-1.  **PKCE**: Mandatory and automatic for WebAuth.
-2.  **State Validation**: Random state strings used to prevent CSRF in web flows.
-3.  **Keychain**: Tokens should never be stored in `UserDefaults`; use `CredentialsManager`.
-4.  **Pinned Certificates**: Supported via `URLSession` configuration if high security is required.
+1. **PKCE**: Enabled by default for all WebAuth flows — never disable
+2. **Token Storage**: `SimpleKeychain` (Keychain) only — never `UserDefaults` or plain files
+3. **Token Logging**: Never log access tokens, refresh tokens, or ID tokens
+4. **DPoP**: Supported — see `Auth0/DPoP/` directory
+5. **State Validation**: Random state strings used to prevent CSRF in web flows
+6. **Certificate Pinning**: Configurable via `URLSession` for high-security deployments
 
-## Documentation
+---
 
-- **README.md**: Quickstart.
-- **EXAMPLES.md**: (If present) or inline Code Snippets in docblocks.
-- **MIGRATION.md**: Crucial when moving between major versions (e.g., v1 -> v2).
+## Dependencies
 
-## Common Pitfalls
+### Core
 
-- **Bundle Identifier**: The callback URL in the Auth0 Dashboard must match the App's Bundle ID format (e.g., `com.example.app://YOUR_DOMAIN/ios/com.example.app/callback`).
-- **Dispatcher**: UI updates must happen on `@MainActor` / Main Thread.
-- **Retain Cycles**: Be careful with `self` capture in closures within `CredentialsManager`.
-- **Info.plist Configuration**: Ensure `CFBundleURLTypes` is properly configured for callback URL schemes.
+- **SimpleKeychain** `1.3.0` — Keychain access (iOS/macOS/tvOS/watchOS)
+- **JWTDecode.swift** `4.0.0` — JWT decoding for claims and expiry
 
-## AI Agent Best Practices
+### Test
 
-When assisting with this codebase:
+- **Quick** `7.0+` — BDD test framework
+- **Nimble** `13.0+` — Matcher library for Quick
 
-1.  **Prioritize Async/Await**: Default to `async`/`await` syntax unless the user specifies Combine or Closures.
-2.  **Type Safety**: Strictly use `Result<T, Auth0Error>` types.
-3.  **Availability Checks**: Check `#available(iOS 13.0, *)` if mixing legacy code.
-4.  **Platform Checks**: Be aware of API differences between `iOS` and `macOS` (e.g., `UIApplication` vs `NSApplication`).
+### Dev / Release
 
-## Example Workflows
+- **fastlane** — Release automation (tagging, CocoaPods publish)
+- **cocoapods** — podspec linting and publishing
+- **slather** — Coverage report conversion (Xcode → Cobertura XML for Codecov)
+- **Carthage** — Dependency manager for Xcode project development setup
 
-### Web Authentication (Async/Await)
+---
 
-```swift
-import Auth0
-
-func login() async {
-    do {
-        let credentials = try await Auth0
-            .webAuth()
-            .scope("openid profile email")
-            .start()
-        print("AccessToken: \(credentials.accessToken)")
-    } catch {
-        print("Failed with error: \(error)")
-    }
-}
-```
+## Release Process
 
-### Credentials Manager (Storage & Refresh)
+1. Update version in `Auth0/Version.swift` (e.g., `let version = "2.19.0"`)
+2. Update `Auth0.podspec` `s.version` to match
+3. Update `CHANGELOG.md` with release date and entries
+4. Open PR on a `release/<version>` branch — CI runs full test suite
+5. Merge PR → `master`
+6. Run `bundle exec fastlane release` to tag and push to CocoaPods
+7. RL Security Scanner runs automatically on merged release PRs
 
-```swift
-let credentialsManager = CredentialsManager(authentication: Auth0.authentication())
-
-// Get a valid token (refreshes automatically if needed)
-func fetchToken() async {
-    do {
-        let credentials = try await credentialsManager.credentials()
-        print("Valid Access Token: \(credentials.accessToken)")
-    } catch {
-        // Handle login required
-    }
-}
-```
+---
 
-### Direct Authentication (Login with Password)
+## Common Pitfalls
 
-```swift
-import Auth0
-
-func directLogin() {
-    Auth0
-        .authentication()
-        .login(username: "email@example.com", password: "password", realm: "Username-Password-Authentication")
-        .start { result in
-            switch result {
-            case .success(let credentials):
-                print("Logged in: \(credentials)")
-            case .failure(let error):
-                print("Error: \(error)")
-            }
-        }
-}
-```
+- **Callback URL mismatch**: The URL scheme in `Auth0 Dashboard` must match `CFBundleURLTypes` in `Info.plist` (format: `com.example.app://YOUR_DOMAIN/ios/com.example.app/callback`)
+- **Missing `@MainActor`**: UI updates from SDK callbacks must be dispatched on the main actor — the SDK does this internally, but calling code must not assume a background thread
+- **Retain cycles in closures**: Use `[weak self]` captures in closures within `CredentialsManager` to avoid leaks
+- **Single podspec/Package.swift sync**: Forgetting to update `Auth0.podspec` after changing `Package.swift` will break `pod lib lint` in CI
+- **Platform-conditional APIs**: `WebAuth` is only available on `iOS`, `macOS`, `macCatalyst`, `visionOS` — guard with `#if WEB_AUTH_PLATFORM` (defined in `Package.swift`)
+- **`Auth0.plist` vs `Info.plist`**: The SDK reads `ClientId`/`Domain` from `Auth0.plist` in test targets; production apps typically use `Auth0.plist` or pass values programmatically
+
+---
+
+## External References
+
+- [README](https://github.com/auth0/Auth0.swift/blob/master/README.md)
+- [EXAMPLES.md](https://github.com/auth0/Auth0.swift/blob/master/EXAMPLES.md)
+- [API Docs (DocC)](https://auth0.github.io/Auth0.swift/documentation/auth0/)
+- [Auth0 Docs — Swift Quickstart](https://auth0.com/docs/quickstart/native/ios-swift)
+- [CONTRIBUTING.md](https://github.com/auth0/Auth0.swift/blob/master/CONTRIBUTING.md)
+- [SimpleKeychain](https://github.com/auth0/SimpleKeychain)
+- [JWTDecode.swift](https://github.com/auth0/JWTDecode.swift)
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1,3 @@
+# Claude Guidelines for Auth0.swift
+
+See @AGENTS.md for all coding guidelines, commands, project structure, code style, testing conventions, and boundaries.
PATCH

echo "Gold patch applied."
