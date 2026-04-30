#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "> **Note (March 2026):** This constraint reflects current Claude Code skill reso" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -117,6 +117,44 @@ Example:
 
 This prevents resolution failures when the plugin is installed alongside other plugins that may define agents with the same short name.
 
+## File References in Skills
+
+Each skill directory is a self-contained unit. A SKILL.md file must only reference files within its own directory tree (e.g., `references/`, `assets/`, `scripts/`) using relative paths from the skill root. Never reference files outside the skill directory — whether by relative traversal or absolute path.
+
+Broken patterns:
+
+- `../other-skill/references/schema.yaml` — relative traversal into a sibling skill
+- `/home/user/plugins/compound-engineering/skills/other-skill/file.md` — absolute path to another skill
+- `~/.claude/plugins/cache/marketplace/compound-engineering/1.0.0/skills/other-skill/file.md` — absolute path to an installed plugin location
+
+Why this matters:
+
+- **Runtime resolution:** Skills execute from the user's working directory, not the skill directory. Cross-directory paths and absolute paths will not resolve as expected.
+- **Unpredictable install paths:** Plugins installed from the marketplace are cached at versioned paths. Absolute paths that worked in the source repo will not match the installed layout, and the version segment changes on every release.
+- **Converter portability:** The CLI copies each skill directory as an isolated unit when converting to other agent platforms. Cross-directory references break because sibling directories are not included in the copy.
+
+If two skills need the same supporting file, duplicate it into each skill's directory. Prefer small, self-contained reference files over shared dependencies.
+
+> **Note (March 2026):** This constraint reflects current Claude Code skill resolution behavior and known path-resolution bugs ([#11011](https://github.com/anthropics/claude-code/issues/11011), [#17741](https://github.com/anthropics/claude-code/issues/17741), [#12541](https://github.com/anthropics/claude-code/issues/12541)). If Anthropic introduces a shared-files mechanism or cross-skill imports in the future, this guidance should be revisited with supporting documentation.
+
+## Platform-Specific Variables in Skills
+
+This plugin is authored once and converted for multiple agent platforms (Claude Code, Codex, Gemini CLI, etc.). Do not use platform-specific environment variables or string substitutions (e.g., `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_SKILL_DIR}`, `${CLAUDE_SESSION_ID}`, `CODEX_SANDBOX`, `CODEX_SESSION_ID`) in skill content without a graceful fallback that works when the variable is unavailable or unresolved.
+
+**Preferred approach — relative paths:** Reference co-located scripts and files using relative paths from the skill directory (e.g., `bash scripts/my-script.sh ARG`). All major platforms resolve these relative to the skill's directory. No variable prefix needed.
+
+**When a platform variable is unavoidable:** Use the pre-resolution pattern (`!` backtick syntax) and include explicit fallback instructions in the skill content, so the agent knows what to do if the value is empty, literal, or an error:
+
+```
+**Plugin version (pre-resolved):** !`jq -r .version "${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json"`
+
+If the line above resolved to a semantic version (e.g., `2.42.0`), use it.
+Otherwise (empty, a literal command string, or an error), use the versionless fallback.
+Do not attempt to resolve the version at runtime.
+```
+
+This applies equally to any platform's variables — a skill converted from Codex, Gemini, or any other platform will have the same problem if it assumes platform-only variables exist without a fallback.
+
 ## Repository Docs Convention
 
 - **Requirements** live in `docs/brainstorms/` — requirements exploration and ideation.
PATCH

echo "Gold patch applied."
