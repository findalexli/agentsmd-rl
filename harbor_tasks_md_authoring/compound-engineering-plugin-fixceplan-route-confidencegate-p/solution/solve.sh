#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "Developers of this plugin also use it via their marketplace install (`~/.claude/" "plugins/compound-engineering/AGENTS.md" && grep -qF "If the plan already appears sufficiently grounded and the thin-grounding overrid" "plugins/compound-engineering/skills/ce-plan/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/AGENTS.md b/plugins/compound-engineering/AGENTS.md
@@ -48,6 +48,15 @@ skills/
 > `/command-name` slash commands now live under `skills/command-name/SKILL.md`
 > and work identically in Claude Code. Other targets may convert or map these references differently.
 
+## Debugging Plugin Bugs
+
+Developers of this plugin also use it via their marketplace install (`~/.claude/plugins/`). When a developer reports a bug they experienced while using a skill or agent, the installed version may be older than the repo. Glob for the component name under `~/.claude/plugins/` and diff the installed content against the repo version.
+
+- **Repo already has the fix**: The developer's install is stale. Tell them to reinstall the plugin or use `--plugin-dir` to load skills from the repo checkout. No code change needed.
+- **Both versions have the bug**: Proceed with the fix normally.
+
+Important: Just because the developer's installed plugin may be out of date, it's possible both old and current repo versions have the bug. The proper fix is to still fix the repo version.
+
 ## Command Naming Convention
 
 **Workflow commands** use `ce:` prefix to unambiguously identify them as compound-engineering commands:
diff --git a/plugins/compound-engineering/skills/ce-plan/SKILL.md b/plugins/compound-engineering/skills/ce-plan/SKILL.md
@@ -696,7 +696,7 @@ Build a risk profile. Treat these as high-risk signals:
 - **Deep** or high-risk plans often benefit from a targeted second pass
 - **Thin local grounding override:** If Phase 1.2 triggered external research because local patterns were thin (fewer than 3 direct examples or adjacent-domain match), always proceed to scoring regardless of how grounded the plan appears. When the plan was built on unfamiliar territory, claims about system behavior are more likely to be assumptions than verified facts. The scoring pass is cheap — if the plan is genuinely solid, scoring finds nothing and exits quickly
 
-If the plan already appears sufficiently grounded and the thin-grounding override does not apply, report "Confidence check passed — no sections need strengthening" and proceed to Phase 5.4.
+If the plan already appears sufficiently grounded and the thin-grounding override does not apply, report "Confidence check passed — no sections need strengthening" and skip to Phase 5.3.8 (Document Review). Document-review always runs regardless of whether deepening was needed — the two tools catch different classes of issues.
 
 ##### 5.3.3 Score Confidence Gaps
 
PATCH

echo "Gold patch applied."
