#!/usr/bin/env bash
set -euo pipefail

cd /workspace/libretto

# Idempotency guard
if grep -qF "2. Check the action log for user interactions by running `npx libretto actions -" ".agents/skills/libretto/SKILL.md" && grep -qF "2. Check the action log for user interactions by running `npx libretto actions -" "packages/libretto/skill/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/libretto/SKILL.md b/.agents/skills/libretto/SKILL.md
@@ -16,6 +16,7 @@ Use the `npx libretto` CLI to automate web interactions, debug browser agent job
 Libretto sessions are **full-access by default**. You can use `exec` and `run` immediately after opening a session.
 
 **Rules:**
+
 - Always announce which session you opened and what page you are on.
 - Use `snapshot`, `network`, and `actions` first when debugging unknown page state.
 - Before any potentially mutating action (submit/save/delete, or non-idempotent API calls), describe what you are about to do and wait for explicit user confirmation.
@@ -436,7 +437,7 @@ After completing interactive exploration, **always generate the TypeScript workf
 **STOP AND ASK BEFORE GENERATING CODE.** Once the interactive workflow is figured out, pause and ask:
 
 1. "Are there any existing files or patterns in the codebase you want me to reference?"
-2. "Do you want me to incorporate any of your manual browser interactions from the actions log (`npx libretto actions --source user`) into the generated code?"
+2. Check the action log for user interactions by running `npx libretto actions --source user`. If there are any recorded user interactions, ask: "I see you performed some manual interactions in the browser (clicks, form fills, etc.). Would you like me to incorporate any of those into the generated code?" — and briefly list what you found. If there are no user interactions, skip this question entirely.
 3. "Any other guidance for how the production code should be structured?"
 
 Wait for the user's response before proceeding. Then:
diff --git a/packages/libretto/skill/SKILL.md b/packages/libretto/skill/SKILL.md
@@ -16,6 +16,7 @@ Use the `npx libretto` CLI to automate web interactions, debug browser agent job
 Libretto sessions are **full-access by default**. You can use `exec` and `run` immediately after opening a session.
 
 **Rules:**
+
 - Always announce which session you opened and what page you are on.
 - Use `snapshot`, `network`, and `actions` first when debugging unknown page state.
 - Before any potentially mutating action (submit/save/delete, or non-idempotent API calls), describe what you are about to do and wait for explicit user confirmation.
@@ -436,7 +437,7 @@ After completing interactive exploration, **always generate the TypeScript workf
 **STOP AND ASK BEFORE GENERATING CODE.** Once the interactive workflow is figured out, pause and ask:
 
 1. "Are there any existing files or patterns in the codebase you want me to reference?"
-2. "Do you want me to incorporate any of your manual browser interactions from the actions log (`npx libretto actions --source user`) into the generated code?"
+2. Check the action log for user interactions by running `npx libretto actions --source user`. If there are any recorded user interactions, ask: "I see you performed some manual interactions in the browser (clicks, form fills, etc.). Would you like me to incorporate any of those into the generated code?" — and briefly list what you found. If there are no user interactions, skip this question entirely.
 3. "Any other guidance for how the production code should be structured?"
 
 Wait for the user's response before proceeding. Then:
PATCH

echo "Gold patch applied."
