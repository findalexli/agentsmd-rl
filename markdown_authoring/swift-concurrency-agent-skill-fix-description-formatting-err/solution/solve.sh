#!/usr/bin/env bash
set -euo pipefail

cd /workspace/swift-concurrency-agent-skill

# Idempotency guard
if grep -qF "description: 'Expert guidance on Swift Concurrency best practices, patterns, and" "swift-concurrency/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/swift-concurrency/SKILL.md b/swift-concurrency/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: swift-concurrency
-description: Expert guidance on Swift Concurrency best practices, patterns, and implementation. Use when developers mention: (1) Swift Concurrency, async/await, actors, or tasks, (2) "use Swift Concurrency" or "modern concurrency patterns", (3) migrating to Swift 6, (4) data races or thread safety issues, (5) refactoring closures to async/await, (6) @MainActor, Sendable, or actor isolation, (7) concurrent code architecture or performance optimization.
+description: 'Expert guidance on Swift Concurrency best practices, patterns, and implementation. Use when developers mention: (1) Swift Concurrency, async/await, actors, or tasks, (2) "use Swift Concurrency" or "modern concurrency patterns", (3) migrating to Swift 6, (4) data races or thread safety issues, (5) refactoring closures to async/await, (6) @MainActor, Sendable, or actor isolation, (7) concurrent code architecture or performance optimization.'
 ---
 # Swift Concurrency
 
PATCH

echo "Gold patch applied."
