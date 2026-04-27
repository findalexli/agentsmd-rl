#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "!`case \"${CLAUDE_SKILL_DIR}\" in */plugins/cache/*/compound-engineering/*/skills/" "plugins/compound-engineering/skills/ce-update/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/ce-update/SKILL.md b/plugins/compound-engineering/skills/ce-update/SKILL.md
@@ -1,76 +1,90 @@
 ---
 name: ce-update
 description: |
-  Check if the compound-engineering plugin is up to date and fix stale cache if not.
-  Use when the user says "update compound engineering", "check compound engineering version",
-  "ce update", "is compound engineering up to date", "update ce plugin", or reports issues
-  that might stem from a stale compound-engineering plugin version. This skill only works
-  in Claude Code — it relies on the plugin harness cache layout.
+  Check if the compound-engineering plugin is up to date and recommend the
+  update command if not. Use when the user says "update compound engineering",
+  "check compound engineering version", "ce update", "is compound engineering
+  up to date", "update ce plugin", or reports issues that might stem from a
+  stale compound-engineering plugin version. This skill only works in Claude
+  Code — it relies on the plugin harness cache layout.
 disable-model-invocation: true
 ce_platforms: [claude]
 ---
 
-# Check & Fix Plugin Version
+# Check Plugin Version
 
-Verify the installed compound-engineering plugin version matches the latest released
-version, and fix stale marketplace/cache state if it doesn't. Claude Code only.
+Verify the installed compound-engineering plugin version matches the latest
+release, and recommend the update command if it doesn't. Claude Code only.
 
 ## Pre-resolved context
 
-The sections below contain pre-resolved data. Only the **Plugin root path**
-determines whether this session is Claude Code — if it contains an error
-sentinel, an empty value, or a literal `${CLAUDE_PLUGIN_ROOT}` string, tell the
-user this skill only works in Claude Code and stop. The other sections may
+Only the **Skill directory** determines whether this session is Claude Code —
+if empty or unresolved, the skill requires Claude Code. The other sections may
 contain error sentinels even in valid Claude Code sessions; the decision logic
 below handles those cases.
 
-`CLAUDE_PLUGIN_ROOT` points at the currently-loaded plugin version directory
-(e.g. `~/.claude/plugins/cache/<marketplace>/compound-engineering/<version>`),
-so the plugin cache directory that holds every cached version is its parent.
+`${CLAUDE_SKILL_DIR}` is a Claude Code-documented substitution that resolves
+at skill-load time. For a marketplace-cached install it looks like
+`~/.claude/plugins/cache/<marketplace>/compound-engineering/<version>/skills/ce-update`,
+so the currently-loaded version is the basename two `dirname` levels up.
 
-**Plugin root path:**
-!`echo "${CLAUDE_PLUGIN_ROOT}" 2>/dev/null || echo '__CE_UPDATE_ROOT_FAILED__'`
+**Skill directory:**
+!`echo "${CLAUDE_SKILL_DIR}"`
 
 **Latest released version:**
 !`gh release list --repo EveryInc/compound-engineering-plugin --limit 30 --json tagName --jq '[.[] | select(.tagName | startswith("compound-engineering-v"))][0].tagName | sub("compound-engineering-v";"")' 2>/dev/null || echo '__CE_UPDATE_VERSION_FAILED__'`
 
-**Plugin cache directory:**
-!`case "$(dirname "${CLAUDE_PLUGIN_ROOT:-}")" in */cache/*/compound-engineering) dirname "${CLAUDE_PLUGIN_ROOT}" ;; *) echo '__CE_UPDATE_CACHE_FAILED__' ;; esac`
+**Currently loaded version:**
+!`case "${CLAUDE_SKILL_DIR}" in */plugins/cache/*/compound-engineering/*/skills/ce-update) basename "$(dirname "$(dirname "${CLAUDE_SKILL_DIR}")")" ;; *) echo '__CE_UPDATE_NOT_MARKETPLACE__' ;; esac`
 
