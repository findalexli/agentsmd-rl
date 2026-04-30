#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cc-sdd

# Idempotency guard
if grep -qF "Skills are located in `.windsurf/skills/kiro-*/SKILL.md`" "tools/cc-sdd/templates/agents/windsurf-skills/docs/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/tools/cc-sdd/templates/agents/windsurf-skills/docs/AGENTS.md b/tools/cc-sdd/templates/agents/windsurf-skills/docs/AGENTS.md
@@ -47,7 +47,7 @@ Project memory keeps persistent guidance (steering, specs notes, component docs)
 - Progress check: `@kiro-spec-status {feature}` (use anytime)
 
 ## Skills Structure
-Skills are located in `.windsurf/skills@kiro-*/SKILL.md`
+Skills are located in `.windsurf/skills/kiro-*/SKILL.md`
 - Each skill is a directory with a `SKILL.md` file
 - Use `/skills` to inspect currently available skills
 - Invoke a skill directly with `@kiro-<skill-name>`
PATCH

echo "Gold patch applied."
