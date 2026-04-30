#!/usr/bin/env bash
set -euo pipefail

cd /workspace/anytype-swift

# Idempotency guard
if grep -qF "- **Code Review Guidelines**: `/.github/workflows/code-review-guidelines.md` - S" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -155,6 +155,7 @@ When removing code that uses localization keys, **always check if the key is sti
 - **Design System Mapping**: `/PresentationLayer/Common/DESIGN_SYSTEM_MAPPING.md`
 - **Typography Mapping**: `/PresentationLayer/Common/TYPOGRAPHY_MAPPING.md` - Maps Figma text styles to Swift constants
 - **Analytics Patterns**: `/PresentationLayer/Common/Analytics/ANALYTICS_PATTERNS.md`
+- **Code Review Guidelines**: `/.github/workflows/code-review-guidelines.md` - Shared review standards for local and automated CI reviews
 
 ### Icons
 Icons are code-generated from assets organized by size (x18, x24, x32, x40).
PATCH

echo "Gold patch applied."
