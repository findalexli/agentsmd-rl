#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vibe-remote

# Idempotency guard
if grep -qF "Important DM caveat: current DM authorization checks whether the user is bound, " "skills/use-vibe-remote/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/use-vibe-remote/SKILL.md b/skills/use-vibe-remote/SKILL.md
@@ -47,18 +47,6 @@ Important paths:
 - `~/.vibe_remote/runtime/doctor.json`: latest doctor result
 - `~/.vibe_remote/attachments/`: attachment staging area
 
-Repository source-of-truth files for maintainers:
-
-- `config/paths.py`
-- `config/v2_config.py`
-- `config/v2_settings.py`
-- `config/v2_sessions.py`
-- `core/controller.py`
-- `core/handlers/session_handler.py`
-- `modules/agents/opencode/agent.py`
-- `modules/agents/codex/agent.py`
-- `modules/agents/subagent_router.py`
-
 ## Edit Workflow
 
 When changing Vibe Remote config, use this order:
@@ -79,7 +67,9 @@ cp ~/.vibe_remote/config/config.json ~/.vibe_remote/config/config.json.bak.$(dat
 6. Validate the file, for example:
 
 ```bash
-python3 -c "import json,sys; json.load(open(sys.argv[1]))" ~/.vibe_remote/state/settings.json
+VIBE_HOME="${VIBE_REMOTE_HOME:-$HOME/.vibe_remote}"
+TARGET_FILE="$VIBE_HOME/state/settings.json"  # or the exact file you just edited
+python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$TARGET_FILE"
 ```
 
 7. If the config change affects behavior, recommend:
@@ -219,13 +209,15 @@ User scope entry:
 
 Meaning of important fields:
 
-- `enabled`: whether the channel or bound DM user can use the bot
+- `enabled`: for channel scopes, this is the enforceable on/off gate; for DM user scopes, do not treat it as the access-control source of truth
 - `show_message_types`: which intermediate messages are visible; allowed values are `system`, `assistant`, `toolcall`
 - `custom_cwd`: scope-level working directory override
 - `routing`: backend choice and backend-specific overrides
 - `require_mention`: channel-level override for mention gating; `null` means use platform global default
 - `bind_codes`: DM authorization codes
 
+Important DM caveat: current DM authorization checks whether the user is bound, not whether `scopes.user.<platform>.<user_id>.enabled` is `true`. If the user wants to revoke DM access, do not rely on flipping `enabled` to `false`; use the supported unbind/remove-user path instead.
+
 If a user asks for "vault messages", "internal messages", or "tool execution messages", map that request to `show_message_types`. Current Vibe Remote does not expose a separate `vault` field.
 
 ### `sessions.json`
@@ -283,12 +275,12 @@ Current Vibe Remote routing support is:
 | Claude | yes | yes | yes | not currently applied by Vibe Remote runtime |
 | Codex | yes | no | yes | yes |
 
-Implementation notes:
+Behavior notes:
 
 - OpenCode subagents are selected through `routing.opencode_agent` or through prefix routing such as `reviewer: ...`.
 - Claude subagents are selected through `routing.claude_agent` or prefix routing.
 - Codex subagents are not currently supported in Vibe Remote routing.
-- Current Claude runtime code accepts `subagent_reasoning_effort` in the request object but does not apply it to the backend execution path. Do not promise channel-level Claude reasoning control unless the repo implementation changes.
+- Current Vibe Remote behavior does not apply channel-level Claude reasoning control. Do not promise that setting as an available per-scope feature.
 
 ## Subagent and Prefix Routing
 
@@ -381,7 +373,9 @@ If you must adjust an existing DM user scope:
 
 - read the existing user entry first
 - preserve `display_name`, `is_admin`, `bound_at`, and `dm_chat_id`
-- only change requested keys such as `enabled`, `custom_cwd`, `show_message_types`, or `routing`
+- only change requested keys such as `custom_cwd`, `show_message_types`, or `routing`
+
+If the user wants to revoke an existing DM binding, treat that as a bind-state change rather than a normal settings toggle. In the current implementation, removing the user entry is the reliable way to revoke bound DM access.
 
 Avoid creating fake bind or admin state unless the user explicitly asks for manual recovery.
 
@@ -533,7 +527,7 @@ Relevant docs:
 
 - subagents: `https://docs.anthropic.com/en/docs/claude-code/sub-agents`
 
-Remember: current Vibe Remote runtime supports Claude backend selection, model, and subagent routing, but not channel-level Claude reasoning control in the active code path.
+Remember: current Vibe Remote behavior supports Claude backend selection, model, and subagent routing, but not channel-level Claude reasoning control.
 
 ### Codex
 
@@ -563,11 +557,25 @@ Always follow these constraints:
 
 - never delete unrelated platform scopes from `settings.json`
 - never blank out tokens or secrets as part of an unrelated config task
-- never claim a backend feature exists if the current repo does not apply it
+- never claim a backend feature exists if current Vibe Remote behavior does not actually support it
 - never manually rewrite `sessions.json` for routine routing changes
 - never expose bind codes unless the user explicitly asks
 - always say when a requested change actually belongs in OpenCode, Claude Code, or Codex config instead of Vibe Remote
 
+## Escalation
+
+If the user still cannot solve a problem after normal config fixes, `vibe doctor`, restart, and log inspection, point them to the Vibe Remote repository:
+
+- repo: `https://github.com/cyhhao/vibe-remote`
+
+Use that link when:
+
+- the behavior looks like a real bug rather than a local misconfiguration
+- the user is asking for a feature Vibe Remote does not support yet
+- backend integration behavior appears inconsistent with the documented configuration surface
+
+If the user wants to contribute back, suggest opening an issue or a pull request in that repository.
+
 ## Response Pattern
 
 When you complete a Vibe Remote maintenance task, report back with:
PATCH

echo "Gold patch applied."
