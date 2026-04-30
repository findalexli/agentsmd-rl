#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lynx-website

# Idempotency guard
if grep -qF "- The `svg` element differs significantly from its web counterpart. Pass the SVG" "docs/public/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/docs/public/AGENTS.md b/docs/public/AGENTS.md
@@ -43,7 +43,13 @@
 
 Additionally:
 
-- The `svg` element differs significantly from its web counterpart. Pass the SVG markup through the `content` attribute on `<svg />`.
+- The `svg` element differs significantly from its web counterpart. Pass the SVG markup through the `content` attribute or SVG url through the `src` attribute on `<svg />`:
+  
+  ```jsx
+  <svg content={`<svg ... />`} />;
+  // or
+  <svg src={urlOfYourSvgFile} />;
+  ```
 
 ## 5. Layout System: Block by Default with Four Layout Modes
 
PATCH

echo "Gold patch applied."
