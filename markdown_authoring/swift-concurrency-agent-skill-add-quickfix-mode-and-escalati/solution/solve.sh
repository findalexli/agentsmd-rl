#!/usr/bin/env bash
set -euo pipefail

cd /workspace/swift-concurrency-agent-skill

# Idempotency guard
if grep -qF "- **Background work**: for work that should always hop off the caller\u2019s isolatio" "swift-concurrency/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/swift-concurrency/SKILL.md b/swift-concurrency/SKILL.md
@@ -20,6 +20,24 @@ This skill provides expert guidance on Swift Concurrency, covering modern async/
 6. For migration work, optimize for minimal blast radius (small, reviewable changes) and add verification steps.
 7. Course references are for deeper learning only. Use them sparingly and only when they clearly help answer the developer's question.
 
+## Triage Checklist (Before Advising)
+
+- Capture the exact compiler diagnostics and the offending symbol(s).
+- Identify the current isolation boundary and module defaults (`@MainActor`, custom actor, default isolation).
+- Confirm whether the code is UI-bound or intended to run off the main actor.
+
+## Quick Fix Mode (Use When)
+
+Use Quick Fix Mode when:
+- The errors are localized (single file or one type) and the isolation boundary is clear.
+- The fix does not require API redesign or multi-module changes.
+- You can explain the fix in 1–2 steps without changing behavior.
+
+Skip Quick Fix Mode when:
+- Default isolation or strict concurrency settings are unknown and likely affect behavior.
+- The error crosses module boundaries or involves public API changes.
+- The fix would require `@unchecked Sendable`, `@preconcurrency`, or `nonisolated(unsafe)` without a clear invariant.
+
 ## Recommended Tools for Analysis
 
 When analyzing Swift projects for concurrency issues:
@@ -55,6 +73,38 @@ Concurrency behavior depends on build settings. Always try to determine:
 
 If any of these are unknown, ask the developer to confirm them before giving migration-sensitive guidance.
 
+## Smallest Safe Fixes (Quick Wins)
+
+Prefer edits that preserve behavior while satisfying data-race safety.
+
+- **UI-bound types**: isolate the type or specific members to `@MainActor` (justify why UI-bound).
+- **Global/static mutable state**: move into an `actor` or isolate to `@MainActor` if UI-only.
+- **Background work**: for work that should always hop off the caller’s isolation, move expensive work into an `async` function marked `@concurrent`; for work that doesn’t touch isolated state but can inherit the caller’s isolation (for example with `NonisolatedNonsendingByDefault`), use `nonisolated` without `@concurrent`, or use an `actor` to guard mutable state.
+- **Sendable errors**: prefer immutable/value types; avoid `@unchecked Sendable` unless you can prove and document thread safety.
+
+## Quick Fix Playbook (Common Diagnostics -> Minimal Fix)
+
+- **"Main actor-isolated ... cannot be used from a nonisolated context"**
+  - Quick fix: if UI-bound, make the caller `@MainActor` or hop with `await MainActor.run { ... }`.
+  - Escalate if this is non-UI code or causes reentrancy; use `references/actors.md`.
+- **"Actor-isolated type does not conform to protocol"**
+  - Quick fix: add isolated conformance (e.g., `extension Foo: @MainActor SomeProtocol`).
+  - Escalate if the protocol requirements must be `nonisolated`; use `references/actors.md`.
+- **"Sending value of non-Sendable type ... risks causing data races"**
+  - Quick fix: confine access inside an actor or convert to a value type with immutable (`let`) state.
+  - Escalate before `@unchecked Sendable`; use `references/sendable.md` and `references/threading.md`.
+- **SwiftLint `async_without_await`**
+  - Quick fix: remove `async` if not required; if required by protocol/override/@concurrent, use narrow suppression with rationale. See `references/linting.md`.
+- **"wait(...) is unavailable from asynchronous contexts" (XCTest)**
+  - Quick fix: use `await fulfillment(of:)` or Swift Testing equivalents. See `references/testing.md`.
+
+## Escalation Path (When Quick Fixes Aren't Enough)
+
+1. Gather project settings (default isolation, strict concurrency level, upcoming features).
+2. Re-evaluate isolation boundaries and which types cross them.
+3. Use the decision tree + references for the deeper fix.
+4. If behavior changes are possible, document the invariant and add tests/verification steps.
+
 ## Quick Decision Tree
 
 When a developer needs concurrency guidance, follow this decision tree:
@@ -99,6 +149,9 @@ When a developer needs concurrency guidance, follow this decision tree:
   - Then: use `references/actors.md` (global actors, `nonisolated`, isolated parameters) and `references/threading.md` (default isolation)
 - "Class property 'current' is unavailable from asynchronous contexts" (Thread APIs)
   - Use `references/threading.md` to avoid thread-centric debugging and rely on isolation + Instruments
+- "Actor-isolated type does not conform to protocol" (protocol conformance errors)
+  - First: determine whether the protocol requirements must execute on the actor (for example, UI work on `@MainActor`) or can safely be `nonisolated`.
+  - Then: follow the Quick Fix Playbook entry for actor-isolated protocol conformance and `references/actors.md` for implementation patterns (isolated conformances, `nonisolated` requirements, and escalation steps).
 - XCTest async errors like "wait(...) is unavailable from asynchronous contexts"
   - Use `references/testing.md` (`await fulfillment(of:)` and Swift Testing patterns)
 - Core Data concurrency warnings/errors
@@ -232,6 +285,7 @@ Load these files as needed for specific topics:
 ## Verification Checklist (When You Change Concurrency Code)
 
 - Confirm build settings (default isolation, strict concurrency, upcoming features) before interpreting diagnostics.
+- For Quick Fix Mode: compile the affected target/module and rerun the specific diagnostics or lints.
 - After refactors:
   - Run tests, especially concurrency-sensitive ones (see `references/testing.md`).
   - If performance-related, verify with Instruments (see `references/performance.md`).
PATCH

echo "Gold patch applied."
