#!/usr/bin/env bash
set -euo pipefail

cd /workspace/android

# Idempotency guard
if grep -qF ".claude/skills/testing-android-code/SKILL.md" ".claude/skills/testing-android-code/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/testing-android-code/SKILL.md b/.claude/skills/testing-android-code/SKILL.md
@@ -245,8 +245,6 @@ fun `test exception`() {
 
 Common testing mistakes in Bitwarden. **For complete details and examples:** See `references/critical-gotchas.md`
 
-> **⛔ STOP — `@Suppress("MaxLineLength")`**: Do NOT add this annotation unless the `fun` declaration line **actually exceeds 100 characters**. Count the characters first. Do not copy it from nearby tests. Detekt will tell you if it's needed — when in doubt, leave it off.
-
 **Core Patterns:**
 - **assertCoroutineThrows + runTest** - Never wrap in `runTest`; call directly
 - **Static mock cleanup** - Always `unmockkStatic()` in `@After`
PATCH

echo "Gold patch applied."
