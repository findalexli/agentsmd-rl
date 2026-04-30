#!/usr/bin/env bash
set -euo pipefail

cd /workspace/quarto-web

# Idempotency guard
if grep -qF "Shows a pre-release callout before X.Y ships, disappears automatically after \u2014 n" ".claude/rules/docs-authoring.md" && grep -qF "See `prerelease.lua` for implementation and #1961 for design rationale." "_extensions/prerelease/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/rules/docs-authoring.md b/.claude/rules/docs-authoring.md
@@ -0,0 +1,16 @@
+---
+paths:
+  - "docs/**/*.qmd"
+---
+
+# Docs Authoring
+
+## Prerelease shortcodes
+
+When documenting a feature introduced in a specific Quarto version, add at the top of the section:
+
+```
+{{< prerelease-callout X.Y >}}
+```
+
+Shows a pre-release callout before X.Y ships, disappears automatically after — never remove them manually. For blog posts use `type="blog"`. For URLs use `{{< prerelease-docs-url X.Y >}}`. See `_extensions/prerelease/` for details.
diff --git a/_extensions/prerelease/CLAUDE.md b/_extensions/prerelease/CLAUDE.md
@@ -0,0 +1,3 @@
+# Prerelease Extension
+
+See `prerelease.lua` for implementation and #1961 for design rationale.
PATCH

echo "Gold patch applied."
