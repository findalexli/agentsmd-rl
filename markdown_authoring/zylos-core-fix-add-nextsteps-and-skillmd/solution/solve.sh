#!/usr/bin/env bash
set -euo pipefail

cd /workspace/zylos-core

# Idempotency guard
if grep -qF "5. **Next Steps**: If `skill.nextSteps` exists, follow the instructions \u2014 this t" "skills/component-management/references/install.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/component-management/references/install.md b/skills/component-management/references/install.md
@@ -93,3 +93,5 @@ After `zylos add <name> --json` succeeds, the JSON `skill` field tells you what
 2. **Config**: If `skill.config.required` exists, inform user which config values are needed. In C4 mode, user provides values via follow-up messages.
 3. **Hooks**: If `skill.hooks.post-install` exists, run it (with PATH prefix if step 1 applied).
 4. **Service**: If `skill.service` exists, start it and verify.
+5. **Next Steps**: If `skill.nextSteps` exists, follow the instructions — this typically includes post-service-start guidance (e.g., configuring webhook URLs, optional security settings). Always show these to the user.
+6. **SKILL.md**: If the component's SKILL.md has additional setup documentation beyond the frontmatter, read and follow it for any remaining configuration steps.
PATCH

echo "Gold patch applied."