-**Cached version folder(s):**
-!`case "$(dirname "${CLAUDE_PLUGIN_ROOT:-}")" in */cache/*/compound-engineering) ls "$(dirname "${CLAUDE_PLUGIN_ROOT}")" 2>/dev/null ;; *) echo '__CE_UPDATE_CACHE_FAILED__' ;; esac`
+**Marketplace name:**
+!`case "${CLAUDE_SKILL_DIR}" in */plugins/cache/*/compound-engineering/*/skills/ce-update) basename "$(dirname "$(dirname "$(dirname "$(dirname "${CLAUDE_SKILL_DIR}")")")")" ;; *) echo '__CE_UPDATE_NOT_MARKETPLACE__' ;; esac`
 
 ## Decision logic
 
 ### 1. Platform gate
 
-If **Plugin root path** contains `__CE_UPDATE_ROOT_FAILED__`, a literal
-`${CLAUDE_PLUGIN_ROOT}` string, or is empty: tell the user this skill requires Claude Code
-and stop. No further action.
+If **Skill directory** is empty or unresolved: tell the user this skill
+requires Claude Code and stop. No further action.
 
-### 2. Compare versions
+### 2. Handle failure cases
 
-If **Latest released version** contains `__CE_UPDATE_VERSION_FAILED__`: tell the user the
-latest release could not be fetched (gh may be unavailable or rate-limited) and stop.
+If **Latest released version** contains `__CE_UPDATE_VERSION_FAILED__`: tell
+the user the latest release could not be fetched (gh may be unavailable or
+rate-limited) and stop.
 
-If **Cached version folder(s)** contains `__CE_UPDATE_CACHE_FAILED__`: no marketplace cache
-exists. Tell the user: "No marketplace cache found — this appears to be a local dev checkout
-or fresh install." and stop.
+If **Currently loaded version** contains `__CE_UPDATE_NOT_MARKETPLACE__`: this
+session loaded the skill from outside the standard marketplace cache (typical
+when using `claude --plugin-dir` for local development, or for a non-standard
+install). Tell the user (substituting the actual path):
 
-Take the **latest released version** and the **cached folder list**.
+> "Skill is loaded from `{skill-directory}` — not the standard marketplace
+> cache at `~/.claude/plugins/cache/`. This is normal when using
+> `claude --plugin-dir` for local development. No action for this session.
+> Your marketplace install (if any) is unaffected — run `/ce-update` in a
+> regular Claude Code session (no `--plugin-dir`) to check that cache."
 
-**Up to date** — exactly one cached folder exists AND its name matches the latest version:
-- Tell the user: "compound-engineering **v{version}** is installed and up to date."
+Then stop.
 
-**Out of date or corrupted** — multiple cached folders exist, OR the single folder name
-does not match the latest version. Use the **Plugin cache directory** value from above
-as the delete path.
+### 3. Compare versions
 
-**Clear the stale cache:**
-```bash
-rm -rf "<plugin-cache-directory>"
-```
+**Up to date** — `{currently loaded} == {latest}`:
 
-Tell the user:
-- "compound-engineering was on **v{old}** but **v{latest}** is available."
-- "Cleared the plugin cache. Now run `/plugin marketplace update` in this session, then restart Claude Code to pick up v{latest}."
+> "compound-engineering **v{version}** is installed and up to date."
+
+**Out of date** — `{currently loaded} != {latest}`:
+
+> "compound-engineering is on **v{currently loaded}** but **v{latest}** is available.
+>
+> Update with:
+> ```
+> claude plugin update compound-engineering@{marketplace-name}
+> ```
+> Then restart Claude Code to apply."
+
+The `claude plugin update` command ships with Claude Code itself and updates
+installed plugins to their latest version; it replaces earlier manual cache
+sweep / marketplace-refresh workarounds. The marketplace name is derived from
+the skill path rather than hardcoded because this plugin is distributed under
+multiple marketplace names (for example, `compound-engineering-plugin` for
+public installs per the README, or other names for internal/team marketplaces).
PATCH

echo "Gold patch applied."
