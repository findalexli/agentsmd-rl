#!/usr/bin/env bash
set -euo pipefail

cd /workspace/swift-concurrency-agent-skill

# Idempotency guard
if grep -qF "description: 'Diagnose data races, convert callback-based code to async/await, i" "swift-concurrency/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/swift-concurrency/SKILL.md b/swift-concurrency/SKILL.md
@@ -1,23 +1,19 @@
 ---
 name: swift-concurrency
-description: 'Expert guidance on Swift Concurrency best practices, patterns, and implementation. Use when developers mention: (1) Swift Concurrency, async/await, actors, or tasks, (2) "use Swift Concurrency" or "modern concurrency patterns", (3) migrating to Swift 6, (4) data races or thread safety issues, (5) refactoring closures to async/await, (6) @MainActor, Sendable, or actor isolation, (7) concurrent code architecture or performance optimization, (8) concurrency-related linter warnings (SwiftLint or similar; e.g. async_without_await, Sendable/actor isolation/MainActor lint).'
+description: 'Diagnose data races, convert callback-based code to async/await, implement actor isolation patterns, resolve Sendable conformance issues, and guide Swift 6 migration. Use when developers mention: (1) Swift Concurrency, async/await, actors, or tasks, (2) "use Swift Concurrency" or "modern concurrency patterns", (3) migrating to Swift 6, (4) data races or thread safety issues, (5) refactoring closures to async/await, (6) @MainActor, Sendable, or actor isolation, (7) concurrent code architecture or performance optimization, (8) concurrency-related linter warnings (SwiftLint or similar; e.g. async_without_await, Sendable/actor isolation/MainActor lint).'
 ---
 # Swift Concurrency
 
-## Overview
+## Agent Rules
 
-This skill provides expert guidance on Swift Concurrency, covering modern async/await patterns, actors, tasks, Sendable conformance, and migration to Swift 6. Use this skill to help developers write safe, performant concurrent code and navigate the complexities of Swift's structured concurrency model.
-
-## Agent Behavior Contract (Follow These Rules)
-
-1. Analyze the project/package file to find out which Swift language mode (Swift 5.x vs Swift 6) and which Xcode/Swift toolchain is used when advice depends on it.
+1. Analyze `Package.swift` or `.pbxproj` to determine Swift language mode (5.x vs 6) and toolchain before giving advice.
 2. Before proposing fixes, identify the isolation boundary: `@MainActor`, custom actor, actor instance isolation, or nonisolated.
 3. Do not recommend `@MainActor` as a blanket fix. Justify why main-actor isolation is correct for the code.
 4. Prefer structured concurrency (child tasks, task groups) over unstructured tasks. Use `Task.detached` only with a clear reason.
 5. If recommending `@preconcurrency`, `@unchecked Sendable`, or `nonisolated(unsafe)`, require:
    - a documented safety invariant
    - a follow-up ticket to remove or migrate it
-6. For migration work, optimize for minimal blast radius (small, reviewable changes) and add verification steps.
+6. For migration work, optimize for minimal blast radius (small, reviewable changes) and follow the validation loop: **Build → Fix errors → Rebuild → Only proceed when clean**.
 7. Course references are for deeper learning only. Use them sparingly and only when they clearly help answer the developer's question.
 
 ## Triage Checklist (Before Advising)
@@ -38,38 +34,16 @@ Skip Quick Fix Mode when:
 - The error crosses module boundaries or involves public API changes.
 - The fix would require `@unchecked Sendable`, `@preconcurrency`, or `nonisolated(unsafe)` without a clear invariant.
 
-## Recommended Tools for Analysis
-
-When analyzing Swift projects for concurrency issues:
-
-1. **Project Settings Discovery**
-   - Use `Read` on `Package.swift` for SwiftPM settings (tools version, strict concurrency flags, upcoming features)
-   - Use `Grep` for `SWIFT_STRICT_CONCURRENCY` or `SWIFT_DEFAULT_ACTOR_ISOLATION` in `.pbxproj` files
-   - Use `Grep` for `SWIFT_UPCOMING_FEATURE_` to find enabled upcoming features
-
-
-
 ## Project Settings Intake (Evaluate Before Advising)
 
