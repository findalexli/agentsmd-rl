#!/usr/bin/env bash
set -euo pipefail

cd /workspace/swift-concurrency-agent-skill

# Idempotency guard
if grep -qF "7. Course references are for deeper learning only. Use them sparingly and only w" "swift-concurrency/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/swift-concurrency/SKILL.md b/swift-concurrency/SKILL.md
@@ -18,7 +18,18 @@ This skill provides expert guidance on Swift Concurrency, covering modern async/
    - a documented safety invariant
    - a follow-up ticket to remove or migrate it
 6. For migration work, optimize for minimal blast radius (small, reviewable changes) and add verification steps.
-7. Course references are for deeper learning only. Use them sparingly and only when they clearly help answer the developer’s question.
+7. Course references are for deeper learning only. Use them sparingly and only when they clearly help answer the developer's question.
+
+## Recommended Tools for Analysis
+
+When analyzing Swift projects for concurrency issues:
+
+1. **Project Settings Discovery**
+   - Use `Read` on `Package.swift` for SwiftPM settings (tools version, strict concurrency flags, upcoming features)
+   - Use `Grep` for `SWIFT_STRICT_CONCURRENCY` or `SWIFT_DEFAULT_ACTOR_ISOLATION` in `.pbxproj` files
+   - Use `Grep` for `SWIFT_UPCOMING_FEATURE_` to find enabled upcoming features
+
+
 
 ## Project Settings Intake (Evaluate Before Advising)
 
PATCH

echo "Gold patch applied."
