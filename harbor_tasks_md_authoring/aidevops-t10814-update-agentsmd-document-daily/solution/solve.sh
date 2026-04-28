#!/usr/bin/env bash
set -euo pipefail

cd /workspace/aidevops

# Idempotency guard
if grep -qF "**Daily skill refresh**: Each auto-update check also runs a 24h-gated skill fres" ".agents/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/AGENTS.md b/.agents/AGENTS.md
@@ -412,6 +412,10 @@ Automatic polling for new releases. Checks GitHub every 10 minutes and runs `aid
 
 **Logs**: `~/.aidevops/logs/auto-update.log`
 
+**Daily skill refresh**: Each auto-update check also runs a 24h-gated skill freshness check. If >24h have passed since the last check, `skill-update-helper.sh --auto-update --quiet` pulls upstream changes for all imported skills. State is tracked in `~/.aidevops/cache/auto-update-state.json` (`last_skill_check`, `skill_updates_applied`). Disable with `AIDEVOPS_SKILL_AUTO_UPDATE=false`; adjust frequency with `AIDEVOPS_SKILL_FRESHNESS_HOURS=<hours>` (default: 24). View skill check status with `aidevops auto-update status`.
+
+**Repo version wins on update**: When `aidevops update` runs, shared agents in `~/.aidevops/agents/` are overwritten by the repo version. Only `custom/` and `draft/` directories are preserved. Imported skills stored outside these directories will be overwritten. To keep a skill across updates, either re-import it after each update or move it to `custom/`.
+
 ## Bot Reviewer Feedback
 
 AI code review bots (Gemini, CodeRabbit, Copilot) can provide incorrect suggestions. **Never blindly implement bot feedback.** Verify factual claims (versions, paths, APIs) against runtime/docs/project conventions before acting. Dismiss incorrect suggestions with evidence; address valid ones.
@@ -428,7 +432,9 @@ Development → @code-standards → /code-simplifier → /linters-local → /pr
 
 Import community skills: `aidevops skill add <source>` (→ `*-skill.md` suffix)
 
-**Cross-tool**: Claude marketplace plugin, Agent Skills (SKILL.md), OpenCode agents, manual AGENTS.md reference.
+**Cross-tool**: Claude marketplace plugin, Agent Skills (SKILL.md), Claude Code agents, manual AGENTS.md reference.
+
+**Skill persistence**: Imported skills are stored in `~/.aidevops/agents/` and tracked in `configs/skill-sources.json`. The daily auto-update skill refresh (see Auto-Update above) keeps them current from upstream. Note: `aidevops update` overwrites shared agent files — only `custom/` and `draft/` survive. Re-import skills after an update, or place them in `custom/` for persistence.
 
 **Full docs**: `scripts/commands/add-skill.md`
 
PATCH

echo "Gold patch applied."
