#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vibe-remote

# Idempotency guard
if grep -qF "- keep the selected reasoning value compatible with the chosen model; common val" "skills/use-vibe-remote/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/use-vibe-remote/SKILL.md b/skills/use-vibe-remote/SKILL.md
@@ -181,6 +181,7 @@ Channel scope entry:
     "opencode_reasoning_effort": null,
     "claude_agent": null,
     "claude_model": null,
+    "claude_reasoning_effort": null,
     "codex_model": "gpt-5.4",
     "codex_reasoning_effort": "high"
   },
@@ -201,7 +202,8 @@ User scope entry:
   "routing": {
     "agent_backend": "claude",
     "claude_agent": "reviewer",
-    "claude_model": "sonnet"
+    "claude_model": "claude-sonnet-4-6",
+    "claude_reasoning_effort": "high"
   },
   "dm_chat_id": "D123456"
 }
@@ -272,15 +274,16 @@ Current Vibe Remote routing support is:
 | Backend | Channel/User backend select | Subagent | Model | Reasoning |
 | --- | --- | --- | --- | --- |
 | OpenCode | yes | yes | yes | yes |
-| Claude | yes | yes | yes | not currently applied by Vibe Remote runtime |
+| Claude | yes | yes | yes | yes |
 | Codex | yes | no | yes | yes |
 
 Behavior notes:
 
 - OpenCode subagents are selected through `routing.opencode_agent` or through prefix routing such as `reviewer: ...`.
 - Claude subagents are selected through `routing.claude_agent` or prefix routing.
+- Claude reasoning is selected through `routing.claude_reasoning_effort`; common values are `low`, `medium`, and `high`, and some models also allow `max`.
 - Codex subagents are not currently supported in Vibe Remote routing.
-- Current Vibe Remote behavior does not apply channel-level Claude reasoning control. Do not promise that setting as an available per-scope feature.
+- If a Claude reasoning value is invalid for the chosen model, Vibe Remote drops that override and falls back to the backend default.
 
 ## Subagent and Prefix Routing
 
@@ -418,7 +421,25 @@ Action:
 
 If the user instead wants to change OpenCode-native defaults such as model, reasoning, providers, or MCP behavior across projects, edit OpenCode config rather than Vibe Remote. If the user wants Vibe Remote to use a specific OpenCode agent in one scope, edit `routing.opencode_agent` in `settings.json`.
 
-### Recipe 3: Change the global default working directory
+### Recipe 3: Route one scope to Claude with model and reasoning
+
+User intent:
+
+- use Claude in one channel or DM
+- choose subagent `reviewer`
+- choose model `claude-sonnet-4-6`
+- set reasoning `high`
+
+Action:
+
+- edit `settings.json`
+- set `routing.agent_backend = "claude"`
+- set `routing.claude_agent = "reviewer"` if requested
+- set `routing.claude_model = "claude-sonnet-4-6"`
+- set `routing.claude_reasoning_effort = "high"`
+- keep the selected reasoning value compatible with the chosen model; common values are `low`, `medium`, and `high`, while `max` is only valid on supported models
+
+### Recipe 4: Change the global default working directory
 
 User intent:
 
@@ -430,7 +451,7 @@ Action:
 - set `runtime.default_cwd`
 - do not overwrite scope-level `custom_cwd` entries in `settings.json`
 
-### Recipe 4: Show tool execution messages in one channel
+### Recipe 5: Show tool execution messages in one channel
 
 User intent:
 
@@ -442,7 +463,7 @@ Action:
 - add `toolcall`
 - preserve existing `system` and `assistant` values unless the user asked for a full replacement
 
-### Recipe 5: Switch the whole installation from Slack to Discord
+### Recipe 6: Switch the whole installation from Slack to Discord
 
 User intent:
 
@@ -527,7 +548,7 @@ Relevant docs:
 
 - subagents: `https://docs.anthropic.com/en/docs/claude-code/sub-agents`
 
-Remember: current Vibe Remote behavior supports Claude backend selection, model, and subagent routing, but not channel-level Claude reasoning control.
+Inside Vibe Remote, Claude scope routing currently controls backend choice, model, subagent, and reasoning effort.
 
 ### Codex
 
PATCH

echo "Gold patch applied."
