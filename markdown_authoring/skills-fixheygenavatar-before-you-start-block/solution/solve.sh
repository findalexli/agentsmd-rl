#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "**\u26a0\ufe0f Do NOT fetch HeyGen avatars yet.** That's a Phase 0 sub-step (only after ta" "heygen-avatar/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/heygen-avatar/SKILL.md b/heygen-avatar/SKILL.md
@@ -36,27 +36,16 @@ Create and manage HeyGen avatars for anyone: the agent, the user, or named chara
 
 **Prompt-based is the default creation path.** Photo is opt-in, only relevant when the user explicitly wants a real-person digital twin of themselves. Agents and named characters almost always use prompt-based creation.
 
-## Before You Start (Claude Code only)
+## Before You Start (environment detection)
 
 Try to read `SOUL.md` from the workspace root.
 
-- **Found** → OpenClaw environment. Skip this section entirely and go straight to Phase 0.
-- **Not found** → Claude Code environment. Say this before anything else:
-
-First, fetch the user's existing HeyGen avatars.
-
-**MCP:** `list_avatar_groups(ownership=private)` — returns the user's private avatar groups.
-**CLI:** `heygen avatar list --ownership private`
-
-Parse the `data` array.
+- **Found** → OpenClaw environment. Skip this entire section and go straight to Phase 0. Workspace-native identity (SOUL.md, IDENTITY.md) will drive agent onboarding.
+- **Not found** → Claude Code environment, no workspace identity files. Still go to Phase 0 next — do NOT skip ahead to listing user avatars or asking the user for a photo.
 
 **⚠️ AVATAR file caveat:** Ignore any AVATAR-*.md files found in the workspace that belong to a *different* person or agent (e.g., AVATAR-Eve.md when creating an avatar for Claude). Only use an AVATAR file if its name matches the subject you're creating for right now.
 
-If the user **has existing avatars** (non-empty `data` array), present them as numbered options and ask which to use or whether to create a new one. Communicate in `user_language`.
-
-If the user has **no existing avatars** (empty `data`), tell them none were found and offer to create one with a few quick questions. Mention the OpenClaw `SOUL.md` shortcut for future reference. Communicate in `user_language`.
-
-Wait for their answer before proceeding.
+**⚠️ Do NOT fetch HeyGen avatars yet.** That's a Phase 0 sub-step (only after target detection). Fetching before Phase 0 causes the agent to frame the conversation around "your existing avatars" when the default should be creating one for the agent itself.
 
 ## API Mode Detection
 
@@ -149,6 +138,13 @@ Then check `AVATAR-<NAME>.md` at the workspace root:
 - **AVATAR file exists but HeyGen section empty** → skip to Phase 2.
 - **No AVATAR file** → proceed to Phase 1.
 
+**Optional existing-avatar check** (only useful on the user path when the user might already have avatars in their HeyGen account). If Phase 0 target = **user** AND no `AVATAR-<USER>.md` exists, list their HeyGen avatars first:
+
+**MCP:** `list_avatar_groups(ownership=private)`
+**CLI:** `heygen avatar list --ownership private`
+
+If the list is non-empty, present the options and ask which to use or whether to create new. If empty, proceed to Phase 1. Skip this check entirely for agent and named-character targets — those live in AVATAR-*.md, not the HeyGen catalog.
+
 ### Phase 1 — Identity Extraction
 
 **Order matters. Files first, questions second. Prompt-based creation is the default path — photo is an opt-in upgrade.**
PATCH

echo "Gold patch applied."
