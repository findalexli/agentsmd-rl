#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ag-grid

# Idempotency guard
if grep -qF "While this transition is in progress, changes made to Theming API should be appl" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -139,6 +139,12 @@ Essential practices:
 -   Self-review your changes before proposing commits
 -   Ensure tests exercise real implementations, not test helpers
 
+#### Styling
+
+The grid is in transition from Legacy Themes (.scss files written in Sass under `/community-modules/styles/`) to the Theming API (.css written in modern nested CSS under `/packages/`).
+
+While this transition is in progress, changes made to Theming API should be applied to Legacy Themes. When reviewing a PR with changes to the Theming API CSS, if the same PR does not have corresponding changes to Legacy Themes, this should be flagged as a P1 level issue.
+
 ### Common Development Tasks
 
 #### Quick Playbooks
PATCH

echo "Gold patch applied."
