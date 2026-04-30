#!/usr/bin/env bash
set -euo pipefail

cd /workspace/it-autonomos-spain

# Idempotency guard
if grep -qF "**CRITICAL RULE**: When renaming any heading that may have been publicly shared," "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -197,6 +197,27 @@ The site uses **different Telegram links for different languages**:
 
 Always use the correct link for the language version you're working on.
 
+### Legacy Anchors for Renamed Content
+
+**CRITICAL RULE**: When renaming any heading that may have been publicly shared, ALWAYS add a legacy anchor to preserve old links.
+
+Add invisible anchor with the old ID immediately before the new heading:
+
+```markdown
+<span id="old-anchor-id" class="legacy-anchor"></span>
+## New Heading Name
+```
+
+Example:
+```markdown
+<span id="денис-и" class="legacy-anchor"></span>
+## Денис И. - Хестор
+```
+
+**Important**:
+- Never remove legacy anchors once added
+- Apply to ALL language versions when renaming content
+
 ## Code Standards
 
 ### CSS
@@ -259,6 +280,7 @@ Apply consistently across all partners; don't hardcode exceptions.
 - [ ] Internal links use `{% raw %}{% link path.md %}{% endraw %}`
 - [ ] External links have `{:target="_blank"}`
 - [ ] Correct Telegram links for Russian version
+- [ ] Legacy anchor added if content/heading was renamed
 - [ ] Markdown formatting correct
 - [ ] **STOPPED - waiting for user approval**
 
@@ -273,5 +295,6 @@ Apply consistently across all partners; don't hardcode exceptions.
 - [ ] Only short hyphen "-" used in all versions (no em dash "—" or en dash "–")
 - [ ] All formatting preserved exactly
 - [ ] Correct Telegram links for each language
+- [ ] Legacy anchors added in ALL language versions if content was renamed
 - [ ] Updated all 4 index files (if structure changed)
 - [ ] All navigation links work in all languages
PATCH

echo "Gold patch applied."
