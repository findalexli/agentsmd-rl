#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agent-skills

# Idempotency guard
if grep -qF "description: Provides React Native performance optimization guidelines for FPS, " "skills/react-native-best-practices/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/react-native-best-practices/SKILL.md b/skills/react-native-best-practices/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: react-native-best-practices
-description: React Native performance optimization guidelines from Callstack's Ultimate Guide. Use this skill when writing, reviewing, or debugging React Native code for performance issues. Triggers on tasks involving FPS optimization, TTI improvement, bundle size reduction, native module development, memory leaks, or animation performance.
+description: Provides React Native performance optimization guidelines for FPS, TTI, bundle size, memory leaks, re-renders, and animations. Applies to tasks involving Hermes optimization, JS thread blocking, bridge overhead, FlashList, native modules, or debugging jank and frame drops.
 license: MIT
 metadata:
   author: Callstack
PATCH

echo "Gold patch applied."
