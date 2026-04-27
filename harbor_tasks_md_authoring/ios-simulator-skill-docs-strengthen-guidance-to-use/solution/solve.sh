#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ios-simulator-skill

# Idempotency guard
if grep -qF "The 12 scripts in this skill cover all common workflows. **Only use raw tools if" "skill/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skill/SKILL.md b/skill/SKILL.md
@@ -34,6 +34,34 @@ bash scripts/sim_health_check.sh
 - Python 3
 - IDB (optional but recommended)
 
+## ⚠️ Important: Use Skill Scripts, Not Raw Tools
+
+**Always use these skill scripts instead of running `xcrun simctl`, `idb`, or `xcodebuild` directly.**
+
+Why? This skill provides:
+- ✅ **Semantic navigation** - Find elements by meaning, not coordinates
+- ✅ **Progressive disclosure** - Minimal output by default, details on demand
+- ✅ **Structured data** - Consistent JSON output, not raw CLI text
+- ✅ **Error handling** - Clear, actionable error messages
+- ✅ **Token efficiency** - Optimized for AI agents (5-10 tokens vs 400+)
+
+**What you lose by using raw tools:**
+- Coordinate-based navigation (fragile, breaks on UI changes)
+- Massive token consumption (entire build logs, full accessibility trees)
+- Inconsistent output formats
+- Generic error messages
+
+**Example - Find and tap a button:**
+```bash
+# ❌ Fragile - uses raw coordinates
+idb ui tap 320 400  # Which element is this? Will it work next week?
+
+# ✅ Robust - semantic navigation with skill script
+python scripts/navigator.py --find-text "Login" --tap
+```
+
+The 12 scripts in this skill cover all common workflows. **Only use raw tools if you need something not covered by these scripts.**
+
 ## Configuration (Optional)
 
 The skill **automatically learns your simulator preferences**. No setup required!
@@ -806,23 +834,38 @@ python scripts/navigator.py --find-text "Login" --tap
 
 ---
 
-## Integration with Raw Tools
+## When to Use Raw Tools (Advanced)
 
-All scripts wrap lower-level tools, but you can always use them directly:
+The 12 scripts in this skill cover all standard workflows. Raw tools should only be used for edge cases not covered:
 
 ```bash
-# Use script (recommended - semantic)
+# ✅ Covered by skill - use script
 python scripts/navigator.py --find-text "Login" --tap
 
-# Or use raw IDB (if you have coordinates)
-idb ui tap 320 400
+# ⚠️ Not covered - only then use raw tool
+idb ui tap 320 400  # Only if you absolutely need coordinates
 
-# Or use raw simctl
-xcrun simctl launch booted com.example.app
+# ✅ Covered by skill - use script
+python scripts/app_launcher.py --launch com.example.app
 
-# Scripts are helpful abstractions, not restrictions
+# ⚠️ Not covered - only then use raw tool
+xcrun simctl launch booted com.example.app  # Bypass all skill benefits
 ```
 
+**Benefits you get with skill scripts:**
+- Robust semantic navigation (survives UI changes)
+- Token-efficient output (5-10 tokens vs 400+)
+- Structured error messages (clear fixes)
+- Consistent output across all scripts
+
+**What you lose with raw tools:**
+- Fragile coordinate-based navigation
+- Massive token consumption
+- Unstructured output
+- Generic error messages
+
+**Rule of thumb:** If one of the 12 scripts can do the job, use it. Never use raw tools for standard operations.
+
 ---
 
 ## Help for Each Script
PATCH

echo "Gold patch applied."
