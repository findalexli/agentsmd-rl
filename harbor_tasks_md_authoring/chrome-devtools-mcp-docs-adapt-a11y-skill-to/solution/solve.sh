#!/usr/bin/env bash
set -euo pipefail

cd /workspace/chrome-devtools-mcp

# Idempotency guard
if grep -qF "node -e \"const r=require('./report.json'); Object.values(r.audits).filter(a=>a.s" "skills/a11y-debugging/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/a11y-debugging/SKILL.md b/skills/a11y-debugging/SKILL.md
@@ -11,16 +11,34 @@ description: Uses Chrome DevTools MCP for accessibility (a11y) debugging and aud
 
 ## Workflow Patterns
 
-### 1. Browser Issues & Audits
+### 1. Automated Audit (Lighthouse)
 
-Chrome automatically checks for common accessibility problems. Use `list_console_messages` to check for these native audits first:
+Start by running a Lighthouse accessibility audit to get a comprehensive baseline. This tool provides a high-level score and lists specific failing elements with remediation advice.
+
+1.  Run the audit:
+    - Set `mode` to `"navigation"` to refresh the page and capture load issues.
+    - Set `outputDirPath` (e.g., `/tmp/lh-report`) to save the full JSON report.
+2.  **Analyze the Summary**:
+    - Check `scores` (0-1 scale). A score < 1 indicates violations.
+    - Review `audits.failed` count.
+3.  **Review the Report (CRITICAL)**:
+    - **Parsing**: Do not read the entire file line-by-line. Use a CLI tool like `jq` or a Node.js one-liner to filter for failures:
+      ```bash
+      # Extract failing audits with their details
+      node -e "const r=require('./report.json'); Object.values(r.audits).filter(a=>a.score!==null && a.score<1).forEach(a=>console.log(JSON.stringify({id:a.id, title:a.title, items:a.details?.items})))"
+      ```
+    - This efficiently extracts the `selector` and `snippet` of failing elements without loading the full report into context.
+
+### 2. Browser Issues & Audits
+
+Chrome automatically checks for common accessibility problems. Use `list_console_messages` to check for these native audits:
 
 - `types`: `["issue"]`
 - `includePreservedMessages`: `true` (to catch issues that occurred during page load)
 
 This often reveals missing labels, invalid ARIA attributes, and other critical errors without manual investigation.
 
-### 2. Semantics & Structure
+### 3. Semantics & Structure
 
 The accessibility tree exposes the heading hierarchy and semantic landmarks.
 
@@ -29,7 +47,7 @@ The accessibility tree exposes the heading hierarchy and semantic landmarks.
 3.  **Check Heading Levels**: Ensure heading levels (`h1`, `h2`, `h3`, etc.) are logical and do not skip levels. The snapshot will include heading roles.
 4.  **Content Reordering**: Verify that the DOM order (which drives the accessibility tree) matches the visual reading order. Use `take_screenshot` to inspect the visual layout and compare it against the snapshot structure to catch CSS floats or absolute positioning that jumbles the logical flow.
 
-### 3. Labels, Forms & Text Alternatives
+### 4. Labels, Forms & Text Alternatives
 
 1.  Locate buttons, inputs, and images in the `take_snapshot` output.
 2.  Ensure interactive elements have an accessible name (e.g., a button should not just say `""` if it only contains an icon).
@@ -55,7 +73,7 @@ The accessibility tree exposes the heading hierarchy and semantic landmarks.
 
 4.  Check images for `alt` text.
 
-### 4. Focus & Keyboard Navigation
+### 5. Focus & Keyboard Navigation
 
 Testing "keyboard traps" and proper focus management without visual feedback relies on tracking the focused element.
 
@@ -64,7 +82,7 @@ Testing "keyboard traps" and proper focus management without visual feedback rel
 3.  Locate the element marked as focused in the snapshot to verify focus moved to the expected interactive element.
 4.  If a modal opens, focus must move into the modal and "trap" within it until closed.
 
-### 5. Tap Targets and Visuals
+### 6. Tap Targets and Visuals
 
 According to web.dev, tap targets should be at least 48x48 pixels with sufficient spacing. Since the accessibility tree doesn't show sizes, use `evaluate_script`:
 
@@ -78,7 +96,7 @@ el => {
 
 _Pass the element's `uid` from the snapshot as an argument to `evaluate_script`._
 
-### 6. Color Contrast
+### 7. Color Contrast
 
 To verify color contrast ratios, start by checking for native accessibility issues:
 
@@ -124,7 +142,7 @@ el => {
 
 _Pass the element's `uid` to test the contrast against WCAG AA (4.5:1 for normal text, 3:1 for large text)._
 
-### 7. Global Page Checks
+### 8. Global Page Checks
 
 Verify document-level accessibility settings often missed in component testing:
 
PATCH

echo "Gold patch applied."