-Concurrency behavior depends on build settings. Always try to determine:
-
-- Default actor isolation (is the module default `@MainActor` or `nonisolated`?)
-- Strict concurrency checking level (minimal/targeted/complete)
-- Whether upcoming features are enabled (especially `NonisolatedNonsendingByDefault`)
-- Swift language mode (Swift 5.x vs Swift 6) and SwiftPM tools version
-
-### Manual checks (no scripts)
+Concurrency behavior depends on build settings. Before advising, determine these via `Read` on `Package.swift` or `Grep` in `.pbxproj` files:
 
-- SwiftPM:
-  - Check `Package.swift` for `.defaultIsolation(MainActor.self)`.
-  - Check `Package.swift` for `.enableUpcomingFeature("NonisolatedNonsendingByDefault")`.
-  - Check for strict concurrency flags: `.enableExperimentalFeature("StrictConcurrency=targeted")` (or similar).
-  - Check tools version at the top: `// swift-tools-version: ...`
-- Xcode projects:
-  - Search `project.pbxproj` for:
-    - `SWIFT_DEFAULT_ACTOR_ISOLATION`
-    - `SWIFT_STRICT_CONCURRENCY`
-    - `SWIFT_UPCOMING_FEATURE_` (and/or `SWIFT_ENABLE_EXPERIMENTAL_FEATURES`)
+| Setting | SwiftPM (`Package.swift`) | Xcode (`.pbxproj`) |
+|---------|--------------------------|---------------------|
+| Default isolation | `.defaultIsolation(MainActor.self)` | `SWIFT_DEFAULT_ACTOR_ISOLATION` |
+| Strict concurrency | `.enableExperimentalFeature("StrictConcurrency=targeted")` | `SWIFT_STRICT_CONCURRENCY` |
+| Upcoming features | `.enableUpcomingFeature("NonisolatedNonsendingByDefault")` | `SWIFT_UPCOMING_FEATURE_*` |
+| Language mode | `// swift-tools-version:` at top | Swift Language Version build setting |
 
 If any of these are unknown, ask the developer to confirm them before giving migration-sensitive guidance.
 
@@ -159,81 +133,28 @@ When a developer needs concurrency guidance, follow this decision tree:
 
 ## Core Patterns Reference
 
-### When to Use Each Concurrency Tool
-
-**async/await** - Making existing synchronous code asynchronous
-```swift
-// Use for: Single asynchronous operations
-func fetchUser() async throws -> User {
-    try await networkClient.get("/user")
-}
-```
-
-**async let** - Running multiple independent async operations in parallel
-```swift
-// Use for: Fixed number of parallel operations known at compile time
-async let user = fetchUser()
-async let posts = fetchPosts()
-let profile = try await (user, posts)
-```
-
-**Task** - Starting unstructured asynchronous work
-```swift
-// Use for: Fire-and-forget operations, bridging sync to async contexts
-Task {
-    await updateUI()
-}
-```
-
-**Task Group** - Dynamic parallel operations with structured concurrency
-```swift
-// Use for: Unknown number of parallel operations at compile time
-await withTaskGroup(of: Result.self) { group in
-    for item in items {
-        group.addTask { await process(item) }
-    }
-}
-```
-
-**Actor** - Protecting mutable state from data races
-```swift
-// Use for: Shared mutable state accessed from multiple contexts
-actor DataCache {
-    private var cache: [String: Data] = [:]
-    func get(_ key: String) -> Data? { cache[key] }
-}
-```
+### Concurrency Tool Selection
 
-**@MainActor** - Ensuring UI updates on main thread
-```swift
-// Use for: View models, UI-related classes
-@MainActor
-class ViewModel: ObservableObject {
-    @Published var data: String = ""
-}
-```
+| Need | Tool | Key Guidance |
+|------|------|-------------|
+| Single async operation | `async/await` | Default choice for sequential async work |
+| Fixed parallel operations | `async let` | Known count at compile time; auto-cancelled on throw |
+| Dynamic parallel operations | `withTaskGroup` | Unknown count; structured — cancels children on scope exit |
+| Sync → async bridge | `Task { }` | Inherits actor context; use `Task.detached` only with documented reason |
+| Shared mutable state | `actor` | Prefer over locks/queues; keep isolated sections small |
+| UI-bound state | `@MainActor` | Only for truly UI-related code; justify isolation |
 
 ### Common Scenarios
 
