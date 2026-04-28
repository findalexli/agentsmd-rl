#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vscode

# Idempotency guard
if grep -qF "description: Accessibility guidelines for VS Code features \u2014 covers accessibilit" ".github/skills/accessibility/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/skills/accessibility/SKILL.md b/.github/skills/accessibility/SKILL.md
@@ -1,6 +1,6 @@
 ---
-name: vscode-accessibility
-description: Use when creating new UI or updating existing UI features. Accessibility guidelines for VS Code features — covers accessibility help dialogs, accessible views, verbosity settings, accessibility signals, ARIA alerts/status announcements, keyboard navigation, and ARIA labels/roles. Applies to both new interactive UI surfaces and updates to existing features.
+name: accessibility
+description: Accessibility guidelines for VS Code features — covers accessibility help dialogs, accessible views, verbosity settings, accessibility signals, ARIA alerts/status announcements, keyboard navigation, and ARIA labels/roles. Applies to both new interactive UI surfaces and updates to existing features. Use when creating new UI or updating existing UI features.
 ---
 
 When adding a **new interactive UI surface** to VS Code — a panel, view, widget, editor overlay, dialog, or any rich focusable component the user interacts with — you **must** provide three accessibility components (if they do not already exist for the feature):
PATCH

echo "Gold patch applied."
