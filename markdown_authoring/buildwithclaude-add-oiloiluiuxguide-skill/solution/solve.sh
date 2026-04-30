#!/usr/bin/env bash
set -euo pipefail

cd /workspace/buildwithclaude

# Idempotency guard
if grep -qF "description: Modern, clean UI/UX guidance + review skill. Use when you need acti" "plugins/all-skills/skills/oiloil-ui-ux-guide/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/all-skills/skills/oiloil-ui-ux-guide/SKILL.md b/plugins/all-skills/skills/oiloil-ui-ux-guide/SKILL.md
@@ -0,0 +1,15 @@
+---
+name: oiloil-ui-ux-guide
+description: Modern, clean UI/UX guidance + review skill. Use when you need actionable UX/UI recommendations, design principles, or a design review checklist for new features or existing systems (web/app). Focus on CRAP (Contrast/Repetition/Alignment/Proximity) plus task-first UX, information architecture, feedback & system status, consistency, affordances, error prevention/recovery, and cognitive load. Enforce a modern minimal style (clean, spacious, typography-led), reduce unnecessary copy, forbid emoji as icons, and recommend intuitive refined icons from a consistent icon set.
+---
+
+# OilOil UI/UX Guide
+
+Modern UI/UX guidance and review skill with two modes:
+
+- `guide`: Actionable do/don't rules for modern clean UI/UX
+- `review`: Prioritized P0/P1/P2 fix lists with design psychology diagnosis
+
+Full skill with references available at: https://github.com/oil-oil/oiloil-ui-ux-guide
+
+Install via: `npx skills add oil-oil/oiloil-ui-ux-guide`
PATCH

echo "Gold patch applied."