-**Scenario: Network request with UI update**
+**Network request with UI update**
 ```swift
 Task { @concurrent in
-    let data = try await fetchData() // Background
-    await MainActor.run {
-        self.updateUI(with: data) // Main thread
-    }
+    let data = try await fetchData()
+    await MainActor.run { self.updateUI(with: data) }
 }
 ```
 
-**Scenario: Multiple parallel network requests**
-```swift
-async let users = fetchUsers()
-async let posts = fetchPosts()
-async let comments = fetchComments()
-let (u, p, c) = try await (users, posts, comments)
-```
-
-**Scenario: Processing array items in parallel**
+**Processing array items in parallel**
 ```swift
 await withTaskGroup(of: ProcessedItem.self) { group in
     for item in items {
@@ -253,6 +174,18 @@ Key changes in Swift 6:
 - **Sendable requirements** enforced on boundaries
 - **Isolation checking** for all async boundaries
 
+### Migration Validation Loop
+
+Apply this cycle for each migration change:
+
+1. **Build** — Run `swift build` or Xcode build to surface new diagnostics
+2. **Fix** — Address one category of error at a time (e.g., all Sendable issues first)
+3. **Rebuild** — Confirm the fix compiles cleanly before moving on
+4. **Test** — Run the test suite to catch regressions (`swift test` or Cmd+U)
+5. **Only proceed** to the next file/module when all diagnostics are resolved
+
+If a fix introduces new warnings, resolve them before continuing. Never batch multiple unrelated fixes — keep commits small and reviewable.
+
 For detailed migration steps, see `references/migration.md`.
 
 ## Reference Files
@@ -272,24 +205,15 @@ Load these files as needed for specific topics:
 - **`testing.md`** - XCTest async patterns, Swift Testing, concurrency testing utilities
 - **`migration.md`** - Swift 6 migration strategy, closure-to-async conversion, @preconcurrency, FRP migration
 
-## Best Practices Summary
-
-1. **Prefer structured concurrency** - Use task groups over unstructured tasks when possible
-2. **Minimize suspension points** - Keep actor-isolated sections small to reduce context switches
-3. **Use @MainActor judiciously** - Only for truly UI-related code
-4. **Make types Sendable** - Enable safe concurrent access by conforming to Sendable
-5. **Handle cancellation** - Check Task.isCancelled in long-running operations
-6. **Avoid blocking** - Never use semaphores or locks in async contexts
-7. **Test concurrent code** - Use proper async test methods and consider timing issues
-
 ## Verification Checklist (When You Change Concurrency Code)
 
-- Confirm build settings (default isolation, strict concurrency, upcoming features) before interpreting diagnostics.
-- For Quick Fix Mode: compile the affected target/module and rerun the specific diagnostics or lints.
-- After refactors:
-  - Run tests, especially concurrency-sensitive ones (see `references/testing.md`).
-  - If performance-related, verify with Instruments (see `references/performance.md`).
-  - If lifetime-related, verify deinit/cancellation behavior (see `references/memory-management.md`).
+1. Confirm build settings (default isolation, strict concurrency, upcoming features) before interpreting diagnostics.
+2. **Build** — Verify the project compiles without new warnings or errors.
+3. **Test** — Run tests, especially concurrency-sensitive ones (see `references/testing.md`).
+4. **Performance** — If performance-related, verify with Instruments (see `references/performance.md`).
+5. **Lifetime** — If lifetime-related, verify deinit/cancellation behavior (see `references/memory-management.md`).
+6. Check `Task.isCancelled` in long-running operations.
+7. Never use semaphores or locks in async contexts — use actors or `Mutex` instead.
 
 ## Glossary
 
PATCH

echo "Gold patch applied."
