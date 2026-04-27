#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "description: 'Build web interfaces with genuine design quality, not AI slop. Use" "plugins/compound-engineering/skills/frontend-design/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/frontend-design/SKILL.md b/plugins/compound-engineering/skills/frontend-design/SKILL.md
@@ -1,11 +1,6 @@
 ---
 name: frontend-design
-description: Build web interfaces with genuine design quality, not AI slop. Use for
-  any frontend work: landing pages, web apps, dashboards, admin panels, components,
-  interactive experiences. Activates for both greenfield builds and modifications to
-  existing applications. Detects existing design systems and respects them. Covers
-  composition, typography, color, motion, and copy. Verifies results via screenshots
-  before declaring done.
+description: 'Build web interfaces with genuine design quality, not AI slop. Use for any frontend work - landing pages, web apps, dashboards, admin panels, components, interactive experiences. Activates for both greenfield builds and modifications to existing applications. Detects existing design systems and respects them. Covers composition, typography, color, motion, and copy. Verifies results via screenshots before declaring done.'
 ---
 
 # Frontend Design
PATCH

echo "Gold patch applied."
